# Lista de revisión de la ERS

| Campo | Valor |
|---|---|
| Documento revisado | ERS del Sistema Cóndor: versión 0.9 (revisión 1) y versión 1.1 (revisión 2) |
| Técnica | Revisión por lista de comprobación (*checklist*), con los atributos de calidad de una ERS de IEEE 830 |
| Revisión 1 | 2026-10-29 · ERS 0.9 · Revisores: Integrante 3 e Integrante 4 (no participaron en la redacción) · Validación: gerente representado (Integrante 2) |
| Revisión 2 | 2026-10-30 · ERS 1.1 (tras CC-01) · Revisores: Integrante 1 e Integrante 3 |
| Resultado | Revisión 1: **14 observaciones**, todas corregidas en la 1.0. Revisión 2: **0 observaciones abiertas**. |

## 1. Criterios de la lista

| Código | Criterio (IEEE 830) | Pregunta de comprobación |
|---|---|---|
| CL | Claridad (no ambiguo) | ¿El requisito admite una sola interpretación? ¿Evita palabras vagas («rápido», «fácil», «varios», «una semana»)? |
| CO | Consistencia | ¿No contradice a otro requisito? ¿Usa los mismos términos del glosario en todo el documento? |
| CM | Completitud | ¿Define las entradas, el comportamiento ante errores y los casos límite? ¿Tiene fuente, prioridad y criterio de aceptación? |
| VE | Verificabilidad | ¿Existe un procedimiento finito y de costo razonable para comprobar que se cumple? ¿El criterio es observable y está vinculado a una prueba? |
| TR | Trazabilidad | ¿Tiene ID único, fuente y objetivo, y puede vincularse con el diseño y las pruebas? |
| PR | Priorización | ¿Tiene importancia, urgencia y estabilidad? |

## 2. Observaciones de la revisión 1 (ERS 0.9) y su corrección

| ID | Requisito (ID vigente) | Criterio | Observación en la versión 0.9 | Corrección aplicada en la 1.0 | Estado |
|---|---|---|---|---|---|
| OR-01 | RF-05 / RNF-01 | VE | «La búsqueda de productos debe ser rápida.» | Se separó un RNF medible: sugerencias en menos de 1 s desde la tercera letra con 3 000 productos. | Cerrada |
| OR-02 | RF-07 | CM | No indicaba cuándo la boleta exige el DNI del cliente. | Se agregó CRQ-02 (más de S/ 700.00) y la excepción del paso 2 con su CA-07.2 (valor límite S/ 700.00 y S/ 700.01). | Cerrada |
| OR-03 | RF-08 | CL | «La proforma vale una semana.» | «7 días contando el de su emisión» (CRQ-06), con un ejemplo de fecha en CA-08.1. | Cerrada |
| OR-04 | RNF-06 | VE | «El sistema debe ser fácil de usar.» | Venta de 3 productos solo con teclado en 60 s o menos, medida con la ficha OBS-01. | Cerrada |
| OR-05 | RNF-04 | VE | «Debe soportar varias PC.» | 3 terminales emitiendo a la vez, 0 números repetidos y 0 saltados. | Cerrada |
| OR-06 | RF-10 | CM | No definía qué pasa si no hay internet al emitir. | Excepción del paso 2: el comprobante queda PENDIENTE y se reintenta; conflicto CFL-02 y RNF-05. | Cerrada |
| OR-07 | RF-04, RF-05, IRQ-01 | CO | Se usaban «artículo», «ítem» y «producto» como sinónimos. | Se unificó en «producto»; «ítem» queda solo para la línea del comprobante (glosario). | Cerrada |
| OR-08 | RF-12 | CM | No decía qué hacer si se registra dos veces la misma factura del proveedor. | Nueva regla CRQ-09 y excepción del paso 3. | Cerrada |
| OR-09 | RF-13 | CM | No listaba los datos obligatorios de la guía de remisión. | Nueva regla CRQ-13 con los datos por modalidad de transporte. | Cerrada |
| OR-10 | RF-14 | CO | El total del historial sumaba las proformas, a diferencia del reporte. | El total excluye proformas y rechazados en RF-14 y en CRQ-15. | Cerrada |
| OR-11 | RNF-07 | VE | «No se deben perder datos.» | 0 registros perdidos tras reiniciar y restauración exitosa de un respaldo; aviso a las 24 h. | Cerrada |
| OR-12 | RF-09 | CM | No contemplaba las PC sin ticketera ni la ticketera sin papel. | Excepciones: vista previa en pantalla y aviso con reimpresión F11. | Cerrada |
| OR-13 | CRQ-01 | CL | No definía el redondeo del IGV. | Dos decimales; operación gravada + IGV = total. | Cerrada |
| OR-14 | RF-11, RF-12, RF-13, RF-14, RF-16 | PR | Sin prioridad ni urgencia asignadas. | Se asignaron importancia, urgencia y estabilidad (prioridad Media). | Cerrada |

