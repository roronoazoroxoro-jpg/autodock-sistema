@echo off
chcp 65001 >nul
title Instalando Sistema de Docking Molecular...

set "PROYECTO=%~dp0"
if "%PROYECTO:~-1%"=="\" set "PROYECTO=%PROYECTO:~0,-1%"
set "INSTDIR=%PROYECTO%\instaladores"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║      INSTALACION AUTOMATICA — SISTEMA DE DOCKING MOLECULAR  ║
echo  ║      AutoDock Vina 1.2.7  +  MGLTools 1.5.6  +  Web App    ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Por favor NO cierre esta ventana hasta que termine.
echo  Puede tardar entre 5 y 15 minutos segun la velocidad del equipo.
echo.
echo ----------------------------------------------------------------
echo.

:: Verificar que el script se ejecuta desde la carpeta correcta
if not exist "%PROYECTO%\webapp.py" (
    echo [ERROR] No se encontro webapp.py en %PROYECTO%
    echo         Asegurate de ejecutar este archivo desde la carpeta del sistema.
    pause
    exit /b 1
)

:: ================================================================
:: PASO 1 — Instalar Python si no esta presente
:: ================================================================
echo  [PASO 1/5]  Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo             Python no encontrado. Instalando automaticamente...
    echo.

    set "PYTHON_EXE=%INSTDIR%\python_installer.exe"

    if exist "%PYTHON_EXE%" (
        echo             Usando instalador incluido en USB...
    ) else (
        echo             Descargando Python 3.11 desde python.org...
        if not exist "%INSTDIR%" mkdir "%INSTDIR%"
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%INSTDIR%\python_installer.exe' -UseBasicParsing"
        if not exist "%PYTHON_EXE%" (
            echo.
            echo [ERROR] No se pudo descargar Python. Verifica la conexion a internet.
            echo         O descarga Python manualmente desde: https://www.python.org/downloads/
            echo         (marcar "Add Python to PATH") y vuelve a ejecutar este archivo.
            pause
            exit /b 1
        )
    )

    echo             Instalando Python 3.11 en silencio...
    "%PYTHON_EXE%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if errorlevel 1 (
        echo [ERROR] La instalacion de Python fallo.
        echo         Intenta instalar Python manualmente desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )

    :: Recargar PATH para que python este disponible en esta sesion
    for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set "SYS_PATH=%%a %%b"
    set "PATH=%SYS_PATH%;%PATH%"
    echo             Python instalado correctamente.
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo             OK — %%v
)

:: ================================================================
:: PASO 2 — Instalar MGLTools 1.5.6
:: ================================================================
echo.
echo  [PASO 2/5]  Verificando MGLTools 1.5.6...

if exist "C:\Program Files (x86)\MGLTools-1.5.6\python.exe" (
    echo             OK — MGLTools ya esta instalado.
) else (
    echo             MGLTools no encontrado. Instalando...
    echo             (Puede aparecer un instalador grafico — acepta todo y haz clic en Next/Finish)
    echo.

    set "MGL_EXE=%INSTDIR%\mgltools_installer.exe"

    if exist "%MGL_EXE%" (
        echo             Usando instalador incluido en USB...
    ) else (
        echo             Descargando MGLTools 1.5.6 (~73 MB)...
        if not exist "%INSTDIR%" mkdir "%INSTDIR%"
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "Invoke-WebRequest -Uri 'https://ccsb.scripps.edu/mgltools/downloads/491/mgltools_win32_1.5.6.exe' -OutFile '%INSTDIR%\mgltools_installer.exe' -UseBasicParsing"
    )

    if not exist "%MGL_EXE%" (
        echo.
        echo [AVISO] No se pudo descargar MGLTools automaticamente.
        echo         Descargalo manualmente desde:
        echo           https://ccsb.scripps.edu/mgltools/downloads/
        echo         Instala la version 1.5.6 para Windows y vuelve a ejecutar.
        echo.
        echo         El sistema de docking web funcionara igual.
        echo         Solo no podras preparar archivos .pdb desde AutoDockTools.
        echo.
        set MGL_SKIP=1
    ) else (
        echo             Instalando MGLTools...
        "%MGL_EXE%" /S
        if errorlevel 1 (
            echo [AVISO] MGLTools no pudo instalarse en modo silencioso.
            echo         Intenta ejecutarlo manualmente: %MGL_EXE%
            set MGL_SKIP=1
        ) else (
            echo             MGLTools instalado correctamente.
        )
    )
)

:: ================================================================
:: PASO 3 — Crear entorno virtual Python
:: ================================================================
echo.
echo  [PASO 3/5]  Configurando entorno virtual Python...

