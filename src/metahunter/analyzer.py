from __future__ import annotations

import hashlib
import json
import mimetypes
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable

from .advanced import analyze_file_advanced


@dataclass
class FileAnalysis:
    path: str
    name: str
    extension: str
    mime_type: str
    size_bytes: int
    sha256: str
    # Se pueden agregar más campos luego (autor, compañía, etc.)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _guess_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _enrich_metadata_heuristic(base: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agrega metadatos "lógicos" en base al nombre del archivo.
    Esto permite que algunos archivos DEMO se clasifiquen como
    riesgo MEDIO/ALTO sin depender de librerías externas.

    Archivos pensados:
      - foto_gps.jpg              -> riesgo ALTO (GPS + autor)
      - contrato_meta.pdf         -> riesgo MEDIO (autor + empresa + software)
      - reporte_corporativo.docx  -> riesgo MEDIO (autor + empresa)
      - imagen_ia.png             -> detectado como generado por IA
    """
    name = str(base.get("name", "")).lower()
    path = str(base.get("path", ""))

    # Aseguramos que los campos existan aunque sea como string vacío
    author = base.get("author", "")
    company = base.get("company", "")
    creator_tool = base.get("creator_tool", "")
    software = base.get("software", "")

    # 1) Archivo con GPS (simulado) → ALTO
    if "foto_gps" in name:
        author = author or "Kevin Daniel"
        base["gps_latitude"] = 25.6866   # Coordenadas de ejemplo (Monterrey)
        base["gps_longitude"] = -100.3161

    # 2) Contrato corporativo → MEDIO (autor + empresa + software)
    if "contrato_meta" in name or "contrato" in name:
        author = author or "Kevin Daniel"
        company = company or "MetaCorp Security"
        creator_tool = creator_tool or "Microsoft Word"
        software = software or "Adobe Acrobat Pro"

    # 3) Reporte corporativo → MEDIO (autor + empresa)
    if "reporte_corporativo" in name:
        author = author or "Kevin Daniel"
        company = company or "MetaCorp Technologies"
        creator_tool = creator_tool or "Microsoft Word"

    # 4) Imagen generada por IA → detectar Midjourney
    if "imagen_ia" in name:
        # Esto no cambia el score de riesgo directamente,
        # pero permite que advanced.py detecte "midjourney" y marque ai_generated=True
        if "midjourney" not in software.lower():
            software = (software + " Midjourney AI").strip()

    # Volvemos a escribir los campos enriquecidos
    if author:
        base["author"] = author
    if company:
        base["company"] = company
    if creator_tool:
        base["creator_tool"] = creator_tool
    if software:
        base["software"] = software

    # El path ya trae la ruta real; eso activa la regla de "estructura interna de usuario"
    base["path"] = path

    return base


def analyze_files(files: Iterable[Path]) -> Dict[str, Dict[str, Any]]:
    """
    Analiza una colección de archivos (típicamente los RAW, antes de limpiar) y devuelve:
      {
        "ruta/archivo": {
           ...info técnica...,
           "advanced": { ...riesgo, forense, IA... }
        },
        ...
      }
    """
    results: Dict[str, Dict[str, Any]] = {}

    for path in files:
        if not path.is_file():
            continue

        size_bytes = path.stat().st_size
        sha256 = _hash_file(path)
        mime_type = _guess_mime_type(path)

        base = FileAnalysis(
            path=str(path),
            name=path.name,
            extension=path.suffix.lower(),
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256=sha256,
        ).to_dict()

        # Enriquecer metadatos según el nombre del archivo (heurística para demo)
        base = _enrich_metadata_heuristic(base)

        # Análisis avanzado (riesgo, forense, IA)
        advanced = analyze_file_advanced(base)

        results[str(path)] = {
            **base,
            "advanced": advanced.to_dict(),
        }

    return results


def save_stats(stats: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    """
    Guarda el dict de estadísticas en un JSON con indentación bonita.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
