@echo off
chcp 65001 >nul

set "SC_PROYECTO=%~dp0"
if "%SC_PROYECTO:~-1%"=="\" set "SC_PROYECTO=%SC_PROYECTO:~0,-1%"
set "SC_DESKTOP=%USERPROFILE%\Desktop"

:: Buscar MGLTools en ubicaciones conocidas
set "SC_MGL=%PROGRAMFILES(X86)%\MGLTools-1.5.6"
if not exist "%SC_MGL%" set "SC_MGL=%USERPROFILE%\Desktop\sistema para el doctor policonsultorio\MGLTools-1.5.6"
if not exist "%SC_MGL%" set "SC_MGL=C:\MGLTools-1.5.6"

:: Reparar lanzadores de MGLTools cuando vienen con ruta fija invalida
if exist "%SC_MGL%\python.exe" (
    >"%SC_MGL%\adt.bat" echo @echo off
    >>"%SC_MGL%\adt.bat" echo "%%~dp0python.exe" "%%~dp0Lib\site-packages\AutoDockTools\bin\runAdt.py" %%*

    >"%SC_MGL%\pmv.bat" echo @echo off
    >>"%SC_MGL%\pmv.bat" echo "%%~dp0python.exe" "%%~dp0Lib\site-packages\Pmv\bin\runPmv.py" %%*

    >"%SC_MGL%\vision.bat" echo @echo off
    >>"%SC_MGL%\vision.bat" echo "%%~dp0python.exe" "%%~dp0Lib\site-packages\Vision\bin\runVision.py" %%*

    >"%SC_MGL%\cadd.bat" echo @echo off
    >>"%SC_MGL%\cadd.bat" echo "%%~dp0python.exe" "%%~dp0Lib\site-packages\CADD\bin\runCADD.py" %%*
)

echo Creando iconos en el Escritorio...

:: --- 1: Sistema Web ---
set "SC_NAME=Docking Molecular - Web.lnk"
set "SC_TARGET=%SC_PROYECTO%\INICIAR.bat"
set "SC_DESC=Sistema de Docking Molecular - Interfaz Web"
set "SC_ICON=%SC_MGL%\adt.ico"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_PROYECTO; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
echo [OK] Docking Molecular - Web

:: --- 2: AutoDockTools ---
if exist "%SC_MGL%\adt.bat" (
    set "SC_NAME=AutoDockTools 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\adt.bat"
    set "SC_DESC=AutoDockTools - Preparacion de moleculas y docking"
    set "SC_ICON=%SC_MGL%\adt.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
    echo [OK] AutoDockTools 1.5.6
)

:: --- 3: PMV ---
if exist "%SC_MGL%\pmv.bat" (
    set "SC_NAME=PMV 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\pmv.bat"
    set "SC_DESC=PMV - Python Molecular Viewer - Visualizacion 3D"
    set "SC_ICON=%SC_MGL%\pmv.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
    echo [OK] PMV 1.5.6
)

:: --- 4: Vision ---
if exist "%SC_MGL%\vision.bat" (
    set "SC_NAME=Vision 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\vision.bat"
    set "SC_DESC=Vision - Automatizacion visual de flujos de docking"
    set "SC_ICON=%SC_MGL%\vision.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
    echo [OK] Vision 1.5.6
)

:: --- 5: CADD ---
if exist "%SC_MGL%\cadd.bat" (
    set "SC_NAME=CADD 1.5.6.lnk"
    set "SC_TARGET=%SC_MGL%\cadd.bat"
    set "SC_DESC=CADD - Suite completa de diseno computacional de farmacos"
    set "SC_ICON=%SC_MGL%\cadd.ico"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($env:SC_DESKTOP+'\'+$env:SC_NAME); $s.TargetPath=$env:SC_TARGET; $s.WorkingDirectory=$env:SC_MGL; $s.Description=$env:SC_DESC; $s.IconLocation=$env:SC_ICON; $s.Save()"
    echo [OK] CADD 1.5.6
)

echo.
echo Todos los iconos creados en el Escritorio.
