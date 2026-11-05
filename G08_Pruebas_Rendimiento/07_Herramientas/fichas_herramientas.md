# Fichas de herramientas — G08

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## Apache JMeter (generador de carga)

| Campo | Contenido |
|---|---|
| Versión exacta | **Apache JMeter 5.6.3** (la misma instalación del Lab 8: `Lab/8/apache-jmeter-5.6.3`) |
| Finalidad | Ejecutar los cuatro escenarios (carga, estrés, pico y estabilidad) sobre `Condor.Api` y generar el `.jtl` y el reporte HTML (dashboard) |
| Requisitos de instalación | Java 8 o superior en el PATH; descomprimir el `.zip` binario. Se ejecutó con **Java 26.0.2.1** (HotSpot 64 bits) |
| Procedencia | https://jmeter.apache.org/download_jmeter.cgi (`apache-jmeter-5.6.3.zip`) |
| Licencia | Apache License 2.0 |
| Configuración | Plan `02_Scripts/condor_rendimiento.jmx` (lo genera `generar_plan.py`). Elementos usados, todos del núcleo de JMeter (sin plugins): Thread Group con planificador, Once Only Controller, If Controller, HTTP Request (HttpClient4, keep-alive), HTTP Request Defaults (conexión 5 s, respuesta 10 s), HTTP Header Manager, CSV Data Set Config, JSON Extractor, Response Assertion, JSON Assertion, Uniform Random Timer. Listeners deshabilitados (buena práctica para el modo no gráfico). Reporte: APDEX 500/2 000 ms, granularidad 10 s |
| Ejecución | `02_Scripts/ejecutar_escenario.ps1 -Escenario <carga\|estres\|pico\|estabilidad> -Fase <1_antes\|2_despues>`, que llama a `jmeter.bat -n -t condor_rendimiento.jmx -J... -l resultado.jtl -j jmeter.log -e -o dashboard`. Ruta de JMeter: parámetro `-JMeter` o variable `JMETER_HOME` |
| Archivos generados | `04_Resultados/<fase>/<escenario>/resultado.jtl` (CSV por muestra), `jmeter.log`, `dashboard/index.html` |

## typeperf — Monitor de rendimiento de Windows (monitoreo de CPU y memoria)

| Campo | Contenido |
|---|---|
| Versión exacta | `typeperf.exe` de **Windows 11 Home 10.0.26300** (contadores PDH del sistema) |
| Finalidad | Medir, cada 2 s, la CPU total, la memoria disponible y la CPU, memoria privada e hilos de los procesos `CondorApi` y `java` (JMeter) |
| Requisitos | Incluido en Windows; no requiere instalación ni permisos de administrador |
| Procedencia | Microsoft — https://learn.microsoft.com/windows-server/administration/windows-commands/typeperf |
| Licencia | Parte de Windows |
| Configuración | Contadores `\Processor(_Total)\% Processor Time`, `\Memory\Available MBytes`, `\Process(CondorApi)\% Processor Time`, `\Process(CondorApi)\Working Set - Private`, `\Process(CondorApi)\Thread Count`, `\Process(java*)\...`; `-si 2 -f CSV`. El `%` por proceso es de un núcleo: el análisis lo divide entre 20 hilos lógicos |
| Ejecución | Automática dentro de `ejecutar_escenario.ps1` |
| Archivos generados | `monitoreo_windows.csv` en cada carpeta de resultado |

## docker stats y pg_stat_activity (monitoreo de PostgreSQL)

| Campo | Contenido |
|---|---|
| Versión exacta | **Docker Desktop 29.7.2** (`docker stats`); **PostgreSQL 16.15** (vista `pg_stat_activity`) |
| Finalidad | Cada 5 s: CPU y memoria del contenedor `Cas_condor` y conexiones de la API a `condor_rendimiento` (total, activas y en espera de un bloqueo). Sirve para ver si el pool de conexiones o el bloqueo de la serie B001 limitan |
| Requisitos | Docker Desktop con WSL 2; el contenedor `Cas_condor` de `ejecutar.ps1` |
| Procedencia | https://www.docker.com/products/docker-desktop/ · https://www.postgresql.org/docs/16/monitoring-stats.html |
| Licencia | Docker Desktop: suscripción gratuita para uso educativo y personal · PostgreSQL: licencia PostgreSQL |
| Configuración | Consulta `SELECT count(*), count(*) FILTER (WHERE state='active'), count(*) FILTER (WHERE wait_event_type='Lock') FROM pg_stat_activity WHERE datname='condor_rendimiento' AND application_name LIKE 'Condor%'` |
| Ejecución | Trabajo en segundo plano de `ejecutar_escenario.ps1` |
| Archivos generados | `monitoreo_postgres.csv` en cada carpeta de resultado |

## Condor.Api y base de pruebas (sistema bajo prueba)

| Campo | Contenido |
|---|---|
| Versión exacta | Sistema Logístico Cóndor **1.1.1** (`CondorApi.exe` autocontenido win-x64 Release, publicado por `ejecutar.ps1`); PostgreSQL 16.15 en el contenedor `Cas_condor` |
| Finalidad | Rutas `POST /api/auth/login`, `GET /api/productos` (T1) y `POST /api/comprobantes` (T2) |
| Configuración | `02_Scripts/preparar_entorno.ps1`: base dedicada `condor_rendimiento`, variables `BaseDatos__*` y `BaseDatos__MaxConexiones`; datos de `03_Datos/preparar_bd_rendimiento.sql` |
| Archivos generados | `02_Scripts/entorno_actual.json`, copiado como `entorno.json` a cada resultado |

## Python, matplotlib y openpyxl (análisis)

| Campo | Contenido |
|---|---|
| Versión exacta | Python **3.12.0**, matplotlib **3.11.2**, openpyxl **3.1.5** |
| Finalidad | `06_Analisis/analizar_resultados.py`: percentiles por transacción y por ventana (niveles de estrés, fases del pico, minuto a minuto en estabilidad), resumen del monitoreo, comparación antes/después; `03_Datos/generar_datos.py` y `02_Scripts/generar_plan.py` |
| Requisitos | `pip install matplotlib openpyxl` |
| Procedencia | https://www.python.org · https://matplotlib.org · https://pypi.org/project/openpyxl/ |
| Licencia | PSF · matplotlib (licencia PSF-compatible) · MIT |
| Archivos generados | `06_Analisis/resumen_resultados.xlsx`, `06_Analisis/graficas/*.png` |

## Comparación con alternativas

| Criterio | JMeter 5.6.3 (elegido) | Gatling 3 | k6 | Locust |
|---|---|---|---|---|
| Lo exige la guía / el enunciado | Sí | No | No | No |
| Definición del plan | `.jmx` (XML) editable en GUI | Código Scala/Java/Kotlin | JavaScript | Python |
| Modo no gráfico y reporte HTML | `-n -e -o`, dashboard incluido | Reporte HTML incluido | Resumen en consola; HTML con extensión | Interfaz web; CSV |
| Perfiles escalonados y pico | Varios Thread Group con retraso (núcleo) o plugins | Inyección abierta/cerrada nativa | `stages` nativos | `LoadTestShape` |
| Monitoreo del servidor | Requiere herramienta aparte (aquí typeperf) o plugin PerfMon | Aparte | Aparte | Aparte |
| Motivo | Herramienta de la guía PRAC08 y del Lab 8; el docente pide conservar JMeter | — | — | — |
