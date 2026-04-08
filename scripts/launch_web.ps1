param(
    [string]$ProjectRoot = "$(Resolve-Path "$PSScriptRoot\..")",
    [string]$BindAddress = "127.0.0.1",
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "No existe .venv. Ejecuta primero .\\scripts\\setup_venv.ps1"
}

& .\.venv\Scripts\python.exe webapp.py --host $BindAddress --port $Port
