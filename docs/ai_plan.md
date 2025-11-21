# 🧠 Plan de Integración de IA – MetaHunter

## 🎯 Objetivo
Integrar capacidades de Inteligencia Artificial en MetaHunter para generar resúmenes, análisis y reportes automáticos de los archivos procesados.

---

## 🔗 Puntos de integración dentro del pipeline
1. Después de la limpieza de metadatos.
2. Después del análisis técnico.
3. Antes de generar el reporte final.

---

## 🧬 Flujo de IA
- El pipeline envía información de los archivos procesados.
- La IA genera un resumen técnico con detalles relevantes.
- Se crea un documento en formato Markdown con interpretación humana.
- Los resultados se almacenan en `/examples/` y `/reports/`.

---

## 🤖 Modelo utilizado
- ChatGPT / GPT-4o (o modelo equivalente)
- **Entrada:** lista de archivos procesados + detalles técnicos.
- **Salida:** resumen técnico y reporte explicativo en lenguaje natural.

---

## 📝 Ejemplo de prompt

```
Analiza los siguientes archivos procesados y genera un resumen técnico con riesgos potenciales,
elementos importantes y acciones realizadas por el sistema.
```

---

## 📁 Evidencia generada
- `examples/ai_summary_<run_id>.json`
- `reports/ai_report_<run_id>.md`
