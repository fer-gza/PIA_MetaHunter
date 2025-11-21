from pathlib import Path
from typing import List, Dict, Any
from PyPDF2 import PdfReader


def analyze_file(path: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "file": str(path),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
    }

    if path.suffix.lower() == ".pdf":
        try:
            reader = PdfReader(str(path))
            info["pages"] = len(reader.pages)
            info["is_encrypted"] = bool(reader.is_encrypted)
        except Exception as e:
            info["error"] = f"Error analizando PDF: {e}"

    return info


def analyze_files(paths: List[Path]) -> List[Dict[str, Any]]:
    return [analyze_file(p) for p in paths]
