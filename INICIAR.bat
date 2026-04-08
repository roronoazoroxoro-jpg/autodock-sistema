@echo off
chcp 65001 >nul
title AutoDock Vina — Sistema de Docking Molecular

:: Directorio raiz del proyecto (donde esta este .bat)
set "PROYECTO=%~dp0"
if "%PROYECTO:~-1%"=="\" set "PROYECTO=%PROYECTO:~0,-1%"

echo.
echo ================================================================
echo   SISTEMA DE DOCKING MOLECULAR
echo   AutoDock Vina 1.2.7 + MGLTools 1.5.6
echo ================================================================
echo.

:: ================================================================
:: FASE 1 — Verificar que Python este instalado
:: ================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en esta computadora.
    echo.
    echo  Para instalar Python:
    echo   1. Abre el navegador y ve a: https://www.python.org/downloads/
    echo   2. Descarga Python 3.10 o superior
    echo   3. Ejecuta el instalador
    echo   4. IMPORTANTE: marca la casilla "Add Python to PATH"
    echo   5. Reinicia la computadora
    echo   6. Vuelve a abrir este archivo
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Python encontrado: %%v

:: ================================================================
:: FASE 2 — Primera instalacion automatica (solo si es necesario)
:: ================================================================
if not exist "%PROYECTO%\.venv\Scripts\python.exe" (
    echo.
    echo ----------------------------------------------------------------
    echo   PRIMERA EJECUCION — Instalando el sistema automaticamente
    echo   Esto puede tardar entre 5 y 15 minutos.
    echo   Por favor NO cierre esta ventana.
    echo ----------------------------------------------------------------
    echo.

    :: --- Paso 1: Crear entorno virtual ---
    echo  [1/3] Creando entorno virtual Python...
    python -m venv "%PROYECTO%\.venv"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual.
        echo         Asegurate de tener Python 3.10+ y ejecutar como administrador.
        pause
        exit /b 1
    )
    echo  [1/3] OK

    :: --- Paso 2: Instalar dependencias Python ---
    echo  [2/3] Instalando dependencias Python ^(Flask, BioPython, etc.^)...
    "%PROYECTO%\.venv\Scripts\pip" install -r "%PROYECTO%\requirements.txt" -q --disable-pip-version-check
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudieron instalar las dependencias Python.
        echo         Verifica la conexion a internet e intenta de nuevo.
        pause
        exit /b 1
    )
    echo  [2/3] OK

    :: --- Paso 3: Instalar MGLTools ---
    echo  [3/3] Verificando MGLTools 1.5.6...
    if exist "C:\Program Files (x86)\MGLTools-1.5.6\pythonsh.exe" (
        echo  [3/3] OK  ^(MGLTools ya estaba instalado^)
    ) else (
        echo        MGLTools no encontrado. Instalando ahora ^(~73 MB^)...
        echo        Puede aparecer una ventana del instalador, sigue los pasos.
        powershell -ExecutionPolicy Bypass -File "%PROYECTO%\scripts\install_windows.ps1" -AllowPartialInstall
        if errorlevel 1 (
            echo.
            echo  [AVISO] MGLTools no se instalo completamente.
            echo          El sistema funciona con archivos .pdbqt directamente.
            echo          Para preparar archivos .pdb necesitaras MGLTools.
        ) else (
            echo  [3/3] OK
        )
    )

    :: --- Verificacion final ---
    echo.
    echo  Verificando instalacion completa...
    "%PROYECTO%\.venv\Scripts\python" -m scripts.verify_install
    echo.

    echo ----------------------------------------------------------------
    echo   INSTALACION COMPLETADA
    echo ----------------------------------------------------------------
    echo.

    :: --- Crear acceso directo en el Escritorio ---
    echo  Creando acceso directo en el Escritorio...
    call "%PROYECTO%\CREAR_ACCESO_DIRECTO.bat"
    echo.

    timeout /t 3 /nobreak >nul
) else (
    echo  Sistema ya instalado. Iniciando directamente...
    echo.
)

:: ================================================================
:: FASE 3 — Iniciar la interfaz web
:: ================================================================
echo ================================================================
echo   Abriendo interfaz web en: http://127.0.0.1:5000
echo   Para cerrar el sistema: cierre esta ventana o presione Ctrl+C
echo ================================================================
echo.

start "" http://127.0.0.1:5000
"%PROYECTO%\.venv\Scripts\python" "%PROYECTO%\webapp.py"

echo.
echo  El servidor se ha detenido.
pause
