# Memoria de cálculo — Dimensionamiento y estimación del Sistema Cóndor

| Campo | Valor |
|---|---|
| Libro editable | `01_Libro/estimacion_condor.xlsx`: todos los resultados son fórmulas; las celdas amarillas son datos editables |
| Alcance medido | Línea base **ERS 1.1** (16 RF, 8 RNF), producto **1.1.0** |
| Responsable | Integrante 4 — Chaisa Fernández, Anthony Leonel (líder de G04) · revisó: Integrante 1 |
| Fecha | 2026-10-30 |
| Capturas de Excel | `03_Capturas/01_parametros.png` a `16_cuadro_comparativo.png` (valores y vistas de fórmulas) |

Las magnitudes se mantienen separadas en todo el documento:

- **tamaño funcional:** PF NESMA y CFP COSMIC;
- **tamaño en código:** KSLOC;
- **esfuerzo:** horas y persona-mes (PM);
- **duración:** meses de calendario;
- **costo:** soles.

## 1. Frontera y línea base

- **Dentro de la frontera:** la aplicación WPF, el backend `Condor.Api` y la base PostgreSQL. Se miden como una sola aplicación, porque el usuario los percibe como un único sistema.
- **Fuera:** la SUNAT, la ticketera, el lector de código de barras y `pg_dump`.
- **Usuarios funcionales:** el Vendedor, el Encargado general y la SUNAT (que devuelve el CDR).
- **Propósito del conteo:** estimar el desarrollo completo del producto.
- **Correspondencia con la ERS:** hoja *Frontera*. Cada RF apunta a sus funciones NESMA. Los RNF no suman puntos de función; se modelan como factores de COCOMO.

## 2. Conteo NESMA

**Tipo de conteo:** NESMA **detallado**, que equivale a IFPUG 4.3 en la identificación de funciones y en las matrices de complejidad. Como comparación se calculan también el NESMA **estimado** y el **indicativo**. Se informan PF **sin ajustar**: NESMA 2.x no recomienda aplicar el factor de ajuste, y el entorno se modela en COCOMO.

**Reglas aplicadas**

- **Archivos lógicos internos (ALI):** grupos de datos que la aplicación mantiene. La complejidad sale de los datos elementales (DET) y de los subgrupos de registro (RET).
- **Entradas (EI):** mantienen un ALI. **Salidas (EO):** tienen datos derivados o calculados. **Consultas (EQ):** recuperan datos sin calcular. La complejidad sale de los DET y de los archivos referenciados (FTR).
- **Matrices y pesos:** hoja *Pesos NESMA*. La complejidad y los PF de cada función se calculan con `IF` e `INDEX/MATCH` (captura `05_nesma_formulas.png`).

**Hipótesis del conteo**

1. Boleta, factura, nota de venta y proforma son **un mismo ALI** (Comprobante, con 3 RET: cabecera, detalle y envío a la SUNAT).
2. La **proforma** es una EI distinta de la emisión de venta: tiene otra lógica (calcula la vigencia y no va a la SUNAT).
3. **No se cuentan:** RF-02 Cerrar sesión (no cruza datos de negocio); RF-03 Restricción por rol (control dentro de cada función); el reenvío automático (reutiliza la lógica de T15); la configuración *Empresa* (se carga por migración y ninguna función la mantiene).
4. **No hay AIE:** la SUNAT se comunica por transacciones (EO al enviar el XML, EI al registrar el CDR), no por un archivo que la aplicación consulte.

**Resultado** (capturas `03`, `04` y `06`)

| Componente | Cantidad | Baja / Media / Alta | PF |
|---|---|---|---|
| ALI | 10 | 8 / 2 / 0 | 76 |
| AIE | 0 | — | 0 |
| EI | 15 | 9 / 1 / 5 | 61 |
| EO | 10 | 2 / 4 / 4 | 56 |
| EQ | 9 | 7 / 2 / 0 | 29 |
| **Total NESMA detallado** | **44 funciones** | | **222 PF** |

| Variante NESMA | Fórmula | PF | Diferencia con el detallado |
|---|---|---|---|
| Indicativo | 35 × ALI + 15 × AIE = 35 × 10 | 350 | +57.7 % |
| Estimado | ALI y AIE en Baja; EI, EO y EQ en Media | 216 | −2.7 % |
| Detallado | Complejidad medida | **222** | — |

El indicativo sobreestima porque el producto tiene pocos archivos lógicos (10) para la cantidad de transacciones (34). El estimado casi coincide con el detallado porque las complejidades altas y bajas se compensan.

