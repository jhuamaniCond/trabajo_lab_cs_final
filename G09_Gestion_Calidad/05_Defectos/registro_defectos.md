# Registro de defectos — G09

Continúa la numeración del proyecto: DEF-01 se halló en la revisión del SDD (G03) y DEF-02 es el defecto controlado de G07.

- **Severidad** (enunciado, sección 13): **crítico** impide un proceso esencial o expone información; **mayor** afecta una función importante; **menor** tiene impacto limitado.
- **Prioridad** (alta, media o baja): la urgencia de corregirlo para la entrega. Se registra aparte de la severidad.

## Resumen

| ID | Fecha | Versión | Requisito | Origen | Severidad | Prioridad | Estado | Corrección | Prueba de cierre |
|---|---|---|---|---|---|---|---|---|---|
| DEF-03 | 2026-11-04 | 1.2.0 (r30) | RF-12 | Revisión de las capturas de la ejecución `r30_primera`; confirmado por CP-13 | Menor | Media | **Cerrado** | r31 | CP-13 aprobado en r31 y en la regresión final r32 (Chrome ×2, Edge) |
| DEF-04 | 2026-11-04 | 1.2.0 (r30) | RF-08 | Revisión de las capturas de la ejecución `r30_primera`; confirmado por CP-10 | Menor | Baja | **Cerrado** | r31 | CP-10 aprobado en r31 y en la regresión final r32 (Chrome ×2, Edge) |
| DEF-06 | 2026-11-04 | Suite G09 (rama r31) | — (defecto de la prueba) | Ejecución `r31_correccion`: CP-10 en ERROR | Menor | Alta (impedía la regresión) | **Cerrado** | Suite: `ignored_exceptions` en las esperas | CP-10 aprobado en las 7 ejecuciones siguientes |
| DEF-07 | 2026-11-04 | Suite G09 (trunk r32) | RF-12 (dato de la prueba) | Revisión de las capturas de `r32_final-1`, `r32_final-2` y `r32_edge` | Menor | Alta (invalida la evidencia de CP-13) | **Cerrado** | Suite: espera a las opciones de la búsqueda actual + aserción de las líneas | CP-13 en `r32_final-3`, `r32_final-4`, `r32_edge-2` |

Hay 4 defectos en G09 (DEF-03, DEF-04, DEF-06, DEF-07), todos cerrados. Ninguno fue crítico ni mayor. DEF-06 y DEF-07 son defectos de la suite: una prueba que falla sin motivo (DEF-06) o que pasa con datos equivocados (DEF-07) invalida la evidencia igual que un defecto del producto.

---

## DEF-03 · La lista de Compras muestra 0 líneas en compras con productos

| Campo | Valor |
|---|---|
| Fecha | 2026-11-04 |
| Versión | 1.2.0, rama `CC-03-portal-web` r30 |
| Requisito | RF-12 Registrar compra a proveedor (consulta de compras del período) |
| Pasos de reproducción | 1. Ingresar como `encargado`. 2. Compras (F4) → Nueva compra. 3. RUC de un proveedor registrado, factura `F###`, número nuevo, fecha de ayer. 4. Agregar 10 × «cemento» a S/ 15.50 y 2 × «clavo» a S/ 25.00. 5. Registrar compra. 6. Mirar la fila de la compra en la lista |
| Datos | Proveedor y serie de la ejecución (`Distribuidora G09 1104185134 S.A.C.`, `Factura F134-15326665`) |
| Resultado esperado | La fila muestra datos correctos de la compra: total S/ 205.00 y op. gravada S/ 173.73 |
| Resultado obtenido | La columna «Líneas» muestra **0** en una compra de 2 productos: `Factura F134-15326665 03/11/2026 20855294339 Distribuidora G09 … 0 S/ 205.00` |
| Causa | `GET /api/compras` usa `ICompraRepositorio.BuscarAsync`, que trae solo las cabeceras. `CompraDto.De` contaba `Detalle.Count` de una lista vacía |
| Severidad / prioridad | Menor (dato informativo incorrecto; el total y el registro están bien) / Media |
| Responsable | Detecta: Payehuanca R., J. J. · Corrige: Condo Z., R. A. · Verifica: Chaisa F., A. L. |
| Corrección | r31: la lista muestra **Op. gravada, IGV y Total**, que sí vienen en la cabecera, y `CompraDto.lineas` es `null` cuando el detalle no se cargó (`Modelos.cs`, `index.html`, `portal.js`) |
| Prueba de cierre | CP-13 con la aserción nueva `S/ 173.73 en la fila`. Falla en r30 (`04_Reportes/20261104_1851_1.2.0-r30_defectos`, captura `evidencias/DEF-03_antes_CP-13_FALLO.png`) y pasa en r31 y en la regresión final r32 (`evidencias/DEF-03_despues_CP-13.png`) |
| Estado | Cerrado |

## DEF-04 · Al convertir una proforma queda a la vista el aviso de la emisión anterior

