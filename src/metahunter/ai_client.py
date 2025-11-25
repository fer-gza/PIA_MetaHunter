from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Opcional: integración con OpenAI (no es obligatoria)
# ---------------------------------------------------------------------------

try:
    # Nuevo SDK (openai>=1.0.0)
    from openai import OpenAI  # type: ignore[import]
    _HAS_OPENAI_NEW = True
except Exception:  # noqa: BLE001
    OpenAI = None  # type: ignore[assignment]
    _HAS_OPENAI_NEW = False

try:
    # Compatibilidad con SDK viejo (openai<1.0.0)
    import openai  # type: ignore[import]
    _HAS_OPENAI_OLD = True
except Exception:  # noqa: BLE001
    openai = None  # type: ignore[assignment]
    _HAS_OPENAI_OLD = False


# ---------------------------------------------------------------------------
# Dataclasses para resumen
# ---------------------------------------------------------------------------

@dataclass
class RiskSummary:
    total_files: int
    risk_low: int
    risk_medium: int
    risk_high: int
    ai_generated_count: int
    by_extension: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_stats(stats_path: Path) -> Dict[str, Any]:
    data = json.loads(stats_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("El archivo de estadísticas no contiene un objeto JSON de nivel raíz.")
    return data


def _compute_risk_summary(stats: Dict[str, Any]) -> RiskSummary:
    total = 0
    low = medium = high = 0
    ai_count = 0
    by_ext: Dict[str, int] = {}

    for file_path, info in stats.items():
        total += 1
        ext = str(info.get("extension", "")).lower()
        by_ext[ext] = by_ext.get(ext, 0) + 1

        advanced = info.get("advanced", {})
        level = str(advanced.get("risk_level", "")).upper()
        if level == "ALTO":
            high += 1
        elif level == "MEDIO":
            medium += 1
        else:
            low += 1

        if advanced.get("ai_generated"):
            ai_count += 1

    return RiskSummary(
        total_files=total,
        risk_low=low,
        risk_medium=medium,
        risk_high=high,
        ai_generated_count=ai_count,
        by_extension=by_ext,
    )


def _select_top_risky_files(stats: Dict[str, Any], n: int = 5) -> List[Tuple[str, int, str]]:
    """
    Devuelve una lista de tuplas:
      (ruta, risk_score, risk_level)
    ordenadas de mayor a menor riesgo.
    """
    items: List[Tuple[str, int, str]] = []

    for file_path, info in stats.items():
        advanced = info.get("advanced", {})
        score = int(advanced.get("risk_score", 0))
        level = str(advanced.get("risk_level", "BAJO"))
        items.append((file_path, score, level))

    items.sort(key=lambda x: x[1], reverse=True)
    return items[:n]


# ---------------------------------------------------------------------------
# Generación de reporte en Markdown (sin IA externa)
# ---------------------------------------------------------------------------

def _build_markdown_report(
    summary: RiskSummary,
    stats: Dict[str, Any],
    run_id: str,
) -> str:
    top_files = _select_top_risky_files(stats, n=5)

    lines: List[str] = []
    lines.append(f"# MetaHunter - Reporte de análisis avanzado")
    lines.append("")
    lines.append(f"- Fecha de generación: `{_now_iso()}`")
    lines.append(f"- ID de ejecución (`run_id`): `{run_id}`")
    lines.append("")
    lines.append("## Resumen general")
    lines.append("")
    lines.append(f"- Archivos analizados: **{summary.total_files}**")
    lines.append(f"- Riesgo **ALTO**: **{summary.risk_high}**")
    lines.append(f"- Riesgo **MEDIO**: **{summary.risk_medium}**")
    lines.append(f"- Riesgo **BAJO**: **{summary.risk_low}**")
    lines.append(f"- Archivos detectados como generados por IA: **{summary.ai_generated_count}**")
    lines.append("")

    lines.append("## Distribución por tipo de archivo")
    lines.append("")
    if summary.by_extension:
        lines.append("| Extensión | Cantidad |")
        lines.append("|----------|----------|")
        for ext, count in sorted(summary.by_extension.items(), key=lambda x: x[0]):
            ext_str = ext if ext else "(sin extensión)"
            lines.append(f"| `{ext_str}` | {count} |")
        lines.append("")
    else:
        lines.append("No se pudo determinar la extensión de los archivos.")
        lines.append("")

    lines.append("## Archivos con mayor nivel de riesgo")
    lines.append("")
    if top_files:
        lines.append("| Archivo | Risk score | Nivel |")
        lines.append("|---------|------------|-------|")
        for path, score, level in top_files:
            lines.append(f"| `{path}` | **{score}** | **{level}** |")
        lines.append("")
    else:
        lines.append("No se encontraron archivos con información de riesgo.")
        lines.append("")

    lines.append("## Interpretación del riesgo")
    lines.append("")
    lines.append(
        "- **Riesgo ALTO**: archivos que exponen metadatos sensibles fuertes "
        "(por ejemplo, coordenadas GPS, autor identificado, organización y software corporativo)."
    )
    lines.append(
        "- **Riesgo MEDIO**: archivos con algunos metadatos sensibles, pero sin combinar todos los factores de mayor impacto."
    )
    lines.append(
        "- **Riesgo BAJO**: archivos con metadatos mínimos o con poca información sensible."
    )
    lines.append("")
    lines.append(
        "MetaHunter permite detectar este tipo de patrones antes de compartir documentos "
        "o imágenes hacia fuera de la organización."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# (Opcional) Enriquecer el reporte con un LLM de OpenAI
# ---------------------------------------------------------------------------

def _call_openai_if_available(summary: RiskSummary, stats: Dict[str, Any]) -> str | None:
    """
    Intenta generar un comentario extra usando OpenAI si:
      - Existe OPENAI_API_KEY
      - Está instalado el SDK (nuevo o viejo)
    Si algo falla, devuelve None y el resto del pipeline sigue normal.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    # Texto base para describir el resumen
    base_prompt = f"""
Eres un analista de ciberseguridad. Te paso un resumen de análisis de metadatos:

- Archivos analizados: {summary.total_files}
- Riesgo ALTO: {summary.risk_high}
- Riesgo MEDIO: {summary.risk_medium}
- Riesgo BAJO: {summary.risk_low}
- Archivos detectados como generados por IA: {summary.ai_generated_count}
- Distribución por extensión: {summary.by_extension}

Escribe un comentario corto (2-3 párrafos) explicando:
1) Qué significa este resultado para la seguridad de la organización.
2) Qué tipos de archivos deberían revisarse con mayor prioridad.
3) Una recomendación concreta para el siguiente paso.
"""

    try:
        # SDK nuevo
        if _HAS_OPENAI_NEW and OpenAI is not None:
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un analista de ciberseguridad especializado en metadatos."},
                    {"role": "user", "content": base_prompt},
                ],
                temperature=0.4,
            )
            return resp.choices[0].message.content  # type: ignore[return-value]

        # SDK viejo
        if _HAS_OPENAI_OLD and openai is not None:
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un analista de ciberseguridad especializado en metadatos."},
                    {"role": "user", "content": base_prompt},
                ],
                temperature=0.4,
            )
            return resp.choices[0].message["content"]  # type: ignore[index]

    except Exception:
        # Si algo falla con la API, simplemente no añadimos comentario extra
        return None

    return None


# ---------------------------------------------------------------------------
# Logging desde este módulo
# ---------------------------------------------------------------------------

def _log_event(
    log_path: Path,
    run_id: str,
    module: str,
    level: str,
    event: str,
    details: Dict | None = None,
) -> None:
    record = {
        "timestamp": _now_iso(),
        "run_id": run_id,
        "module": module,
        "level": level,
        "event": event,
        "details": details or {},
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL QUE ESPERA EL CLI
# ---------------------------------------------------------------------------

def run_ai_pipeline(
    stats_path: Path,
    summary_path: Path,
    report_path: Path,
    run_id: str,
    log_path: Path,
) -> None:
    """
    Pipeline de IA de alto nivel:

    1) Lee el JSON de estadísticas (stats_path).
    2) Calcula un resumen (RiskSummary) y lo guarda en summary_path.
    3) Construye un reporte Markdown base (sin LLM) en report_path.
    4) Si hay OPENAI_API_KEY y la librería está instalada, añade
       una sección extra con observaciones generadas por IA.
    """
    stats_path = stats_path.resolve()
    summary_path = summary_path.resolve()
    report_path = report_path.resolve()
    log_path = log_path.resolve()

    _log_event(
        log_path,
        run_id,
        "ai_client",
        "INFO",
        "ai_pipeline_started",
        {
            "stats_path": str(stats_path),
            "summary_path": str(summary_path),
            "report_path": str(report_path),
        },
    )

    # 1) Cargar estadísticas
    stats = _load_stats(stats_path)

    # 2) Resumen
    summary = _compute_risk_summary(stats)

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    _log_event(
        log_path,
        run_id,
        "ai_client",
        "INFO",
        "ai_summary_saved",
        {"summary_path": str(summary_path)},
    )

    # 3) Reporte Markdown base
    base_report = _build_markdown_report(summary, stats, run_id)

    # 4) Intentar añadir comentario de IA (si está disponible la API)
    ai_comment = _call_openai_if_available(summary, stats)

    report_text = base_report
    if ai_comment:
        report_text += "\n\n---\n\n"
        report_text += "## Comentario generado por IA\n\n"
        report_text += ai_comment
        report_text += "\n"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")

    _log_event(
        log_path,
        run_id,
        "ai_client",
        "INFO",
        "ai_report_saved",
        {
            "summary_path": str(summary_path),
            "report_path": str(report_path),
            "used_openai": bool(ai_comment),
        },
    )
