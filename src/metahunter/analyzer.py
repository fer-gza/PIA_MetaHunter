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
    Clasifica archivos DEMO según su nombre, pero sin inyectar metadatos.
    Solo ajusta banderas de riesgo basadas en patrones realistas.
    """

    name = str(base.get("name", "")).lower()

    # Solo marcamos indicios, NO datos personales
    indicators = []

    if "gps" in name:
        indicators.append("posible información de ubicación")
        base["has_gps_metadata"] = True

    if "contrato" in name or "corporativo" in name:
        indicators.append("documento empresarial sensible")

    if "ia" in name:
        indicators.append("posible generación asistida por IA")
        base["suspected_ai_generation"] = True

    if indicators:
        base["risk_indicators"] = indicators

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
