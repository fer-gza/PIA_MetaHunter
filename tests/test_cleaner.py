import os
from metahunter.cleaner import clean_file

CARPETA = r"C:\Users\Fer_g\Documents\PIA_MetaHunter\tests\info"
print(f"Limpieza de metadatos en: {CARPETA}\n")

for archivo in os.listdir(CARPETA):
    ruta = os.path.join(CARPETA, archivo)
    if archivo.lower().endswith((".docx", ".pdf")):
        clean_file(ruta)
        print(f"Limpieza completada: {archivo}")