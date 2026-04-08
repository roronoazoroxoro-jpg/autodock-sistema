param(
    [string]$ProjectRoot = "$(Resolve-Path "$PSScriptRoot\..")",
    [string]$MglToolsUrl = "http://mgltools.scripps.edu/downloads/tars/releases/1.5.7/mgltools_win32_1.5.7.exe",
    [string]$MglToolsInstallDir = "$env:USERPROFILE\MGLTools-1.5.7",
    [switch]$AllowPartialInstall
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

$toolsDir = Join-Path $ProjectRoot "tools"
$vinaDir = Join-Path $toolsDir "vina"
$tmpDir = Join-Path $toolsDir "tmp"

New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
New-Item -ItemType Directory -Path $vinaDir -Force | Out-Null
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

function Add-UserPath([string]$PathToAdd) {
    if (-not (Test-Path $PathToAdd)) {
        Write-Warning "Ruta no existe, se omite PATH: $PathToAdd"
        return
    }

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($currentPath) {
        $parts = $currentPath.Split(';') | Where-Object { $_ -and $_.Trim() -ne '' }
    }

    if ($parts -contains $PathToAdd) {
        Write-Host "PATH ya contiene: $PathToAdd"
        return
    }

    $newPath = if ($currentPath) { "$currentPath;$PathToAdd" } else { $PathToAdd }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "Agregado al PATH de usuario: $PathToAdd"
}

function Download-LatestVina {
    param([string]$DestinationFolder)

    Write-Host "Buscando release mas reciente de AutoDock Vina..."
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/ccsb-scripps/AutoDock-Vina/releases/latest"
    $asset = $release.assets |
        Where-Object { $_.name -match "win" -and ($_.name -match "zip|exe") } |
        Select-Object -First 1

    if (-not $asset) {
        throw "No se encontro asset de Windows en release de Vina"
    }

    $downloadPath = Join-Path $tmpDir $asset.name
    Write-Host "Descargando Vina: $($asset.browser_download_url)"
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $downloadPath

    if ($downloadPath.ToLower().EndsWith(".zip")) {
        Expand-Archive -Path $downloadPath -DestinationPath $DestinationFolder -Force
    } else {
        Copy-Item $downloadPath (Join-Path $DestinationFolder $asset.name) -Force
    }

    $vinaExe = Get-ChildItem -Path $DestinationFolder -Recurse -Filter "vina*.exe" | Select-Object -First 1
    if (-not $vinaExe) {
        throw "No se encontro vina.exe tras la descarga"
    }

    $standardExe = Join-Path $DestinationFolder "vina.exe"
    if ($vinaExe.FullName -ne $standardExe) {
        Copy-Item $vinaExe.FullName $standardExe -Force
        $vinaExe = Get-Item $standardExe
    }

    return $vinaExe.FullName
}

function Install-MGLTools {
    param(
        [string]$Url,
        [string]$InstallDir
    )

    Write-Host "Instalando MGLTools desde: $Url"
    $installerPath = Join-Path $tmpDir "mgltools_installer.exe"
    Invoke-WebRequest -Uri $Url -OutFile $installerPath

    Write-Host "Ejecutando instalador silencioso de MGLTools..."
    $args = @("/S", "/D=$InstallDir")
    $p = Start-Process -FilePath $installerPath -ArgumentList $args -Wait -PassThru
    if ($p.ExitCode -ne 0) {
        throw "Instalador MGLTools termino con codigo $($p.ExitCode)"
    }

    if (-not (Test-Path $InstallDir)) {
        throw "No se encontro carpeta de instalacion MGLTools: $InstallDir"
    }

    return $InstallDir
}

Write-Host "[1/4] Instalando AutoDock Vina..."
$vinaExe = Download-LatestVina -DestinationFolder $vinaDir
$vinaFolder = Split-Path $vinaExe -Parent

Add-UserPath $vinaFolder
[Environment]::SetEnvironmentVariable("VINA_EXE", $vinaExe, "User")
$env:VINA_EXE = $vinaExe

Write-Host "[2/4] Instalando MGLTools..."
$mglInstalled = $false
$mglRoot = ""
try {
    $mglRoot = Install-MGLTools -Url $MglToolsUrl -InstallDir $MglToolsInstallDir
    $mglInstalled = $true
} catch {
    Write-Warning "No fue posible instalar MGLTools automaticamente. URL usada: $MglToolsUrl"
    Write-Host "Descarga manual sugerida: http://mgltools.scripps.edu/downloads"
    if (-not $AllowPartialInstall) {
        throw
    }
}

Write-Host "[3/4] Configurando PATH y variables de entorno de usuario..."
if ($mglInstalled) {
    Add-UserPath (Join-Path $mglRoot "bin")
    [Environment]::SetEnvironmentVariable("MGLTOOLS_ROOT", $mglRoot, "User")
    [Environment]::SetEnvironmentVariable("MGLTOOLS_PYTHONSH", (Join-Path $mglRoot "pythonsh"), "User")
    [Environment]::SetEnvironmentVariable("MGLTOOLS_PREPARE_RECEPTOR", (Join-Path $mglRoot "MGLToolsPckgs\AutoDockTools\Utilities24\prepare_receptor4.py"), "User")
    [Environment]::SetEnvironmentVariable("MGLTOOLS_PREPARE_LIGAND", (Join-Path $mglRoot "MGLToolsPckgs\AutoDockTools\Utilities24\prepare_ligand4.py"), "User")
    $env:MGLTOOLS_ROOT = $mglRoot
    $env:MGLTOOLS_PYTHONSH = (Join-Path $mglRoot "pythonsh")
    $env:MGLTOOLS_PREPARE_RECEPTOR = (Join-Path $mglRoot "MGLToolsPckgs\AutoDockTools\Utilities24\prepare_receptor4.py")
    $env:MGLTOOLS_PREPARE_LIGAND = (Join-Path $mglRoot "MGLToolsPckgs\AutoDockTools\Utilities24\prepare_ligand4.py")
}

Write-Host "[4/4] Verificando instalacion..."
& $vinaExe --help | Out-Null

if ($mglInstalled) {
    $pythonsh = Join-Path $mglRoot "pythonsh"
    if (-not (Test-Path $pythonsh)) {
        $pythonsh = Join-Path $mglRoot "pythonsh.exe"
    }
    if (-not (Test-Path $pythonsh)) {
        $pythonsh = Join-Path $mglRoot "bin\pythonsh.exe"
    }

    if (-not (Test-Path $pythonsh)) {
        throw "No se encontro pythonsh en MGLTools"
    }
}

Write-Host "Vina OK: $vinaExe"
if ($mglInstalled) {
    Write-Host "MGLTools OK: $mglRoot"
} else {
    Write-Warning "MGLTools no instalado. Puedes trabajar con archivos PDBQT usando --skip-prepare."
}
Write-Host "Instalacion completada. Cierra y reabre terminal para refrescar PATH."
