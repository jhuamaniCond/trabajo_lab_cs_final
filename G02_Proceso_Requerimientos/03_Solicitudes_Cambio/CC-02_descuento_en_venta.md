# CC-02 · Descuento manual del vendedor en la línea de venta

| Campo | Valor |
|---|---|
| ID | CC-02 (Redmine: petición «CC-02», tipo *Solicitud de cambio*) |
| Fecha de registro | 2026-10-30 |
| Solicitante | Vendedores de mostrador (representados), pregunta P12 del cuestionario CUE-01 |
| Registró | Integrante 4 — Chaisa Fernández, Anthony Leonel |
| Analizó | Integrante 3 — Condo Zamata, Richard Alberto |
| Decidió | Comité de cambios (CCB): gerente general, Integrante 1 e Integrante 2 |
| Prioridad | Media |
| Línea base afectada | ERS 1.1. No cambia, porque el cambio se rechazó. |
| Versión del producto afectada | Ninguna. Si se hubiera aprobado, habría sido la 1.2.0. |
| Decisión | **Rechazada** |
| Estado final | **Rechazado** |

## 1. Descripción del cambio

Permitir que el vendedor aplique un descuento de hasta el 10 % a cada línea de la venta (boleta, factura, nota de venta o proforma), con el motivo del descuento. El sistema recalcularía la operación gravada y el IGV sobre el precio rebajado.

## 2. Motivo

El 75 % de los vendedores está de acuerdo o muy de acuerdo con «poder cambiar el precio en la venta para hacer descuentos» (CUE-01, P12, media de 3.75 sobre 4). Hoy rebajan «a ojo» y eso descuadra la caja (ENT-01, pregunta B9). La ERS 1.1 dejó el tema como posible cambio futuro al resolver el conflicto CFL-03.

## 3. Análisis de impacto

### 3.1 Requisitos (ERS)

| Elemento | Impacto |
|---|---|
| CRQ-07 | **Se contradice.** Hoy el precio de cada línea sale del catálogo y el servidor no acepta el precio de la terminal. Habría que reescribir la regla. |
| CFL-03 | Se reabre: su resolución fue «los precios los fija solo el catálogo». |
| RF-07, RF-08 | Nuevos criterios de aceptación para la línea con descuento y para la proforma con descuento que se convierte en venta. |
| RF-09, RF-10, RF-14, RF-15 | El ticket, el XML para la SUNAT, el historial y el reporte tendrían que mostrar el descuento. |
| CRQ-01 | El cálculo del IGV se haría sobre el precio rebajado; habría que redefinir el redondeo por línea. |
| Nuevo requisito | Límite y autorización: ¿quién puede pasar del 10 %? Haría falta una regla de rol (RF-03). |

### 3.2 Diseño

| Componente | Cambio |
|---|---|
| Base de datos | Migración V015: `comprobante_detalle.descuento` y `motivo_descuento`, y nueva restricción `importe = cantidad × precio − descuento`. |
| Condor.Dominio | `CalculadoraVenta` y `EmisionComprobante` (cálculo y validación del tope), `ReporteVentas` (total de descuentos). |
| Condor.Sunat | `GeneradorXmlUbl`: elemento `cac:AllowanceCharge` con el código de descuento del catálogo 53 por línea. Es la parte de mayor riesgo frente a la SUNAT. |
| Condor.Impresion | Formato del ticket con la línea de descuento. |
| Condor.Api / ClienteApi | La emisión aceptaría un descuento de la terminal, validado contra el tope y el rol. |
| Presentación | Columna de descuento editable en la grilla de venta; atajo de teclado. |

### 3.3 Costo

Tarifa de referencia: S/ 25.00 por hora.

| Actividad | Horas |
|---|---|
| Análisis y actualización de la ERS y de REMUS | 4 |
| Migración, dominio y API | 10 |
| XML UBL con descuentos y prueba en la SUNAT beta | 8 |
| Ticket, interfaz y reporte | 6 |
| Pruebas (unitarias, aceptación, SUNAT, API) y regresión | 10 |
| **Total** | **38 h ≈ S/ 950.00** |

### 3.4 Plazo

Con 4 integrantes, unos 3 días hábiles. Llegaría en el incremento 2, el mismo de G07 y G08. Habría que repetir la línea base de rendimiento de G08 y la cobertura de G07, porque cambia el núcleo del cálculo. **Pone en riesgo el hito del 25-11-2026.**

### 3.5 Riesgos

| Riesgo | Nivel |
|---|---|
| Pérdida de margen y fraude: el vendedor rebaja sin control. Es justamente el problema que el gerente quería eliminar (B9). | Alto |
| Rechazo de la SUNAT por un XML de descuentos mal formado: el comprobante emitido e impreso termina RECHAZADO. | Alto |
| Regresión en el cálculo del IGV, que es una regla crítica (CRQ-01) con cobertura alta hoy. | Medio |
| Contradice una resolución ya acordada con el cliente (CFL-03) y la regla de seguridad CRQ-07: la terminal volvería a influir en el importe. | Medio |

### 3.6 Pruebas afectadas

`Dominio/CalculadoraVentaTests`, `Dominio/EmisionComprobanteTests`, `Aceptacion/HU05_EmitirBoletaTests`, `HU06_EmitirFacturaTests`, `HU08_NotasVentaTests`, `HU09_ProformasTests`, `Sunat/*` (XML UBL), `Dominio/FormatoTicketTests`, `Dominio/ReporteVentasTests`, `Api/ApiTests`. Además, el escenario «emitir boleta» de G08 y el caso «registro válido» de G09.

## 4. Decisión

**Rechazada por el CCB el 2026-10-30.** Sustento:

1. Contradice CRQ-07 y la resolución de CFL-03 acordada con el gerente: los precios los fija solo el catálogo.
2. Dos riesgos altos (fraude o pérdida de margen y rechazo de la SUNAT) que esta versión no tiene cómo mitigar sin un flujo de autorización adicional.
3. Su costo (38 h) y su plazo comprometen el hito del 25-11-2026 y obligan a repetir las líneas base de G07 y G08.

**Alternativa aprobada sin cambiar los requisitos:** para promociones, el Encargado general actualiza el precio en el catálogo (RF-04). Así el precio sigue saliendo de una sola fuente y queda registrado.

**Reevaluación:** después de la versión 1.0.0 del trabajo, como descuento autorizado por el Encargado general (con su usuario y contraseña) y con tope por rol.

La línea base no cambia: **ERS 1.1** y producto **1.1.0**. No hubo cambios de diseño, código ni pruebas.
