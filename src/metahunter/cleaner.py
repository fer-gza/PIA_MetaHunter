from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def clean_file(input_path: Path, output_path: Path):
    """
    Limpia metadatos básicos del archivo PDF y lo guarda en output_path.
    Compatible con PyPDF2 moderno.
    """
    ext = input_path.suffix.lower()

    if ext != ".pdf":
        # Si no es PDF, solo copiar el archivo tal cual
        output_path.write_bytes(input_path.read_bytes())
        return

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    # Copiar páginas
    for page in reader.pages:
        writer.add_page(page)

    # Limpiar metadatos con la forma actual correcta
    writer.add_metadata({})

    # Guardar PDF limpio
    with open(output_path, "wb") as f:
        writer.write(f)
