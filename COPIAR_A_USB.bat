@echo off
chcp 65001 >nul
title Preparar USB — Sistema de Docking Molecular

set "ORIGEN=%~dp0"
if "%ORIGEN:~-1%"=="\" set "ORIGEN=%ORIGEN:~0,-1%"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║      PREPARAR USB — SISTEMA DE DOCKING MOLECULAR            ║
echo  ║      Copia archivos + descarga instaladores para offline     ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Este script:
echo    1. Copia todos los archivos del sistema al USB
echo    2. Descarga Python 3.11 para instalar sin internet
echo    3. Descarga MGLTools 1.5.6 para instalar sin internet
echo    4. Descarga paquetes Python para instalar sin internet
echo.
echo  NOTAS:
echo    - El entorno virtual (.venv) NO se copia (no es portable)
echo    - El doctor solo necesitara hacer doble clic en INSTALAR_TODO.bat
echo    - Necesitas conexion a internet en ESTA computadora para descargar
echo.
echo ----------------------------------------------------------------

:: Detectar USBs disponibles
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

if not defined USB_LETRA ( echo [ERROR] Letra no ingresada. & pause & exit /b 1 )
set "USB_LETRA=%USB_LETRA: =%"
if not exist "%USB_LETRA%:\" (
    echo.
    echo [ERROR] La unidad %USB_LETRA%: no existe o no esta conectada.
    pause & exit /b 1
)

set "DESTINO=%USB_LETRA%:\AutoDockVina"
set "INSTDIR=%DESTINO%\instaladores"

echo.
echo  Destino: %DESTINO%
echo.

:: ================================================================
:: PASO 1 — Copiar archivos del proyecto
:: ================================================================
echo  [1/4] Copiando archivos del sistema...
robocopy "%ORIGEN%" "%DESTINO%" /E /XD ".venv" "__pycache__" "tmp" ".git" /XF "*.pyc" "*.pyo" "*.tmp" /NFL /NDL /NJH /NJS /nc /ns /np
if %errorlevel% GEQ 8 (
    echo [ERROR] Error al copiar archivos (codigo %errorlevel%). Verifica espacio en USB.
    pause & exit /b 1
)
echo  [1/4] OK — Archivos copiados.

if not exist "%INSTDIR%" mkdir "%INSTDIR%"

:: ================================================================
:: PASO 2 — Descargar Python 3.11
:: ================================================================
echo.
echo  [2/4] Descargando Python 3.11.9 (~27 MB)...
if exist "%INSTDIR%\python_installer.exe" (
    echo        Ya existe — omitiendo descarga.
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%INSTDIR%\python_installer.exe' -UseBasicParsing"
    if not exist "%INSTDIR%\python_installer.exe" (
        echo [AVISO] No se pudo descargar Python. El doctor necesitara internet en su PC.
    ) else (
        echo  [2/4] OK — Python descargado.
    )
)

:: ================================================================
:: PASO 3 — Descargar MGLTools 1.5.6
:: ================================================================
echo.
echo  [3/4] Descargando MGLTools 1.5.6 (~73 MB)...
if exist "%INSTDIR%\mgltools_installer.exe" (
    echo        Ya existe — omitiendo descarga.
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://ccsb.scripps.edu/mgltools/downloads/491/mgltools_win32_1.5.6.exe' -OutFile '%INSTDIR%\mgltools_installer.exe' -UseBasicParsing"
    if not exist "%INSTDIR%\mgltools_installer.exe" (
        echo [AVISO] No se pudo descargar MGLTools. Se descargara durante la instalacion.
    ) else (
        echo  [3/4] OK — MGLTools descargado.
    )
)

:: ================================================================
:: PASO 4 — Descargar paquetes Python (wheels offline)
:: ================================================================
echo.
echo  [4/4] Descargando paquetes Python para instalar sin internet...
if exist "%INSTDIR%\pip_wheels" (
    echo        Carpeta pip_wheels ya existe — limpiando y actualizando...
    rmdir /s /q "%INSTDIR%\pip_wheels"
)
mkdir "%INSTDIR%\pip_wheels"
"%ORIGEN%\.venv\Scripts\pip" download -r "%ORIGEN%\requirements.txt" -d "%INSTDIR%\pip_wheels" -q --disable-pip-version-check
if errorlevel 1 (
    echo [AVISO] No se pudieron descargar todos los wheels. El doctor necesitara internet para este paso.
) else (
    echo  [4/4] OK — Paquetes Python descargados.
)

:: ================================================================
:: RESULTADO
:: ================================================================
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║   USB LISTO — TODO PREPARADO                                ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Contenido del USB (%DESTINO%):
echo    AutoDockVina\              <- carpeta con todo el sistema
echo    AutoDockVina\INSTALAR_TODO.bat  <- EL UNICO ARCHIVO QUE TOCA EL DOCTOR
echo    AutoDockVina\instaladores\ <- Python + MGLTools + paquetes (offline)
echo.
echo ----------------------------------------------------------------
echo  INSTRUCCIONES PARA EL DOCTOR (solo 3 pasos):
echo ----------------------------------------------------------------
echo.
echo  1. Insertar el USB en su computadora
echo.
echo  2. Copiar la carpeta "AutoDockVina" a su PC
echo     (por ejemplo a C:\AutoDockVina\)
echo.
echo  3. Abrir la carpeta y hacer DOBLE CLIC en:
echo        INSTALAR_TODO.bat
echo.
echo     El sistema instalara Python, MGLTools y todos los programas
echo     automaticamente, creara los iconos en el Escritorio
echo     y abrira el programa listo para usar.
echo.
echo     La proxima vez: doble clic en el icono del Escritorio.
echo.
echo ================================================================
echo.
pause
