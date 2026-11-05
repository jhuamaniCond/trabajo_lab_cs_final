# Comparación de herramientas — G04 Dimensionamiento

La guía PRAC04 propone Excel con la plantilla NESMA, la herramienta *Function Points* de SourceForge y la plantilla *QMS COCOMO II Estimation Sheet*. El enunciado del trabajo pide Excel o LibreOffice Calc con fórmulas, parámetros, unidades y fuentes visibles. Las plantillas QMS y PERT se usaron en el Laboratorio 4.

## 1. Hoja de cálculo para la estimación

| Criterio | **Excel 16 + libro propio** (elegido) | LibreOffice Calc 7 | Plantilla QMS COCOMO II (.xls) | USC COCOMO II (herramienta web / escritorio) |
|---|---|---|---|---|
| Costo | Licencia institucional | Gratuita (MPL) | Gratuita | Gratuita |
| Fórmulas visibles y recalculables | **Sí**, todas | Sí | Sí, pero mezcladas con macros y celdas protegidas | No: calcula por dentro |
| NESMA detallado con DET/RET/FTR | Sí (hoja propia con matrices) | Sí | No (pide PF ya contados) | No |
| COSMIC | Sí (hoja propia) | Sí | No | No |
| COCOMO II post-arquitectura (SF + 17 EM) | Sí, con la justificación de cada nivel | Sí | Sí | Sí |
| Escenarios de 1 y 3 personas con coordinación | Sí | Sí | Parcial (plan por fases) | No |
| Sensibilidad ±20 % | Sí | Sí | No | Parcial |
| Unidades y fuentes por parámetro | Sí (hoja *Parámetros*) | Sí | No | No |
| Reproducible desde un script versionado | Sí (`generar_libro.py`) | Sí (openpyxl genera un .xlsx compatible) | No | No |

**Conclusión:** se eligió un libro propio en Excel porque cumple la condición del enunciado: el docente puede recalcular los valores y ver fórmulas, parámetros, unidades y fuentes. Además reúne en un solo archivo NESMA, COSMIC y COCOMO, con las magnitudes separadas. LibreOffice Calc es una alternativa gratuita equivalente: el libro solo usa funciones estándar. La plantilla QMS y la herramienta de USC sirven para contrastar el cálculo de COCOMO, pero no muestran el conteo funcional ni permiten agregar los escenarios pedidos.

## 2. Método de conteo funcional

| Criterio | **NESMA** (detallado, estimado, indicativo) | IFPUG 4.3 | COSMIC (ISO/IEC 19761) |
|---|---|---|---|
| Unidad | PF | PF | CFP |
| Momento de uso | Desde el modelo de datos (indicativo) hasta el detalle | Detalle | Detalle de procesos |
| Ajuste por entorno | No recomendado | Factor de ajuste (14 características) | No |
| Ventaja en Cóndor | Tres niveles con el mismo alcance; la variante estimada se acercó al detallado (−2.7 %) | Igual que NESMA detallado | Refleja mejor los procesos con mucho movimiento de datos (SUNAT, reporte) |
| Uso en el trabajo | Tamaño de entrada a COCOMO | Las mismas matrices que NESMA detallado | Segunda medición, sin convertirla a PF |
