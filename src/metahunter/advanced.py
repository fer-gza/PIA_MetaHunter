from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple


@dataclass
class AdvancedAnalysisResult:
    """
    Resultado combinado de análisis avanzado para un archivo:
    - Clasificación de riesgo
    - Línea de tiempo forense
    - Detección heurística de generación por IA
    """
    risk_score: int
    risk_level: str
    risk_reasons: List[str]
    forensic_timeline: List[str]
    ai_generated: bool
    ai_evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def analyze_file_advanced(metadata: Dict[str, Any]) -> AdvancedAnalysisResult:
    """
    Punto de entrada principal.

    `metadata` es el dict base con información del archivo (ruta, mime_type,
    tamaño, hash, fechas, etc.) generado en analyzer.py.
    """
    risk_score, risk_level, reasons = _compute_risk(metadata)
    timeline = _build_forensic_timeline(metadata)
    ai_flag, ai_evidence = _detect_ai_generation(metadata)

    return AdvancedAnalysisResult(
        risk_score=risk_score,
        risk_level=risk_level,
        risk_reasons=reasons,
        forensic_timeline=timeline,
        ai_generated=ai_flag,
        ai_evidence=ai_evidence,
    )


# ---------------------------------------------------------------------------
# Clasificación de riesgo
# ---------------------------------------------------------------------------

def _compute_risk(metadata: Dict[str, Any]) -> Tuple[int, str, List[str]]:
    """
    Calcula un score de riesgo (0-100) y un nivel (BAJO/MEDIO/ALTO)
    según los metadatos detectados.
    """
    score = 0
    reasons: List[str] = []

    path = str(metadata.get("path", "")).lower()
    mime_type = str(metadata.get("mime_type", "")).lower()
    author = str(metadata.get("author", "")).strip()
    company = str(metadata.get("company", "")).strip()
    creator_tool = str(metadata.get("creator_tool", "")).lower()
    software = str(metadata.get("software", "")).lower()
    gps_lat = metadata.get("gps_latitude")
    gps_lon = metadata.get("gps_longitude")

    # 1) GPS → MUY sensible
    if gps_lat is not None and gps_lon is not None:
        score += 40
        reasons.append("Contiene coordenadas GPS en metadatos (posible filtración de ubicación).")

    # 2) Autor explícito
    if author and author.lower() not in {"desconocido", "unknown", "system"}:
        score += 15
        reasons.append(f"Metadatos indican autor: '{author}'.")

    # 3) Empresa / organización
    if company:
        score += 15
        reasons.append(f"Metadatos incluyen organización/empresa: '{company}'.")

    # 4) Software corporativo / de oficina
    software_str = f"{creator_tool} {software}"
    if any(term in software_str for term in ["microsoft", "office", "adobe", "acrobat", "corp", "corporate"]):
        score += 15
        reasons.append("Indica software de oficina/corporativo en metadatos (Microsoft/Adobe/etc.).")

    # 5) Ruta que revela estructura interna
    if any(part in path for part in ["\\users\\", "/home/", "desktop", "documentos", "empresa", "corporativo"]):
        score += 10
        reasons.append("Ruta del archivo sugiere estructura interna de usuario/equipo.")

    # 6) Tipos de archivo propensos a muchos metadatos
    if any(mt in mime_type for mt in ["pdf", "word", "officedocument", "image/jpeg", "image/png"]):
        score += 5
        reasons.append("Formato proclive a contener metadatos sensibles (PDF/Word/imagen).")

    # Normalizar y asignar nivel
    if score > 100:
        score = 100

    if score >= 70:
        level = "ALTO"
    elif score >= 40:
        level = "MEDIO"
    else:
        level = "BAJO"

    return score, level, reasons


# ---------------------------------------------------------------------------
# Línea de tiempo forense
# ---------------------------------------------------------------------------

def _build_forensic_timeline(metadata: Dict[str, Any]) -> List[str]:
    """
    Reconstrucción básica de la historia del archivo:
    - creación
    - modificación
    - herramienta
    - dispositivo
    - GPS
    """
    timeline: List[str] = []

    created = metadata.get("created_at") or metadata.get("creation_date")
    modified = metadata.get("modified_at") or metadata.get("modification_date")
    camera_model = metadata.get("camera_model")
    device = metadata.get("device") or metadata.get("machine")
    creator_tool = metadata.get("creator_tool") or metadata.get("software")

    if created:
        if camera_model:
            timeline.append(f"{created}: Archivo creado (capturado con '{camera_model}').")
        else:
            timeline.append(f"{created}: Archivo creado.")

    if modified and modified != created:
        timeline.append(f"{modified}: Última modificación registrada.")

    if creator_tool:
        timeline.append(f"Herramienta de creación/edición: {creator_tool}.")

    if device:
        timeline.append(f"Dispositivo/equipo asociado: {device}.")

    gps_lat = metadata.get("gps_latitude")
    gps_lon = metadata.get("gps_longitude")
    if gps_lat is not None and gps_lon is not None:
        timeline.append(f"Coordenadas en EXIF: lat={gps_lat}, lon={gps_lon}.")

    if not timeline:
        timeline.append("No se encontraron metadatos suficientes para reconstruir la línea del tiempo.")

    return timeline


# ---------------------------------------------------------------------------
# Detector de archivos generados por IA
# ---------------------------------------------------------------------------

AI_HINT_KEYWORDS = [
    "midjourney",
    "stable diffusion",
    "stablediffusion",
    "dall-e",
    "dalle",
    "openai",
    "firefly",
    "adobe firefly",
    "canva",
    "ai generated",
    "generated with ai",
    "artificial intelligence",
    "leonardo.ai",
]


def _detect_ai_generation(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Heurística simple: busca cadenas típicas de generadores de IA
    en los metadatos (EXIF, XMP, productor de PDF, etc.).
    """
    evidence: List[str] = []
    meta_strings: List[str] = []

    for key, value in metadata.items():
        if value is None:
            continue
        meta_strings.append(str(value).lower())
        meta_strings.append(str(key).lower())

    joined = " ".join(meta_strings)

    for hint in AI_HINT_KEYWORDS:
        if hint in joined:
            evidence.append(f"Coincidencia de '{hint}' en metadatos.")

    return (len(evidence) > 0), evidence
