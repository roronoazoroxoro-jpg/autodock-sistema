@echo off
chcp 65001 >nul
title AutoDock Vina MVP - Configuracion Inicial

echo.
echo ================================================================
echo   AUTODOCK VINA MVP  -  Configuracion de Primera Vez
echo ================================================================
echo.

:: ---------- 1. Verificar Python ----------
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python no encontrado en PATH.
    echo         Descarga Python 3.10 o superior desde:
    echo         https://www.python.org/downloads/
    echo         Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo         Encontrado: %%v

:: ---------- 2. Crear entorno virtual ----------
echo.
echo [2/5] Configurando entorno virtual Python...
if exist ".venv\Scripts\python.exe" (
    echo         Entorno virtual ya existe, omitiendo creacion.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo         Entorno virtual creado.
)

:: ---------- 3. Instalar dependencias ----------
echo.
echo [3/5] Instalando dependencias Python...
.venv\Scripts\pip install -r requirements.txt -q --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias. Revisa requirements.txt.
    pause
    exit /b 1
)
echo         Dependencias instaladas correctamente.

:: ---------- 4. Instalar MGLTools (PowerShell) ----------
echo.
echo [4/5] Instalando MGLTools (requerido para preparar moleculas PDB)...
echo         Esto puede tardar unos minutos. Se descargara el instalador (~73 MB)...
powershell -ExecutionPolicy Bypass -File "scripts\install_windows.ps1"
if %errorlevel% neq 0 (
    echo.
    echo [WARN] La instalacion de MGLTools reporto un error.
    echo        Si usas archivos .pdbqt directamente (modo --skip-prepare), puedes continuar.
    echo        Para preparar moleculas desde PDB, instala MGLTools manualmente:
    echo        https://ccsb.scripps.edu/mgltools/downloads/
)

:: ---------- 5. Verificar instalacion ----------
echo.
echo [5/5] Verificando instalacion completa...
echo.
.venv\Scripts\python -m scripts.verify_install
echo.
echo ================================================================
echo   SETUP COMPLETADO
echo   
echo   Siguientes pasos:
echo     - Docking demo:        DOCK.bat
echo     - Interfaz web:        INICIAR_WEB.bat
echo     - Linea de comandos:   .venv\Scripts\python main.py --help
echo ================================================================
echo.
pause
