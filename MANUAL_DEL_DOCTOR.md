# MANUAL DEL SISTEMA DE DOCKING MOLECULAR
## Guía completa para el Doctor — Policonsultorio

> **Sistema:** AutoDock Vina 1.2.7 · MGLTools 1.5.6 · Pipeline personalizado  
> **Plataforma:** Windows 10 / 11  
> **Fecha de emisión:** Abril 2026

---

## ÍNDICE

1. [¿Qué es el docking molecular?](#1-qué-es-el-docking-molecular)
2. [Mapa del sistema — qué programa hace qué](#2-mapa-del-sistema)
3. [HERRAMIENTA 1 — Pipeline Personalizado (DOCK.bat / Web)](#3-herramienta-1--pipeline-personalizado)
4. [HERRAMIENTA 2 — AutoDockTools 1.5.6](#4-herramienta-2--autodocktools-156)
5. [HERRAMIENTA 3 — PMV 1.5.6 (Python Molecular Viewer)](#5-herramienta-3--pmv-156)
6. [HERRAMIENTA 4 — Vision 1.5.6](#6-herramienta-4--vision-156)
7. [HERRAMIENTA 5 — CADD 1.5.6](#7-herramienta-5--cadd-156)
8. [Flujo de trabajo recomendado](#8-flujo-de-trabajo-recomendado)
9. [Reglas de oro — Buenas prácticas](#9-reglas-de-oro)
10. [Glosario esencial](#10-glosario-esencial)

---

## 1. ¿Qué es el docking molecular?

El **docking molecular** (acoplamiento molecular) es una técnica computacional que predice **cómo y con qué fuerza** una molécula pequeña (fármaco candidato, llamada **ligando**) se une a una proteína diana (llamada **receptor**).

### ¿Por qué es útil?

- Permite evaluar **cientos de compuestos** sin necesidad de sintetizarlos físicamente
- Predice la **energía de afinidad** de unión en kcal/mol
- Un valor **más negativo = mejor unión** (ej: −9.2 kcal/mol es mejor que −5.1 kcal/mol)
- Reduce costos y tiempo en el desarrollo de fármacos

### Analogía simple

Imagine que el receptor es una **cerradura** y el ligando es una **llave**. El docking calcula qué tan bien encaja la llave en la cerradura y cuántas formas diferentes puede entrar.

---

## 2. Mapa del sistema

Tiene instalados **5 componentes** que trabajan en conjunto:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE DOCKING MOLECULAR                  │
├─────────────────┬───────────────────────────────────────────────┤
│   PROGRAMA      │   FUNCIÓN PRINCIPAL                           │
├─────────────────┼───────────────────────────────────────────────┤
│ Pipeline Web/   │ Docking automatizado con 1 doble clic o       │
│ DOCK.bat        │ interfaz web. USO MÁS FRECUENTE.             │
├─────────────────┼───────────────────────────────────────────────┤
│ AutoDockTools   │ Preparar proteínas y ligandos en formato      │
│ 1.5.6           │ PDBQT. Definir la zona de búsqueda (grid).   │
├─────────────────┼───────────────────────────────────────────────┤
│ PMV 1.5.6       │ Visualizar moléculas en 3D. Examinar          │
│                 │ resultados del docking. Explorar estructuras. │
├─────────────────┼───────────────────────────────────────────────┤
│ Vision 1.5.6    │ Automatizar flujos de trabajo complejos       │
│                 │ mediante nodos visuales (uso avanzado).       │
├─────────────────┼───────────────────────────────────────────────┤
│ CADD 1.5.6      │ Suite completa de diseño computacional de     │
│                 │ fármacos. Incluye los 3 anteriores + extras.  │
└─────────────────┴───────────────────────────────────────────────┘
```

### ¿Cuando usar cada uno?

| Situación | Herramienta recomendada |
|---|---|
| Quiero hacer un docking rápido con mis archivos | **Pipeline (DOCK.bat o Web)** |
| Necesito preparar una proteína nueva para docking | **AutoDockTools** |
| Quiero ver en 3D cómo quedó el resultado | **PMV** |
| Quiero explorar la proteína antes del docking | **PMV** |
| Quiero automatizar múltiples experimentos | **Vision** |
| Necesito todo en un solo lugar | **CADD** |

---

## 3. HERRAMIENTA 1 — Pipeline Personalizado

> **Archivos:** `SETUP.bat`, `DOCK.bat`, `INICIAR_WEB.bat`  
> **Nivel de uso:** Básico — Cotidiano  
> **Requiere:** Haber ejecutado SETUP.bat al menos una vez

### ¿Qué es?

Es el sistema automatizado que se desarrolló específicamente para usted. Toma sus archivos de proteína y fármaco, ejecuta el docking automáticamente, y le muestra los resultados de energía de unión — sin necesidad de conocer los tecnicismos.

---

### 3.1 — SETUP.bat (Instalación inicial)

**Solo se ejecuta UNA VEZ**, la primera vez que configura el sistema.

**Procedimiento:**
1. Haga doble clic en `SETUP.bat`
2. Espere entre 5 y 10 minutos (descarga MGLTools automáticamente)
3. Confirme que aparecen los 9 checks en verde `[OK]`

**Reglas:**
- ✅ Ejecutarlo con conexión a internet activa
- ✅ No cerrar la ventana negra mientras trabaja
- ❌ No ejecutarlo nuevamente a menos que el sistema dé errores persistentes
- ❌ No mover la carpeta del proyecto después de ejecutar SETUP.bat sin volver a configurar

---

### 3.2 — DOCK.bat (Docking de un clic)

Ejecuta el docking usando los archivos actualmente en las carpetas `receptors/` y `ligands/`.

**Procedimiento:**
1. Coloque su receptor en la carpeta `receptors\` (formatos `.pdb` o `.pdbqt`)
2. Coloque su ligando en la carpeta `ligands\` (formatos `.pdb` o `.pdbqt`)
3. Edite `config.yaml` con las coordenadas del sitio activo (ver sección 8)
4. Haga doble clic en `DOCK.bat`
5. Espere a que termine — los resultados aparecen en `outputs\`

**Reglas:**
- ✅ Los archivos deben estar en las carpetas correctas antes de iniciar
- ✅ Las coordenadas del grid en `config.yaml` deben corresponder al sitio activo de su proteína
- ✅ Revise el archivo `.log` en `outputs\` para ver las energías de afinidad
- ❌ No use nombres de archivo con espacios o caracteres especiales (acentos, ñ, etc.)
- ❌ No cierre la ventana negra mientras el docking está en progreso

**Cómo leer los resultados (archivo .log):**
```
mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1        -8.5      0.000      0.000   ← MEJOR POSE (la más favorable)
   2        -8.1      1.234      2.108
   3        -7.9      2.456      3.201
```
- **mode 1** = la mejor pose de unión
- **affinity** = energía de afinidad (más negativo = mejor)
- Los modos siguientes son poses alternativas ordenadas de mejor a peor

---

### 3.3 — INICIAR_WEB.bat (Interfaz web)

Abre una interfaz gráfica en su navegador para hacer docking sin tocar archivos directamente.

**Procedimiento:**
1. Haga doble clic en `INICIAR_WEB.bat`
2. Espere a que aparezca el mensaje `Running on http://127.0.0.1:5000`
3. Su navegador se abrirá automáticamente (o abra Chrome/Edge y vaya a `http://localhost:5000`)
4. Suba el archivo del receptor y del ligando usando los botones de la página
5. Active "Saltar preparación" si sus archivos ya están en formato `.pdbqt`
6. Haga clic en **Ejecutar Docking**

**Reglas:**
- ✅ No cerrar la ventana negra de la terminal mientras usa la interfaz web
- ✅ El servidor solo funciona en su computadora (no es accesible desde internet por defecto)
- ✅ Formatos aceptados: `.pdb` y `.pdbqt` únicamente
- ✅ Para detener el servidor: cierre la ventana negra o presione `Ctrl+C` en ella
- ❌ No abrir la interfaz web desde otra computadora sin configuración adicional (seguridad)
- ❌ No subir archivos con datos sensibles de pacientes a través de la interfaz web sin medidas de seguridad adicionales

---

## 4. HERRAMIENTA 2 — AutoDockTools 1.5.6

> **Acceso:** Ícono de escritorio "AutoDockTools-1.5.6"  
> **Nivel de uso:** Intermedio  
> **Uso principal:** Preparar archivos y definir parámetros de docking

### ¿Qué es?

AutoDockTools (ADT) es la **interfaz gráfica oficial** del laboratorio Scripps Research para preparar experimentos de docking. Permite cargar proteínas y moléculas, editarlas, añadir hidrógenos, asignar cargas, y definir la zona de búsqueda (grid box).

### ¿Cuándo lo necesita?

Lo necesita cuando tiene un archivo PDB de una proteína nueva y necesita:
- Limpiarla (eliminar moléculas de agua, ligandos co-cristalizados)
- Añadir hidrógenos polares
- Asignar cargas de Gasteiger
- Definir el grid box (caja de búsqueda del sitio activo)
- Convertirla al formato PDBQT que entiende AutoDock Vina

---

### 4.1 — Cómo abrir AutoDockTools

1. Haga doble clic en el ícono **AutoDockTools-1.5.6** del escritorio
2. Espere a que cargue la interfaz (puede tardar 20-30 segundos)
3. Verá una ventana con menús: `File`, `Edit`, `Select`, `Docking`, `Grid`, `Help`

---

### 4.2 — Preparar un receptor (proteína)

Este proceso convierte su proteína `.pdb` al formato `.pdbqt` que necesita el sistema.

**Pasos:**
1. Menú `File → Read Molecule` → seleccione su archivo `.pdb`
2. La proteína aparecerá en la ventana 3D
3. Menú `Edit → Hydrogens → Add` → seleccione **"Polar only"** → OK
4. Menú `Edit → Charges → Compute Gasteiger`
5. Menú `Grid → Macromolecule → Choose` → seleccione su proteína → OK
6. Cuando pregunte "¿Guardar como PDBQT?", haga clic en **Yes**
7. Guarde el archivo en la carpeta `receptors\` del proyecto

**Reglas:**
- ✅ Siempre añadir hidrógenos polares antes de guardar como PDBQT
- ✅ Siempre computar cargas de Gasteiger antes de guardar
- ✅ Eliminar moléculas de agua (`Edit → Delete Water`) antes de preparar
- ✅ Eliminar ligandos co-cristalizados si no son el objetivo de estudio
- ❌ No guardar con todos los hidrógenos (solo polares)
- ❌ No usar archivos PDB con errores de estructura (verifique en RCSB que tenga resolución < 2.5 Å)
- ❌ No incluir cadenas alternativas — quédese solo con la cadena A

---

### 4.3 — Preparar un ligando (fármaco candidato)

**Pasos:**
1. Menú `Ligand → Input → Open` → seleccione su archivo `.pdb` del ligando
2. ADT detectará automáticamente los enlaces rotables
3. Revise los **torsion angles** (enlaces rotables) en la ventana que aparece
4. Menú `Ligand → Output → Save as PDBQT`
5. Guarde en la carpeta `ligands\` del proyecto

**Reglas:**
- ✅ El ligando debe tener hidrógenos explícitos en el archivo PDB antes de cargarlo
- ✅ Verificar que los enlaces rotables detectados sean razonables (no más de 10-12 para docking eficiente)
- ✅ Si tiene más de 15 enlaces rotables, considere fijar algunos (`Ligand → Torsion tree → Fix selected bonds`)
- ❌ No guardar moléculas con cargas formales incorrectas
- ❌ Evitar ligas con más de 30 átomos pesados para docking rápido

---

### 4.4 — Definir el Grid Box (zona de búsqueda)

El grid box define **dónde** buscará AutoDock Vina las poses de unión. Es crítico orientarlo sobre el sitio activo.

**Pasos:**
1. Con el receptor cargado, vaya a `Grid → Grid Box`
2. Aparecerá una caja verde en la pantalla 3D
3. Use los sliders para mover el **centro** (X, Y, Z) sobre el sitio activo
4. Ajuste el **tamaño** (Spacing × Npts) para cubrir toda la cavidad
5. **Anote los valores** de Center X, Y, Z y Size X, Y, Z
6. Copie esos valores a `config.yaml` en el proyecto

**Reglas:**
- ✅ El grid debe cubrir completamente el sitio activo con al menos 2 Å de margen
- ✅ Un tamaño de 20×20×20 Å (Spacing=1.0, Npts=20) funciona para la mayoría de sitios activos
- ✅ Si conoce el ligando co-cristalizado, centre el grid sobre él
- ❌ No usar grids muy grandes (>40×40×40) — aumenta mucho el tiempo de cálculo
- ❌ No colocar el grid en una zona abierta lejos del sitio activo

---

## 5. HERRAMIENTA 3 — PMV 1.5.6

> **Acceso:** Ícono de escritorio "PMV-1.5.6"  
> **Nivel de uso:** Básico-Intermedio  
> **Uso principal:** Visualización 3D de moléculas y resultados

### ¿Qué es?

PMV (Python Molecular Viewer) es un **visor molecular 3D** de alto rendimiento. Permite cargar proteínas, ligandos y resultados de docking para inspeccionarlos visualmente, medir distancias, analizar interacciones y generar imágenes.

### ¿Cuándo lo necesita?

- Después de un docking, para ver cómo quedó el ligando dentro del sitio activo
- Para explorar una proteína antes de definir el grid box
- Para generar imágenes de calidad para presentaciones o publicaciones
- Para medir distancias entre átomos

---

### 5.1 — Cómo abrir PMV

1. Haga doble clic en el ícono **PMV-1.5.6** del escritorio
2. Espere a que cargue (30-45 segundos la primera vez)
3. Verá una ventana 3D gris con menús en la parte superior

---

### 5.2 — Cargar y visualizar una molécula

**Cargar el receptor:**
1. Menú `File → Read Molecule` → seleccione su archivo `.pdb` o `.pdbqt`
2. La molécula aparecerá representada como líneas (`lines`)
3. Para una mejor visualización: `Display → Ribbon` (muestra la estructura secundaria)

**Cargar el resultado del docking:**
1. Menú `File → Read Molecule` → seleccione el archivo `docked_*.pdbqt` de la carpeta `outputs\`
2. Aparecerá el ligando en su pose de mejor unión
3. Para ver todas las poses: el archivo PDBQT contiene todos los modos, navegue con los controles de MODEL

---

### 5.3 — Controles de navegación 3D

| Acción | Cómo hacerlo |
|---|---|
| Rotar la molécula | Clic izquierdo + arrastrar |
| Hacer zoom | Rueda del ratón o clic derecho + arrastrar |
| Trasladar (mover en pantalla) | Clic del medio + arrastrar |
| Centrar en una selección | Tecla `F` o `View → Center on Selection` |
| Restablecer vista | `View → Reset` |

---

### 5.4 — Cambiar representaciones visuales

| Representación | Cuándo usarla | Menú |
|---|---|---|
| **Lines** | Vista rápida general | `Display → Lines` |
| **Sticks** | Ver ligandos claramente | `Display → Sticks` |
| **Ribbon/Cartoon** | Estructura secundaria de la proteína | `Display → Ribbon` |
| **Surface** | Ver cavidades y sitios activos | `Display → MSMS Surface` |
| **Balls & Sticks** | Vista detallada de atomos | `Display → Balls & Sticks` |

---

### 5.5 — Medir distancias entre átomos

Útil para verificar interacciones ligando-receptor (enlaces de hidrógeno, etc.)

1. Menú `Tools → Measurements → Add Distance`
2. Haga clic en el primer átomo
3. Haga clic en el segundo átomo
4. Aparecerá la distancia en Angstroms (Å) entre ellos

**Interpretación:**
- Distancia < 3.5 Å entre N/O = posible **enlace de hidrógeno** (favorable)
- Distancia 3.5–4.5 Å entre carbonos = posible **interacción hidrofóbica**

**Reglas:**
- ✅ Siempre visualizar el resultado del docking junto con el receptor para evaluar la pose
- ✅ Comparar el ligando dockeado con el ligando co-cristalizado del PDB original (si existe)
- ✅ Usar la representación Surface para identificar si el ligando queda dentro de la cavidad
- ❌ No guardar imágenes con resolución menor a 300 DPI para publicaciones
- ❌ No confundir el modo 1 (mejor pose) con los modos alternativos

---

### 5.6 — Guardar una imagen

1. Menú `File → Save → Image`
2. Elija formato PNG o TIFF para mejor calidad
3. Ajuste la resolución (300 DPI para publicación)
4. Haga clic en **Save**

---

## 6. HERRAMIENTA 4 — Vision 1.5.6

> **Acceso:** Ícono de escritorio "Vision-1.5.6"  
> **Nivel de uso:** Avanzado  
> **Uso principal:** Automatización visual de flujos de trabajo complejos

### ¿Qué es?

Vision es un **entorno de programación visual basado en nodos**. En lugar de escribir código, usted conecta "cajas" (nodos) que representan operaciones moleculares, formando flujos de trabajo visualmente. Es poderoso para:

- Automatizar el procesamiento de múltiples moléculas a la vez
- Crear pipelines personalizados de análisis
- Ejecutar operaciones en lote sin escribir código

### ¿Cuándo usarlo?

Vision está pensado para uso **avanzado e investigación**. Para el trabajo clínico y de investigación cotidiano, el Pipeline Personalizado (DOCK.bat) es suficiente y más simple.

Considere Vision cuando necesite:
- Procesar **decenas o cientos** de ligandos de forma automatizada
- Crear un flujo de trabajo **reusable** y documentado visualmente
- Integrar múltiples operaciones (carga → preparación → docking → análisis) en un solo diagrama

---

### 6.1 — Cómo abrir Vision

1. Haga doble clic en el ícono **Vision-1.5.6** del escritorio
2. Se abrirá una interfaz con panel de nodos disponibles (izquierda) y área de trabajo (derecha)

---

### 6.2 — Flujo básico en Vision

1. **Arrastre nodos** desde el panel izquierdo hacia el área de trabajo
2. **Conecte las salidas** de un nodo con las entradas del siguiente (haga clic en el puerto de salida y arrastre al puerto de entrada)
3. **Configure cada nodo** haciendo doble clic sobre él
4. **Ejecute** el flujo con el botón `Run` o `F5`
5. **Guarde** el flujo de trabajo con `File → Save` (extensión `.vf`)

---

### 6.3 — Reglas de uso de Vision

- ✅ Guarde su flujo de trabajo frecuentemente con `File → Save`
- ✅ Nombre los flujos de trabajo de forma descriptiva (ej: `docking_lote_proteina_X.vf`)
- ✅ Pruebe el flujo con una sola molécula antes de ejecutarlo en lote
- ✅ Documente sus nodos con comentarios (clic derecho → Add Comment)
- ❌ No ejecutar flujos en lote con más de 50 moléculas sin verificar que la computadora tiene suficiente RAM (recomendado: 8 GB o más)
- ❌ No cerrar Vision mientras un flujo está en ejecución
- ❌ Vision no es recomendable para usuarios sin conocimiento previo de AutoDock/MGLTools

---

## 7. HERRAMIENTA 5 — CADD 1.5.6

> **Acceso:** Ícono de escritorio "CADD-1.5.6"  
> **Nivel de uso:** Avanzado  
> **Uso principal:** Suite completa de diseño de fármacos computacional

### ¿Qué es?

CADD (Computer-Aided Drug Design Suite) es la **suite completa de MGLTools** que integra en un solo lanzador:
- PMV (visualización)
- AutoDockTools (preparación y docking)
- Vision (automatización)
- Herramientas adicionales de análisis

### ¿Cuándo usarlo?

CADD es el punto de entrada **todo-en-uno** de MGLTools. Si no está seguro de qué herramienta necesita, abra CADD y desde allí puede acceder a todas las funciones.

---

### 7.1 — Cómo abrir CADD

1. Haga doble clic en el ícono **CADD-1.5.6** del escritorio
2. Se abrirá la interfaz principal de la suite
3. Desde el menú puede acceder a todas las herramientas integradas

---

### 7.2 — Funciones principales accesibles desde CADD

| Función | Descripción |
|---|---|
| **Molecular Viewer** | Equivalente a PMV — visualización 3D |
| **AutoDock Setup** | Configurar y ejecutar experimentos de docking |
| **Ligand Scout** | Buscar y analizar ligandos |
| **Docking Analysis** | Analizar resultados de múltiples experimentos |
| **Virtual Screening** | Tamizaje virtual de librerías de compuestos |

---

### 7.3 — Reglas de uso de CADD

- ✅ Use CADD cuando quiera explorar múltiples herramientas en una sesión de trabajo
- ✅ Guarde los proyectos CADD regularmente con `File → Save Project`
- ✅ Para docking simple con sus archivos preparados, siga prefiriendo el Pipeline Personalizado
- ❌ No use CADD para tamizaje virtual masivo en una computadora con menos de 16 GB de RAM
- ❌ No mezcle archivos de proyectos CADD con los archivos del Pipeline Personalizado en la misma carpeta

---

## 8. Flujo de trabajo recomendado

### Caso A: Docking rápido con archivos conocidos

```
Tengo archivos .pdbqt listos
          ↓
   DOCK.bat o Web
   (DOCK.bat / INICIAR_WEB.bat)
          ↓
   Ver resultados en
   outputs\docked_*.log
          ↓
   Visualizar en PMV
   (abrir receptor + resultado)
```

---

### Caso B: Docking con proteína nueva (archivo PDB del RCSB)

```
1. Descargar proteína de https://www.rcsb.org/
   (formato PDB)
          ↓
2. Abrir AutoDockTools
   → Cargar PDB
   → Eliminar agua y ligandos no deseados
   → Añadir hidrógenos polares
   → Computar cargas Gasteiger
   → Guardar como .pdbqt en receptors\
          ↓
3. Obtener ligando (RCSB / PubChem / DrugBank)
   → Preparar con AutoDockTools
   → Guardar como .pdbqt en ligands\
          ↓
4. Definir Grid Box en AutoDockTools
   → Anotar Center X, Y, Z y Size X, Y, Z
   → Actualizar config.yaml
          ↓
5. Ejecutar DOCK.bat
          ↓
6. Visualizar resultado en PMV
```

---

### Caso C: Tamizaje de múltiples fármacos candidatos

```
1. Preparar el receptor una sola vez (AutoDockTools)
          ↓
2. Preparar todos los ligandos candidatos (AutoDockTools / Vision en lote)
          ↓
3. Ejecutar el Pipeline por cada ligando
   (automatizable con Vision o scripts PowerShell)
          ↓
4. Comparar energías de afinidad del .log de cada resultado
          ↓
5. Identificar los candidatos con mejor afinidad (más negativos)
          ↓
6. Visualizar top candidatos en PMV / CADD para análisis detallado
```

---

### Dónde obtener proteínas y fármacos candidatos

| Recurso | URL | Qué tiene |
|---|---|---|
| **RCSB Protein Data Bank** | https://www.rcsb.org/ | Estructuras 3D de proteínas |
| **PubChem** | https://pubchem.ncbi.nlm.nih.gov/ | Estructuras de compuestos químicos |
| **DrugBank** | https://go.drugbank.com/ | Fármacos aprobados y candidatos |
| **ChEMBL** | https://www.ebi.ac.uk/chembl/ | Datos de actividad biológica |
| **UniProt** | https://www.uniprot.org/ | Información de proteínas |

---

## 9. Reglas de oro

### Organización de archivos

- ✅ **Siempre** guarde receptores en `receptors\` y ligandos en `ligands\`
- ✅ Use nombres de archivo **sin espacios, sin tildes, sin ñ**: `proteina_EGFR.pdb` ✓ · `proteína EGFR.pdb` ✗
- ✅ Mantenga copias de los archivos `.pdbqt` preparados — no los elimine
- ✅ Cree una subcarpeta por proyecto/experimento si trabaja con múltiples sistemas

### Calidad de los datos

- ✅ Use estructuras de proteína con **resolución cristalográfica ≤ 2.5 Å** (el RCSB la indica)
- ✅ Prefiera estructuras con el ligando co-cristalizado — facilita la validación del grid
- ✅ Verifique que el receptor no tenga residuos faltantes en el sitio activo antes del docking
- ❌ No use estructuras de homología no validadas para docking sin advertir los resultados

### Interpretación de resultados

- ✅ Una energía de afinidad de **−7 a −9 kcal/mol** se considera buena unión para fármacos típicos
- ✅ Compare **siempre** su ligando de interés contra un ligando de referencia conocido
- ✅ Analice las poses visualmente en PMV — una buena energía no garantiza una buena pose geométrica
- ❌ No tome decisiones clínicas o preclínicas basándose **únicamente** en resultados de docking
- ❌ No ignore el análisis visual de la pose aunque la energía sea favorable

### Seguridad y respaldo

- ✅ Haga copia de seguridad de la carpeta del proyecto periódicamente
- ✅ Guarde los archivos `.log` de cada experimento — contienen toda la información de las poses
- ✅ Registre en una hoja de cálculo: proteína, ligando, afinidad del modo 1, fecha, notas
- ❌ No elimine los archivos de la carpeta `outputs\` sin archivar los resultados relevantes

---

## 10. Glosario esencial

| Término | Definición |
|---|---|
| **Receptor** | Proteína diana — la "cerradura" molecular. Generalmente una enzima o receptor farmacológico. |
| **Ligando** | Molécula pequeña (fármaco candidato) — la "llave". |
| **PDBQT** | Formato de archivo requerido por AutoDock Vina. Incluye cargas parciales y tipos de átomos. |
| **PDB** | Formato estándar de estructuras moleculares del Protein Data Bank. |
| **Grid Box** | Caja virtual 3D que define la región de búsqueda del docking. |
| **Sitio activo** | Cavidad de la proteína donde se une naturalmente el ligando/sustrato. |
| **Energía de afinidad** | Medida de qué tan favorable es la unión. En kcal/mol: más negativo = mejor. |
| **Pose** | Una posición/orientación particular del ligando dentro del sitio activo. |
| **RMSD** | Distancia media cuadrática — mide cuán diferente es una pose respecto a la de referencia. |
| **Exhaustiveness** | Parámetro de Vina: intensidad de búsqueda. Valores más altos = más lento pero más preciso. |
| **MGLTools** | Suite de herramientas del Scripps Research que incluye ADT, PMV, Vision y CADD. |
| **AutoDock Vina** | El motor de cálculo de docking. Se ejecuta en segundo plano, no tiene interfaz gráfica. |
| **Hidrógenos polares** | Hidrógenos unidos a N u O — críticos para las interacciones electrostáticas del docking. |
| **Cargas de Gasteiger** | Método para calcular cargas parciales de los átomos — requerido para el docking. |

---

## Contacto y soporte técnico

Para problemas con la instalación o errores del sistema, consulte el archivo `GUIA_DE_USO.md` (sección "Solución de problemas") o contacte al equipo de soporte técnico que configuró el sistema.

---

*Manual generado para uso interno del Policonsultorio — Sistema de Docking Molecular AutoDock Vina MVP*
