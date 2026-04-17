# Muestras Para Pruebas de Docking

Esta carpeta contiene un catalogo de 100 muestras sugeridas para que el doctor pueda probar el sistema con distintos tipos de estudios de docking.

Importante:
- Estas muestras son propuestas de estudio, no estructuras moleculares ya descargadas.
- Para ejecutar un docking real, debes conseguir la estructura del receptor y del ligando en formato compatible y luego convertirla a PDBQT si hace falta.
- Puedes buscar receptores en Protein Data Bank y ligandos en PubChem, DrugBank, ChEBI o Zinc.
- Despues coloca el receptor en la carpeta `receptors/` y el ligando en `ligands/`.

## Archivos incluidos

- `catalogo_100_muestras.csv`: listado principal con 100 ideas de docking.
- `catalogo_100_muestras.json`: el mismo contenido en formato JSON para integracion o revision automatica.

## Como usar estas muestras

1. Elegir una fila del catalogo.
2. Descargar una estructura del receptor adecuada para ese objetivo.
3. Descargar o dibujar la estructura del ligando.
4. Preparar ambos archivos en PDBQT si no vienen listos.
5. Ejecutar el docking desde la web o por linea de comandos.

## Tipos de estudios incluidos

- Vitaminas y cofactores
- Productos naturales
- Antiinflamatorios y analgesicos
- Antivirales
- Antibacterianos
- Oncologia
- Neurologia
- Endocrinologia
- Cardiologia y metabolismo
- Receptores y enzimas de uso comun en docking

## Recomendacion practica

Para empezar rapido, puedes probar primero con estas muestras faciles de interpretar:

- `M001` VDR + calcitriol
- `M008` DHFR + acido folico
- `M022` COX-2 + ibuprofeno
- `M029` EGFR + erlotinib
- `M031` neuraminidasa + oseltamivir
- `M091` AT1 + losartan
