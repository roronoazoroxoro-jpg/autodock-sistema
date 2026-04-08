@echo off
chcp 65001 >nul
title AutoDock Vina MVP - Interfaz Web

echo.
echo ================================================================
echo   AUTODOCK VINA MVP  -  Interfaz Web
echo ================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta SETUP.bat primero.
    pause
    exit /b 1
)

echo   Abriendo: http://127.0.0.1:5000
echo   Presiona Ctrl+C en esta ventana para detener el servidor.
echo.

start "" http://127.0.0.1:5000
.venv\Scripts\python webapp.py

pause
