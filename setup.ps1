param(
  [string]$Python = "python",
  [string]$Venv = ".venv"
)

Write-Host "Creamos venv con $Python en $Venv"
& $Python -m venv $Venv

$Activate = Join-Path $Venv "Scripts\Activate.ps1"
if (Test-Path $Activate) {
  Write-Host "Activando venv..."
  & $Activate
} else {
  Write-Error "No se encontró Activate.ps1 en $Venv\Scripts"
  exit 1
}

python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
  pip install -r requirements.txt
}

pip install -e .

Write-Host "Listo. Para usar: &$Venv\Scripts\Activate.ps1 ; metahunter --help"
