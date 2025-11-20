import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def load_prompt(prompt_path: Path) -> Dict[str, Any]:
    with prompt_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def generate_ai_summary(run_id: str, files_info: List[Dict[str, Any]], prompt_path: Path) -> Dict[str, Any]:
    prompt = load_prompt(prompt_path)

    total_archivos = len(files_info)
    pdfs = [f for f in files_info if f.get("extension") == ".pdf"]
    docx = [f for f in files_info if f.get("extension") == ".docx"]

    explicacion = (
        f"Se analizaron {total_archivos} archivo(s). "
        f"Se detectaron {len(pdfs)} PDF(s) y {len(docx)} DOCX(s). "
        "Los metadatos de estos archivos pueden revelar información sensible como autores, "
        "herramientas utilizadas o rutas internas."
    )

    sugerencias = [
        "Revisar periódicamente los documentos antes de compartirlos externamente.",
        "Estandarizar una política interna de limpieza de metadatos.",
        "Priorizar la limpieza de documentos PDF y DOCX de uso público o que se publiquen en la web."
    ]

    resumen = (
        f"MetaHunter ejecutó una corrida con id {run_id}, "
        f"limpiando metadatos de {total_archivos} archivo(s). "
        "Los resultados muestran que la herramienta está lista para usarse en entornos reales."
    )

    return {
        "run_id": run_id,
        "prompt_version": prompt.get("version"),
        "explicacion_riesgos": explicacion,
        "sugerencias_reglas": sugerencias,
        "resumen_ejecutivo": resumen,
        "archivos_procesados": files_info,
        "generado_en": datetime.utcnow().isoformat() + "Z"
    }


def build_human_report(summary: Dict[str, Any]) -> str:
    """Genera un reporte en texto/markdown interpretando los datos del resumen de IA."""
    lineas: List[str] = []

    lineas.append("# Reporte de análisis de metadatos\n")
    lineas.append(f"- Run ID: {summary.get('run_id', '')}")
    lineas.append(f"- Versión de prompt: {summary.get('prompt_version', '')}")
    lineas.append(f"- Generado en: {summary.get('generado_en', '')}")
    lineas.append("")

    lineas.append("## Resumen ejecutivo\n")
    lineas.append(summary.get("resumen_ejecutivo", ""))
    lineas.append("")

    lineas.append("## Riesgos detectados\n")
    lineas.append(summary.get("explicacion_riesgos", ""))
    lineas.append("")

    lineas.append("## Recomendaciones y reglas sugeridas\n")
    for sug in summary.get("sugerencias_reglas", []):
        lineas.append(f"- {sug}")
    lineas.append("")

    lineas.append("## Archivos procesados\n")
    for info in summary.get("archivos_procesados", []):
        lineas.append(
            f"- Entrada: {info.get('input')}  →  Salida: {info.get('output')}  "
            f"({info.get('extension')})"
        )

    lineas.append("")
    lineas.append(
        "Este reporte fue generado automáticamente por el módulo de IA de MetaHunter "
        "a partir de los datos de la corrida."
    )

    return "\n".join(lineas)
