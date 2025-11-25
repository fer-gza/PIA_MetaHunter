# MetaHunter - Reporte de análisis avanzado

- Fecha de generación: `2025-11-25T23:02:03.456799Z`
- ID de ejecución (`run_id`): `20251125T230203Z`

## Resumen general

- Archivos analizados: **11**
- Riesgo **ALTO**: **1**
- Riesgo **MEDIO**: **2**
- Riesgo **BAJO**: **8**
- Archivos detectados como generados por IA: **1**

## Distribución por tipo de archivo

| Extensión | Cantidad |
|----------|----------|
| `.docx` | 2 |
| `.jpg` | 2 |
| `.pdf` | 2 |
| `.png` | 3 |
| `.txt` | 2 |

## Archivos con mayor nivel de riesgo

| Archivo | Risk score | Nivel |
|---------|------------|-------|
| `C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\data\raw\foto_gps.jpg` | **70** | **ALTO** |
| `C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\data\raw\contrato_fix.pdf` | **60** | **MEDIO** |
| `C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\data\raw\reporte_corporativo.docx` | **60** | **MEDIO** |
| `C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\data\raw\foto.jpg` | **15** | **BAJO** |
| `C:\Users\Kevin G\Documents\GitHub\PIA_MetaHunter\data\raw\foto_normal.png` | **15** | **BAJO** |

## Interpretación del riesgo

- **Riesgo ALTO**: archivos que exponen metadatos sensibles fuertes (por ejemplo, coordenadas GPS, autor identificado, organización y software corporativo).
- **Riesgo MEDIO**: archivos con algunos metadatos sensibles, pero sin combinar todos los factores de mayor impacto.
- **Riesgo BAJO**: archivos con metadatos mínimos o con poca información sensible.

MetaHunter permite detectar este tipo de patrones antes de compartir documentos o imágenes hacia fuera de la organización.
