# ==============================
# 🔍 Script: scanner.ps1
# Descripción:
# Escanea una carpeta buscando archivos de imagen, extrae metadatos (EXIF)
# usando ExifTool si está disponible, y genera un reporte con un resumen.
# ==============================

# --- Configuración inicial ---
$InputDir = "examples"
$OutputDir = "reports"
$Summary = Join-Path $OutputDir "summary.txt"

# --- Crear carpetas si no existen ---
if (-not (Test-Path $InputDir)) {
    Write-Warning "Ruta no encontrada: $InputDir"
}
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory | Out-Null
}

# --- Detectar ExifTool ---
$ExifTool = Get-Command exiftool -ErrorAction SilentlyContinue
if ($null -eq $ExifTool) {
    Write-Host "[INFO] ExifTool no encontrado; usaré fallback Python cuando sea posible."
} else {
    Write-Host "[INFO] ExifTool detectado en $($ExifTool.Source)"
}

# --- Inicializar contadores ---
$Counts = @{
    "ImagenesProcesadas" = 0
    "Errores" = 0
}

# --- Procesar archivos ---
$Files = Get-ChildItem -Path $InputDir -Recurse -Include *.jpg, *.jpeg, *.png, *.gif, *.bmp -ErrorAction SilentlyContinue
if ($Files.Count -eq 0) {
    Write-Warning "No se encontraron imagenes en $InputDir"
} else {
    foreach ($File in $Files) {
        try {
            Write-Host "[INFO] Analizando: $($File.FullName)"
            $OutJson = Join-Path $OutputDir ($File.BaseName + ".json")

            if ($ExifTool) {
                & exiftool -json $File.FullName | Out-File -Encoding UTF8 $OutJson
            } else {
                # Fallback básico: obtener propiedades con .NET
                $Info = [ordered]@{
                    Nombre     = $File.Name
                    TamanoKB   = [math]::Round($File.Length / 1KB, 2)
                    Modificado = $File.LastWriteTime
                }
                $Info | ConvertTo-Json | Out-File -Encoding UTF8 $OutJson
            }

            $Counts["ImagenesProcesadas"]++
        } catch {
            Write-Warning "Error procesando $($File.Name): $_"
            $Counts["Errores"]++
        }
    }
}

# --- Generar resumen ---
"==== Resumen del Escaneo ====" | Out-File -FilePath $Summary -Encoding UTF8
foreach ($Key in $Counts.Keys) {
    "  - ${Key}: $($Counts[$Key])" | Out-File -Append -FilePath $Summary -Encoding UTF8
}

# --- Salida final ---
$Result = @{
    ok = $true
    files = $Counts["ImagenesProcesadas"]
    outdir = (Resolve-Path $OutputDir).Path
}
$Result | ConvertTo-Json -Compress | Write-Host

