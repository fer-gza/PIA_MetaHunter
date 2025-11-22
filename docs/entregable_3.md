# 🧠 MetaHunter  
## Escáner y limpiador inteligente de metadatos  
### Fernando Garza Chávez  
### Kevin Daniel Grimaldo Esquivel  
### Alejandro Martínez Moya  

---

# 📋 Descripción general

**MetaHunter** es una herramienta multiplataforma desarrollada con **Python, Bash y PowerShell** que permite **detectar y eliminar metadatos sensibles** de archivos corporativos antes de compartirlos o publicarlos.

Su propósito es **proteger la privacidad y la información confidencial**, eliminando datos ocultos como nombres de autor, software usado, coordenadas GPS, fecha de creación y rutas internas del sistema.

---

# 🚀 Funcionalidades principales

- 🔍 **Escaneo automatizado** de archivos en carpetas completas.  
- 🧹 **Limpieza de metadatos** en documentos:  
  - PDF  
  - DOCX  
  - Imágenes JPG/PNG  
  - TXT/MD  
- 🔗 **Integración entre módulos**:  
  - Limpieza → Reporte → Logs  
- 🧾 **Generación automática de reportes** (Markdown/JSON).  
- 🤖 **Uso de IA** para interpretar resultados y generar un reporte inteligente.  
- 🖥️ **Scripts de automatización** en PowerShell o Bash.  
- 📝 **Logging JSONL estructurado** (timestamp, run_id, module, event, details).  

---

# 🧩 Tecnologías utilizadas

| Tecnología | Uso |
|-----------|-----|
| **Python** | Módulos funcionales (cleaner, reporter, ai_client, cli) |
| **PowerShell / Bash** | Scripts de orquestación |
| **PyPDF2 / python-docx / Pillow** | Limpieza de metadatos |
| **JSONL Logs** | Auditoría estructurada |
| **IA (OpenAI)** | Generación automática de análisis y reportes |
| **GitHub** | Control de versiones y evidencia colaborativa |

---

# 🏗️ Estructura del proyecto

```
PIA_MetaHunter/
│
├── src/metahunter/
│   ├── cleaner.py
│   ├── reporter.py
│   ├── ai_client.py
│   ├── cli.py
│   ├── __main__.py
│   └── __init__.py
│
├── prompts/
│   └── prompt_v1.json
│
├── docs/
│   ├── ai_plan.md
│   └── entregable_3.md
│
├── scripts/
│   ├── run_pipeline.ps1
│   └── run_pipeline.sh
│
├── examples/
│   ├── logs.jsonl
│   ├── sample_files/
│   └── sample_reports/
│
├── data/
│   ├── raw/
│   └── clean/
│
└── README.md
```

---

# ⚙️ Componentes obligatorios del Entregable 3 — **Cumplidos**

## ✔ 1. Dos tareas funcionales integradas

### Tarea 1 — Limpieza de metadatos (`cleaner.py`)
- Elimina EXIF, XMP, propiedades internas, rutas, autores, timestamps.
- Compatible con PDF, DOCX, JPG, PNG, TXT.

### Tarea 2 — Reporte técnico / IA (`reporter.py` o `ai_client.py`)
- Genera resumen inteligente usando IA.
- Guarda salida estructurada en JSON y Markdown.

---

## ✔ 2. Uso de dos lenguajes de programación

- **Python** (módulos principales)
- **PowerShell** (script de orquestación `run_pipeline.ps1`)
- *(opcional Bash si se utiliza `run_pipeline.sh`)*

---

## ✔ 3. Script de orquestación

```
.\scripts
un_pipeline.ps1 -InputDir "data/raw" -OutputDir "data/clean"
```

Automatiza:

1. Escaneo  
2. Limpieza  
3. Reporte  
4. Logs

---

## ✔ 4. Plan de IA en `/docs/ai_plan.md`

Incluye:

- Objetivo del uso de IA  
- Punto del flujo donde se integra  
- Modelo utilizado  
- Diseño del prompt (en `/prompts/prompt_v1.json`)  
- Ejemplo práctico  

---

## ✔ 5. Carpeta `/prompts` creada

Ejemplo:

```json
{
  "version": "1.0",
  "tarea": "resumen_metadatos",
  "template": "Analiza los archivos procesados y genera un resumen...",
  "instrucciones": "Sé claro, técnico y conciso."
}
```

---

## ✔ 6. Logging estructurado

Ejemplo:

```json
{
  "timestamp": "2025-11-20T22:36:05Z",
  "run_id": "20251120T223605Z",
  "module": "cleaner",
  "level": "INFO",
  "event": "file_cleaned",
  "details": {
    "input": "data/raw/test.pdf",
    "output": "data/clean/test.pdf",
    "extension": ".pdf"
  }
}
```

Se almacena en:

```
examples/logs.jsonl
```

---

## ✔ 7. Documentación `README.md` actualizada

- Estado del entregable  
- Instrucciones de instalación  
- Estructura  
- Ejemplos  
- Autores  

---

# ▶️ Cómo ejecutar el proyecto

### 1. Usando Python

```
python -m metahunter.cli --input-dir data/raw --output-dir data/clean --log-path examples/logs.jsonl
```

### 2. Usando PowerShell

```
.\scripts
un_pipeline.ps1
```

---

# 📤 Entregables confirmados

| Entregable | Archivo |
|-----------|---------|
| Plan de IA | `/docs/ai_plan.md` |
| Prompt inicial | `/prompts/prompt_v1.json` |
| Script de orquestación | `/scripts/run_pipeline.ps1` |
| Logging JSONL funcional | `/examples/logs.jsonl` |
| Flujo técnico conectado | `cleaner.py` + `cli.py` + `ai_client.py` |
| README actualizado | ✔ |

---

# 👥 Autores

**Fernando Garza Chávez**  
**Kevin Daniel Grimaldo Esquivel**  
**Alejandro Martínez Moya**
