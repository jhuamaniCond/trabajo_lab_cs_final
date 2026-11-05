# Informe de seguimiento de requisitos y cambios

| Campo | Valor |
|---|---|
| Herramienta | Redmine 7.0.1 (contenedor `redmine-condor`, http://localhost:3010), proyecto «Sistema Cóndor» |
| Fecha del corte | 30/10/2026 19:51 (hora de Lima) |
| Línea base | ERS 1.1 · producto 1.1.0 |
| Peticiones | 24 requisitos y 2 solicitudes de cambio |
| Fuente de los datos | API REST de Redmine; generado con `generar_informe_seguimiento.py` |

## 1. Estado de los requisitos y cambios

| Tipo | Registrado | Analizado | Aprobado | Rechazado | Implementado | Verificado | Cerrado | Total |
|---|---|---|---|---|---|---|---|---|
| Requisito | · | · | · | · | 19 | · | 5 | 24 |
| Solicitud de cambio | · | · | · | 1 | · | · | 1 | 2 |

De los 24 requisitos (16 RF y 8 RNF), **5 están cerrados** (recorrieron el flujo completo con evidencia de pruebas) y **19 están implementados** en la versión 1.1.0 a la espera de la verificación que harán G06, G07, G08 y G09 (sección 4). Ningún requisito quedó sin implementar.

Por prioridad: Alta 13, Media 11. Reportes de la herramienta: `01_Redmine/capturas/19_informe_resumen.png` (por tipo, prioridad, asignado, autor y versión), `20_informe_estado_por_tipo.png`, `21_informe_por_asignado.png` y `22_hoja_de_ruta_1.1.0.png`.

## 2. Recorrido de los cinco requisitos gestionados en el flujo completo

Cada fila es una transición registrada en el historial de Redmine: fecha, usuario que la hizo (con su rol en el flujo) y la evidencia anotada. Capturas: `01_Redmine/capturas/12_historial_RF-01.png` a `16_historial_RF-15.png`; exportación PDF de cada petición en `01_Redmine/exportaciones/`.

### RF-01 Iniciar sesión (petición #1, prioridad Alta, estado Cerrado)

| Fecha | Transición | Responsable (rol) | Evidencia |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Jeanpiero Sixto Huamani Condori (Analista) | Registrado desde la ERS (`ID ERS` = RF-01, fuente: Gerente general, Encargado general de tienda (ENT-01)) |
| 30/10/2026 19:50 | Registrado → Analizado | Jeanpiero Sixto Huamani Condori (Analista) | Análisis: requisito claro, consistente con el glosario y verificable (2 criterio(s) de aceptación). Revisión con la lista de G01_Requerimientos/07_Revision/lista_revision.md. |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Aprobado por el CCB en la línea base ERS 1.0 (2026-10-29). |
| 30/10/2026 19:50 | (modificación) | Jeanpiero Sixto Huamani Condori (Analista) | Requisito reescrito por CC-01 (#20): de «Acceder con el perfil único MAESTRO» a «Iniciar sesión». Queda en la ERS 1.1 (apéndice B). |
| 30/10/2026 19:50 | Aprobado → Implementado | Jhastyn Jefferson Payehuanca Riquelme (Desarrollador) | Implementado en la versión 1.1.0 del producto (Sistema_Logistico_Condor_final, CHANGELOG). Código: Condor.Dominio/Seguridad/ServicioAutenticacion.cs, HashClave, Condor.Presentacion/ViewModels/LoginViewModel.cs,… |
| 30/10/2026 19:50 | Implementado → Verificado | Richard Alberto Condo Zamata (Evaluador de calidad) | Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 (04_Pruebas/suite_completa_v1.1.0.trx; suite completa: 923 aprobadas, 0 fallidas, 5 omitidas). Adjunto: `suite_completa_v1.1.0.html`. |
| 30/10/2026 19:50 | Verificado → Cerrado | Jeanpiero Sixto Huamani Condori (CCB) | Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas previstas en G08/G09 se agregarán a la matriz de trazabilidad final. |

### RF-03 Restringir módulos según el rol (petición #22, prioridad Alta, estado Cerrado)

| Fecha | Transición | Responsable (rol) | Evidencia |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Jhastyn Jefferson Payehuanca Riquelme (Analista) | Registrado desde la ERS (`ID ERS` = RF-03, fuente: Gerente general, Encargado general de tienda (ENT-01)) |
| 30/10/2026 19:50 | Registrado → Analizado | Jhastyn Jefferson Payehuanca Riquelme (Analista) | Análisis: requisito claro, consistente con el glosario y verificable (4 criterio(s) de aceptación). Revisión con la lista de G01_Requerimientos/07_Revision/lista_revision.md. |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Aprobado por el CCB como parte de CC-01 (#20); entra en la línea base ERS 1.1 (2026-10-30). |
| 30/10/2026 19:50 | Aprobado → Implementado | Anthony Leonel Chaisa Fernández (Desarrollador) | Implementado en la versión 1.1.0 del producto (Sistema_Logistico_Condor_final, CHANGELOG). Código: Condor.Dominio/Seguridad/Roles.cs, Condor.Presentacion/ViewModels/PermisosModulo.cs, política Encargado en Condor.Api/Endpoints.cs. |
| 30/10/2026 19:50 | Implementado → Verificado | Richard Alberto Condo Zamata (Evaluador de calidad) | Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 (04_Pruebas/suite_completa_v1.1.0.trx; suite completa: 923 aprobadas, 0 fallidas, 5 omitidas). |
| 30/10/2026 19:50 | Verificado → Cerrado | Jeanpiero Sixto Huamani Condori (CCB) | Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas previstas en G08/G09 se agregarán a la matriz de trazabilidad final. |

### RF-07 Emitir comprobante de venta (petición #5, prioridad Alta, estado Cerrado)

| Fecha | Transición | Responsable (rol) | Evidencia |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Jeanpiero Sixto Huamani Condori (Analista) | Registrado desde la ERS (`ID ERS` = RF-07, fuente: Gerente general, Vendedores de mostrador, Contador externo (ENT-01, CUE-01, OBS-01)) |
| 30/10/2026 19:50 | Registrado → Analizado | Jeanpiero Sixto Huamani Condori (Analista) | Análisis: requisito claro, consistente con el glosario y verificable (5 criterio(s) de aceptación). Revisión con la lista de G01_Requerimientos/07_Revision/lista_revision.md. |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Aprobado por el CCB en la línea base ERS 1.0 (2026-10-29). |
| 30/10/2026 19:50 | Aprobado → Implementado | Anthony Leonel Chaisa Fernández (Desarrollador) | Implementado en la versión 1.1.0 del producto (Sistema_Logistico_Condor_final, CHANGELOG). Código: Condor.Dominio/Ventas/EmisionComprobante.cs, CalculadoraVenta.cs, POST /api/escritorio/comprobantes (usuario tomado del token). |
| 30/10/2026 19:50 | Implementado → Verificado | Richard Alberto Condo Zamata (Evaluador de calidad) | Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 (04_Pruebas/suite_completa_v1.1.0.trx; suite completa: 923 aprobadas, 0 fallidas, 5 omitidas). |
| 30/10/2026 19:50 | Verificado → Cerrado | Jeanpiero Sixto Huamani Condori (CCB) | Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas previstas en G08/G09 se agregarán a la matriz de trazabilidad final. |

### RF-08 Emitir proforma y convertirla en venta (petición #6, prioridad Media, estado Cerrado)

| Fecha | Transición | Responsable (rol) | Evidencia |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Jhastyn Jefferson Payehuanca Riquelme (Analista) | Registrado desde la ERS (`ID ERS` = RF-08, fuente: Gerente general, Vendedores de mostrador (ENT-01, CUE-01)) |
| 30/10/2026 19:50 | Registrado → Analizado | Jhastyn Jefferson Payehuanca Riquelme (Analista) | Análisis: requisito claro, consistente con el glosario y verificable (3 criterio(s) de aceptación). Revisión con la lista de G01_Requerimientos/07_Revision/lista_revision.md. |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Aprobado por el CCB en la línea base ERS 1.0 (2026-10-29). |
| 30/10/2026 19:50 | Aprobado → Implementado | Jeanpiero Sixto Huamani Condori (Desarrollador) | Implementado en la versión 1.1.0 del producto (Sistema_Logistico_Condor_final, CHANGELOG). Código: EmisionComprobante (conversión), Condor.Presentacion/ViewModels/ProformasViewModel.cs, migración V011 (proforma_id, trigger… |
| 30/10/2026 19:50 | Implementado → Verificado | Anthony Leonel Chaisa Fernández (Evaluador de calidad) | Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 (04_Pruebas/suite_completa_v1.1.0.trx; suite completa: 923 aprobadas, 0 fallidas, 5 omitidas). |
| 30/10/2026 19:50 | Verificado → Cerrado | Jhastyn Jefferson Payehuanca Riquelme (CCB) | Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas previstas en G08/G09 se agregarán a la matriz de trazabilidad final. |

### RF-15 Generar reporte consolidado de ventas (petición #23, prioridad Media, estado Cerrado)

| Fecha | Transición | Responsable (rol) | Evidencia |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Richard Alberto Condo Zamata (Analista) | Registrado desde la ERS (`ID ERS` = RF-15, fuente: Gerente general (ENT-01)) |
| 30/10/2026 19:50 | Registrado → Analizado | Richard Alberto Condo Zamata (Analista) | Análisis: requisito claro, consistente con el glosario y verificable (2 criterio(s) de aceptación). Revisión con la lista de G01_Requerimientos/07_Revision/lista_revision.md. |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Aprobado por el CCB como parte de CC-01 (#20); entra en la línea base ERS 1.1 (2026-10-30). |
| 30/10/2026 19:50 | Aprobado → Implementado | Anthony Leonel Chaisa Fernández (Desarrollador) | Implementado en la versión 1.1.0 del producto (Sistema_Logistico_Condor_final, CHANGELOG). Código: Condor.Dominio/Reportes/ReporteVentas.cs, Condor.Datos/ReporteVentasRepositorio.cs, ruta GET /api/reportes/ventas (solo Encargado). |
| 30/10/2026 19:50 | Implementado → Verificado | Jhastyn Jefferson Payehuanca Riquelme (Evaluador de calidad) | Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 (04_Pruebas/suite_completa_v1.1.0.trx; suite completa: 923 aprobadas, 0 fallidas, 5 omitidas). |
| 30/10/2026 19:50 | Verificado → Cerrado | Jhastyn Jefferson Payehuanca Riquelme (CCB) | Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas previstas en G08/G09 se agregarán a la matriz de trazabilidad final. |

## 3. Solicitudes de cambio

| ID | Petición | Solicitante | Estado | Decisión | Versión | Impacto en costo | Impacto en plazo | Requisitos relacionados |
|---|---|---|---|---|---|---|---|---|
| CC-01 | #20 | Gerente general (representado) | Cerrado | Aprobada | 1.1.0 | 56 h × S/ 25.00 = S/ 1 400.00 | ≈ 4 días hábiles con 4 integrantes; se absorbe en el incremento 1, no mueve el hito del 11-11-2026 | RF-01, RF-02, RF-03, RF-07, RF-15, RNF-02, RNF-03 |
| CC-02 | #26 | Anthony Leonel Chaisa Fernández | Rechazado | Rechazada | — (sigue la 1.1.0) | 38 h × S/ 25.00 = S/ 950.00 | ≈ 3 días hábiles; cae en el incremento 2 y obliga a repetir las líneas base de G07 y G08; riesgo para el hito del 25-11-2026 | RF-07 |

**CC-01** — historial:

| Fecha | Transición | Responsable | Nota |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Gerente general (representado) | El gerente necesita saber quién emitió cada comprobante y que los vendedores no vean costos ni respaldos (ENT-01 A5, CFL-06). El curso exige autenticación, roles, reporte consolidado y rutas HTTP para JMeter. |
| 30/10/2026 19:50 | Registrado → Analizado | Jhastyn Jefferson Payehuanca Riquelme (Analista) | Análisis de impacto completo en los campos de la solicitud y en G02_Proceso_Requerimientos/03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md (requisitos, diseño, costo, plazo, riesgos y pruebas). |
| 30/10/2026 19:50 | Analizado → Aprobado | Gerente general (representado) (CCB) | Decisión del CCB: aprobada. Necesidad del cliente y exigencia del curso; costo moderado (56 h) y sin mover el hito. Versión objetivo: 1.1.0; línea base resultante: ERS 1.1. |
| 30/10/2026 19:50 | Aprobado → Implementado | Jeanpiero Sixto Huamani Condori (Desarrollador) | Implementado en la versión 1.1.0: ERS 1.1 y REMUS regenerado; diseño en docs/seguridad.md, docs/api.md y docs/modelo_datos.md (este último corregido al cerrar el cambio: seguía diciendo «usuario siempre MAESTRO»); código V014,… |
| 30/10/2026 19:50 | Implementado → Verificado | Richard Alberto Condo Zamata (Evaluador de calidad) | Regresión de las pruebas afectadas por CC-01 sobre la versión 1.1.0, con PostgreSQL: 130 aprobadas, 0 fallidas. Se adjunta el reporte. Comando en G02_Proceso_Requerimientos/03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md. |
| 30/10/2026 19:50 | Verificado → Cerrado | Gerente general (representado) (CCB) | Cierre: ERS 1.1, diseño, código y pruebas actualizados y la regresión en verde. Pendiente para G05: registrar la versión 1.1.0 en SVN y etiquetarla. |

**CC-02** — historial:

| Fecha | Transición | Responsable | Nota |
|---|---|---|---|
| 30/10/2026 19:50 | Alta → Registrado | Anthony Leonel Chaisa Fernández | El 75 % de los vendedores pide poder cambiar el precio para hacer descuentos (CUE-01, P12); hoy rebajan «a ojo» (ENT-01 B9). CFL-03 lo dejó como posible cambio futuro. |
| 30/10/2026 19:50 | Registrado → Analizado | Richard Alberto Condo Zamata (Analista) | Análisis de impacto completo en los campos y en G02_Proceso_Requerimientos/03_Solicitudes_Cambio/CC-02_descuento_en_venta.md. |
| 30/10/2026 19:50 | Analizado → Rechazado | Gerente general (representado) (CCB) | Decisión del CCB: rechazada. 1) Contradice CRQ-07 y la resolución de CFL-03: los precios los fija solo el catálogo. 2) Dos riesgos altos sin mitigación en esta versión. 3) Costo y plazo comprometen el hito del 25-11-2026.… |

El análisis de impacto completo (requisitos, diseño, costo, plazo, riesgos y pruebas) está en `03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md` y `03_Solicitudes_Cambio/CC-02_descuento_en_venta.md`.

## 4. Requisitos pendientes de verificación

| Requisito | Petición | Estado | Asignado a (evaluador) | Se verificará en |
|---|---|---|---|---|
| RF-02 Cerrar sesión | #21 | Implementado | Anthony Leonel Chaisa Fernández | G09 (cierre de sesión) |
| RF-04 Registrar producto en el catálogo | #2 | Implementado | Jhastyn Jefferson Payehuanca Riquelme | G07, G09 |
| RF-05 Buscar producto para la venta | #3 | Implementado | Richard Alberto Condo Zamata | G07, G08, G09 |
| RF-06 Registrar y buscar cliente por DNI o RUC | #4 | Implementado | Anthony Leonel Chaisa Fernández | G07, G09 |
| RF-09 Imprimir y reimprimir el ticket | #7 | Implementado | Richard Alberto Condo Zamata | G07 |
| RF-10 Enviar comprobantes a la SUNAT y reenviar pendientes | #8 | Implementado | Anthony Leonel Chaisa Fernández | G07 |
| RF-11 Registrar proveedor | #9 | Implementado | Jeanpiero Sixto Huamani Condori | G07 |
| RF-12 Registrar compra a proveedor | #10 | Implementado | Jhastyn Jefferson Payehuanca Riquelme | G07 |
| RF-13 Emitir guía de remisión electrónica | #11 | Implementado | Richard Alberto Condo Zamata | G07 |
| RF-14 Consultar historial de ventas | #12 | Implementado | Anthony Leonel Chaisa Fernández | G07, G09 |
| RF-16 Generar respaldo de la base de datos | #13 | Implementado | Jhastyn Jefferson Payehuanca Riquelme | G06, G07 |
| RNF-01 Tiempo de respuesta de la búsqueda de productos | #14 | Implementado | Richard Alberto Condo Zamata | G07 |
| RNF-02 Capacidad de la API bajo carga esperada | #24 | Implementado | Anthony Leonel Chaisa Fernández | G08 |
| RNF-03 Protección de credenciales y del acceso | #25 | Implementado | Jeanpiero Sixto Huamani Condori | G06, G07 |
| RNF-04 Integridad con trabajo simultáneo | #15 | Implementado | Jhastyn Jefferson Payehuanca Riquelme | G07 |
| RNF-05 Tolerancia a la caída de internet | #16 | Implementado | Richard Alberto Condo Zamata | G07 |
| RNF-06 Venta operable solo con teclado | #17 | Implementado | Anthony Leonel Chaisa Fernández | G09 (cronometrado) |
| RNF-07 Persistencia y recuperación de los datos | #18 | Implementado | Jeanpiero Sixto Huamani Condori | G06, G07 |
| RNF-08 Cobertura de la lógica de negocio | #19 | Implementado | Jhastyn Jefferson Payehuanca Riquelme | G07 (cobertura) |

Estos requisitos ya tienen pruebas automatizadas en el producto (ERS 1.1, sección 6.2) y la suite 1.1.0 pasa completa, pero se cerrarán en Redmine cuando cada guía aporte su evidencia propia (catálogo de casos de G07, resultados JMeter de G08, suite Selenium de G09 y controles de G06). El flujo los mueve a Verificado y Cerrado en ese momento.

## 5. Indicadores de seguimiento

| Indicador | Valor |
|---|---|
| Requisitos cerrados / total | 5 / 24 (21 %) |
| Requisitos implementados o más avanzados | 24 / 24 |
| Solicitudes de cambio | 2: 1 aprobada(s) e implementada(s), 1 rechazada(s) |
| Requisitos afectados por CC-01 | 7 de 24 (29 % de la línea base) |
| Pruebas de la versión 1.1.0 | 923 aprobadas, 0 fallidas, 5 omitidas (`04_Pruebas/suite_completa_v1.1.0.trx`) |
| Regresión de CC-01 | 130 aprobadas, 0 fallidas (`04_Pruebas/regresion_CC-01.trx`) |
| Esfuerzo estimado de los cambios analizados | CC-01: 56 h (S/ 1 400.00); CC-02: 38 h (S/ 950.00, no ejecutado) |

**Limitación:** todas las transiciones se registraron en Redmine el 30/10/2026, cuando se configuró la herramienta, a partir de la línea base 1.0 (29/10/2026) y de la versión 1.1.0 ya construida. Las fechas del historial son las reales del registro, no se ajustaron hacia atrás. Las transiciones que hagan G06 a G09 quedarán con su propia fecha.
