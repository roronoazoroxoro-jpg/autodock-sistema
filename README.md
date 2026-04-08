# AutoDock Vina MVP (Windows + Python)

MVP reproducible para docking molecular con AutoDock Vina + AutoDockTools (MGLTools) integrado con Python.

## 1) Estructura

```text
/project
  /data
  /ligands
  /receptors
  /outputs
  /scripts
  main.py
  config.yaml
  requirements.txt
  README.md
```

## 2) Instalacion rapida (Windows PowerShell)

Desde la raiz del proyecto:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\bootstrap_all.ps1
```

Si quieres continuar aunque MGLTools falle (modo parcial con Vina activo):

```powershell
.\scripts\bootstrap_all.ps1 -AllowPartialInstall
```

Instalacion paso a paso:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\install_windows.ps1
.\scripts\setup_venv.ps1
```

Notas:
- El script de instalacion intenta descargar la ultima release de Vina automaticamente.
- Para MGLTools usa URL por defecto. Si cambia, ejecutar con:

```powershell
.\scripts\install_windows.ps1 -MglToolsUrl "URL_DIRECTA_AL_INSTALLER_EXE"
```

- Si MGLTools no instala (servidor externo caido), puedes correr docking con archivos `.pdbqt` usando `--skip-prepare`.

## 3) Configuracion

Editar `config.yaml`:

- `docking.center_x`, `center_y`, `center_z`
- `docking.size_x`, `size_y`, `size_z`
- `docking.exhaustiveness`
- Opcional: rutas absolutas en `tools.vina_executable` y `tools.mgltools_root`

## 4) Ejecucion del flujo completo

### Modo 1 comando (segun config.yaml)

Primero define rutas en `inputs.receptor` y `inputs.ligand` dentro de `config.yaml`.

```powershell
.\.venv\Scripts\python.exe main.py
```

### Caso A: Entradas PDB (preparacion automatica + docking)

```powershell
.\.venv\Scripts\python.exe main.py --receptor receptors\mi_receptor.pdb --ligand ligands\mi_ligando.pdb --verbose
```

### Caso B: Entradas ya preparadas en PDBQT

```powershell
.\.venv\Scripts\python.exe main.py --receptor receptors\mi_receptor.pdbqt --ligand ligands\mi_ligando.pdbqt --skip-prepare --verbose
```

## 5) Salidas

- PDBQT dockeado en `outputs/`
- Log de Vina en `outputs/`
- Archivos preparados (si aplica) en `outputs/prepared/`

## 6) Errores comunes

- Falta `vina.exe` en PATH: reabrir terminal o definir `VINA_EXE`.
- Falta `pythonsh` o scripts `prepare_*`: revisar `MGLTOOLS_ROOT` y reinstalar MGLTools.
- Archivos faltantes: validar rutas de `--receptor` y `--ligand`.

## 7) CLI disponible

`main.py` usa `argparse`:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## 8) Verificacion automatica de entorno

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_install
```

Este comando valida:
- Configuracion de docking en config.yaml
- Presencia de Vina y rutas de MGLTools
- Variables de entorno esperadas
- Dependencias Python
- Existencia de inputs configurados

## 9) Bonus: Mini interfaz web Flask

Ejecutar servidor local:

```powershell
.\.venv\Scripts\python.exe webapp.py
```

o con script PowerShell:

```powershell
.\scripts\launch_web.ps1 -BindAddress 127.0.0.1 -Port 5000
```

Abrir en navegador:

```text
http://127.0.0.1:5000
```

Desde la web puedes subir receptor y ligando y ejecutar docking.

