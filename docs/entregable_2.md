📦 Entregable 2 – MetaHunter
✅ Tarea funcional implementada
Se desarrolló el módulo cleaner.py en /src/metahunter/, el cual permite eliminar metadatos sensibles de archivos .docx y .pdf. La función principal clean_file(path) identifica el tipo de archivo y aplica la limpieza correspondiente.
Funciones incluidas:
- clean_docx(path): elimina autor, título, fechas de creación y modificación
- clean_pdf(path): elimina todos los metadatos del PDF
- hash_file(path): calcula el hash SHA256 del archivo antes de la limpieza
- log_report(path, tipo, hash): registra la limpieza en reports/reports.txt en formato JSON lines

📥 Entradas y salidas
Entradas:
- Archivos .docx y .pdf ubicados en /examples/sample_files/
- Script de ejecución: test_cleaner.py
Salidas:
- Archivos modificados sin metadatos
- Registro en reports/reports.txt con:
- Fecha
- Tipo de archivo
- Nombre
- Hash SHA256

📁 Evidencia reproducible
Archivos generados:
- /examples/limpieza_de_carpeta.png: evidencia de ejecución
Formato de log:
{"timestamp": "2025-11-09T23:10:12", "tipo": "PDF", "archivo": "contrato_final.pdf", "hash": "3f2c1a...e9b7"}

---

🧭 Observaciones
¿Qué falta por implementar? ¿Qué ajustes se prevén? ¿Qué se aprendió en esta etapa?

Falta implementar limpieza en imágenes y archivos de texto, validación post-limpieza y generación de reportes en HTML/Markdown. Se prevé modularizar el código, mejorar pruebas y agregar CLI. Aprendimos a mantener trazabilidad, estructurar logs y documentar avances de forma clara y reproducible.
