@echo off
chcp 65001 >nul
title AutoDock Vina MVP - Docking Demo

set "PROYECTO=%~dp0"
if "%PROYECTO:~-1%"=="\" set "PROYECTO=%PROYECTO:~0,-1%"

echo.
echo ================================================================
echo   AUTODOCK VINA MVP  -  Ejecutando Docking (archivos demo)
echo ================================================================
echo.

if not exist "%PROYECTO%\.venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta SETUP.bat primero.
    pause
    exit /b 1
)

echo Receptor : receptors\receptor.pdbqt
echo Ligando  : ligands\ligand.pdbqt
echo Salida   : outputs\
echo.

"%PROYECTO%\.venv\Scripts\python" "%PROYECTO%\main.py" --skip-prepare --verbose

echo.
echo ================================================================
echo   Docking finalizado. Revisa la carpeta outputs\
echo ================================================================
echo.
pause
