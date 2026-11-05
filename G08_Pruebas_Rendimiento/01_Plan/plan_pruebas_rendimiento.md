# Plan de pruebas de rendimiento — G08

| Campo | Valor |
|---|---|
| Producto | Sistema Logístico Cóndor, backend REST `Condor.Api`: **1.1.1** (línea base, SVN r22) y **1.1.2** (después de la mejora MEJ-01, SVN r25) |
| Requisito verificado | **RNF-02**: consultar productos y emitir boleta con **p95 ≤ 2 s** y **error ≤ 1 %**, con 10 usuarios concurrentes durante 5 min (criterio CA-RNF-02.1) |
| Requisitos relacionados | RF-05 Buscar producto (HU-02), RF-07 Emitir comprobante (HU-05); CC-01 (ingreso con JWT y roles, ruta REST evaluable con JMeter) |
| Riesgo relacionado (G06) | Dimensión [D] disponibilidad del activo A07 PC principal (escenarios R06 y R08): la PC principal es el único servidor de la API y de la base, así que su capacidad limita la venta de las tres PC |
| Herramienta | Apache JMeter 5.6.3 en modo no gráfico (`-n`); monitoreo con typeperf (Monitor de rendimiento de Windows) y `docker stats` + `pg_stat_activity` |
| Base de datos | `condor_rendimiento` (dedicada a G08; no se usa la base del local ni `condor_pruebas`) |
| Responsables (RACI de G01) | **A**, R: Condo Z., R. A. (líder de G08: plan, scripts y ejecución) · R: Chaisa F., A. L. (monitoreo y análisis) · C: Huamani C., J. S. y Payehuanca R., J. J. · C: docente (acuerda el perfil) |

## 1. Transacciones críticas

| ID | Transacción | Petición | Respuesta correcta (validación) |
|---|---|---|---|
| T1 | Consultar productos (búsqueda del mostrador, HU-02) | `GET /api/productos?texto=${texto}&limite=20` | HTTP **200** y JSON Assertion `$[0].id` (al menos un producto) |
| T2 | Registrar boleta (emisión, HU-05) | `POST /api/comprobantes` con `{"tipo","documentoCliente","detalle":[...]}` | HTTP **201** y JSON Assertion `$.numero` (boleta numerada en la serie B001) |
| 00 | Ingreso (solo preparación; no cuenta para RNF-02) | `POST /api/auth/login` | HTTP **200**; JSON Extractor `$.token` → `Authorization: Bearer ${token}` |

**Mezcla de operaciones:** en cada iteración se sortea un número de 1 a 100: si es ≤ 70 se hace T1 y, si no, T2. Resultado: **70 % consulta / 30 % registro** (la mezcla sugerida en `docs/api.md`: un vendedor busca varias veces por cada venta).

**Autenticación:** cada hilo representa a un vendedor que ingresa **una sola vez** (Once Only Controller), como en el turno real. El ingreso no va dentro del bucle porque la clave se verifica con PBKDF2 de 100 000 iteraciones, un costo deliberado que no forma parte de la operación de venta.

**Tiempos de espera (think time):** antes de cada transacción, Uniform Random Timer de **1 a 3 s** (1 000 ms + aleatorio 0–2 000 ms), el tiempo que tarda el vendedor en escribir o elegir. Tiempos máximos del cliente HTTP: conexión **5 s**, respuesta **10 s**.

## 2. Datos de prueba

| Archivo | Contenido | Uso |
|---|---|---|
| `03_Datos/preparar_bd_rendimiento.sql` | 3 000 productos (tamaño de catálogo de RNF-01), 200 clientes con DNI, 10 vendedores `carga01`–`carga10` | Conjunto de datos fijo de la base |
| `03_Datos/reiniciar_ventas.sql` | Borra comprobantes y pone las series en 0 | Antes de **cada** escenario, para que todos partan del mismo estado |
| `03_Datos/usuarios.csv` | 12 vendedores (`carga01`–`carga10`, `vendedor1`, `vendedor2`) | Un vendedor por hilo (compartido por todos los grupos, reciclado) |
| `03_Datos/consultas.csv` | 50 textos de búsqueda de 3 a 12 letras, con y sin tildes; todos encuentran productos | T1 |
| `03_Datos/ventas.csv` | 600 boletas de 1 a 3 líneas; 80 % boleta simple y 20 % boleta con DNI | T2 |

