# Comparación de herramientas de gestión de riesgos — G06

El enunciado fija PILAR como ruta de referencia para MAGERIT y nombra RiskyProject y Pirani como alternativas de la guía. Solo se instaló PILAR; las demás se comparan con su documentación oficial, consultada el 2026-11-01.

| Criterio | **PILAR Basic 2026.1.1** (elegida) | RiskyProject | Pirani | Hoja de cálculo (plantilla docente) |
|---|---|---|---|---|
| Enfoque | Riesgos de **seguridad de la información** con MAGERIT | Riesgos de **proyecto**: cronograma y costo, con simulación Monte Carlo | Riesgo **operativo** y cumplimiento (ISO 31000, SARLAFT, seguridad de la información) en la nube | Matriz genérica P × I |
| Soporte de MAGERIT | Nativo: catálogo de activos, amenazas y salvaguardas del CCN, dimensiones D, I, C, A, T | No | Parcial: matriz propia, no aplica el catálogo de MAGERIT | No: solo un complemento |
| Activos y dependencias | Sí, con propagación del valor | No (trabaja con tareas del cronograma) | Procesos y activos, sin propagación de MAGERIT | Columna de texto «Depende de» |
| Cálculo de riesgo | Potencial, actual, objetivo y recomendado | Distribuciones de duración y costo del proyecto | Inherente y residual por matriz | R = P × I |
| Salvaguardas | Madurez L0–L5, normas 27002, 27701, GDPR | Respuestas de mitigación sobre tareas | Controles con evaluación de eficacia | Texto libre |
| Plataforma | Escritorio, Java, sin conexión | Escritorio Windows o integrado con MS Project | Web (SaaS), requiere cuenta | Excel o LibreOffice |
| Licencia | Gratuita con licencia de evaluación; completa para el sector público español o pagada | Comercial, con versión de prueba | Comercial, con plan de prueba | Sin costo adicional |
| Evidencia exportable | `.mgr`; informes bloqueados en evaluación | Informes y gráficos | Informes en la nube | El propio `.xlsx` |
| Encaje con G06 | **Alto**: es la herramienta que pide la guía y cubre todo MAGERIT | Bajo: resuelve otro problema (plazo y costo del proyecto, más cercano a G04) | Medio: sirve para el riesgo operativo, pero no reproduce MAGERIT | Complemento pedido por la plantilla |

## Decisión

Se usa **PILAR Basic** porque es la ruta de referencia del enunciado y la única opción que implementa MAGERIT completo: inventario con dependencias, valoración por dimensiones, catálogo de amenazas y salvaguardas, y riesgo por fases. La restricción de la licencia de evaluación (no exporta informes) se cubre con:

- el archivo del proyecto `CONDOR.mgr`;
- capturas de cada fase;
- la matriz MAGERIT en Excel, que da el detalle por escenario y las fórmulas recalculables.

No se requiere validar una sustitución con el docente: la herramienta de la guía se pudo usar.

Fuentes: https://pilar.ccn-cert.cni.es/ · https://www.intaver.com/riskyproject/ · https://www.piranirisk.com/ · `Plan_Riesgo_Guia_6_Alumnos.xlsx` (docente).
