# MEJ-01 — Reservar el correlativo de la serie al final de la emisión

| Campo | Contenido |
|---|---|
| ID | **MEJ-01** (mejora de rendimiento hallada en G08) |
| Registra | Condo Z., R. A. (líder de G08), 2026-11-01 |
| Análisis de impacto | Payehuanca R., J. J. (comité de cambios) |
| Decisión | **Aprobada** por el Gerente general (representado) |
| Implementa | Condo Z., R. A. — rama `branches/MEJ-01-correlativo-al-final` (r23 creación, r24 cambio) |
| Integra | Payehuanca R., J. J. — trunk **r25** |
| Verifica | Chaisa F., A. L. (repetición de G08) |
| Versión afectada | 1.1.1 → **1.1.2** (`Sistema_Logistico_Condor_final/CHANGELOG.md`) |
| Requisitos vinculados | RNF-02 (capacidad de la API), RF-07 (emitir comprobante, regla de numeración de HU-16) |

## 1. Cómo se localizó el cuello de botella

Con el perfil del enunciado (usuarios con pausas de 1–3 s), la API trabajó muy por debajo de su capacidad: con 50 usuarios el p95 de T2 fue de 19–20 ms y el pool tuvo como máximo 9 conexiones abiertas. Para encontrar el límite se agregó un **diagnóstico de capacidad**: el mismo flujo (70 % T1, 30 % T2) sin pausas, con 10, 25, 50 y 100 hilos, 2 min por nivel y la API recién arrancada (`02_Scripts/capacidad.ps1`). No sustituye a los cuatro escenarios del perfil: sirve para ubicar el recurso que se satura primero.

Resultado de la línea base (1.1.1, `04_Resultados/1_antes/capacidad_*`):

| Hilos sin pausas | T1 p95 | T2 p95 | T2 throughput | Conexiones API (máx) | Activas | **Esperando un bloqueo** | CPU total media |
|---|---|---|---|---|---|---|---|
| 10 | 7 ms | 46 ms | 267/s | 11 | 7 | 6 | 42 % |
| 25 | 10 ms | 225 ms | 247/s | 21 | 20 | **19** | 45 % |
| 50 | 64 ms | 356 ms | 208/s | 21 | 20 | **19** | 48 % |
| 100 | 104 ms | 404 ms | 236/s | 21 | 20 | **19** | 48 % |

Lectura de los datos:

1. **T2 deja de crecer en ~210–270 boletas/s** desde 10 hilos, aunque se dupliquen los hilos: está serializada.
2. **19 de las 20 conexiones del pool esperan un bloqueo de fila** (`pg_stat_activity.wait_event_type = 'Lock'`). La única fila que comparten todas las boletas es la de la serie **B001** (`UPDATE serie ... RETURNING`, regla de HU-16: ningún número repetido ni saltado).
3. **La CPU no es el límite**: el equipo queda por debajo del 50 % de media, PostgreSQL usa ~5 % y CondorApi ~4–5 %.
4. **T1 también se degrada (p95 de 10 a 64 ms) aunque no bloquea nada**: las boletas que esperan ocupan las conexiones del pool y las consultas esperan una conexión libre.

**Causa localizada:** en 1.1.1, `ComprobanteRepositorio.EmitirAsync` toma el número de la serie **al inicio** de la transacción. La fila de B001 queda bloqueada mientras se inserta la cabecera, se insertan las líneas y se confirma (3 viajes a la base + COMMIT). Con 208 boletas/s, cada emisión retiene la serie unos 4,8 ms.

## 2. Mejora aplicada

El número se toma **al final**, justo antes del COMMIT:

1. `INSERT` de la cabecera con un número **provisional negativo** (`-id`, obtenido con `nextval`). Nadie lo ve, porque la transacción no está confirmada, y no choca con la restricción única `(serie_id, numero)`.
2. `INSERT` de las líneas en un solo lote (igual que antes).
3. `SerieRepositorio.NumerarComprobanteAsync`: una sola sentencia (`WITH s AS (UPDATE serie ... RETURNING) UPDATE comprobante SET numero = ...`) incrementa la serie y pone el número definitivo.
4. `COMMIT`.

El bloqueo de la serie pasa de durar *3 sentencias + COMMIT* a *1 sentencia + COMMIT*. Se mantienen las reglas de HU-16: ningún número repetido ni saltado, y un error deshace también el número. El cambio no toca el esquema, la API ni las pantallas. Archivos: `src/Condor.Datos/ComprobanteRepositorio.cs` y `src/Condor.Datos/SerieRepositorio.cs`.

**Alternativas evaluadas:**

| Alternativa | Por qué no se eligió |
|---|---|
| Subir `MaxConexiones` de 20 a 60 | T1 dejaría de esperar conexión, pero T2 seguiría serializada: más conexiones esperando el mismo bloqueo |
| Secuencia de PostgreSQL para el número | Una secuencia no se deshace con ROLLBACK: dejaría números saltados, prohibido por la regla de la SUNAT (HU-16) |
| Una serie por terminal (B001, B002, B003) | Elimina la contención, pero cambia un requisito (series de la SUNAT y numeración del local): necesita una solicitud de cambio propia. Queda como acción pendiente |
| `synchronous_commit = off` | Un apagón podría perder boletas ya numeradas y entregadas. No es aceptable para comprobantes; solo se usó como **diagnóstico** (sección 4) |