## 3. Medición COSMIC

Mismo alcance, **otra unidad (CFP)**. Se identificaron **35 procesos funcionales** con sus movimientos de entrada (E), salida (X), lectura (R) y escritura (W). 1 movimiento equivale a 1 CFP (hoja *COSMIC*, captura `08_cosmic.png`).

| Movimiento | E | X | R | W | **Total** |
|---|---|---|---|---|---|
| CFP | 42 | 53 | 61 | 27 | **183 CFP** |

Reglas destacadas:

- Cada proceso suma 1 X de mensajes de error o confirmación cuando los emite.
- La SUNAT es usuario funcional: el XML enviado cuenta como X y el CDR recibido como E.
- El reporte consolidado cuenta 5 X: uno por cada agrupación (día, tipo, terminal, usuario) y el mensaje de período inválido.

La relación 183 CFP / 222 PF = 0.82 **solo describe este producto**. No se usa como factor de conversión, y los CFP no entran en COCOMO.

## 4. Estimación con COCOMO II

**Variante:** COCOMO II.2000, modelo post-arquitectura. La arquitectura ya está definida (G03), así que corresponde el modelo con 17 multiplicadores de esfuerzo.

Fórmulas (*Model Definition Manual 2000*):

- PM = A × KSLOC^E × ΠEM
- E = B + 0.01 × ΣSF
- TDEV = C × PM^F
- F = D + 0.2 × (E − B)

Constantes: A = 2.94, B = 0.91, C = 3.67, D = 0.28. Una persona-mes son 152 horas.

**Tamaño de entrada (conversión PF → SLOC).** Se usa el factor de **54 SLOC por PF para C#** (QSM *Function Point Languages Table* v5.0: promedio 54, mediana 59, rango 29–70).

Justificación:

- es la fuente pública más usada para C#;
- el producto es casi todo C# (el SQL es mínimo).

Resultado: 222 PF × 54 = **11.99 KSLOC**.

**Comprobación con el tamaño real.** El código entregado de la versión 1.1.0 mide **11.83 KSLOC** de C# y SQL (`contar_sloc.py`, líneas lógicas sin blancos ni comentarios). No incluye 2 844 líneas de XAML (marcado de la interfaz) ni 12 603 líneas de pruebas. El factor real del producto es 11 829 / 222 = **53.3 SLOC por PF**: solo un 1.3 % por debajo del valor de tabla.

**Parámetros** (hoja *COCOMO II*, captura `09`; cada nivel tiene su justificación en el libro)

| Factores de escala | Nivel | Valor |
|---|---|---|
| PREC precedentes | N | 3.72 |
| FLEX flexibilidad | H | 2.03 |
| RESL arquitectura y riesgos | N | 4.24 |
| TEAM cohesión | H | 2.19 |
| PMAT madurez del proceso | N | 4.68 |
| **ΣSF** | | **16.86** |

E = 0.91 + 0.1686 = **1.0786**.

Los multiplicadores distintos de 1 son: RELY H 1.10 (consecuencias tributarias), CPLX H 1.17 (concurrencia, firma XML), PVOL L 0.87, APEX L 1.10, TOOL H 0.90 y SITE H 0.93. Producto: **EAF = 1.031**.

**Resultados** (captura `10`, y `11` con las fórmulas)

| Magnitud | A) Tamaño desde NESMA | B) Tamaño real 1.1.0 | Unidad |
|---|---|---|---|
| Tamaño | 11.99 | 11.83 | KSLOC |
| Esfuerzo | **44.2** | 43.5 | PM |
| Esfuerzo | 6 713 | 6 617 | horas |
| Duración nominal (TDEV) | **12.0** | 12.0 | meses |
| Personal promedio | 3.7 | 3.6 | personas a tiempo completo |
| Costo del esfuerzo (S/ 25/h) | S/ 167 835 | S/ 165 435 | soles |
| COCOMO 81 orgánico (comparación) | 32.6 PM; 9.4 meses | 32.1 PM; 9.3 meses | |

## 5. Costo y plazo con 1 y 3 personas

Parámetros (hoja *Parámetros*):

- **Tarifa:** S/ 25.00 por hora, la misma de los análisis de impacto de G02.
- **Dedicación a tiempo completo:** 152 h por mes y persona.
- **Dedicación parcial:** 20 h por semana × 4.33 = 86.6 h por mes y persona.
- **Coordinación:** 5 % por canal de comunicación, con n(n−1)/2 canales. Con 3 personas hay 3 canales, es decir, +15 % de esfuerzo.
- **Plazo mínimo:** el 75 % del TDEV nominal (9.0 meses), por la compresión máxima de COCOMO.

