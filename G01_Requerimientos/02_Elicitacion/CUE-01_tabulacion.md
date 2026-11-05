# CUE-01 · Tabulación del cuestionario

Generado con `tabular_cuestionario.py` a partir de `CUE-01_respuestas.csv` (n = 4). **Usuario representado:** las respuestas las dieron integrantes del equipo en el rol de vendedor.

## Preguntas cerradas

**P1. Antigüedad como vendedor**

| Opción | Respuestas | % |
|---|---|---|
| < 6 meses | 1 | 25 % |
| 6 a 12 meses | 1 | 25 % |
| 1 a 3 años | 1 | 25 % |
| > 3 años | 1 | 25 % |

**P2. Clientes esperando en hora punta**

| Opción | Respuestas | % |
|---|---|---|
| 0 a 1 | 0 | 0 % |
| 2 a 3 | 1 | 25 % |
| 4 a 5 | 2 | 50 % |
| más de 5 | 1 | 25 % |

**P3. Lo que más demora una venta**

| Opción | Respuestas | % |
|---|---|---|
| Buscar el precio | 2 | 50 % |
| Calcular el total y el IGV | 1 | 25 % |
| Llenar la boleta o factura | 1 | 25 % |
| Pedir los datos del cliente | 0 | 0 % |

**P4. Frecuencia de errores de precio o cálculo**

| Opción | Respuestas | % |
|---|---|---|
| Nunca | 0 | 0 % |
| Una vez al mes | 1 | 25 % |
| Una vez a la semana | 2 | 50 % |
| Casi todos los días | 1 | 25 % |

## Escala de 1 a 5

| N.º | Afirmación | Media | Mediana | % de acuerdo (4 o 5) | Requisito |
|---|---|---|---|---|---|
| P5 | Encontrar el producto con parte del nombre | 4.75 | 5 | 100 % | RF-05, RNF-01 |
| P6 | Usaría el lector de código de barras | 4.75 | 5 | 100 % | RF-04, RF-05 |
| P7 | Trabajar solo con el teclado | 4.50 | 4.5 | 100 % | RNF-06 |
| P8 | Ticket impreso al emitir | 4.75 | 5 | 100 % | RF-09 |
| P9 | Usuario y contraseña al inicio del turno no molesta | 4.00 | 4 | 75 % | RF-01, CFL-01 |
| P10 | Usuario y contraseña en cada venta retrasaría | 4.75 | 5 | 100 % | RF-01, CFL-01 |
| P11 | Consultar las ventas del día | 4.00 | 4 | 75 % | RF-14 |
| P12 | Cambiar el precio para hacer descuentos | 3.75 | 4 | 75 % | CFL-03 |
| P13 | Pedir DNI en todas las boletas demoraría | 4.75 | 5 | 100 % | CRQ-02, CFL-04 |

## Preguntas abiertas

| Vendedor | P14 · Lo que más molesta | P15 · Lo que debe hacer bien |
|---|---|---|
| V1 (mañana) | Buscar el precio en la lista, que además está desactualizada | Encontrar rápido el producto con su precio |
| V2 (mañana) | Calcular el IGV a mano y llenar la boleta con la cola esperando | Calcular solo el total y el IGV |
| V3 (tarde) | No conozco todos los precios y tengo que preguntar | Mostrar el precio al escribir el nombre |
| V4 (tarde) | Repetir la boleta cuando me equivoco | Imprimir la boleta sin escribirla a mano |

## Interpretación y requisitos derivados

- **Buscar el precio** es la principal demora (P3) y la búsqueda por parte del nombre tiene 100 % de acuerdo (P5): confirma **RF-05** y la meta de **RNF-01** (sugerencias en menos de 1 s).
- El **lector de código de barras** sería usado por todos (P6): se incluye en **RF-04** y **RF-05**.
- Trabajar **solo con el teclado** tiene 100 % de acuerdo (P7): **RNF-06** con atajos F1 a F11.
- El ingreso **una vez por turno** es aceptado (P9, 75 %), pero en **cada venta** sería rechazado (P10, 100 %): sustenta la resolución de **CFL-01** (token válido por 480 minutos).
- Tres de cuatro quieren **cambiar el precio** (P12): choca con el gerente; se registra **CFL-03**.
- Pedir el **DNI en todas las boletas** demoraría (P13, 100 %): se exige solo desde S/ 700 (**CRQ-02**, **CFL-04**).
- Errores semanales o diarios en 3 de 4 vendedores (P4): justifica el cálculo automático del IGV (**CRQ-01**).
