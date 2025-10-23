# 🧠 MetaHunter  
### Escáner y limpiador inteligente de metadatos

---

## 📋 Descripción general

**MetaHunter** es una herramienta multiplataforma desarrollada con **Python, Bash y PowerShell** que permite **detectar y eliminar metadatos sensibles** de archivos corporativos antes de compartirlos o publicarlos.

Su propósito es **proteger la privacidad y la información confidencial** de la empresa, evitando que documentos, imágenes o reportes contengan datos ocultos como nombres de autor, ubicación GPS, software usado, fechas de creación o rutas internas del sistema.

---

## 🚀 Funcionalidades principales

- 🔍 **Escaneo de metadatos** en formatos comunes:  
  - Imágenes (`.jpg`, `.png`)  
  - Documentos (`.pdf`, `.docx`)  
  - Archivos de texto (`.txt`, `.md`)

- 🧹 **Limpieza automática** de información sensible.

- 🧾 **Generación de reportes** en formato **Markdown o HTML**, con:
  - Archivos analizados  
  - Metadatos encontrados  
  - Acciones realizadas  

- ⚙️ **Integración con scripts Bash o PowerShell** para automatizar el proceso.

- 🔒 **Validación post-limpieza** para asegurar que los metadatos fueron completamente eliminados.

---

## 🧩 Tecnologías utilizadas

| Tecnología | Uso principal |
|-------------|----------------|
| **Python 3** | Análisis y limpieza de metadatos |
| **ExifTool / Pillow / PyPDF2** | Lectura y manipulación de metadatos |
| **Bash / PowerShell** | Automatización y ejecución masiva |
| **Markdown / HTML** | Reportes técnicos automatizados |
| **GitHub** | Control de versiones y documentación |
