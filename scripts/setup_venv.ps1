param(
    [string]$ProjectRoot = "$(Resolve-Path "$PSScriptRoot\..")"
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

Write-Host "[1/4] Creando entorno virtual (.venv)..."
python -m venv .venv

Write-Host "[2/4] Actualizando pip..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "[3/4] Instalando dependencias Python..."
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "[4/4] Verificando imports principales..."
& .\.venv\Scripts\python.exe -c "import yaml, numpy, pandas, Bio; print('Python deps OK')"

Write-Host "Entorno listo. Activa con: .\\.venv\\Scripts\\Activate.ps1"
