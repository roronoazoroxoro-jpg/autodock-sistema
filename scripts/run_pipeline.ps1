param(
    [Parameter(Mandatory = $true)]
    [string]$Receptor,
    [Parameter(Mandatory = $true)]
    [string]$Ligand,
    [switch]$SkipPrepare,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
Set-Location "$(Resolve-Path "$PSScriptRoot\..")"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "No existe .venv. Ejecuta primero .\\scripts\\setup_venv.ps1"
}

$cmd = @("main.py", "--receptor", $Receptor, "--ligand", $Ligand)
if ($SkipPrepare) { $cmd += "--skip-prepare" }
if ($Verbose) { $cmd += "--verbose" }

& .\.venv\Scripts\python.exe @cmd
