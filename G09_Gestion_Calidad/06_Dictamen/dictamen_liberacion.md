# Dictamen de liberación — Sistema de Ventas y Facturación Cóndor 1.2.0

| Campo | Valor |
|---|---|
| Producto y versión evaluada | Sistema Cóndor **1.2.0**, SVN **trunk r32** (`CondorApi.exe` 1.2.0 + `CondorVentas.exe` 1.2.0) |
| Fecha | 2026-11-04 |
| Emite | Integrante 1 — Huamani Condori, Jeanpiero Sixto (evaluador de calidad, líder del dictamen) |
| Consultados | Integrante 2 (suite G09, configuración), Integrante 3 (diseño, G08), Integrante 4 (G04, G06); gerente general (aceptación) |
| Línea base de requisitos | ERS **1.2** (16 RF, 8 RNF) — `G01_Requerimientos/01_ERS/ERS_Condor_v1.2.md` |

## Decisión

> ## **APTO CON OBSERVACIONES**
>
> Los 16 requisitos funcionales y los 8 no funcionales de la línea base tienen al menos una prueba ejecutada y aprobada en la versión evaluada. Todas las suites están en verde en trunk r32: xUnit 944/0/5, Selenium 14/14 en Chrome dos veces y 14/14 en Edge, con la suite ya corregida (DEF-07). El umbral de rendimiento (RNF-02) se cumple con datos de G08 y no queda abierto ningún defecto crítico ni mayor.
>
> La liberación queda condicionada a las observaciones de la sección 6. Ninguna impide los tres procesos de negocio, pero O-2 (HTTPS) debe resolverse antes de instalar en el local. O-5 (etiqueta de la entrega) quedó cerrada el 2026-11-04 con `tags/v0.2.0` y `tags/v1.0.1`.

## 1. Criterios de liberación y resultado

| # | Criterio (plan de G09, sección 7) | Resultado | ¿Cumple? |
|---|---|---|---|
| C1 | Todos los RF y RNF de la línea base con una prueba aprobada | 24/24 (matriz de la sección 3) | Sí |
| C2 | Suite xUnit del producto sin fallos en la versión evaluada | 944 aprobadas, 0 fallidas, 5 omitidas (`04_Reportes/xunit_1.2.0-r32`) | Sí |
| C3 | Suite Selenium 14/14 en la versión final, repetible | 14/14 en `r32_final-3`, `r32_final-4` (Chrome) y `r32_edge-2` (Edge). Las tres ejecuciones r32 anteriores se anularon por DEF-07 | Sí |
| C4 | Los tres procesos de negocio demostrados de punta a punta | PN-01 en CP-07 y CP-08, PN-02 en CP-10, PN-03 en CP-13 | Sí |
| C5 | Ningún defecto crítico o mayor abierto | Ninguno crítico ni mayor | Sí |
| C6 | Umbral de rendimiento contrastado con datos (RNF-02) | p95 de 11–12 ms (consulta) y 21–22 ms (emisión), 0 % de error (G08) | Sí |
| C7 | Riesgos priorizados con respuesta; controles implantados con prueba | 12 escenarios con responsable; S1–S3 implantados y verificados (18/18, G06) y además ejercidos por G09 | Sí, con salvaguardas propuestas pendientes (O-3) |
| C8 | La versión entregada coincide con una etiqueta | `tags/v0.2.0` (r41) y `tags/v1.0.1` (r44, = `trunk@43`); el código de `v1.0.1` es idéntico al de `v1.0.0` (r35) | Sí (O-5 cerrada) |

## 2. Resultados consolidados por guía

