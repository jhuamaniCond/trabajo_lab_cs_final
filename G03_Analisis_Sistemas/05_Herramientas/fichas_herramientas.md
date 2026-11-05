# Fichas de herramientas — G03

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## PlantUML — diagramas UML

| Campo | Contenido |
|---|---|
| Versión exacta | PlantUML **1.2024.7** (07-09-2024), `plantuml-1.2024.7.jar`; motor de diseño **Smetana** (incluido, no requiere Graphviz) |
| Finalidad | Diagramas UML como texto: casos de uso, clases, secuencia, estados, actividad, componentes y despliegue, y el diagrama entidad–relación |
| Requisitos de instalación | Java 8 o superior (se usó el JRE de Oracle del equipo) |
| Procedencia | https://github.com/plantuml/plantuml/releases/tag/v1.2024.7, guardado en `C:\tools\plantuml\plantuml.jar` |
| Licencia | GPL (distribución de código abierto) |
| Configuración | En cada `.puml`: `!pragma layout smetana` (sin Graphviz), `skinparam monochrome true`, fuente Arial. El diagrama de clases de entidades se exporta con `-DPLANTUML_LIMIT_SIZE=8192` |
| Ejecución | Desde `02_UML`: `java -jar C:\tools\plantuml\plantuml.jar -charset UTF-8 -tpng *.puml` y, para vectores, `-tsvg *.puml` |
| Archivos generados | `02_UML/*.png` y `*.svg` (9 diagramas: 01 a 09, con el de clases dividido en 02a y 02b) |

## PlantUML Salt — mockups

| Campo | Contenido |
|---|---|
| Versión exacta | La misma de PlantUML (1.2024.7), módulo Salt |
| Finalidad | Wireframes de las pantallas de los casos de uso (M01 a M05), con los textos, atajos y columnas de la aplicación WPF |
| Requisitos de instalación | Los de PlantUML |
| Procedencia / licencia | Las de PlantUML |
| Configuración | Bloque `salt` dentro de `@startuml` con `skinparam dpi 170` |
| Ejecución | Desde `03_Mockups`: `java -jar C:\tools\plantuml\plantuml.jar -charset UTF-8 -tpng *.puml` (y `-tsvg`) |
| Archivos generados | `03_Mockups/M01_ingresar` a `M05_acceso_denegado` (`.puml`, `.png` y `.svg`) |
| Sustitución | El enunciado propone Moqups. Se usó Salt porque la fuente es texto versionable en SVN (G05), con historial de cambios línea por línea, y no requiere cuenta en línea. Moqups se comparó con su documentación (ver `comparacion_herramientas.md`). **Sustitución por validar con el docente.** |
