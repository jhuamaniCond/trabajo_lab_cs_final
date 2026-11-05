# ENT-01 · Acta de entrevista

| Campo | Valor |
|---|---|
| Fecha | 2026-10-28 |
| Sesión 1 | Gerente general (PAR-01) — 45 min |
| Sesión 2 | Encargado general de tienda (PAR-02) — 40 min |
| Usuario representado | **Sí.** Integrante 2 (gerente) e Integrante 4 (encargado), con base en el Product Backlog del proyecto Cóndor. |
| Registró | Integrante 3 |
| Instrumento | `ENT-01_guion_entrevista.md` |

## Sesión 1 · Gerente general (resumen de respuestas)

| Preg. | Respuesta resumida |
|---|---|
| A1 | Ferretería en Majes que vende al público y a obras de construcción; las obras compran con factura y piden traslado de material. |
| A2 | Unas 150 ventas en un día normal y hasta 250 en campaña (marzo y agosto). En hora punta (7:00 a 9:00) hay colas de 5 o 6 personas. |
| A3 | «Que el cliente no espere»: armar la venta rápido y sin errores de precio. En segundo lugar, cumplir con la SUNAT sin hacerlo a mano al final del día. |
| A4 | Suma el cuaderno a fin de mes; no sabe cuánto vende cada vendedor ni cada PC. Quiere un reporte por día, por tipo de comprobante y por vendedor. |
| A5 | No lo controla: todos usan la misma clave del portal. Quiere que cada comprobante diga quién lo emitió. |
| A6 | Los vendedores no deben ver costos de compra, egresos ni hacer respaldos. |
| A7 | «Sería grave»: tuvo un corte de luz que borró el archivo de Excel de una semana. Pide respaldo, de preferencia automático en la nube. |
| A8 | Tres PC con Windows en red local, una ticketera térmica en caja y un disco externo; no quiere pagar servidor ni servicio en la nube. |

## Sesión 2 · Encargado general (resumen de respuestas)

| Preg. | Respuesta resumida |
|---|---|
| B1 | Busca el precio en la lista impresa, anota en el cuaderno, calcula a mano el IGV y llena la boleta del talonario. Una venta de 3 productos toma «casi 3 minutos». |
| B2 | Factura para obras y empresas: se pide el RUC, la razón social y la dirección. A veces el RUC está mal escrito y la SUNAT lo rechaza. |
| B3 | La cotización se escribe en una hoja y se respeta «una semana». A veces un cliente vuelve con la misma cotización dos veces. |
| B4 | Al final del día se registra todo en el portal de la SUNAT. Si se cae el internet, se acumula y a veces se pasa del plazo de 3 días. |
| B5 | Las facturas de proveedores se guardan en un archivador; una vez se pagó dos veces la misma factura. |
| B6 | Guía de remisión cuando se lleva material a una obra con la camioneta propia o con una empresa de transporte. |
| B7 | Tres PC; en hora punta venden dos o tres personas al mismo tiempo. |
| B8 | Tienen lector de código de barras sin usar y una ticketera térmica de 80 mm en caja. |
| B9 | Los precios los fija el gerente; algunos vendedores rebajan «a ojo» y eso descuadra la caja. |

## Hallazgos y requisitos derivados

| Hallazgo | Requisito / regla / conflicto |
|---|---|
| Colas y venta lenta (≈ 3 min) | OBJ-01, RF-05, RF-07, RNF-01, RNF-06 |
| Errores de precio y de IGV | CRQ-01, CRQ-07 |
| Facturas con RUC mal escrito | RF-06, CRQ-04 |
| Facturación manual al final del día, plazos vencidos | RF-10, CRQ-10, RNF-05 |
| Cotización respetada una semana; reutilizada dos veces | RF-08, CRQ-06 |
| Factura de proveedor pagada dos veces | RF-12, CRQ-09 |
| No se sabe quién emitió cada comprobante | RF-01, CRQ-11, CFL-01 |
| Vendedores no deben ver costos ni respaldos | RF-03, CRQ-12, CFL-06 |
| Pérdida de datos por corte de luz | RF-16, RNF-07, CFL-05 |
| Reporte por día, tipo y vendedor | RF-15 |
| Tres PC venden a la vez | RNF-04, CRQ-05 |
| Rebajas de precio «a ojo» | CFL-03 |
| Traslado de material a obras | RF-13, CRQ-13 |

## Acuerdos

1. El equipo entrega la ERS 0.9 para revisión el 2026-10-29.
2. La resolución de los conflictos CFL-01 a CFL-06 se valida con el gerente en la revisión.
3. Las metas de tiempo se contrastan con la observación OBS-01.
