# AutoDock Vina MVP — Guía de Uso Completa

> Versión del sistema: AutoDock Vina 1.2.7 · MGLTools 1.5.6 · Python ≥ 3.10  
> Plataforma: Windows 10 / 11

---

## Tabla de Contenidos

1. [¿Qué es este programa?](#1-qué-es-este-programa)
2. [Requisitos del sistema](#2-requisitos-del-sistema)
3. [Instalación paso a paso](#3-instalación-paso-a-paso)
4. [Ejecutar el docking demo](#4-ejecutar-el-docking-demo)
5. [Usar la interfaz web](#5-usar-la-interfaz-web)
6. [Uso por línea de comandos](#6-uso-por-línea-de-comandos)
7. [Docking con moléculas reales](#7-docking-con-moléculas-reales)
8. [Referencia de config.yaml](#8-referencia-de-configyaml)
9. [Estructura de carpetas](#9-estructura-de-carpetas)
10. [Solución de problemas](#10-solución-de-problemas)
11. [Glosario rápido](#11-glosario-rápido)

---

## 1. ¿Qué es este programa?

Este sistema es una plataforma completa de **docking molecular** basada en AutoDock Vina. Permite:

- **Preparar** moléculas (receptor/proteína y ligando) desde formato PDB a PDBQT
- **Ejecutar** simulaciones de acoplamiento (docking) de manera automatizada
- **Analizar** los resultados: nº de modos de unión, energía de afinidad (kcal/mol)
- **Operar** tanto desde línea de comandos como desde una interfaz web

### ¿Para qué sirve?

El docking molecular predice cómo y con qué energía se une un **ligando** (molécula pequeña, fármaco candidato) a un **receptor** (proteína diana). Un valor de afinidad más negativo (ej: −8.5 kcal/mol) indica una unión más favorable.

---

## 2. Requisitos del sistema

| Componente | Versión mínima | Notas |
|---|---|---|
| **Windows** | 10 / 11 (64-bit) | Necesario para MGLTools y Vina |
| **Python** | 3.10 o superior | https://www.python.org/downloads/ |
| **Espacio en disco** | ~500 MB | Vina (~5 MB) + MGLTools (~250 MB) + venv (~100 MB) |
| **Conexión a internet** | Requerida solo 1 vez | Para descargar MGLTools durante SETUP.bat |

> **Nota sobre Python**: al instalar Python, marca la casilla **"Add Python to PATH"** o las herramientas de línea de comandos no podrán encontrarlo.

---

## 3. Instalación paso a paso

### Paso 1 — Extraer el ZIP

Extrae el contenido del ZIP en una carpeta de tu elección, por ejemplo:

```
C:\Usuarios\TuNombre\Documentos\autodock-vina-mvp\
```

### Paso 2 — Ejecutar SETUP.bat

Haz **doble clic** en el archivo `SETUP.bat` en la raíz del proyecto.

El script realizará automáticamente:

1. Verificar que Python esté instalado
2. Crear el entorno virtual `.venv`
3. Instalar dependencias Python (biopython, numpy, pandas, Flask, etc.)
4. Descargar e instalar **MGLTools 1.5.6** (~73 MB, se instala en `C:\Program Files (x86)\MGLTools-1.5.6`)
5. Verificar que todo esté correcto (9 checks)

> **AutoDock Vina** ya está incluido en el ZIP en `tools\vina\vina.exe` — no se necesita descarga adicional.

### Paso 3 — Confirmar que todo está OK

Al finalizar SETUP.bat verás una lista de checks:

```
[OK] Parametros de docking presentes
[OK] Vina encontrado: ...\tools\vina\vina.exe
[OK] MGLTools root encontrado: C:/Program Files (x86)/MGLTools-1.5.6
[OK] MGLTOOLS_PYTHONSH disponible
[OK] MGLTOOLS_PREPARE_RECEPTOR disponible
[OK] MGLTOOLS_PREPARE_LIGAND disponible
[OK] Input receptor encontrado: receptors/receptor.pdbqt
[OK] Input ligando encontrado: ligands/ligand.pdbqt
[OK] Dependencias Python base disponibles
```

Si todos aparecen `[OK]`, el sistema está listo.

---

## 4. Ejecutar el docking demo

Haz doble clic en **`DOCK.bat`**.

El sistema ejecutará un docking de ejemplo usando los archivos incluidos:
- **Receptor**: un tripéptido de Alanina (demo)
- **Ligando**: etanol (demo)

### Resultado esperado

```
2026-04-02 00:36:45 | INFO | Ejecutando AutoDock Vina
2026-04-02 00:36:47 | INFO | AutoDock Vina v1.2.7
...
mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
  1       -0.973          0          0
  2      -0.938      6.019      6.374
  ...
  9      -0.590      7.234      7.315
2026-04-02 00:36:47 | INFO | Resultado: ...\outputs\docked_receptor_ligand.pdbqt
```

El archivo de salida `outputs\docked_receptor_ligand.pdbqt` contiene todos los modos de unión en formato PDBQT, que puede visualizarse en PyMOL, VMD o UCSF Chimera.

---

## 5. Usar la interfaz web

Haz doble clic en **`INICIAR_WEB.bat`**.

Se abrirá automáticamente el navegador en `http://127.0.0.1:5000`.

### Funcionalidades de la web

| Sección | Descripción |
|---|---|
| **Cargar receptor** | Sube un archivo `.pdb` o `.pdbqt` de la proteína |
| **Cargar ligando** | Sube un archivo `.pdb` o `.pdbqt` del ligando |
| **Saltar preparación** | Checkbox: actívalo si tus archivos ya son `.pdbqt` |
| **Ejecutar Docking** | Lanza el pipeline completo |
| **Resultado** | Muestra los modos de unión al terminar |

Para detener el servidor, cierra la ventana de comandos o presiona `Ctrl+C`.

---

## 6. Uso por línea de comandos

Abre una consola en la carpeta del proyecto y activa el entorno virtual:

```powershell
.venv\Scripts\activate
```

### Comandos principales

**Ver ayuda:**
```powershell
python main.py --help
```

**Docking con archivos demo (sin preparación PDB→PDBQT):**
```powershell
python main.py --skip-prepare --verbose
```

**Docking pasando archivos explícitamente:**
```powershell
python main.py --receptor receptors\mi_proteina.pdb --ligand ligands\mi_ligando.pdb --verbose
```

**Si tus archivos ya son PDBQT:**
```powershell
python main.py --receptor receptors\proteina.pdbqt --ligand ligands\ligando.pdbqt --skip-prepare
```

**Verificar el entorno en cualquier momento:**
```powershell
python -m scripts.verify_install
```

**Iniciar la interfaz web manualmente:**
```powershell
python webapp.py --port 8080
```

### Parámetros de main.py

| Parámetro | Descripción |
|---|---|
| `--config` | Ruta a `config.yaml` (por defecto: `config.yaml`) |
| `--receptor` | Ruta al archivo de receptor (`.pdb` o `.pdbqt`) |
| `--ligand` | Ruta al archivo de ligando (`.pdb` o `.pdbqt`) |
| `--skip-prepare` | No convierte PDB→PDBQT (usa los archivos tal cual) |
| `--verbose` | Muestra logs detallados durante la ejecución |

---

## 7. Docking con moléculas reales

### Paso 1 — Obtener el receptor (proteína)

Descarga el archivo PDB de tu proteína desde [RCSB Protein Data Bank](https://www.rcsb.org/):

1. Ve a https://www.rcsb.org/
2. Busca tu proteína (ej: `1HSG` para la HIV Protease)
3. Haz clic en **Download** → **PDB Format**
4. Guarda el archivo en `receptors\`

### Paso 2 — Obtener el ligando

Opciones:

- **Desde RCSB**: El PDB descargado puede contener ya el ligando (molécula co-cristalizada). Puedes extraerlo con PyMOL.
- **Desde PubChem** (https://pubchem.ncbi.nlm.nih.gov/): descarga el compuesto en formato SDF y conviértelo a PDB con Open Babel.
- **Desde DrugBank** (https://go.drugbank.com/): descarga estructuras 3D en formato PDB.

Guarda el archivo del ligando en `ligands\`.

### Paso 3 — Ajustar el grid de búsqueda en config.yaml

Abre `config.yaml` y modifica las coordenadas del centro y tamaño del grid:

```yaml
docking:
  center_x: X   # Coordenada X del centro del sitio activo
  center_y: Y   # Coordenada Y
  center_z: Z   # Coordenada Z
  size_x: 20.0  # Tamaño del grid en angstroms
  size_y: 20.0
  size_z: 20.0
```

**¿Cómo encontrar las coordenadas del sitio activo?**
1. Abre el receptor en PyMOL o UCSF Chimera.
2. Localiza el sitio activo (generalmente donde estaba el ligando co-cristalizado).
3. Mide las coordenadas XYZ del centro del sitio activo.
4. Ajusta el tamaño para cubrir toda la cavidad (20×20×20 Å es un buen punto de partida).

### Paso 4 — Ejecutar el docking

```powershell
python main.py --receptor receptors\1HSG.pdb --ligand ligands\mi_ligando.pdb --verbose
```

El sistema:
1. Convertirá el receptor PDB → PDBQT (usando MGLTools)
2. Convertirá el ligando PDB → PDBQT
3. Ejecutará el docking con Vina
4. Guardará el resultado en `outputs\`

### Paso 5 — Visualizar resultados

Abre el archivo de salida `outputs\docked_*.pdbqt` con:
- **PyMOL** (open source): https://pymol.org/
- **UCSF Chimera**: https://www.cgl.ucsf.edu/chimera/
- **VMD**: https://www.ks.uiuc.edu/Research/vmd/

En PyMOL puedes cargar both el receptor y el resultado del docking para ver las poses de unión.

---

## 8. Referencia de config.yaml

```yaml
# Directorios de trabajo (relativos al proyecto)
project:
  data_dir: data
  ligands_dir: ligands
  receptors_dir: receptors
  outputs_dir: outputs

# Archivos por defecto (usados si no se pasan por CLI)
inputs:
  receptor: receptors/receptor.pdbqt   # Ruta al receptor por defecto
  ligand: ligands/ligand.pdbqt         # Ruta al ligando por defecto

# Herramientas externas
tools:
  # "" = auto-detección (busca tools/vina/vina.exe automáticamente)
  vina_executable: ""
  # Ruta de instalación de MGLTools (donde instala SETUP.bat)
  mgltools_root: "C:/Program Files (x86)/MGLTools-1.5.6"

# Parámetros del docking
docking:
  center_x: 10.0       # Centro del grid de búsqueda (coordenada X)
  center_y: 10.0       # Centro del grid de búsqueda (coordenada Y)
  center_z: 10.0       # Centro del grid de búsqueda (coordenada Z)
  size_x: 20.0         # Tamaño del grid en Å (eje X)
  size_y: 20.0         # Tamaño del grid en Å (eje Y)
  size_z: 20.0         # Tamaño del grid en Å (eje Z)
  exhaustiveness: 8    # Exhaustividad de búsqueda (mayor = más preciso pero más lento)
  num_modes: 9         # Número de poses a generar
  energy_range: 3      # Rango de energía máximo entre poses (kcal/mol)
  cpu: 0               # CPUs a usar (0 = todos los disponibles)
```

---

## 9. Estructura de carpetas

```
autodock-vina-mvp/
├── SETUP.bat              ← Instalación inicial (ejecutar primero)
├── DOCK.bat               ← Docking demo (doble clic)
├── INICIAR_WEB.bat        ← Interfaz web (doble clic)
├── main.py                ← Entrypoint principal del pipeline
├── webapp.py              ← Servidor Flask para interfaz web
├── config.yaml            ← Configuración central (editar aquí tus parámetros)
├── requirements.txt       ← Dependencias Python
├── GUIA_DE_USO.md         ← Este documento
├── README.md              ← Documentación técnica general
│
├── scripts/               ← Módulos Python del pipeline
│   ├── common.py              Utilidades compartidas
│   ├── prepare_receptor.py    Convierte receptor PDB → PDBQT
│   ├── prepare_ligand.py      Convierte ligando PDB → PDBQT
│   ├── run_vina.py            Ejecuta AutoDock Vina
│   ├── verify_install.py      Verificador del entorno
│   ├── install_windows.ps1    Instalador Windows (Vina + MGLTools)
│   ├── bootstrap_all.ps1      Setup completo one-shot
│   ├── setup_venv.ps1         Creador de entorno virtual
│   ├── launch_web.ps1         Lanzador de interfaz web (PowerShell)
│   └── run_pipeline.ps1       Pipeline completo (PowerShell)
│
├── receptors/             ← Pon aquí tus archivos de receptor (.pdb / .pdbqt)
│   ├── receptor.pdb           Demo: tripéptido ALA
│   └── receptor.pdbqt         Demo: tripéptido ALA (preparado)
│
├── ligands/               ← Pon aquí tus archivos de ligando (.pdb / .pdbqt)
│   ├── ligand.pdb             Demo: etanol
│   └── ligand.pdbqt           Demo: etanol (preparado, con átomos de H dentro de ROOT)
│
├── outputs/               ← Resultados del docking (generados automáticamente)
│   └── docked_*.pdbqt         Archivo de salida con poses de unión
│
├── data/                  ← Datos auxiliares (opcional)
│
├── templates/             ← Plantillas HTML para la interfaz web
│   └── index.html
│
└── tools/                 ← Herramientas externas
    └── vina/
        └── vina.exe       ← AutoDock Vina 1.2.7 (incluido en el ZIP)
```

---

## 10. Solución de problemas

### "Python no encontrado" al ejecutar SETUP.bat

**Causa**: Python no está en el PATH del sistema.

**Solución**: 
1. Descarga Python desde https://www.python.org/downloads/
2. Durante la instalación, marca **"Add Python to PATH"**
3. Cierra y vuelve a abrir el explorador de archivos antes de ejecutar SETUP.bat

---

### "Vina no encontrado" durante el docking

**Causa**: El ejecutable `tools\vina\vina.exe` no está presente.

**Solución**: Asegúrate de haber extraído el ZIP completo. El archivo `vina.exe` debe estar en `tools\vina\`. Si falta, descárgalo manualmente:
```
https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.7/vina_1.2.7_win.exe
```
Renómbralo a `vina.exe` y colócalo en `tools\vina\`.

---

### "MGLTools no encontrado" o `[FAIL]` en verify_install

**Causa**: MGLTools no está instalado o no se instaló correctamente.

**Solución**:
1. Ejecuta de nuevo `SETUP.bat`
2. O descarga el instalador manualmente desde https://ccsb.scripps.edu/mgltools/downloads/ y ejecútalo
3. Asegúrate de que quede instalado en `C:\Program Files (x86)\MGLTools-1.5.6`

> Si usas `--skip-prepare` con archivos ya en formato `.pdbqt`, no necesitas MGLTools.

---

### El docking falla con "Unknown or inappropriate tag"

**Causa**: El archivo PDBQT del ligando tiene átomos fuera de los bloques `ROOT`/`BRANCH`.

**Solución**: Regenera el ligando PDBQT usando el sistema de preparación automática:
```powershell
.venv\Scripts\python main.py --receptor receptors\receptor.pdb --ligand ligands\ligando.pdb
```
Esto usará MGLTools para generar un PDBQT válido.

---

### La interfaz web no carga

**Causa**: El servidor no está iniciado o se inició en un puerto diferente.

**Solución**:
1. Asegúrate de haber ejecutado `INICIAR_WEB.bat` (no cerrar la ventana negra)
2. Abre manualmente http://127.0.0.1:5000 en el navegador
3. Si el puerto 5000 está ocupado: `python webapp.py --port 8080`

---

### Error "No module named scripts"

**Causa**: El entorno virtual no está activado o no se instalaron las dependencias.

**Solución**:
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python main.py --help
```

---

### Permiso denegado al instalar MGLTools

**Causa**: Falta de permisos de administrador.

**Solución**: Cierra SETUP.bat, haz clic derecho sobre él → **"Ejecutar como administrador"**, y vuelve a intentarlo.

---

## 11. Glosario rápido

| Término | Descripción |
|---|---|
| **Docking molecular** | Simulación computacional que predice cómo una molécula pequeña se une a una proteína |
| **Receptor** | La proteína diana (ej: una enzima con un sitio activo) |
| **Ligando** | La molécula pequeña que se quiere acoplar (ej: un fármaco candidato) |
| **PDB** | Formato estándar de coordenadas 3D de moléculas (Protein Data Bank) |
| **PDBQT** | Formato extendido de PDB con cargas parciales (q) y tipo de árbol (t), requerido por Vina |
| **Afinidad (kcal/mol)** | Energía de unión estimada. Más negativo = unión más favorable |
| **Grid box** | Caja 3D que define el espacio de búsqueda del docking alrededor del sitio activo |
| **Exhaustiveness** | Nivel de búsqueda exhaustiva de Vina (8 = estándar, 16+ = mayor precisión) |
| **MGLTools** | Suite de herramientas del Scripps Research para preparar moléculas (PDB→PDBQT) |
| **AutoDock Vina** | Motor de docking desarrollado por el Scripps Research (versión 1.2.7) |
| **RMSD** | Root Mean Square Deviation — diferencia espacial entre poses de unión |

---

*Generado con AutoDock Vina MVP · AutoDock Vina 1.2.7 · MGLTools 1.5.6*