Captura `12_escenarios_1_y_3_personas.png`; la `13` muestra las fórmulas.

| Escenario | Esfuerzo total | Duración | Costo |
|---|---|---|---|
| 1 persona, tiempo completo | 6 713 h (44.2 PM) | **44.2 meses** | **S/ 167 835** |
| 3 personas, tiempo completo | 7 720 h (50.8 PM) | **16.9 meses** | **S/ 193 011** |
| 1 persona, dedicación parcial | 6 713 h | 77.5 meses | S/ 167 835 |
| 3 personas, dedicación parcial | 7 720 h | 29.7 meses | S/ 193 011 |

Lectura de los resultados:

- **Esfuerzo y costo:** con 3 personas suben un 15 % por la coordinación.
- **Duración:** baja de 44.2 a 16.9 meses (−62 %), no a la tercera parte (14.7 meses), porque el trabajo aumenta. En ningún escenario la duración baja de los 9.0 meses de compresión máxima.
- **Tamaño:** el funcional (222 PF, 183 CFP) es el mismo en todos los escenarios.

## 6. Sensibilidad (±20 %)

Hoja *Sensibilidad*, captura `14`. Costo del escenario de 3 personas:

| Parámetro variado | −20 % | Base | +20 % |
|---|---|---|---|
| Factor SLOC/PF (43.2 / 54 / 64.8) | S/ 151 724 (**−21.4 %**) | S/ 193 011 | S/ 234 956 (**+21.7 %**) |
| Tamaño en PF (178 / 222 / 266) | −21.4 % | — | +21.7 % |
| Multiplicador CPLX (0.94 / 1.17 / 1.40) | −20.0 % | — | +20.0 % |

- **Factor de conversión y tamaño:** el efecto es **más que proporcional**, porque el exponente E = 1.08 es mayor que 1 (deseconomía de escala). Además es asimétrico: +21.7 % frente a −21.4 %.
- **Multiplicadores de esfuerzo:** su efecto es lineal.
- **Duración:** reacciona mucho menos (TDEV de 11.2 a 12.8 meses ante ±20 % de tamaño), porque F = 0.31.
- **Riesgo del factor:** el factor SLOC/PF es el parámetro de mayor riesgo. Con el rango completo de QSM (29 a 70) el tamaño iría de 6.4 a 15.5 KSLOC. Aquí el riesgo queda acotado porque el factor real medido (53.3) confirma el valor de tabla.

## 7. Comparación de los métodos

Hoja *Comparación*, captura `16`.

| Método | Resultado | Para qué sirve |
|---|---|---|
| NESMA indicativo | 350 PF | Orden de magnitud con solo el modelo de datos; aquí sobreestima un 58 % |
| NESMA estimado | 216 PF | Buena aproximación (−2.7 %) sin medir complejidades |
| NESMA detallado | **222 PF** | Tamaño de referencia del producto |
| COSMIC | **183 CFP** | Tamaño en otra unidad, más sensible a los procesos con mucho movimiento de datos (emisión, envío a la SUNAT) y a las salidas múltiples (reporte) |
| COCOMO II (desde NESMA) | 44.2 PM; 12.0 meses | Esfuerzo y plazo de un equipo industrial |
| COCOMO II (tamaño real) | 43.5 PM; 12.0 meses | Valida la conversión: −1.4 % de esfuerzo frente a la versión desde NESMA |
| COCOMO 81 orgánico | 32.6 PM; 9.4 meses | Modelo antiguo, sin factores de escala: un 26 % menos de esfuerzo |

## 8. Limitaciones de la calibración y confrontación con las horas reales

1. **COCOMO II.2000 se calibró con 161 proyectos industriales** (1970–2000). Supone equipos profesionales, todas las fases desde el diseño hasta la integración y desarrollo mayormente manual. No está calibrado para equipos de estudiantes, ni para el uso intensivo de frameworks (.NET, Npgsql, ASP.NET), contenedores y asistentes de programación, que reducen las horas por línea.
2. **El factor SLOC/PF de QSM es una media de la industria.** En este producto coincidió con el real (53.3 frente a 54), pero eso valida el **tamaño**, no el **esfuerzo**.
3. **La tarifa (S/ 25/h) y la dedicación (20 h por semana) son supuestos del equipo**, no datos de mercado auditados.
4. **El método «wine»** que menciona la guía no está definido, así que no se le asignó una fórmula (aclaración del enunciado).

