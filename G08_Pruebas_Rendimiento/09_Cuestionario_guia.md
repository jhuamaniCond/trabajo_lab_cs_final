# Cuestionario de la guía PRAC08, aplicado al producto

## a) ¿Qué variables se miden en las pruebas de performance?

Se miden variables del **lado del cliente** (lo que percibe el usuario), del **lado del servidor** (los recursos) y de **la carga** que se aplica. En Cóndor se midieron estas (`01_Plan/plan_pruebas_rendimiento.md` y `06_Analisis/analisis_resultados.md`):

| Grupo | Variable | Cómo se midió | Valor en carga esperada (1.1.2) |
|---|---|---|---|
| **Tiempo de respuesta** | Media, **p90, p95**, p99 y máximo, **por transacción** | `.jtl` de JMeter, percentil por rango más cercano | T1 Consultar productos: p95 = 12 ms · T2 Registrar boleta: p95 = 22 ms |
| **Throughput** | Peticiones por segundo | Dashboard HTML de JMeter | T1: 3,43/s · T2: 1,39/s |
| **Tasa de error** | % de respuestas que no cumplen la validación | Código HTTP esperado (200/201), JSON Assertion (`$[0].id`, `$.numero`) y tiempo máximo (5 s de conexión, 10 s de respuesta) | 0,00 % |
| **Satisfacción** | APDEX (satisfecho ≤ 500 ms, tolerado ≤ 2 000 ms) | Dashboard de JMeter | 1,00 |
| **Carga aplicada** | Usuarios activos, rampa, think time y mezcla de operaciones | Thread Groups; pausa de 1 a 3 s; 70 % consulta / 30 % registro | 10 usuarios, rampa de 30 s, mezcla medida 69,5/30,5 |
| **CPU** | Total del equipo, de CondorApi y de PostgreSQL | typeperf cada 2 s; `docker stats` | Total 10,6 % de media · API 0,1 % · base 0,0 % |
| **Memoria** | Memoria privada de la API a lo largo del tiempo (detecta fugas) | typeperf | Estabilidad: 307 → 305 MB en 15 min (plana) |
| **Base de datos** | Conexiones activas y conexiones esperando un bloqueo | `pg_stat_activity` cada 5 s | Máximo 3 conexiones, 0 esperando |
| **Capacidad** | Punto de saturación y recurso que se agota primero | Diagnóstico sin pausas con 10, 25, 50 y 100 hilos | Bloqueo de la fila de la serie B001: 19 de 20 conexiones esperando |

Las variables se miden **por transacción** y **por escenario**, porque un promedio global esconde problemas. Así se vio en el pico: en 1.1.1 el p95 de T2 subió a 146 ms solo durante los 10 s de la subida de 10 a 50 usuarios, y el promedio del escenario no lo muestra.

## b) ¿Cuál es el protocolo para revisar y evaluar los resultados de JMeter?

El que se aplicó en G08 tiene ocho pasos:

1. **Fijar antes de ejecutar los criterios y la definición de error.** p95 ≤ 2 s y error ≤ 1 % por transacción en carga esperada (RNF-02). Es error todo código inesperado, respuesta sin el campo validado o tiempo de espera superado. Un tiempo entre 2 y 10 s no es error, pero cuenta para el p95.
2. **Verificar que la ejecución es válida.** Se usa el modo no gráfico (`jmeter -n`), se revisa `jmeter.log` sin errores del propio generador, se confirma que la mezcla real se parece a la planificada (69,5/30,5 frente a 70/30) y que la base partió del mismo estado (`reiniciar_ventas.sql` antes de cada escenario). También se comprueba que el generador no fue el cuello de botella: en el diagnóstico, JMeter usó un 3 % de CPU de media (en la línea base no se midió, ver la limitación del análisis).
3. **Descartar la rampa.** Las métricas se calculan solo en las ventanas estables. Por ejemplo, la carga se mide de 0:30 a 5:30 y no desde 0:00.
4. **Leer el dashboard HTML por transacción:** Statistics (percentiles, throughput, error), Errors, Response Times Over Time y Active Threads. El p95 del dashboard coincidió con el de `analizar_resultados.py`. El p99 puede diferir, porque el dashboard lo interpola.
5. **Contrastar cada umbral con el dato** y emitir un veredicto. RNF-02 **se cumple**: p95 de 11–12 ms en T1 y de 21–22 ms en T2, con 0 % de error.
6. **Analizar cada escenario según su objetivo:** carga (cumplimiento del umbral), estrés (punto de quiebre: no lo hubo con 50 usuarios), pico (degradación y **recuperación** tras la ráfaga) y estabilidad (deriva de tiempos y de memoria minuto a minuto, sin tendencia).
7. **Correlacionar con el monitoreo** para localizar el cuello de botella: CPU, memoria y bloqueos de PostgreSQL. Así se encontró el bloqueo de la serie B001, se aplicó **MEJ-01** (producto 1.1.2) y se **repitió** todo en condiciones equivalentes. La mejora fue parcial: +27 % de throughput de T2 con 50 hilos sin pausas. La causa restante, la escritura del WAL en el COMMIT, quedó documentada con sus acciones pendientes.
8. **Informar con alcance y limitaciones.** Se conservan `.jmx`, `.jtl`, el dashboard y el monitoreo. El informe aclara que 15 minutos de estabilidad no descartan fugas de horas y que los datos son sintéticos.
