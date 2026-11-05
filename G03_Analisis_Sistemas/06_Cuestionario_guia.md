# Cuestionario de la guía PRAC03, aplicado al producto

**Nota:** las tres preguntas del cuestionario de PRAC03 son las mismas de PRAC02 (gestión de requerimientos). Ya se respondieron en `G02_Proceso_Requerimientos/07_Cuestionario_guia.md` desde el control de requisitos y cambios. Aquí se responden desde el **análisis y diseño del sistema**, que es el tema de esta guía, para no repetir la misma respuesta.

## ¿Qué actividades se usan con frecuencia en la gestión de requerimientos y cuáles son esenciales?

En el análisis de sistemas la gestión de requerimientos continúa en el diseño. En G03 se hicieron cuatro actividades:

| Actividad | Cómo se hizo en Cóndor |
|---|---|
| **Convertir requisitos en casos de uso** | CU-01 (RF-07), CU-02 (RF-08) y CU-03 (RF-12), con precondiciones, flujo principal, alternativas, excepciones y poscondiciones: uno por cada proceso de negocio (PN-01 a PN-03) |
| **Justificar cada decisión de diseño con el requisito que la origina** | DD-01 a DD-09 en la sección 6 del SDD. Por ejemplo, DD-03 (correlativo con bloqueo de fila) responde a CRQ-05 y RNF-04, y DD-09 (portal web) responde a INT-07 y G09 |
| **Mantener la trazabilidad** requisito → diseño → código → prueba | Sección 7 del SDD |
| **Revisar el diseño contra los requisitos y el código** | `04_Revision/revision_SDD.md`: 7 observaciones (OS-01 a OS-07) |

La **esencial** es la última, la revisión contra los requisitos **y** contra el código. OS-07 descubrió que la ruta `POST /api/escritorio/comprobantes` aceptaba el precio enviado por la PC, lo que contradice CRQ-07. Así se registró el defecto real **DEF-01**, que se corrigió con trazabilidad en la rama `DEF-01-precio-catalogo` (producto 1.1.1). Sin esa revisión el defecto habría llegado a la entrega.

La segunda es la trazabilidad de las decisiones de diseño. Cuando llegaron CC-01 y CC-03, la sección 9 del SDD permitió saber exactamente qué vistas, componentes y tablas cambiar.

## ¿Qué herramienta es de mejor utilidad para la gestión de requerimientos?

En el análisis, la herramienta útil es la que mantiene el diseño **versionado y coherente** con los requisitos (comparación en `05_Herramientas/comparacion_herramientas.md`):

- **PlantUML** para los 9 diagramas y los 5 mockups. Al ser texto, cada diagrama se versiona en SVN como el código, el `diff` muestra qué cambió (por ejemplo, el componente «Portal web» de CC-03) y se regenera con un comando. diagrams.net es más cómodo para dibujar, pero su XML se compara mal entre versiones.
- **Redmine**, el mismo de G02, para registrar que un requisito ya tiene diseño, y el campo `ID ERS` para enlazarlo.

Ninguna herramienta reemplaza la revisión manual: la coherencia entre nombres, clases, tablas y pantallas se comprobó leyendo el código (OS-02, OS-03).

## ¿Qué porcentaje de los recursos del proyecto es aceptable para la gestión de cambios?

Desde el diseño, el costo de un cambio depende de **cuánto del diseño toca**:

| Cambio | Impacto en el diseño (SDD, sección 9) | Esfuerzo de diseño |
|---|---|---|
| CC-01 | Arquitectura nueva (DD-02, DD-07), 2 componentes, 2 tablas y 2 mockups | Parte de las 56 h del cambio |
| CC-02 | Ninguno (rechazado) | — |
| CC-03 | 1 decisión (DD-09), 1 componente y 1 nodo de despliegue | 1 h de 17,5 h |

Para el diseño, el equipo considera aceptable entre el **10 % y el 15 % del esfuerzo**, la misma cifra de G02. Lo que mantiene ese porcentaje bajo es la propia arquitectura: con las reglas en `Condor.Dominio` (DD-01) y los contratos intercambiables (DD-04), CC-03 agregó una interfaz web sin duplicar ninguna regla y costó 1 h de diseño. Un diseño acoplado haría que cada cambio cueste más que ese rango.