`03_Datos/generar_datos.py` genera los CSV con semilla fija. El total máximo de una boleta es 3 × 3 × S/ 59,99 = S/ 539,91 < S/ 700, así que ninguna boleta simple exige DNI: un 400 en T2 es un error real, no un dato mal armado.

No hay servicios externos simulados: la emisión **no** llama a la SUNAT (sin la sección `Sunat` en la configuración las boletas quedan `PENDIENTE`, igual que en el local sin internet).

## 3. Escenarios (perfil académico del enunciado)

Todos los tiempos se cuentan desde el arranque del escenario. Cada grupo de hilos es un *Thread Group* con planificador; los que no usa el escenario quedan con 0 hilos.

| Escenario | Grupos de hilos | Transiciones exactas | Duración |
|---|---|---|---|
| **Carga esperada** | 10 hilos, rampa 30 s | 0:00–0:30 rampa de 0 a 10 · **0:30–5:30 10 usuarios** | 5:30 (300 s estables) |
| **Estrés escalonado** | E1: 10 hilos, rampa 30 s, 0:00–9:30 · E2: +15, retraso 210 s, rampa 10 s · E3: +25, retraso 390 s, rampa 10 s | **0:30–3:30 10 u** · 3:30–3:40 sube a 25 · **3:40–6:30 25 u** · 6:30–6:40 sube a 50 · **6:40–9:30 50 u** | 9:30 (3 min por nivel) |
| **Pico** | Base: 10 hilos, rampa 30 s, 0:00–7:00 · Ráfaga: +40, retraso 180 s, rampa 10 s, duración 70 s | 0:30–3:00 10 u · **3:00–3:10 sube de 10 a 50** · 3:10–4:10 50 u · **4:10 vuelve a 10** · 4:10–7:00 10 u | 7:00 |
| **Estabilidad** | 10 hilos, rampa 30 s | 0:00–0:30 rampa · **0:30–15:30 10 usuarios** | 15:30 (900 s estables) |

Los niveles de estrés se analizan por ventana de tiempo (columna `allThreads` y `timeStamp` del .jtl). Una ejecución de 15 min de estabilidad solo permite concluir sobre ese intervalo (no sobre fugas de memoria de horas o días).

**Perfil acordado:** se usa el perfil inicial del enunciado sin cambios; el equipo de pruebas lo soporta (ver entorno). Queda sujeto a validación del docente.

**Diagnóstico de capacidad (adicional; no es uno de los cuatro escenarios).** Con usuarios con pausas no se satura ningún recurso. Para localizar el cuello de botella se agregó el grupo *Capacidad (sin pausas, diagnóstico)*: el mismo flujo 70/30 con `pausa.min=0` y `pausa.rango=0`, con 10, 25, 50 y 100 hilos, rampa de 10 s y 2 min por nivel, arrancando la API de nuevo antes de cada nivel (`02_Scripts/capacidad.ps1`). En cada nivel se mide el throughput, el p95 y las conexiones que esperan un bloqueo en PostgreSQL. Se ejecuta antes y después de la mejora.

## 4. Criterios de aceptación y definición de error

| Criterio | Umbral | Dónde se mide |
|---|---|---|
| p95 de T1 y de T2, **por transacción**, en carga esperada | **≤ 2 000 ms** | Dashboard HTML (Statistics, 95th pct) y `06_Analisis` |
| Tasa de error de T1 y de T2 en carga esperada | **≤ 1 %** | Dashboard HTML (Errors) |
| Estrés, pico y estabilidad | Sin umbral de aprobación: se informa el nivel en que el p95 supera 2 s o aparecen errores, y la recuperación tras el pico | `06_Analisis` |

**Se cuenta como error** toda muestra con: código HTTP distinto del esperado (200 en T1, 201 en T2), un 4xx inesperado (400 de validación, 401 token rechazado, 409), cualquier 5xx (503 base caída), respuesta sin el campo validado (`$[0].id` o `$.numero`), o tiempo de espera superado (conexión > 5 s o respuesta > 10 s). Un tiempo entre 2 y 10 s **no** es error: afecta el p95.

