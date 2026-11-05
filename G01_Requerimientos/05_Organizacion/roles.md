# Organización y roles del equipo

El enunciado pide que **cada alumno asuma y documente los cuatro roles**: analista, desarrollador, responsable de configuración y evaluador de calidad. Por eso los cuatro integrantes ejercen los cuatro roles. Además, cada uno **lidera** las guías que se le asignan; el líder responde por la evidencia de esa guía, pero no la hace solo.

Organigrama: `organigrama.png` (fuente editable: `generar_organigrama.py`).

## Integrantes

| N.º | Integrante | Guías que lidera | Responsabilidad de coordinación |
|---|---|---|---|
| 1 | Huamani Condori, Jeanpiero Sixto | G01, G07, dictamen de G09 | Coordinación del proyecto, cronograma, entregas |
| 2 | Payehuanca Riquelme, Jhastyn Jefferson | G02, G05, suite de G09 | Comité de cambios, repositorio SVN |
| 3 | Condo Zamata, Richard Alberto | G03, G08 | Diseño (SDD, UML) y rendimiento |
| 4 | Chaisa Fernández, Anthony Leonel | G04, G06 | Estimación y riesgos |

## Qué hace cada rol

| Rol | Responsabilidades | Evidencia en la que deja su firma |
|---|---|---|
| Analista | Elicita, especifica y revisa requisitos; analiza el impacto de los cambios; mantiene la trazabilidad. | ERS, actas, solicitudes de cambio, matriz de trazabilidad |
| Desarrollador | Implementa los cambios aprobados, sus pruebas unitarias y las correcciones de defectos. | Revisiones SVN, código, pruebas unitarias |
| Responsable de configuración | Identifica los elementos de configuración, hace los commits y las ramas, integra y etiqueta versiones. | Historial SVN, política de configuración, etiquetas |
| Evaluador de calidad | Diseña y ejecuta las pruebas de rendimiento y de aceptación, registra los defectos y emite el dictamen. | Reportes de pruebas, registro de defectos, dictamen |

## Matriz RACI por guía

R = realiza · A = aprueba y responde por la evidencia · C = es consultado · I = es informado

| Guía | Integrante 1 | Integrante 2 | Integrante 3 | Integrante 4 | Gerente (cliente) | Docente |
|---|---|---|---|---|---|---|
| G01 Requerimientos | **A**, R | R | R | C | C (valida la ERS) | I (valida el alcance) |
| G02 Proceso de requerimientos | C | **A**, R | R | C | A (decide los cambios) | I |
| G03 Análisis de sistemas | C | C | **A**, R | R | I | I |
| G04 Dimensionamiento | C | R | C | **A**, R | I | I |
| G05 Gestión de configuración | R | **A**, R | R | R | — | I |
| G06 Gestión de riesgos | C | R | C | **A**, R | C (valora los activos) | I |
| G07 Pruebas unitarias | **A**, R | R | C | R | — | I |
| G08 Pruebas de rendimiento | C | C | **A**, R | R | — | C (acuerda el perfil) |
| G09 Gestión de calidad | **A** (dictamen) | R (suite) | R | R | C (aceptación) | I |

> Todos los integrantes hacen commits en SVN con su propio usuario, de modo que el historial de G05 muestra el trabajo de cada uno.
