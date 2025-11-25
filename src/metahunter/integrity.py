from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class IntegrityReport:
    """
    Reporte de integridad basado en:
    - algoritmo usado (SHA-256)
    - Merkle root del conjunto de hashes
    - lista de archivos y su hash
    """
    algorithm: str
    merkle_root: str
    files: List[Dict[str, str]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_integrity_report(file_hashes: Dict[str, str]) -> IntegrityReport:
    """
    Construye un reporte de integridad a partir de un dict:
      { "ruta/archivo": "hash_hex_sha256" }
    """
    if not file_hashes:
        raise ValueError("No se proporcionaron hashes de archivo para construir el reporte de integridad.")

    hashes = list(file_hashes.values())
    root = _build_merkle_root(hashes)

    files_list = [
        {"path": path, "hash": h}
        for path, h in file_hashes.items()
    ]

    return IntegrityReport(
        algorithm="SHA-256",
        merkle_root=root,
        files=files_list,
    )


def _build_merkle_root(hashes: List[str]) -> str:
    """
    Construye un Merkle root simple a partir de una lista de hashes hex.
    Si el número de nodos es impar, duplica el último (estándar en Merkle).
    """
    current_level = [h.lower() for h in hashes]

    while len(current_level) > 1:
        next_level: List[str] = []

        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1]
            combined = (left + right).encode("utf-8")
            digest = hashlib.sha256(combined).hexdigest()
            next_level.append(digest)

        current_level = next_level

    return current_level[0]
