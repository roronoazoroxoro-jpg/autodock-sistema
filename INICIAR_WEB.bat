@echo off
chcp 65001 >nul
title AutoDock Vina MVP - Interfaz Web

set "PROYECTO=%~dp0"
if "%PROYECTO:~-1%"=="\" set "PROYECTO=%PROYECTO:~0,-1%"

echo.
echo ================================================================
echo   AUTODOCK VINA MVP  -  Interfaz Web
echo ================================================================
echo.

if not exist "%PROYECTO%\.venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta SETUP.bat primero.
    pause
    exit /b 1
)

echo   Abriendo: http://127.0.0.1:5000
echo   Presiona Ctrl+C en esta ventana para detener el servidor.
echo.

start "" http://127.0.0.1:5000
"%PROYECTO%\.venv\Scripts\python" "%PROYECTO%\webapp.py"

pause
