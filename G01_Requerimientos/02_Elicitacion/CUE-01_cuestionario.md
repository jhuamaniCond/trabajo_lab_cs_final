# CUE-01 · Cuestionario a vendedores de mostrador

| Campo | Valor |
|---|---|
| Técnica | Cuestionario autoadministrado (preguntas cerradas, escala Likert de 1 a 5 y preguntas abiertas) |
| Población | Vendedores de mostrador de la ferretería (PAR-03), en los dos turnos |
| Muestra | 4 vendedores (V1 a V4): la población completa |
| Aplicación | 2026-10-29, en papel; 10 minutos |
| Datos crudos | `CUE-01_respuestas.csv` |
| Tabulación | `CUE-01_tabulacion.md`, generada con `tabular_cuestionario.py` |
| Usuario representado | **Sí.** Los cuatro integrantes respondieron cada uno como un vendedor, con base en el Product Backlog y en la observación OBS-01. |

**Indicaciones:** marque una sola opción por pregunta. En la escala, 1 = totalmente en desacuerdo y 5 = totalmente de acuerdo. Sus respuestas son anónimas.

## Sección 1 · Su trabajo actual

| N.º | Pregunta | Opciones |
|---|---|---|
| P1 | ¿Cuánto tiempo lleva trabajando como vendedor en la ferretería? | a) < 6 meses · b) 6 a 12 meses · c) 1 a 3 años · d) > 3 años |
| P2 | En hora punta, ¿cuántos clientes suele tener esperando? | a) 0 a 1 · b) 2 a 3 · c) 4 a 5 · d) más de 5 |
| P3 | ¿Qué es lo que más demora una venta? (elija una) | a) Buscar el precio · b) Calcular el total y el IGV · c) Llenar la boleta o factura · d) Pedir los datos del cliente |
| P4 | ¿Con qué frecuencia comete o detecta errores de precio o de cálculo? | a) Nunca · b) Una vez al mes · c) Una vez a la semana · d) Casi todos los días |

## Sección 2 · Lo que necesita del sistema (escala de 1 a 5)

| N.º | Afirmación | Requisito relacionado |
|---|---|---|
| P5 | Necesito encontrar un producto escribiendo solo parte de su nombre. | RF-05, RNF-01 |
| P6 | Usaría el lector de código de barras si el sistema lo reconociera. | RF-04, RF-05 |
| P7 | Prefiero trabajar solo con el teclado, sin usar el mouse. | RNF-06 |
| P8 | El ticket debe imprimirse solo al emitir el comprobante. | RF-09 |
| P9 | Escribir un usuario y una contraseña al inicio del turno no me molesta. | RF-01, CFL-01 |
| P10 | Escribir un usuario y una contraseña en cada venta me retrasaría. | RF-01, CFL-01 |
| P11 | Necesito consultar las ventas que hice en el día. | RF-14 |
| P12 | Me gustaría poder cambiar el precio en la venta para hacer descuentos. | CFL-03 |
| P13 | Pedir el DNI en todas las boletas demoraría la atención. | CRQ-02, CFL-04 |

## Sección 3 · Preguntas abiertas

- **P14** ¿Qué es lo que más le molesta del proceso de venta actual?
- **P15** Si el sistema hiciera una sola cosa bien, ¿cuál debería ser?
