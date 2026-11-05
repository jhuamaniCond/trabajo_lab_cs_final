# ENT-01 · Guion de entrevista semiestructurada

| Campo | Valor |
|---|---|
| Técnica | Entrevista semiestructurada (preguntas abiertas con repreguntas) |
| Entrevistados | PAR-01 Gerente general · PAR-02 Encargado general de tienda |
| Entrevistadores | Integrante 1 (conduce) · Integrante 3 (registra el acta) |
| Duración prevista | 45 min por entrevistado |
| Lugar / medio | Reunión presencial del equipo (usuario representado) |
| Registro | Acta escrita (`ENT-01_acta_entrevista.md`); sin grabación de audio |
| Usuario representado | **Sí.** El Integrante 2 asumió el rol de gerente y el Integrante 4 el de encargado, a partir del Product Backlog (HU-01 a HU-18) y de las notas del proyecto Cóndor. |

## Objetivos de la entrevista

1. Entender el proceso actual de venta, cobro, facturación y compras.
2. Identificar problemas, prioridades y restricciones del negocio.
3. Obtener reglas de negocio (comprobantes, IGV, SUNAT, proformas, compras).
4. Acordar metas medibles (tiempos, disponibilidad, seguridad).
5. Detectar necesidades en conflicto entre los interesados.

## Apertura (5 min)

- Presentación del equipo y del propósito: «Queremos entender cómo trabaja la ferretería para especificar el sistema».
- Confidencialidad y uso académico de la información.
- Confirmar el tiempo disponible.

## Bloque A · Contexto del negocio (gerente)

| N.º | Pregunta | Repregunta / qué se busca |
|---|---|---|
| A1 | ¿Cómo describiría el negocio y a sus clientes? | Público frente a obras; volumen diario. |
| A2 | ¿Cuántas ventas atienden en un día normal y en uno de campaña? | Frecuencia de RF-07 y carga de RNF-02. |
| A3 | ¿Qué problema le gustaría resolver primero? | Prioridades (MoSCoW). |
| A4 | ¿Cómo sabe hoy cuánto vendió en el día o en el mes? | Necesidad de reporte consolidado (RF-15). |
| A5 | ¿Cómo controla qué vendedor emitió cada comprobante? | Autenticación y trazabilidad (RF-01, CRQ-11). |
| A6 | ¿Qué información no deberían ver los vendedores? | Roles (RF-03, CRQ-12). |
| A7 | ¿Qué pasaría si se pierde la información del día? | Respaldo (RF-16, RNF-07). |
| A8 | ¿Con qué presupuesto e infraestructura cuenta? | Restricciones (PC, red, nube). |

## Bloque B · Operación (encargado)

| N.º | Pregunta | Repregunta / qué se busca |
|---|---|---|
| B1 | Describa paso a paso una venta con boleta, desde que llega el cliente. | Flujo de RF-05, RF-07, RF-09. |
| B2 | ¿Cuándo piden factura y qué datos solicitan? | CRQ-03, CRQ-04. |
| B3 | ¿Cómo hacen las cotizaciones y cuánto tiempo las respetan? | Proformas: vigencia (CRQ-06). |
| B4 | ¿Cómo informan los comprobantes a la SUNAT? ¿Qué pasa si no hay internet? | RF-10, CFL-02. |
| B5 | ¿Cómo registran las compras a proveedores? ¿Han duplicado alguna? | RF-11, RF-12, CRQ-09. |
| B6 | ¿Cuándo emiten guías de remisión? | RF-13, CRQ-13. |
| B7 | ¿Cuántas PC hay y cuántas personas venden a la vez? | RNF-04 (concurrencia). |
| B8 | ¿Usan lector de código de barras o ticketera? | INT-03, RF-09. |
| B9 | ¿Cómo actualizan los precios? ¿Los vendedores pueden cambiarlos? | CRQ-07, CFL-03. |

## Cierre (5 min)

- Resumir los puntos clave y confirmar lo entendido.
- Preguntar: «¿Hay algo importante que no le hayamos preguntado?».
- Acordar la validación de la ERS (revisión de la versión 0.9).
