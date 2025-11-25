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
    # Aquí podrías agregar más campos si luego extraes EXIF/PDF/etc.

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


def analyze_files(files: Iterable[Path]) -> Dict[str, Dict[str, Any]]:
    """
    Analiza una colección de archivos limpios y devuelve un dict:
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

        # En este punto solo tenemos metadatos "básicos".
        # Si en el futuro enriqueces con EXIF, autor, compañía, etc.,
        # solo añade esos campos a `base` antes de llamar a analyze_file_advanced.
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
