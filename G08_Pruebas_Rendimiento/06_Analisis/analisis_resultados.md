# Análisis de resultados — G08 Pruebas de rendimiento

Producto: Sistema Logístico Cóndor **1.1.1** (línea base, SVN r22) y **1.1.2** (después de MEJ-01, SVN r25). Ejecución: 2026-11-01, JMeter 5.6.3 en modo no gráfico. Plan, datos y entorno: `01_Plan/plan_pruebas_rendimiento.md`. Las cifras salen de `analizar_resultados.py` (libro `resumen_resultados.xlsx`, gráficas en `graficas/`, capturas de los dashboards en `capturas/`). Percentiles por rango más cercano sobre todas las muestras del escenario. El dashboard de JMeter interpola el p99 y puede diferir en algunos milisegundos (por ejemplo, 57,49 ms frente a 26 ms en T2 de la 1.1.2); el p95 coincide.

## 1. RNF-02 — carga esperada (10 usuarios, 5 min, rampa de 30 s)

| Versión | Transacción | Muestras | Media | p90 | **p95** | p99 | Máx | **Error** | Throughput |
|---|---|---|---|---|---|---|---|---|---|
| 1.1.1 | T1 Consultar productos | 1 096 | 9 ms | 11 | **11 ms** | 13 | 26 | **0,00 %** | 3,38/s |
| 1.1.1 | T2 Registrar boleta | 481 | 17 ms | 20 | **21 ms** | 22 | 189 | **0,00 %** | 1,47/s |
| 1.1.2 | T1 Consultar productos | 1 122 | 10 ms | 12 | **12 ms** | 13 | 51 | **0,00 %** | 3,43/s |
| 1.1.2 | T2 Registrar boleta | 452 | 19 ms | 22 | **22 ms** | 26 | 194 | **0,00 %** | 1,39/s |

**Veredicto: RNF-02 se cumple** en las dos versiones. Por transacción, el p95 queda dos órdenes de magnitud por debajo de los 2 000 ms y no hay ninguna respuesta con error (código inesperado, aserción JSON fallida ni tiempo de espera). APDEX = 1,00 (todas las muestras ≤ 500 ms; captura `capturas/03_apdex_carga_despues.png`). La mezcla medida es 69,5 % / 30,5 %, coherente con el 70/30 del plan. El ingreso (no cuenta para RNF-02) tardó 26–79 ms por la verificación PBKDF2 de 100 000 iteraciones.

## 2. Estrés escalonado (10 → 25 → 50 usuarios, 3 min por nivel)

| Nivel | Versión | T1 p95 | T2 p95 | Error | Throughput T1+T2 | Conexiones API (máx) |
|---|---|---|---|---|---|---|
| 10 u (0:30–3:30) | 1.1.1 / 1.1.2 | 12 / 11 ms | 21 / 21 ms | 0 % | 5,0 / 4,9 /s | — |
| 25 u (3:40–6:30) | 1.1.1 / 1.1.2 | 11 / 11 ms | 21 / 21 ms | 0 % | 12,3 / 12,4 /s | — |
| 50 u (6:40–9:30) | 1.1.1 / 1.1.2 | 9 / 10 ms | 19 / 20 ms | 0 % | 24,8 / 24,9 /s | 9 / 6 |

El throughput crece linealmente con los usuarios (5 → 12 → 25 peticiones/s) y el tiempo de respuesta no cambia: con 50 usuarios con pausas **no se alcanza ningún punto de quiebre**. CPU total media del equipo: 8,5 % (máx 23 %) en 1.1.1. Gráficas: `graficas/*_estres_tiempos.png`, captura `capturas/04_estres_despues_tiempos.png`.

## 3. Pico (10 → 50 → 10 usuarios)

| Ventana | Versión | T1 p95 | T2 p95 | T2 máx | Error |
|---|---|---|---|---|---|
| Antes, 10 u (0:30–3:00) | 1.1.1 / 1.1.2 | 12 / 11 ms | 22 / 21 ms | 124 / — ms | 0 % |
| Subida 10→50 (3:00–3:10) | 1.1.1 / 1.1.2 | 12 / 11 ms | **146** / 21 ms | 224 / 30 ms | 0 % |
| Pico, 50 u (3:10–4:10) | 1.1.1 / 1.1.2 | 10 / 11 ms | 20 / 20 ms | 97 / 185 ms | 0 % |
| Después, 10 u (4:10–7:00) | 1.1.1 / 1.1.2 | 11 / 11 ms | 21 / 21 ms | 102 / 125 ms | 0 % |

En la subida entran 40 vendedores en 10 s. Cada uno hace su ingreso (PBKDF2) y su primera boleta casi a la vez. En 1.1.1 eso llevó el p95 de T2 a 146 ms durante esos 10 s (51 muestras); en 1.1.2 no pasó de 21 ms. La ventana es corta: indica que la mejora ayuda en ráfagas, pero no basta para afirmarlo. **Recuperación:** a los 4:10 los 40 hilos se detienen y en la ventana siguiente los tiempos vuelven a los del inicio (T2 p95 21 ms), sin errores ni conexiones colgadas. Capturas `capturas/06_pico_despues_tiempos.png` y `07_pico_despues_usuarios_activos.png`.