| Campo | Valor |
|---|---|
| Fecha | 2026-11-04 |
| Versión | 1.2.0, rama r30 |
| Requisito | RF-08 Emitir proforma y convertirla en venta |
| Pasos de reproducción | 1. Ingresar como `vendedor1`. 2. Emitir una proforma, que muestra «Proforma PR01-… emitida». 3. Proformas (F7) → elegir esa proforma → Convertir en venta |
| Datos | Proforma PR01-00000029 de 5 bolsas para un cliente nuevo |
| Resultado esperado | Nueva venta muestra el detalle, el cliente y el aviso «Venta desde la proforma …», sin mensajes de otra operación |
| Resultado obtenido | Sigue visible, en verde, «Proforma PR01-00000029 emitida · Total S/ 154.00» encima de Emitir. El vendedor puede creer que la venta ya se emitió |
| Causa | `convertirProforma()` llama a `cancelarVenta()`, que no oculta el aviso de resultado (`ResultadoEmision`) |
| Severidad / prioridad | Menor (confunde, pero no altera datos) / Baja |
| Responsable | Detecta: Payehuanca R., J. J. · Corrige: Condo Z., R. A. · Verifica: Chaisa F., A. L. |
| Corrección | r31: `convertirProforma()` llama a `ocultarResultado()` después de `cancelarVenta()` (`portal.js`) |
| Prueba de cierre | CP-10 con la aserción nueva `ResultadoEmision no visible`. Falla en r30 (`evidencias/DEF-04_antes_CP-10_FALLO.png`) y pasa en r31 y r32 (`evidencias/DEF-04_despues_CP-10.png`) |
| Estado | Cerrado |

## DEF-06 · Falla intermitente de la suite en CP-10 (`StaleElementReferenceException`)

| Campo | Valor |
|---|---|
| Fecha | 2026-11-04 |
| Versión | Suite G09 sobre el producto r31 |
| Requisito | — (defecto de la prueba, no del producto) |
| Pasos de reproducción | Ejecutar CP-10. Al abrir Proformas, el portal pinta la tabla; la búsqueda por DNI la vuelve a pintar mientras la espera lee la celda «Estado» de la fila vieja |
| Resultado esperado | La espera reintenta hasta encontrar la fila nueva |
| Resultado obtenido | ERROR `StaleElementReferenceException: stale element not found` (`04_Reportes/20261104_1855_1.2.0-r31_correccion`, `evidencias/DEF-06_CP-10_stale.png`) |
| Causa | `WebDriverWait` por defecto solo ignora `NoSuchElementException`. Un elemento reemplazado en el DOM interrumpía la espera |
| Severidad / prioridad | Menor / Alta: un caso inestable invalida la regresión |
| Responsable | Payehuanca R., J. J. |
| Corrección | `WebDriverWait(..., ignored_exceptions=(StaleElementReferenceException,))` en `comun.py` y `paginas.py`. No se agregaron `sleep` |
| Prueba de cierre | CP-10 aprobado en las 7 ejecuciones siguientes, de `r31_regresion` a `r32_edge-2` |
| Estado | Cerrado |

## DEF-07 · CP-13 registraba dos veces cemento en lugar de cemento y clavo

| Campo | Valor |
|---|---|
| Fecha | 2026-11-04 |
| Versión | Suite G09 sobre el producto 1.2.0 (trunk r32) |
| Requisito | RF-12 (los datos del caso no eran los del plan) |
| Pasos de reproducción | CP-13 escribe «clavo» en Producto de Nueva compra y espera a que el `datalist` tenga opciones. Las opciones de «cemento» de la línea anterior siguen ahí mientras llega la nueva búsqueda (220 ms de espera más la API), y la prueba elige la primera |
| Resultado esperado | Líneas «Cemento Portland … × 10 a 15.50» y «Clavo … × 2 a 25.00» |
| Resultado obtenido | Dos líneas «Cemento Portland tipo IP x 42.5 kg» (`evidencias/DEF-07_antes_dos_lineas_cemento.png`). El caso pasó porque el total (S/ 205.00) solo depende de los costos y las cantidades |
| Causa | Espera por «hay opciones» en lugar de «hay opciones de esta búsqueda», y ninguna aserción sobre las líneas |
| Severidad / prioridad | Menor / Alta: la evidencia de CP-13 en `r32_final-1`, `r32_final-2` y `r32_edge` no prueba lo que dice el plan |
| Responsable | Detecta: Huamani C., J. S. (revisión de capturas para el dictamen) · Corrige: Payehuanca R., J. J. |
| Corrección | `opciones_de(texto)`: se espera a que haya opciones que contengan el texto buscado, y se comprueba que la línea 1 sea cemento y la 2 clavo (`test_05_abastecimiento.py`) |
| Prueba de cierre | CP-13 en `r32_final-3`, `r32_final-4` y `r32_edge-2` (`evidencias/DEF-07_despues_cemento_y_clavo.png`). Las tres ejecuciones anteriores quedan anuladas para el dictamen |
| Estado | Cerrado |

## Defectos de otras guías (referencia)

| ID | Guía | Resumen | Estado |
|---|---|---|---|
| DEF-01 | G03 | `POST /api/escritorio/comprobantes` aceptaba el precio enviado por la PC (CRQ-07) | Cerrado en 1.1.1 (r11) |
| DEF-02 | G07 | Defecto controlado en `EmisionComprobante` para demostrar que PU-13 falla | Restaurado (controlado) |