APDEX del reporte: satisfecho ≤ 500 ms, tolerado ≤ 2 000 ms (el umbral de RNF-02).

## 5. Entorno de prueba

| Elemento | Valor |
|---|---|
| Equipo | ASUS ROG Strix G614JV (portátil) |
| Procesador | Intel Core i7-13650HX, 14 núcleos / 20 hilos lógicos |
| Memoria | 15,6 GB (Docker Desktop limitado a 7,6 GB) |
| Sistema operativo | Windows 11 Home 10.0.26300 |
| Red | Bucle local: JMeter, `Condor.Api` y PostgreSQL en el mismo equipo |
| Base de datos | PostgreSQL 16.15 en Docker 29.7.2 (contenedor `Cas_condor`, puerto 5433), base `condor_rendimiento` |
| Tamaño del conjunto de datos | 3 000 productos, 200 clientes, 13 usuarios; 0 comprobantes al inicio de cada escenario |
| Producto | `Condor.Api` 1.1.1 publicado por `ejecutar.ps1` (`.ejecutar/api/CondorApi.exe`, autocontenido win-x64, Release). El ensamblado informa 1.1.0 en `/api/salud` porque el `.csproj` no se actualizó al integrar DEF-01 (observación) |
| Configuración de la API | `BaseDatos:MaxConexiones` = 20 (pool de Npgsql) en la línea base; registro `Microsoft.AspNetCore` en Warning |
| Generador de carga | Apache JMeter 5.6.3, Java 26.0.2.1, modo no gráfico, montículo por omisión de `jmeter.bat` (1 GB), HttpClient4 con keep-alive, sin listeners activos |
| Monitoreo | typeperf cada 2 s (CPU total, memoria disponible, CPU/memoria/hilos de CondorApi); proceso java de JMeter por PID cada 2 s; `docker stats` + `pg_stat_activity` cada 5 s |

Cada ejecución guarda su `entorno.json` con los valores medidos en ese momento.

## 6. Procedimiento

```powershell
# 1. Base y API (una vez; vuelve a cargar los datos)
..\Sistema_Logistico_Condor_final\ejecutar.ps1 -Api      # solo si Cas_condor o CondorApi.exe no existen
.\02_Scripts\preparar_entorno.ps1                         # condor_rendimiento + API con pool de 20
# 2. Línea base: los cuatro escenarios
.\02_Scripts\ejecutar_todos.ps1 -Fase 1_antes
# 3. Análisis
python 06_Analisis\analizar_resultados.py
# 4. Diagnóstico de capacidad (localiza el cuello de botella)
.\02_Scripts\capacidad.ps1 -Fase 1_antes
# 5. Mejora MEJ-01 (05_Cuello_de_Botella) y repetición con las mismas condiciones
$api = '..\..\Sistema_Logistico_Condor_final\.ejecutar\api_1.1.2'
.\02_Scripts\preparar_entorno.ps1 -CarpetaApi $api
.\02_Scripts\ejecutar_todos.ps1 -Fase 2_despues
.\02_Scripts\capacidad.ps1 -Fase 2_despues -CarpetaApi $api
# 6. Análisis y capturas de los dashboards
python 06_Analisis\analizar_resultados.py
python 06_Analisis\capturar_evidencias.py
```

Un escenario suelto: `.\02_Scripts\ejecutar_escenario.ps1 -Escenario estres -Fase 1_antes`. Para revisar el plan en la GUI: `jmeter.bat -t 02_Scripts\condor_rendimiento.jmx` (los listeners están deshabilitados y solo sirven para depurar en la GUI).

## 7. Condiciones equivalentes antes y después

Mismo equipo, mismo plan `.jmx`, mismos CSV, misma base reiniciada con `reiniciar_ventas.sql`, la API recién arrancada, el mismo pool (20 conexiones) y una pausa de 30 s entre escenarios. Solo cambia la mejora aplicada (versión 1.1.2 en `.ejecutar/api_1.1.2`). Después de la línea base, el `.jmx` cambió en dos cosas: la pausa pasó a leerse de las propiedades `pausa.min` y `pausa.rango` (con los mismos valores por omisión, 1 000 y 2 000 ms) y se agregó el grupo de capacidad (0 hilos salvo en el diagnóstico). Con eso los cuatro escenarios no cambian.