### 8.1 Confrontación con las horas reales

El equipo registró sus horas de desarrollo del producto, día por día, del **20 al 30 de octubre de 2026**, hasta llegar a la versión 1.1.1 (`01_Libro/horas_reales_desarrollo.json`; hoja *Horas reales*, captura `15`).

| Magnitud | Estimado (COCOMO II, sin calibrar) | Real | Unidad |
|---|---|---|---|
| Esfuerzo | 6 713 (44.2 PM) | **422** (2.78 PM) | horas |
| Duración | 12.0 | **0.36** (11 días) | meses |
| Personas | 3.7 a tiempo completo | **4**, con 9.6 h por persona y día en promedio | personas |
| Productividad | 1.8 | **28.0** | SLOC / hora |
| Costo del esfuerzo (S/ 25/h) | S/ 167 835 | **S/ 10 550** | soles |

Reparto por integrante: Integrante 3, 107 h; Integrante 4, 109 h; Integrante 1, 107 h; Integrante 2, 99 h.

**Error de la estimación:** MRE = |6 713 − 422| / 422 = **1 491 %**. COCOMO II sin calibrar sobreestimó el esfuerzo de este equipo unas 16 veces. Con el tamaño real en lugar del de NESMA el error es casi el mismo (1 468 %). Esto confirma que **el error no está en el tamaño**: el conteo NESMA y la conversión acertaron. Está en la **productividad** que supone el modelo.

**Causas probables** (las dos primeras son verificables en los datos; la tercera la debe confirmar el equipo):

1. **Intensidad del trabajo:** 4 personas durante 11 días seguidos, a casi 10 h por día. COCOMO supone 152 h por persona-mes, en meses de trabajo normal.
2. **Reutilización de frameworks y bibliotecas** que COCOMO no descuenta del tamaño: ASP.NET Core, WPF, Npgsql, xUnit y el modelo UBL de Greenter (DEP-01).
3. **Herramientas de productividad:** el IDE, plantillas, generadores y, si se usó, **asistencia de IA para programar**. El enunciado pide declarar esa asistencia en el paquete final. Si se usó, explica buena parte de la productividad de 28 SLOC por hora, unas 15 veces la de la base de calibración industrial.

**Calibración local:** factor = real / estimado = 422 / 6 713 = **0.063**, por lo que **A calibrada = 2.94 × 0.063 = 0.185**. Con esa constante el modelo reproduce las 422 h de este proyecto. Es el valor que el equipo debe usar para estimar sus próximos incrementos con el mismo tipo de trabajo. Con un solo proyecto, sin embargo, la calibración es débil: COCOMO recomienda varios proyectos para ajustar A y, si es posible, también B.

**Duración:** la real (11 días) queda muy por debajo del 75 % del TDEV nominal (9 meses), que COCOMO considera el límite de compresión. El proyecto real está fuera del rango en que el modelo es válido. Se trató de un desarrollo corto e intensivo, no del proyecto de un año que supone el modelo.

## 9. Conclusiones

- **Tamaño:** el producto mide **222 PF NESMA** (tamaño medio) y **183 CFP COSMIC**. Son magnitudes distintas que no se convierten entre sí.
- **Conversión a código:** con el factor de C# se obtienen 12.0 KSLOC, prácticamente el tamaño real (11.8 KSLOC). Esto da confianza en el conteo NESMA.
- **Esfuerzo industrial:** COCOMO II estima **44 PM (≈ 6 700 h)** y **12 meses** con un equipo de 3.7 personas a tiempo completo.
- **Escenarios:** con 3 personas el costo sube a **S/ 193 011** y la duración baja a **16.9 meses**, no a la tercera parte. Con 1 persona: **S/ 167 835** y **44.2 meses**.
- **Sensibilidad:** el resultado es más sensible al tamaño y al factor de conversión que a los multiplicadores, por la deseconomía de escala (E > 1).
- **Calibración:** frente a las **422 h reales** (4 personas, 11 días), COCOMO II sin calibrar sobreestima unas 16 veces (MRE de 1 491 %). El tamaño sí fue correcto; el desvío está en la productividad (28 SLOC/h reales frente a 1.8 de la base industrial). La constante calibrada con este proyecto es **A = 0.185**, y debe usarse, con prudencia, para los próximos incrementos del equipo.
