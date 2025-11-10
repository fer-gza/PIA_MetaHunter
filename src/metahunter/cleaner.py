import os
import hashlib
from datetime import datetime
from docx import Document
from PyPDF2 import PdfReader, PdfWriter

REPORT_PATH = os.path.join("reports", "reports.txt")

def hash_file(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def log_report(path, tipo, hash_value):
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {tipo} | {os.path.basename(path)} | {hash_value}\n")

def clean_docx(path):
    hash_value = hash_file(path)
    doc = Document(path)
    props = doc.core_properties
    props.author = ""
    props.title = ""
    props.created = None
    props.modified = None
    doc.save(path)
    log_report(path, "DOCX", hash_value)

def clean_pdf(path):
    hash_value = hash_file(path)
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})
    with open(path, "wb") as f:
        writer.write(f)
    log_report(path, "PDF", hash_value)

def clean_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        clean_docx(path)
    elif ext == ".pdf":
        clean_pdf(path)