**Resumen por criterio (revisión 1):** CL 2 · CO 2 · CM 5 · VE 4 · TR 0 · PR 1 → 14 observaciones (OR-14 afecta a 5 requisitos y se cuenta una vez). Las observaciones de verificabilidad se concentraron en los RNF, que en la 0.9 estaban redactados sin unidades.

## 3. Resultado de la revisión 2 (ERS 1.1, línea base vigente)

✔ = cumple. Las columnas de la derecha indican cómo se verificará cada requisito.

| Requisito | CL | CO | CM | VE | TR | PR | Criterios | Observaciones previas | Verificación prevista |
|---|---|---|---|---|---|---|---|---|---|
| RF-01 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 4 | Nuevo en 1.1 (CC-01) | G07, G09 |
| RF-02 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 2 | Nuevo en 1.1 (CC-01) | G09 |
| RF-03 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 4 | Nuevo en 1.1 (CC-01) | G07, G09 |
| RF-04 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-07 | G07, G09 |
| RF-05 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-01, OR-07 | G07, G08, G09 |
| RF-06 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | — | G07, G09 |
| RF-07 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 5 | OR-02 | G07, G08, G09 |
| RF-08 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-03 | G07, G09 |
| RF-09 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-12 | G07 |
| RF-10 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-06 | G07 |
| RF-11 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-14 | G07 |
| RF-12 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-08, OR-14 | G07 |
| RF-13 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-09, OR-14 | G07 |
| RF-14 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 2 | OR-10, OR-14 | G07, G09 |
| RF-15 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 2 | Nuevo en 1.1 (CC-01) | G07 |
| RF-16 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 3 | OR-14 | G06, G07 |
| RNF-01 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | OR-01 | G07 |
| RNF-02 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | Nuevo en 1.1 (CC-01) | G08 |
| RNF-03 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | Nuevo en 1.1 (CC-01) | G06, G07 |
| RNF-04 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | OR-05 | G07 |
| RNF-05 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | OR-06 | G07 |
| RNF-06 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | OR-04 | G09 (cronometrado) |
| RNF-07 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 2 | OR-11 | G06, G07 |
| RNF-08 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 | — | G07 |

## 4. Comprobaciones globales

| Comprobación | Resultado |
|---|---|
| Al menos 10 RF y 5 RNF | ✔ 16 RF y 8 RNF |
| Cada requisito tiene ID, descripción, fuente, prioridad y criterio de aceptación | ✔ 24 de 24 |
| Cada requisito puede vincularse con una prueba | ✔ 24 de 24 (sección 6.2 de la ERS) |
| Dos roles de usuario y tres procesos de negocio completos | ✔ Vendedor y Encargado general; PN-01, PN-02, PN-03 |
| Autenticación, autorización, validaciones, registro, consulta y reporte consolidado | ✔ RF-01, RF-03, CRQ-02 a CRQ-04, RF-04/06/07/11/12, RF-14, RF-15 |
| Persistencia tras reiniciar | ✔ RNF-07 |
| Conflictos identificados y resueltos | ✔ 6 de 6 resueltos |
| Servicios externos simulados documentados | ✔ SUP-03 (SUNAT y API de guías simuladas) |
| REMUS no informa errores al abrir el documento | ✔ `condor.log.xml` vacío |
| Términos del glosario usados de forma uniforme | ✔ tras OR-07 |
