# Cuestionario de la guía PRAC04, aplicado al producto

## a) ¿Qué resuelve conocer el dimensionamiento temprano del proceso de construcción de software?

Permite decidir **antes de construir**, cuando cambiar el alcance todavía es barato. En Cóndor resolvió cuatro cosas:

1. **Si el alcance cabe en el plazo y en el presupuesto.** Con 222 PF NESMA, COCOMO II estima 44,2 PM y 12 meses para un equipo industrial (memoria de cálculo, sección 4). Esa cifra obligó a preguntarse qué entra en cada incremento antes de aceptar nuevos cambios.
2. **Cuántas personas poner y qué pasa con el plazo.** El escenario de 3 personas baja la duración de 44,2 a 16,9 meses y no a la tercera parte, porque la coordinación suma un 15 % de esfuerzo (sección 5). Sin el cálculo se habría supuesto que tres personas hacen el trabajo en un tercio del tiempo.
3. **Una base para valorar los cambios.** La tarifa y las horas de G04 (S/ 25/h) son las mismas con que se costaron CC-01 (S/ 1 400), CC-03 (S/ 440) y el plan de riesgos de G06 (S/ 1 525). Así, todos los costos del proyecto son comparables.
4. **Una referencia para medir el desvío.** Al confrontar con las 422 h reales se vio que el tamaño estaba bien medido (11,99 KSLOC estimados frente a 11,83 reales) y que el error estaba en la productividad. De ahí sale la constante calibrada A = 0,185 para los próximos incrementos.

Lo que no resuelve es la exactitud del esfuerzo. Un dimensionamiento temprano da un **orden de magnitud** que hay que calibrar con datos propios.

## b) ¿Qué ventaja tiene usar la metodología NESMA?

1. **Tres niveles de detalle con el mismo método.** El conteo **indicativo** solo necesita el modelo de datos, el **estimado** las funciones sin complejidad y el **detallado** la complejidad completa. En Cóndor dieron 350, 216 y 222 PF. El estimado quedó a −2,7 % del detallado, así que **sirve para dimensionar al inicio, cuando todavía no hay un diseño detallado**.
2. **Compatible con IFPUG.** El detallado identifica las funciones y aplica las matrices de complejidad de IFPUG 4.3. Los resultados se pueden comparar con datos históricos y con tablas de conversión como la de QSM (54 SLOC por PF para C#), que aquí coincidió con el tamaño real (53,3).
3. **Independiente de la tecnología.** Mide lo que el usuario recibe (ALI, EI, EO, EQ), no el lenguaje. El mismo conteo vale para la app WPF y para la API, que el usuario percibe como un solo sistema.
4. **Reglas claras y documentables.** Las cuatro hipótesis del conteo (por ejemplo, que boleta, factura, nota de venta y proforma son un mismo ALI) quedaron escritas y el docente puede recalcularlas en el libro.

Su desventaja frente a COSMIC: valora menos los procesos con muchos movimientos de datos, como la emisión con envío a la SUNAT o el reporte con varias agrupaciones. Por eso también se midió COSMIC (183 CFP), sin mezclar las unidades.

## c) ¿Es confiable el dimensionamiento COCOMO? ¿Por qué?

**Para el tamaño y la forma de la curva, sí; para el esfuerzo absoluto, solo después de calibrarlo.** Los datos del proyecto lo muestran:

| Magnitud | COCOMO II (sin calibrar) | Real | Lectura |
|---|---|---|---|
| Tamaño | 11,99 KSLOC (desde NESMA) | 11,83 KSLOC | **Confiable**: 1,3 % de diferencia |
| Esfuerzo | 6 713 h | 422 h | **No confiable sin calibrar**: MRE de 1 491 %, unas 16 veces más |
| Duración | 12 meses (mínimo 9 meses) | 11 días | Fuera del rango en que el modelo es válido |

Por qué falla sin calibrar:

- **Base de calibración ajena.** COCOMO II.2000 se calibró con 161 proyectos industriales de 1970 a 2000, con desarrollo mayormente manual y meses de 152 h. Cóndor lo hicieron 4 personas en 11 días intensivos, con frameworks (.NET, ASP.NET, Npgsql) y herramientas de productividad, entre ellas asistencia de IA.
- **Sensibilidad.** Con E = 1,08 > 1, un ±20 % en el tamaño o en el factor SLOC/PF mueve el costo entre −21,4 % y +21,7 % (sección 6). El factor de conversión es el parámetro de mayor riesgo.

Por qué sí es útil:

- **Sus relaciones se cumplieron:** la deseconomía de escala, el efecto de la coordinación al pasar de 1 a 3 personas y el límite de compresión del plazo.
- **Se puede calibrar.** Con A = 2,94 × 0,063 = **0,185** el modelo reproduce las horas reales del equipo. Con un solo proyecto esa calibración es débil, y COCOMO recomienda varios proyectos para ajustar A y B.

**Conclusión:** COCOMO es confiable como modelo de **relaciones** y de **comparación de escenarios**, pero no como predicción absoluta sin datos históricos propios. El tamaño medido con NESMA, en cambio, sí resultó confiable desde el inicio.