## 4. Estabilidad (10 usuarios, 15 min)

| Versión | Muestras | T1 p95 por minuto (mín–máx) | T2 p95 por minuto (mín–máx) | Error | Memoria privada de CondorApi |
|---|---|---|---|---|---|
| 1.1.1 | 4 546 | 10–12 ms | 19–22 ms | 0 % | 290 → 305 MB (máx 306) |
| 1.1.2 | 4 560 | 11–12 ms | 20–22 ms | 0 % | 307 → 305 MB (máx 307) |

No hay tendencia creciente en los tiempos minuto a minuto (hoja *Estabilidad por minuto*) ni en la memoria de la API. Tras la subida inicial de 30 a ~300 MB, propia del recolector de .NET en modo servidor, la memoria se mantiene plana. **Alcance:** solo permite concluir que el servicio es estable durante 15 minutos con 10 usuarios; no descarta fugas que aparezcan en horas o días.

## 5. Recursos (monitoreo)

| Escenario (1.1.1) | CPU total media / máx | CPU CondorApi media / máx | CPU PostgreSQL media / máx | Conexiones API máx | Esperando bloqueo |
|---|---|---|---|---|---|
| Carga | 10,6 / 28,7 % | 0,1 / 0,3 % | 0,0 / 0,1 % | 3 | 0 |
| Estrés | 8,5 / 22,9 % | 0,1 / 0,4 % | 0,1 / 0,3 % | 9 | 0 |
| Pico | 6,4 / 26,2 % | 0,1 / 0,5 % | 0,1 / 0,2 % | 9 | 0 |
| Estabilidad | 8,2 / 24,8 % | 0,0 / 0,4 % | 0,0 / 0,1 % | 5 | 0 |

La CPU total incluye Docker Desktop. La API y la base apenas se usan con el perfil académico. Herramientas: typeperf (CPU y memoria por proceso, cada 2 s), `docker stats` y `pg_stat_activity` (cada 5 s). Gráficas `graficas/*_monitoreo.png`.

## 6. Cuello de botella, mejora y repetición

Como el perfil con pausas no satura nada, se ejecutó un diagnóstico de capacidad sin pausas (10/25/50/100 hilos). El recurso que se satura primero es **el bloqueo de la fila de la serie B001**: 19 de las 20 conexiones del pool quedan esperándolo, T2 se estanca en ~210–270 boletas/s y las consultas esperan conexión. Se aplicó **MEJ-01** (el número se reserva al final de la transacción) y se repitieron los cuatro escenarios y la capacidad en condiciones equivalentes. Detalle completo en `05_Cuello_de_Botella/MEJ-01_correlativo_al_final.md`.

| Capacidad, 50 hilos sin pausas | 1.1.1 | 1.1.2 |
|---|---|---|
| T2 p95 / throughput | 356 ms / 208/s | 290 ms / 263/s |
| T1 p95 / throughput | 64 ms / 483/s | 40 ms / 615/s |

La mejora es **parcial**. Con 50 hilos sube el throughput de T2 un 27 % y baja el p95 de T1 un 38 %; con 10, 25 y 100 hilos el efecto es nulo o negativo, y siguen 17–18 conexiones esperando la serie. Un diagnóstico con `synchronous_commit = off` (revertido) llevó T2 a 466/s con p95 de 78 ms, con la CPU del equipo al 89–99 %. Eso indica que **la causa restante es la escritura a disco del WAL en el COMMIT**, que se hace con la serie todavía bloqueada. Acciones pendientes: WAL en un disco de baja latencia, series por terminal (requiere una solicitud de cambio) y agrupar los COMMIT (`commit_delay`).

En el perfil académico la 1.1.2 da los mismos tiempos que la 1.1.1 (comparación en la hoja *Antes vs después* y en `graficas/comparacion_antes_despues_p95.png`).

## 7. Conclusiones

1. **RNF-02 cumplido con datos**: en carga esperada, T1 p95 = 11–12 ms y T2 p95 = 21–22 ms, con 0 % de error, en las versiones 1.1.1 y 1.1.2.
2. **Carga, estrés, pico y estabilidad se distinguen y ninguno degrada el servicio** con el perfil del enunciado: el throughput escala con los usuarios, el pico se absorbe y se recupera, y en 15 minutos no hay deriva de tiempos ni de memoria.
3. **La capacidad real está limitada por la numeración serializada de la serie B001**, una regla de negocio deliberada (HU-16). MEJ-01 reduce el tramo bloqueado. Lo que queda es el COMMIT a disco.
4. **Ese límite está muy por encima de la necesidad del local** (3 PC): incluso la versión 1.1.1 emitiría unas 200 boletas por segundo.

## 8. Limitaciones

- En la línea base no se midió la CPU de JMeter: el comodín `java*` de typeperf se resolvió antes de que arrancara JMeter. El monitor se corrigió (seguimiento por PID) y se usó en el diagnóstico (JMeter: 3 % de media y 12 % como máximo con 50 hilos sin pausas).
- La estabilidad de 15 minutos solo permite conclusiones sobre ese intervalo.
- El conjunto de datos (3 000 productos, 200 clientes) es sintético, con la forma del catálogo real; la base se reinicia sin comprobantes en cada escenario, así que no mide el efecto de un historial de años.
