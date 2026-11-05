# Fichas de herramientas — G09

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## Selenium WebDriver (cliente Python)

| Campo | Contenido |
|---|---|
| Versión exacta | **selenium 4.52.0** para Python (`pip show selenium`); la misma instalación del Lab 9 |
| Finalidad | Manejar el navegador como un usuario: escribir, pulsar, leer textos y tomar capturas del portal web de Cóndor (CC-03) |
| Requisitos de instalación | Python 3.8 o superior; `pip install -r 02_Suite/requirements.txt` |
| Procedencia | https://pypi.org/project/selenium/ · documentación https://www.selenium.dev/documentation/webdriver/ |
| Licencia | Apache License 2.0 |
| Configuración | `02_Suite/config.ini`: URL, navegador, headless, tamaño de ventana (1440 × 900), espera explícita de 10 s y umbrales de RNF-01 y RNF-06. Opciones del navegador en `comun.crear_driver()`: `--headless=new`, `--lang=es-PE`, preferencia `intl.accept_languages` |
| Ejecución | `02_Suite/ejecutar_suite.ps1 -Etiqueta <versión>_<motivo> [-Navegador edge] [-Ventana]` o `python ejecutar_suite.py --etiqueta …` |
| Archivos generados | `04_Reportes/<fecha>_<etiqueta>/`: `reporte.html`, `resultados.xml` (JUnit), `resultados.json`, `ejecucion.log`, `entorno.json`, `capturas/*.png` |

## Selenium Manager (gestión del controlador)

| Campo | Contenido |
|---|---|
| Versión exacta | La que viene con selenium 4.52.0 (binario `selenium-manager`); resolvió **chromedriver 156.0.8078.80** y **msedgedriver 156.0.4314.58** (ver `entorno.json`) |
| Finalidad | Encontrar o descargar el controlador que corresponde a la versión del navegador, sin rutas fijas en el código. En el repositorio del Lab 9 el controlador se pasaba con `executable_path` |
| Requisitos | Ninguno aparte de Selenium 4.6 o superior; internet la primera vez (guarda el controlador en `%USERPROFILE%\.cache\selenium`) |
| Procedencia | https://www.selenium.dev/documentation/selenium_manager/ |
| Licencia | Apache License 2.0 |
| Configuración | Ninguna: `webdriver.Chrome(options=…)` o `webdriver.Edge(options=…)` sin `Service` |
| Ejecución | Automática al crear el driver |
| Archivos generados | Caché de controladores en `%USERPROFILE%\.cache\selenium` |

## Navegadores

| Campo | Google Chrome | Microsoft Edge |
|---|---|---|
| Versión exacta | **156.0.8078.80** | **156.0.4314.58** |
| Finalidad | Navegador principal de la regresión | Segundo navegador para comprobar que la suite y el portal no dependen de Chrome |
| Procedencia | https://www.google.com/chrome/ | Incluido en Windows 11 |
| Licencia | Propietaria gratuita (Chromium: BSD) | Propietaria gratuita |
| Ejecución | `-Navegador chrome` (por defecto) | `-Navegador edge` (`CONDOR_NAVEGADOR=edge`) |

## Python y unittest (marco y ejecutor)

| Campo | Contenido |
|---|---|
| Versión exacta | **Python 3.12.0** (CPython, 64 bits); `unittest` de la biblioteca estándar |
| Finalidad | Estructurar los casos (`TestCase`, `setUp`, `tearDown`), las aserciones y la ejecución, como en los ejercicios del Lab 9 (EJ3, EJ9) |
| Requisitos | Python en el PATH |
| Procedencia | https://www.python.org/downloads/release/python-3120/ |
| Licencia | PSF License |
| Configuración | `PruebaWeb(unittest.TestCase)` en `comun.py`: navegador por caso, captura del fallo en `_callTestMethod` y evidencias. `Resultado(TextTestResult)` en `ejecutar_suite.py` guarda estado, duración, mediciones y capturas |
| Ejecución | `python ejecutar_suite.py …` o `python -m unittest test_03_venta -v` |
| Archivos generados | Los de Selenium (arriba). El formato JUnit XML lo escribe el propio ejecutor, sin dependencias extra |

## Producto bajo prueba

| Campo | Contenido |
|---|---|
| Versión exacta | **Sistema Cóndor 1.2.0**, `CondorApi.exe` publicado desde trunk r32 (`GET /api/salud` → `"version":"1.2.0"`) |
| Arranque | `Sistema_Logistico_Condor_final\ejecutar.ps1 -Api`: PostgreSQL 16 en Docker (`Cas_condor`), compilación en Docker (`mcr.microsoft.com/dotnet/sdk:8.0`) y API en http://localhost:5080 |
| Suite del producto | xUnit con `dotnet test` en el contenedor del SDK y `CONDOR_TEST_CONN` hacia `condor_pruebas` (ver `04_Reportes/xunit_1.2.0-r32`) |

## Comparación de herramientas de automatización web

| Criterio | **Selenium WebDriver** (elegido) | Playwright | Cypress | Appium + WinAppDriver (sobre la app WPF) |
|---|---|---|---|---|
| Lo pide la guía | Sí (Guía 9) | No | No | Usa el protocolo WebDriver, pero sin navegador |
| Estándar | W3C WebDriver | Protocolo propio (CDP o el de cada navegador) | Corre dentro del navegador | WebDriver/JSONWP |
| Lenguajes | Python, Java, C#, JS, Ruby | Python, JS/TS, Java, C# | Solo JS/TS | Python, Java, C# |
| Navegadores | Chrome, Edge, Firefox, Safari | Chromium, Firefox, WebKit | Chrome, Edge, Firefox (WebKit experimental) | — (aplicaciones Windows) |
| Esperas | Explícitas (`WebDriverWait`), a cargo del autor | Automáticas | Automáticas | Explícitas |
| Gestión del controlador | Selenium Manager | Descarga sus navegadores | No usa controlador | WinAppDriver 1.2.1 (2020, sin mantenimiento), Modo de desarrollador |
| Continuidad con el curso | Lab 9 en Python con `unittest` | Nueva | Nueva, y en otro lenguaje | Nueva |
| Decisión | **Elegido**: lo exige la guía, el equipo ya lo usó y es multinavegador | Buena alternativa: menos fallos por sincronización, como DEF-06 | Descartado por el lenguaje | Descartado (ver CC-03 §2) |

> Si el docente aceptara automatizar la app WPF, los AutomationId de CC-01 permitirían hacerlo con Appium. El portal se diseñó con los mismos `id` para que los casos puedan trasladarse.
