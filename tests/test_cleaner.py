import os
from src.metahunter.cleaner import clean_file, hash_file

CARPETA = r"C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\examples\sample_files"
print(f"Limpieza de metadatos en: {CARPETA}\n")

for archivo in os.listdir(CARPETA):
    ruta = os.path.join(CARPETA, archivo)
    if archivo.lower().endswith((".docx", ".pdf")):
        hash_antes = hash_file(ruta)
        clean_file(ruta)
        print(f"✅ Limpieza completada: {archivo}")
        print(f"🔐 Hash antes de limpieza: {hash_antes}")
        print("-" * 40)