# MANUAL DEL ASISTENTE PARA EL DOCTOR

Este manual sirve para consultar rapidamente como usar los 5 programas del paquete y el sistema web.

## 1. Que programa usar segun objetivo

- Docking rapido con interfaz simple: INICIAR_WEB.bat
- Docking rapido por doble clic: DOCK.bat
- Preparar archivos PDB a PDBQT: AutoDockTools 1.5.6
- Ver resultados 3D y medir distancias: PMV 1.5.6
- Automatizar flujos con nodos: Vision 1.5.6
- Usar entorno avanzado integral: CADD 1.5.6

## 2. Flujo recomendado para trabajo real

1. Preparar receptor y ligando en AutoDockTools.
2. Guardar receptor en receptors y ligando en ligands.
3. Ajustar center_x, center_y, center_z, size_x, size_y, size_z en config.yaml.
4. Ejecutar docking con INICIAR_WEB.bat o DOCK.bat.
5. Revisar resultados en outputs.
6. Visualizar pose en PMV.

## 3. Uso del sistema web

1. Doble clic en INICIAR_WEB.bat.
2. Esperar mensaje de servidor en http://127.0.0.1:5000.
3. Subir receptor y ligando.
4. Activar "Saltar preparacion" si ambos son .pdbqt.
5. Ejecutar docking.
6. Revisar energias y descargar salida.

Validacion:
- Si aparece "Running on http://127.0.0.1:5000", el servidor esta correcto.
- Si genera archivo en outputs, el docking termino bien.

### Funcionalidades nuevas en web (modo completo)

1. Modo de trabajo:
	- Docking completo: preparar + correr + analizar.
	- Solo preparar archivos PDBQT.
2. Resumen clinico-tecnico:
	- Mejor modo.
	- Mejor afinidad (kcal/mol).
	- Numero de poses evaluadas.
3. Tabla de resultados en pantalla:
	- Mode, Affinity, RMSD l.b., RMSD u.b.
4. Historial de corridas:
	- Fecha, operacion, receptor, ligando, mejor afinidad, salida.
5. Vista 3D integrada:
	- Visualiza receptor y mejor pose (MODE 1) directamente en navegador.

### Funcionalidades profesionales (doctor)

1. Identificador de caso clinico:
	- Campo para registrar y rastrear cada corrida por caso.
2. Objetivo clinico-tecnico:
	- Campo de contexto para documentar la finalidad del docking.
3. Evaluacion clinica automatica:
	- Clasificacion de senal (alta, media, baja) basada en afinidad.
	- Consistencia entre MODE 1 y MODE 2 para apoyo de interpretacion.
	- Recomendacion tecnica orientativa para siguientes pasos.
4. Historial trazable y limpio:
	- Columna de caso en historial.
	- Boton para limpiar historial cuando se inicia una nueva serie.

## 4. AutoDockTools 1.5.6 (preparacion)

### Receptor
1. File -> Read Molecule (cargar .pdb).
2. Edit -> Hydrogens -> Add -> Polar only.
3. Edit -> Charges -> Compute Gasteiger.
4. Grid -> Macromolecule -> Choose.
5. Guardar como .pdbqt en receptors.

### Ligando
1. Ligand -> Input -> Open.
2. Revisar torsiones.
3. Ligand -> Output -> Save as PDBQT en ligands.

## 5. PMV 1.5.6 (visualizacion)

1. File -> Read Molecule (receptor y resultado docked_*.pdbqt).
2. Display -> Ribbon o Sticks para vista clara.
3. Tools -> Measurements -> Add Distance para medir interacciones.

Validacion:
- El ligando debe verse dentro de la cavidad objetivo.

## 6. Vision 1.5.6 (automatizacion)

Uso recomendado:
- Para usuarios avanzados que quieren repetir pipelines con menos pasos manuales.

Flujo:
1. Abrir Vision.
2. Crear flujo por nodos (entrada, preparacion, docking, salida).
3. Ejecutar y validar archivos de salida.

## 7. CADD 1.5.6

Uso recomendado:
- Cuando se quiere integrar herramientas avanzadas en una sola sesion.

Flujo:
1. Abrir CADD.
2. Cargar flujo o iniciar entorno interactivo.
3. Ejecutar tareas y validar resultados con PMV.

## 8. Interpretacion de resultados de docking

- Affinity (kcal/mol): mas negativa suele ser mejor.
- mode 1: mejor pose segun scoring de Vina.
- RMSD: diferencia entre poses.

Ejemplo:
- -8.5 kcal/mol suele indicar mejor afinidad que -6.0 kcal/mol.

## 9. Errores frecuentes y solucion rapida

### Error: no abre AutoDockTools, PMV, Vision o CADD
- Causa: lanzadores .bat de MGLTools con ruta fija vieja.
- Solucion: ejecutar CREAR_ACCESO_DIRECTO.bat para reparar accesos.

### Error: Entorno virtual no encontrado
- Causa: falta instalacion inicial.
- Solucion: ejecutar SETUP.bat o INSTALAR_TODO.bat.

### Error: No existe config.yaml
- Causa: ejecucion desde carpeta incorrecta con scripts antiguos.
- Solucion: usar los scripts actualizados del repositorio.

## 10. Como preguntarle al asistente

Plantilla recomendada:
1. Programa que estas usando.
2. Objetivo que quieres lograr.
3. Mensaje de error exacto (si existe).
4. En que paso fallaste.

Ejemplo:
"Estoy en PMV, quiero ver la mejor pose del docking y medir distancia de un H-bond. Que pasos hago?"

## 11. Limites del asistente

- El asistente orienta en uso de software, no da diagnostico medico de pacientes.
- Para resultados cientificos, siempre validar con controles experimentales y criterio profesional.
