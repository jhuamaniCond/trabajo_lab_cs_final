# Comparación de herramientas — G01 Requerimientos

El enunciado pide comparar al menos dos opciones por área. Para G01 se comparan las herramientas de **gestión de requisitos** propuestas por la guía (REM, OSRMT y Gatherspace) más la elegida (REMUS), y las de **cronograma**. No fue necesario instalar todas las alternativas: las que no se instalaron se evaluaron con su documentación oficial.

## 1. Gestión de requisitos

| Criterio | REM 1.2.2 | **REMUS 1.3** (elegida) | OSRMT 1.5 | Gatherspace |
|---|---|---|---|---|
| Autor / procedencia | A. Durán, Universidad de Sevilla | A. Durán, Universidad de Sevilla (sucesor de REM) | Proyecto de código abierto (SourceForge) | Gatherspace.com (comercial) |
| Disponibilidad | **Descontinuado:** el enlace oficial devuelve 404 | Binario en GitHub (`amador-duran-toro/remus`), actualizado en 2022 | Descarga en SourceForge; sin mantenimiento desde 2008 | Servicio web con suscripción y periodo de prueba |
| Licencia / costo | Gratuita | Gratuita (uso académico) | GPL | De pago |
| Plataforma | Windows | Windows (Linux con Wine) | Java (multiplataforma) | Navegador |
| Plantillas IEEE / ERS | Plantillas de Durán y Bernárdez (objetivos, IRQ, CRQ, UC, NFR) | Las mismas plantillas, con patrones lingüísticos que completan la frase | Requisitos, diseño, pruebas y artefactos genéricos | Historias de usuario y casos de uso |
| Matrices de trazabilidad | Sí | **Sí, automáticas** (requisito ↔ objetivo) | Sí | Limitadas |
| Conflictos | Sí | **Sí, con estado y solución** | No | No |
| Exportación | HTML por XSLT | **HTML y XML por XSLT** (`condor__CRS.html`, `condor.xml`) | Informes HTML | PDF, Word |
| Carga por script | No documentada | **Sí:** el `.rem` es una base Access (Jet 4.0) y se escribe por OLEDB (`generar_rem.ps1`) | API Java, compleja | API REST de pago |
| Trabajo colaborativo | Archivo único | Archivo único (se versiona en SVN) | Base de datos multiusuario | Multiusuario en la nube |
| Curva de aprendizaje | Baja | Baja | Media | Baja |

### Ventajas y desventajas

| Herramienta | Ventajas | Desventajas |
|---|---|---|
| REMUS | Plantillas académicas alineadas con IEEE 830; conflictos y matrices automáticas; gratuita; documento HTML legible; se puede generar por script desde una fuente versionable. | Solo Windows; archivo monousuario; interfaz antigua; no tiene un flujo de estados configurable, que se cubre en G02 con otra herramienta. |
| REM | Es la herramienta nombrada en la guía. | Ya no se puede descargar (404); REMUS la reemplaza con el mismo modelo. |
| OSRMT | Multiusuario, multiplataforma y con trazabilidad hacia diseño y pruebas. | Abandonado desde 2008; requiere un Java antiguo; no gestiona conflictos. |
| Gatherspace | Web, colaborativo y sin instalación. | De pago; orientado a historias de usuario; exporta poco para una ERS IEEE. |

### Conclusión

Se eligió **REMUS 1.3**: conserva el modelo de REM, que pide la guía, está disponible y es gratuito, gestiona conflictos y matrices de trazabilidad y genera un documento HTML verificable. Su principal limitación, el archivo monousuario, se compensa generando el `.rem` desde `condor_datos.json`, que se versiona en SVN (G05) y permite que cualquier integrante regenere el documento. El seguimiento de estados de los requisitos se hace en G02 con un gestor de incidencias.

## 2. Cronograma

| Criterio | **Excel + script Python** (elegido) | GanttProject 3.3 | Microsoft Project |
|---|---|---|---|
| Costo | Incluido en Office / gratuito | Gratuito (GPL) | De pago |
| Editable por el docente | **Sí, con fórmulas visibles** (duración, totales, Gantt por formato condicional) | Sí, con GanttProject instalado | Requiere una licencia |
| Horas planificadas frente a reales | Columnas propias, que reutiliza G04 | Sí | Sí |
| Dependencias entre tareas | No (se indican por las fechas) | Sí | Sí |

**Conclusión:** se usa **Excel** porque el enunciado pide entregables editables con fórmulas y porque G04 necesita confrontar las horas planificadas con las reales en la misma hoja.
