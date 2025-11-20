Param(
    [string]$InputDir = "data/raw",
    [string]$OutputDir = "data/clean",
    [string]$LogPath = "examples/logs.jsonl",
    [switch]$UseAI
)

Write-Host "== MetaHunter pipeline =="
Write-Host "InputDir : $InputDir"
Write-Host "OutputDir: $OutputDir"
Write-Host "LogPath  : $LogPath"
Write-Host "UseAI    : $UseAI"

# Crear directorios si no existen
if (-not (Test-Path $InputDir)) {
    Write-Error "No existe el directorio de entrada: $InputDir"
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$logDir = Split-Path $LogPath -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Construir argumentos para Python
$arguments = @(
    "src\metahunter\cli.py",
    "--input-dir", $InputDir,
    "--output-dir", $OutputDir,
    "--log-path", $LogPath
)

if ($UseAI) {
    $arguments += "--use-ai"
}

# Ejecutar CLI
python @arguments

if ($LASTEXITCODE -ne 0) {
    Write-Error "La ejecución del pipeline falló con código $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "Pipeline finalizado correctamente."
