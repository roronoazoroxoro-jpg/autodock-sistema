@echo off
chcp 65001 >nul
title Copiar sistema a USB (sin descargas)

set "ORIGEN=%~dp0"
if "%ORIGEN:~-1%"=="\" set "ORIGEN=%ORIGEN:~0,-1%"

echo.
echo  ================================================================
echo   COPIAR SISTEMA A USB (SIN DESCARGAS)
echo  ================================================================
echo.
echo  Este script copia solo el proyecto al USB.
echo  No descarga Python, MGLTools ni paquetes de internet.
echo.

echo  Unidades disponibles:
echo.
for %%d in (D E F G H I J K) do (
    if exist "%%d:\" (
        for /f "tokens=2 delims==" %%l in ('wmic logicaldisk where "DeviceID='%%d:'" get VolumeName /value 2^>nul ^| findstr "="') do (
            echo    %%d:  [%%l]
        )
    )
)

echo.
set /p USB_LETRA="  Ingresa la letra de tu USB (D, E, F, etc.): "

if not defined USB_LETRA (
    echo [ERROR] Letra no ingresada.
    pause
    exit /b 1
)

set "USB_LETRA=%USB_LETRA: =%"
if not exist "%USB_LETRA%:\" (
    echo.
    echo [ERROR] La unidad %USB_LETRA%: no existe o no esta conectada.
    pause
    exit /b 1
)

set "DESTINO=%USB_LETRA%:\AutoDockVina"

echo.
echo  Origen : %ORIGEN%
echo  Destino: %DESTINO%
echo.
echo  Copiando archivos...

robocopy "%ORIGEN%" "%DESTINO%" /E /XD ".venv" "__pycache__" "tmp" ".git" /XF "*.pyc" "*.pyo" "*.tmp" /NFL /NDL /NJH /NJS /nc /ns /np

if %errorlevel% GEQ 8 (
    echo.
    echo [ERROR] Error al copiar archivos (codigo %errorlevel%).
    echo         Revisa espacio disponible y permisos del USB.
    pause
    exit /b 1
)

echo.
echo  [OK] Sistema copiado correctamente.
echo.
echo  Siguiente paso en la PC destino:
echo    1. Copiar carpeta AutoDockVina del USB al disco local
echo    2. Ejecutar INSTALAR_TODO.bat
echo.
pause
