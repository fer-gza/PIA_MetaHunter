
# 🧠 MetaHunter  
## Escáner, limpiador, analizador avanzado y verificador criptográfico de metadatos  
### Fernando Garza Chávez  
### Kevin Daniel Grimaldo Esquivel  
### Alejandro Martínez Moya  

---

# 📘 Descripción general

**MetaHunter** es una herramienta multiplataforma desarrollada en **Python + PowerShell + Bash** diseñada para automatizar y asegurar el manejo de archivos corporativos mediante:

- **Análisis técnico** completo (tipo, hash, extensión, tamaño).
- **Clasificación de riesgo** basada en metadatos sensibles.
- **Reconstrucción forense** (línea del tiempo del archivo).
- **Detección de contenido generado por IA**.
- **Limpieza profunda de metadatos** en PDF, imágenes, DOCX y más.
- **Verificación criptográfica de integridad** utilizando *Merkle Trees*.
- **Generación automática de reportes con IA**.
- **Logging estructurado JSONL** para auditorías profesionales.

El objetivo es proteger la privacidad, mejorar los flujos de auditoría y ofrecer un pipeline de ciberseguridad reproducible y automatizado.

---

# 🚀 Novedades y mejoras recientes

MetaHunter ahora incluye capacidades avanzadas:

## 🔥 1. Análisis avanzado — `advanced.py`
Nuevo módulo que agrega:
- Clasificación de riesgo (**BAJO / MEDIO / ALTO**).
- Reconstrucción de línea forense (fechas, dispositivo, software).
- Detección heurística de archivos generados por IA.
- Evaluación automática según:
  - GPS
  - Autor
  - Empresa
  - Software corporativo (Microsoft/Adobe)
  - Rutas internas sensibles

## 🧠 2. Integración IA mejorada — `ai_client.py`
- Genera **resúmenes JSON**.
- Crea **reportes Markdown** para auditoría.
- Si existe `OPENAI_API_KEY`, añade un análisis profesional generado por IA.
- Si NO existe, no truena: genera reporte local sin IA.

## 🔗 3. Verificación de integridad — `integrity.py`
- Cálculo de hashes SHA-256 de archivos limpios.
- Construcción de un **Merkle Tree**.
- Generación de reporte criptográfico:

```
reports/integrity_<run_id>.json
```

## 🎯 4. Pipeline perfeccionado — `cli.py`
Ahora el proceso es:

```
RAW → ANALYSIS → CLEANING → MERKLE TREE → IA REPORT
```

Así se conserva el análisis real del archivo ANTES de limpiarlo.

---

# 🧹 5. Limpieza profunda — `cleaner.py`
Compatible con:
- JPG (EXIF)
- PNG (chunks)
- PDF (propiedades internas)
- DOCX (propiedades de Office)
- TXT / CSV / MD (normalizado)

---

# 📊 6. Análisis técnico — `analyzer.py`
Extrae automáticamente:

- Tamaño exacto  
- Extensión  
- Tipo MIME  
- SHA-256  
- Atributos enriquecidos  
- Heurísticas para demo (GPS, empresa, IA, autor, etc.)

Salida estándar:

📄 `examples/stats_<run_id>.json`

---

# 🔗 Pipeline técnico completo — `cli.py`

El pipeline realiza automáticamente:

1. **Escaneo RAW**
2. **Análisis avanzado (riesgo, IA, forense)**
3. **Limpieza de metadatos**
4. **Hashing + Merkle Root**
5. **Resumen IA (opcional)**
6. **Reporte Markdown**
7. **Logging JSONL**

---

# ⚙️ Scripts de orquestación

| Script | Uso |
|--------|------|
| `scripts/run_pipeline.ps1` | Ejecuta todo el pipeline en Windows |
| `scripts/run_pipeline.sh` | Ejecuta en Linux/Mac |
| `metahunter` (entry point global) | Ejecutar desde cualquier ubicación |

---

# 📁 Estructura del repositorio

```
PIA_MetaHunter/
│
├── src/
│   └── metahunter/
│       ├── cleaner.py
│       ├── analyzer.py
│       ├── advanced.py
│       ├── integrity.py
│       ├── ai_client.py
│       ├── cli.py
│       ├── __main__.py
│       └── __init__.py
│
├── prompts/
│   └── prompt_v1.json
│
├── examples/
│   ├── logs.jsonl
│   ├── stats_*.json
│   └── ai_summary_*.json
│
├── reports/
│   ├── ai_report_*.md
│   └── integrity_*.json
│
├── docs/
│   ├── ai_plan.md
│   └── entregable_4.md
│
├── scripts/
│   ├── run_pipeline.ps1
│   └── run_pipeline.sh
│
├── data/
│   ├── raw/
│   └── clean/
│
└── README.md
```

---

# 🔧 Instalación

### 📌 Instalar en modo desarrollo

```
pip install -e .
```

Esto habilita el comando:

```
metahunter
```

---

# ▶️ Uso del programa

### 🔵 Ejecución estándar

```
metahunter --input-dir data/raw --output-dir data/clean --log-path examples/logs.jsonl --stats-path examples/stats.json --integrity-report reports/integrity.json
```

### 🔵 Ejecutar con IA

```
metahunter --input-dir data/raw --output-dir data/clean --log-path examples/logs.jsonl --use-ai
```

### 🔵 Ejecutar dentro de un venv

```
python -m metahunter.cli --input-dir data/raw --output-dir data/clean --log-path examples/logs.jsonl
```

### 🔵 Ejecutar desde Powershell

```
.\scripts\run_pipeline.ps1
```

### 🔵 Ejecutar desde Bash

```
./scripts/run_pipeline.sh
```

---

# 📝 Ejemplos de salida

### ✔ Archivo limpio
```
data/clean/contrato_meta.pdf
```

### ✔ Logs estructurados en JSONL

`examples/logs.jsonl`:

```json
{
  "timestamp": "2025-11-20T22:51:12Z",
  "run_id": "20251120T225112Z",
  "module": "cleaner",
  "level": "INFO",
  "event": "file_cleaned",
  "details": {
    "input": "data/raw/test.pdf",
    "output": "data/clean/test.pdf"
  }
}
```

---

# 📑 Documentación incluida

📘 `/docs/ai_plan.md` → Plan formal de integración de IA  
📗 `/docs/entregable_4.md` → Documentación del entregable 4  

---

# 🔥 Estado actual del proyecto — Entregable Final

| Requisito | Estado |
|----------|--------|
| Mínimo dos tareas funcionales | ✔ cleaner + analyzer |
| Integración IA | ✔ ai_client completo |
| Pipeline técnico | ✔ cli.py avanzado |
| Logging | ✔ JSONL estructurado |
| Reportes automáticos | ✔ AI + Markdown |
| Verificación criptográfica | ✔ Merkle root funcionando |
| Evidencia reproducible | ✔ examples + reports |
| Documentación clara | ✔ README actualizado |
| Scripts de orquestación | ✔ PS1 / SH |
| Análisis RAW + Limpieza | ✔ Implementado |