| Guía | Evidencia | Resultado relevante para la liberación |
|---|---|---|
| G01 Requerimientos | ERS 1.2, revisión, indicadores | 16 RF y 8 RNF con criterio observable; CC-03 agrega INT-07 sin cambiar requisitos |
| G02 Proceso de requerimientos | Redmine, CC-01 (aprobada), CC-02 (rechazada) | Recorrido de cinco requisitos. CC-03 se registra con el mismo flujo (`08_Redmine`) |
| G03 Análisis | SDD 1.1, UML, mockups | DEF-01 hallado en la revisión y cerrado en 1.1.1. DD-09 y diagramas actualizados por CC-03 |
| G04 Dimensionamiento | NESMA, COSMIC, COCOMO | CC-03 costó 17,5 h reales frente a 17 h estimadas (S/ 440) |
| G05 Configuración | SVN, ramas DEF-01, MEJ-01 y CC-03 | CC-03 en `branches/CC-03-portal-web` r28–r31, integrada en trunk r32 sin conflictos. Etiquetas `v0.2.0` (r41), `v1.0.0` (r35) y `v1.0.1` (r44) creadas (O-5 cerrada) |
| G06 Riesgos | PILAR, matriz de 12 escenarios, S1–S11 | S1 (roles), S2 (validación de entradas) y S3 (respaldo) implantados y verificados. S4–S11 propuestos (O-3). R12 sube con el portal (O-2) |
| G07 Pruebas unitarias | 27 casos PU sobre 5 componentes, DEF-02 controlado | 43/43 en la suite de G07; **95,6 %** de líneas en `Condor.Dominio` (RNF-08 ≥ 80 %). Regresión antes y después de CC-01 |
| G08 Rendimiento | JMeter: carga, estrés, pico, estabilidad y capacidad | RNF-02 cumplido. MEJ-01 mejora parcial. El límite (unas 200 boletas/s) supera de lejos la necesidad de 3 PC |
| G09 Gestión de calidad | Suite Selenium, 10 ejecuciones, 4 defectos | Defectos del portal: DEF-03 y DEF-04 cerrados. Defectos de la suite: DEF-06 y DEF-07 cerrados. Regresión final 14/14 en dos navegadores |

## 3. Matriz de trazabilidad: requisito → prueba → resultado en la versión 1.2.0

Pruebas automatizadas del producto (xUnit) según la ERS 1.2, sección 6. Todas aprobadas en `xunit_1.2.0-r32`.

