import os
from docx import Document
from PyPDF2 import PdfReader, PdfWriter

def clean_docx(path):
    doc = Document(path)
    props = doc.core_properties
    props.author = ""
    props.title = ""
    props.created = None
    props.modified = None
    doc.save(path)

def clean_pdf(path):
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})  # Limpia los metadatos
    with open(path, "wb") as f:
        writer.write(f)


def clean_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        clean_docx(path)
    elif ext == ".pdf":
        clean_pdf(path)