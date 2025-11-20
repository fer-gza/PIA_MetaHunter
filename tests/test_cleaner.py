import sys
from pathlib import Path

# Ruta raíz del repo y src/ para poder importar metahunter
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from metahunter.cleaner import clean_file

INPUT_DIR = ROOT / "examples" / "sample_files"
OUTPUT_DIR = ROOT / "examples" / "sample_files" / "cleaned"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Limpieza de metadatos en: {INPUT_DIR}\n")

for path in INPUT_DIR.iterdir():
    if path.is_file() and path.suffix.lower() in (".pdf", ".docx"):
        out_path = OUTPUT_DIR / path.name
        clean_file(path, out_path)
        print(f"✅ Limpieza completada: {path.name}")
        print(f"📄 Archivo limpio generado en: {out_path}")
        print("-" * 40)