| Requisito | Pruebas unitarias / integración (xUnit) | G08 / G06 / G07 | G09 Selenium (trunk r32) | Estado |
|---|---|---|---|---|
| RF-01 Iniciar sesión | `ServicioAutenticacionTests`, `LoginViewModelTests`, `UsuarioRepositorioTests`, `ApiTests` | G06 S1 | CP-01, CP-02 ✔ | Verificado |
| RF-02 Cerrar sesión | `CC01_IngresoConRolesTests` | — | CP-14 ✔ | Verificado |
| RF-03 Restringir módulos según el rol | `CC01_IngresoConRolesTests`, `ApiTests`, `PortalWebTests` (403) | G06 S1 | CP-03, CP-12, CP-13 ✔ | Verificado |
| RF-04 Registrar producto | `HU01_RegistrarProductoTests`, `HU13_LectorCodigoBarrasTests`, `ValidadorProducto` | G07 | CP-05, CP-06 ✔ | Verificado |
| RF-05 Buscar producto | `HU02_BuscarProductoTests`, `HU13_*`, `BuscadorProductoViewModel` | G08 T1 | CP-05, CP-06, CP-07 ✔ | Verificado |
| RF-06 Registrar y buscar cliente | `HU03_ClienteTests`, `ValidadorDocumento` | G07 | CP-04, CP-05, CP-08 ✔ | Verificado |
| RF-07 Emitir comprobante | `HU05_*`, `HU06_*`, `HU08_*`, `EmisionComprobante`, `CalculadoraVenta`, `ClienteApiTests` | G08 T2; G07 DEF-02; G06 S2 | CP-07, CP-08, CP-09, CP-10 ✔ | Verificado |
| RF-08 Proforma y conversión | `HU09_ProformasTests`, `EmisionComprobante`, `PortalWebTests` | — | CP-10 ✔ (cambio de estado) | Verificado |
| RF-09 Imprimir y reimprimir ticket | `HU12_ImprimirTicketTests`, `HU18_HistorialTests`, `Impresion/*`, `MontoEnLetras` | G07 | — (solo app de escritorio) | Verificado (xUnit) |
| RF-10 Enviar a la SUNAT y reenviar | `HU07_EnviarSunatTests`, `HU17_ReenvioAutomaticoTests`, `Sunat/*` | — | — (SUNAT simulada; O-7) | Verificado (xUnit) |
| RF-11 Registrar proveedor | `HU04_ProveedoresTests`, `ValidadorProveedor` | — | CP-13 ✔ | Verificado |
| RF-12 Registrar compra | `HU11_ComprasTests`, `ValidadorCompra`, `PortalWebTests` | — | CP-13 ✔ (DEF-03 cerrado) | Verificado |
| RF-13 Guía de remisión | `HU10_GuiasRemisionTests`, `ValidadorGuia` | — | — (solo app de escritorio) | Verificado (xUnit) |
| RF-14 Consultar historial | `HU18_HistorialTests` | — | CP-07, CP-11 ✔ | Verificado |
| RF-15 Reporte consolidado | `ReporteVentasTests`, `ApiTests` | — | CP-12 ✔ | Verificado |
| RF-16 Respaldo de la base | `HU15_RespaldoTests` | G06 S3 (respaldo y restauración, conteos idénticos) | — (consulta de respaldos en el portal) | Verificado |
| RNF-01 Sugerencias < 1 s | `HU02_BuscarProductoTests` | — | CP-07: **570–585 ms** en 10 ejecuciones (incluye 220 ms de espera intencional del buscador) ✔ | Cumple |
| RNF-02 p95 ≤ 2 s, error ≤ 1 % | — | G08: p95 de 11–12 ms y 21–22 ms, 0 % | — | Cumple |
| RNF-03 Seguridad de credenciales | `HashClaveTests`, `ServicioAutenticacionTests`, `ApiTests` | G06 S1 | CP-02, CP-03 ✔ | Cumple |
| RNF-04 0 repetidos y 0 saltados | `HU16_ConcurrenciaTests`, `MEJ01_CorrelativoAlFinalTests` | G08 (capacidad) | — | Cumple |
| RNF-05 Venta sin internet | `HU07_*`, `HU17_*` | G06 (R07 aceptado) | — | Cumple |
| RNF-06 Venta ≤ 60 s, 0 clics | — | G01 OBS-01 (línea base manual) | CP-07: venta completa solo con teclado, **1,2–1,8 s** de sistema ✔ | Cumple con observación (O-4) |
| RNF-07 Persistencia y recuperación | `HU15_RespaldoTests`, `Datos/*` ([FactConBD]) | G06 S3 | CP-04, CP-06, CP-07: lo registrado se encuentra después en otra pantalla | Cumple |
| RNF-08 Cobertura ≥ 80 % | — | G07: **95,6 %** de `Condor.Dominio` | — | Cumple |

## 4. Defectos

| ID | Severidad | Estado | Efecto en la decisión |
|---|---|---|---|
| DEF-01 (G03) | Mayor | Cerrado en 1.1.1 | — |
| DEF-02 (G07) | — (controlado) | Restaurado | — |
| DEF-03 (G09) | Menor | Cerrado en r31, regresión en r32 | — |
| DEF-04 (G09) | Menor | Cerrado en r31, regresión en r32 | — |
| DEF-06 (suite G09) | Menor | Cerrado | — |
| DEF-07 (suite G09) | Menor | Cerrado | Se anularon y repitieron las tres ejecuciones finales |

En la primera versión del portal aparecieron 2 defectos de producto (DEF-03, DEF-04) y 2 de la suite (DEF-06, DEF-07). Tres se vieron **en las capturas** y no en las aserciones; luego se agregaron aserciones para los que se corrigieron (ver la limitación L-1).

## 5. Riesgos (G06) después de G09

| Riesgo | Antes | Efecto de CC-03 y G09 | Residual |
|---|---|---|---|
| R01 Acceso a costos, R02 Suplantación | M / A | CP-03, CP-12 y CP-13 ejercen S1 también en la interfaz web: el Vendedor no ve ni abre los módulos del Encargado, y la API responde 403 | Sin cambio (S1 verificado) |
| R03 Precio manipulado | M | El portal solo envía el Id del producto y la cantidad; la API toma el precio del catálogo (S2, `PortalWebTests`) | Sin cambio |
| R12 Interceptación en la LAN | M | **Sube la exposición**: cualquier navegador de la LAN abre el portal por HTTP y el JWT viaja sin cifrar | **Sigue en M hasta implantar S10 (HTTPS)**: observación O-2 |
| Nuevo: XSS en el portal | — | Todo texto de la API se escapa (`escapar()`); los datos de prueba con caracteres especiales no rompieron la página | B (control implantado, sin prueba dedicada; L-2) |

