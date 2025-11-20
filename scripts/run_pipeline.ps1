Param(
    [Parameter(Mandatory = $true)]
    [string]$InputDir,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [switch]$UseAI
)

Write-Host "== MetaHunter pipeline =="

if (-not (Test-Path $InputDir)) { Write-Error "No existe: $InputDir"; exit 1 }

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$useAiFlag = $UseAI.IsPresent

python src/metahunter/cli.py `
  --input-dir "$InputDir" `
  --output-dir "$OutputDir" `
  --log-path "$LogPath" `
  --use-ai:$useAiFlag