if exist "%PROYECTO%\.venv\Scripts\python.exe" (
    echo             OK — entorno virtual ya existe.
) else (
    python -m venv "%PROYECTO%\.venv"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual Python.
        echo         Asegurate de que Python 3.10+ este correctamente instalado.
        pause
        exit /b 1
    )
    echo             Entorno virtual creado.
)

:: ================================================================
:: PASO 4 — Instalar dependencias Python
:: ================================================================
echo.
echo  [PASO 4/5]  Instalando dependencias Python (Flask, BioPython, etc.)...

set "PIP=%PROYECTO%\.venv\Scripts\pip"
set "WHEELS=%INSTDIR%\pip_wheels"

if exist "%WHEELS%" (
    echo             Instalando desde paquetes incluidos en USB (sin internet)...
    "%PIP%" install --no-index --find-links="%WHEELS%" -r "%PROYECTO%\requirements.txt" -q --disable-pip-version-check
) else (
    echo             Instalando desde internet...
    "%PIP%" install -r "%PROYECTO%\requirements.txt" -q --disable-pip-version-check
)

if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias.
    echo         Verifica la conexion a internet e intenta de nuevo.
    pause
    exit /b 1
)
echo             Dependencias instaladas correctamente.

:: ================================================================
:: PASO 5 — Crear accesos directos en el Escritorio
:: ================================================================
echo.
echo  [PASO 5/5]  Creando iconos en el Escritorio...

:: Pasar rutas via variables de entorno para que PowerShell las lea con $env:
:: (evita problemas con espacios en rutas dentro de strings de PowerShell)
set "SC_DESKTOP=%USERPROFILE%\Desktop"
set "SC_MGL=%PROGRAMFILES(X86)%\MGLTools-1.5.6"
set "SC_PROYECTO=%PROYECTO%"

:: --- Icono 1: Sistema Web ---
set "SC_NAME=Docking Molecular - Web.lnk"
set "SC_TARGET=%PROYECTO%\INICIAR.bat"
set "SC_DESC=Sistema de Docking Molecular - Interfaz Web"
set "SC_ICON=%PROGRAMFILES(X86)%\MGLTools-1.5.6\adt.ico"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_PROYECTO; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"

:: --- Icono 2: AutoDockTools ---
if exist "%SC_MGL%\adt.bat" (
    set "SC_NAME=AutoDockTools 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\adt.bat"
    set "SC_DESC=AutoDockTools - Preparacion de moleculas y docking"
    set "SC_ICON=%SC_MGL%\adt.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
)

:: --- Icono 3: PMV ---
if exist "%SC_MGL%\pmv.bat" (
    set "SC_NAME=PMV 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\pmv.bat"
    set "SC_DESC=PMV - Python Molecular Viewer - Visualizacion 3D"
    set "SC_ICON=%SC_MGL%\pmv.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
)

:: --- Icono 4: Vision ---
if exist "%SC_MGL%\vision.bat" (
    set "SC_NAME=Vision 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\vision.bat"
    set "SC_DESC=Vision - Automatizacion visual de flujos de docking"
    set "SC_ICON=%SC_MGL%\vision.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
)

:: --- Icono 5: CADD ---
if exist "%SC_MGL%\cadd.bat" (
    set "SC_NAME=CADD 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\cadd.bat"
    set "SC_DESC=CADD - Suite completa de diseno computacional de farmacos"
    set "SC_ICON=%SC_MGL%\cadd.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
)

echo             Iconos creados en el Escritorio.

:: ================================================================
:: VERIFICACION FINAL
:: ================================================================
echo.
echo ----------------------------------------------------------------
echo  Verificando instalacion completa...
echo.
"%PROYECTO%\.venv\Scripts\python" -m scripts.verify_install
echo.

:: ================================================================
:: LANZAR EL SISTEMA
:: ================================================================
echo ================================================================
echo.
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo.
echo   Iconos creados en tu Escritorio:
echo     Docking Molecular - Web   (el que usaras habitualmente)
echo     AutoDockTools 1.5.6       (preparar moleculas)
echo     PMV 1.5.6                 (visualizar resultados en 3D)
echo     Vision 1.5.6              (automatizacion avanzada)
echo     CADD 1.5.6                (suite completa)
echo.
echo   El sistema se abrira en tu navegador en 5 segundos...
echo   (La proxima vez solo haz doble clic en el icono del Escritorio)
echo.
echo ================================================================
echo.

timeout /t 5 /nobreak

start "" http://127.0.0.1:5000
"%PROYECTO%\.venv\Scripts\python" "%PROYECTO%\webapp.py"

pause