## 6. Observaciones (condiciones de la liberación)

| ID | Observación | Responsable | Plazo | Acción |
|---|---|---|---|---|
| O-2 | La API y el portal funcionan por HTTP en la LAN (R12, S10 propuesta) | Payehuanca R., J. J. | Antes de instalar en el local (2026-12-10, plan de G06) | Implantar S10: certificado de la LAN y redirección a HTTPS |
| O-3 | Las salvaguardas S4–S11 de G06 siguen propuestas (riesgo residual previsto) | Responsables del plan de G06 | Fechas del plan de tratamiento | Implantarlas o aceptar su riesgo de forma explícita con el gerente |
| O-4 | RNF-06: la automatización demuestra la venta **solo con teclado** (0 clics) y un tiempo de sistema de 1,2–1,8 s, pero no mide al cajero real | Huamani C., J. S. con el gerente | Sustentación | Repetir la observación OBS-01 cronometrando a un vendedor con la versión 1.2.0 |
| O-5 | No existe la etiqueta de la versión entregada: `tags/v0.2.0` para el avance 2 y `tags/v1.0.0` para la final (política de G05) | Payehuanca R., J. J. (único con permiso en `/tags`) | Antes del 25-11-2026 | **Cerrada 2026-11-04**: `tags/v0.2.0` (r41) y `tags/v1.0.1` (r44); ver `G05_Gestion_Configuracion/04_Evidencias/06_etiqueta_v1.0.1.txt` |
| O-6 | La capacidad está limitada por el COMMIT con la serie bloqueada (MEJ-01 parcial, G08) | Condo Z., R. A. | Sin plazo (supera la necesidad) | Las acciones pendientes de G08 si el local crece |
| O-7 | RF-09, RF-10, RF-13 y RF-16 no tienen prueba web de punta a punta: la ticketera, la SUNAT (ambiente beta sin configurar, con 5 pendientes en la base de demostración), las guías y la generación del respaldo están solo en la app | Huamani C., J. S. | Sustentación | Demostrarlos en la app de escritorio; la verificación automática es la de xUnit |
| O-8 | Los commits de CC-03 y G09 (r28–r33) se hicieron con la cuenta `rcondo` por falta de credenciales de los demás en el equipo de trabajo; el historial no refleja quién integró ni quién dictaminó | Payehuanca R., J. J. | — | Dejarlo anotado (hecho en CC-03 §5); en adelante, cada integrante usa su cuenta |

## 7. Limitaciones del dictamen

- **L-1.** Las aserciones solo verifican lo que se les pide: la primera ejecución pasó 14/14 con DEF-03 y DEF-04 a la vista, y la primera regresión final pasó 14/14 con DEF-07 a la vista. Las 26 capturas de `r32_final-3` se revisaron una por una antes de este dictamen, sin hallazgos nuevos.
- **L-2.** No se hizo una prueba de seguridad dedicada del portal (inyección, XSS o robo del token). Los controles se revisaron en el código y con las pruebas de autorización.
- **L-3.** Las pruebas web corren en una sola PC contra la base de demostración, que guarda los registros de prueba «G09». No se probaron tres navegadores a la vez; la concurrencia la cubren `HU16_ConcurrenciaTests` y G08.
- **L-4.** Los resultados valen para la versión 1.2.0 en trunk r32 y para Chrome 156 y Edge 156.

## 8. Firmas

| Rol | Integrante | Conformidad |
|---|---|---|
| Evaluador de calidad (dictamen) | Huamani Condori, Jeanpiero Sixto | Emite |
| Responsable de la suite y de configuración | Payehuanca Riquelme, Jhastyn Jefferson | Conforme |
| Diseño y rendimiento | Condo Zamata, Richard Alberto | Conforme |
| Estimación y riesgos | Chaisa Fernández, Anthony Leonel | Conforme |
| Cliente | Gerente general (usuario representado) | Pendiente de la sustentación |
