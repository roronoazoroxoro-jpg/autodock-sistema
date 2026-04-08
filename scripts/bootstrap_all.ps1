param(
    [string]$ProjectRoot = "$(Resolve-Path "$PSScriptRoot\..")",
    [string]$MglToolsUrl = "http://mgltools.scripps.edu/downloads/tars/releases/1.5.7/mgltools_win32_1.5.7.exe",
    [switch]$AllowPartialInstall
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

Write-Host "[1/3] Instalando Vina + MGLTools..."
$installArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", ".\scripts\install_windows.ps1",
    "-ProjectRoot", $ProjectRoot,
    "-MglToolsUrl", $MglToolsUrl
)
if ($AllowPartialInstall) {
    $installArgs += "-AllowPartialInstall"
}
powershell @installArgs
if ($LASTEXITCODE -ne 0) {
    throw "Fallo instalando herramientas externas (Vina/MGLTools)."
}

Write-Host "[2/3] Creando venv e instalando dependencias Python..."
powershell -ExecutionPolicy Bypass -File .\scripts\setup_venv.ps1 -ProjectRoot $ProjectRoot
if ($LASTEXITCODE -ne 0) {
    throw "Fallo creando entorno Python."
}

Write-Host "[3/3] Verificando CLI principal..."
& .\.venv\Scripts\python.exe main.py --help | Out-Null

Write-Host "[extra] Verificando entorno de docking..."
& .\.venv\Scripts\python.exe -m scripts.verify_install
if ($LASTEXITCODE -ne 0 -and -not $AllowPartialInstall) {
    throw "Verificacion final fallo. Revisa mensajes de scripts.verify_install"
}

Write-Host "Bootstrap completo."
Write-Host "Ahora ejecuta: .\\.venv\\Scripts\\python.exe main.py"
