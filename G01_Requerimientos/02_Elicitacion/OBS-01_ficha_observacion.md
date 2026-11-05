# OBS-01 · Ficha de observación directa del proceso de venta actual

| Campo | Valor |
|---|---|
| Técnica | Observación directa no participante, con toma de tiempos (cronómetro) |
| Proceso observado | Venta en mostrador con boleta manual (situación actual, sin sistema) |
| Fecha y horario | 2026-10-28, de 7:30 a 9:00 (hora punta) |
| Observadores | Integrante 1 (cronometra) · Integrante 3 (anota pasos y errores) |
| Muestra | 12 ventas de **3 productos** con boleta; se descartaron las ventas de otro tamaño para comparar en igualdad de condiciones |
| Usuario representado | **Sí.** Se simuló el mostrador con el Integrante 2 como vendedor y el Integrante 4 como cliente, usando la lista de precios `db/datos/lista_precios.csv` y un talonario de boletas impreso. |

## Pasos observados (proceso actual)

| Paso | Actividad | Problema observado | Requisito |
|---|---|---|---|
| 1 | El cliente pide los productos de palabra. | — | — |
| 2 | El vendedor busca cada precio en la lista impresa. | Lista desordenada; en 4 ventas tuvo que preguntar el precio. | RF-05, RNF-01 |
| 3 | Anota los productos en el cuaderno de ventas. | Doble registro: cuaderno y boleta. | RF-07 |
| 4 | Suma el total y calcula el IGV con calculadora. | 2 errores de IGV en 12 ventas. | CRQ-01 |
| 5 | Pide el DNI si el cliente quiere boleta con nombre. | — | RF-06, CRQ-02 |
| 6 | Llena la boleta del talonario a mano. | 1 boleta anulada y rehecha por un error de escritura. | RF-07, RF-09 |
| 7 | Cobra y entrega la boleta. | — | — |
| 8 | Al final del día, registra las boletas en el portal de la SUNAT. | Fuera del horario de atención; riesgo de vencer el plazo. | RF-10 |

## Tiempos registrados

| Venta | Tiempo (s) | Consultó el precio a otra persona | Error de IGV | Boleta rehecha |
|---|---|---|---|---|
| 1 | 155 | No | No | No |
| 2 | 190 | Sí | No | No |
| 3 | 170 | No | No | No |
| 4 | 140 | No | No | No |
| 5 | 210 | Sí | **Sí** | No |
| 6 | 165 | No | No | No |
| 7 | 180 | Sí | No | No |
| 8 | 150 | No | No | No |
| 9 | 230 | No | **Sí** | **Sí** |
| 10 | 170 | No | No | No |
| 11 | 160 | No | No | No |
| 12 | 185 | Sí | No | No |

## Resultados

| Indicador | Valor |
|---|---|
| Mediana del tiempo por venta | **170 s (2 min 50 s)** |
| Mínimo / máximo | 140 s / 230 s |
| Media | 175.4 s |
| Ventas con error de IGV | **2 de 12 (16.7 %)** |
| Ventas en que se consultó el precio | 4 de 12 (33.3 %) |
| Boletas rehechas | 1 de 12 |

## Conclusiones para la ERS

1. La **línea base** de una venta de 3 productos es 170 s. La meta de **RNF-06** (60 s o menos) supone reducir el tiempo en un 65 %; la búsqueda con sugerencias (**RF-05**, **RNF-01**) y el cálculo automático (**CRQ-01**) atacan los pasos 2 y 4, que concentran las demoras.
2. Los errores de IGV (16.7 %) justifican que el IGV se calcule siempre a partir del precio del catálogo (**CRQ-01**, **CRQ-07**).
3. El registro duplicado (cuaderno y boleta) y la facturación nocturna en el portal desaparecen con la emisión electrónica y el envío automático (**RF-07**, **RF-10**).
4. La misma ficha se usará en G09 para medir el tiempo con el sistema (criterio CA-RNF-06.1).