**Análisis de impacto:** costo 6 h × S/ 25,00 = S/ 150,00 (código 2 h, pruebas 2 h, repetición de G08 2 h). Plazo: 1 día con 1 integrante, sin mover hitos. El riesgo principal, romper la regla de numeración, se mitiga con las pruebas de la sección 3.

## 3. Pruebas del cambio

| Prueba | Resultado |
|---|---|
| `tests/Condor.Pruebas/Datos/MEJ01_CorrelativoAlFinalTests` (nuevas): tres PC emitiendo a la vez con el repositorio real (90 boletas, números 1–90), una emisión fallida que no consume número ni deja el provisional, y comprobación de que la serie solo se bloquea al numerar | 3 de 3 aprobadas |
| Suite completa del producto (incluye `HU16_ConcurrenciaTests` y las de emisión) | **933 aprobadas, 0 fallidas, 5 omitidas** (`suite_producto_1.1.2/suite_producto_1.1.2.trx`) |
| Repetición de los cuatro escenarios de G08 y del diagnóstico de capacidad con condiciones equivalentes | Ver la sección 4 |

## 4. Resultado antes y después

Mismo equipo, plan, datos y pool (20). La base se reinicia antes de cada escenario y la API se arranca de nuevo antes de cada nivel de capacidad.

| Hilos sin pausas | T2 p95 antes → después | T2 throughput | T1 p95 | T1 throughput | Esperando bloqueo |
|---|---|---|---|---|---|
| 10 | 46 → 81 ms | 267 → 241/s | 7 → 8 ms | 631 → 559/s | 6 → 9 |
| 25 | 225 → 231 ms | 247 → 261/s | 10 → 10 ms | 574 → 610/s | 19 → 17 |
| **50** | **356 → 290 ms (−19 %)** | **208 → 263/s (+27 %)** | **64 → 40 ms (−38 %)** | 483 → 615/s | 19 → 18 |
| 100 | 404 → 426 ms | 236 → 254/s | 104 → 96 ms | 548 → 593/s | 19 → 18 |

En los cuatro escenarios del perfil (con pausas), antes y después coinciden: p95 de 11–12 ms en T1 y de 20–22 ms en T2, sin errores. Las diferencias de ±1 ms son ruido de medición.

**La mejora es parcial.** Sube el techo de T2 (de ~210–250 a ~250–265 boletas/s) y alivia a T1 con 50 hilos, pero la serie sigue siendo el punto de espera: 17–18 conexiones continúan bloqueadas. Con 10 hilos el p95 de T2 empeoró (46 → 81 ms). Con pocos hilos casi no hay espera por la serie, así que acortar el bloqueo no aporta; en cambio, la segunda sentencia (`UPDATE comprobante`) agrega un viaje a la base en cada emisión.

**Diagnóstico de la causa restante** (`04_Resultados/3_diagnostico_synchronous_commit_off/capacidad_50u`). Se repitió el nivel de 50 hilos con `ALTER DATABASE condor_rendimiento SET synchronous_commit = off`, que hace que el COMMIT no espere la escritura del WAL a disco. Se revirtió al terminar (`SHOW synchronous_commit` = `on`).

| 50 hilos sin pausas | 1.1.1 | 1.1.2 | 1.1.2 + COMMIT sin espera (solo diagnóstico) |
|---|---|---|---|
| T2 p95 | 356 ms | 290 ms | **78 ms** |
| T2 throughput | 208/s | 263/s | **466/s** |
| T1 p95 / throughput | 64 ms / 483/s | 40 ms / 615/s | 56 ms / 1 086/s |
| Esperando bloqueo (máx) | 19 | 18 | 13 |
| CPU total media / máx | 48 / 72 % | 56 / 90 % | **89 / 99 %** |

Si el COMMIT no espera el disco, T2 casi se duplica y el límite pasa a ser la **CPU del equipo**, que comparten JMeter, la API, PostgreSQL y Docker. Conclusión: lo que queda de la retención de la serie es, sobre todo, **la escritura del WAL del COMMIT**. Esa escritura no se puede sacar del bloqueo sin perder la garantía de "ni repetidos ni saltados".

## 5. Acciones pendientes

| Acción | Efecto esperado | Responsable propuesto |
|---|---|---|
| Poner el WAL de PostgreSQL en un disco de baja latencia (SSD NVMe) en la PC principal | Escritura del WAL más rápida, que es el tramo que hoy retiene la serie | Condo Z., R. A. |
| Solicitud de cambio: una serie de boletas por terminal (B001, B002, B003) | Las tres PC dejan de esperarse entre sí; requiere aprobar el cambio de numeración | Payehuanca R., J. J. (CCB) |
| Separar el pool de consultas del de emisión, o subir `MaxConexiones` | T1 no espera conexión aunque T2 se encole | Huamani C., J. S. |
| `commit_delay` / `commit_siblings` de PostgreSQL (agrupar las escrituras del WAL de varios COMMIT) | Más boletas por cada escritura a disco, sin perder durabilidad | Chaisa F., A. L. |

**Proporción con la necesidad real:** el local tiene 3 PC. Incluso el techo de la versión 1.1.1 (~210 boletas por segundo) supera en varios órdenes de magnitud la venta real de una ferretería, y RNF-02 se cumple con mucha holgura. La mejora y las acciones pendientes amplían el margen; no corrigen un incumplimiento.
