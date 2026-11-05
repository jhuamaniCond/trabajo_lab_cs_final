# Cuestionario de la Guía 9 aplicado al producto

## a) ¿Cuál es la técnica de diseño de prueba más utilizada? ¿Por qué?

La más utilizada es la **partición de equivalencia** junto con el **análisis de valores límite**, ambas de caja negra. Son las más comunes porque no exigen conocer el código, reducen un dominio infinito de entradas a pocas clases representativas y encuentran los errores donde más se concentran: en los bordes de las reglas.

Así se usaron en la suite de Cóndor:

| Técnica | Aplicación en G09 |
|---|---|
| Partición de equivalencia | Documento: DNI de 8 dígitos y RUC de 11 válidos, frente a corto, no registrado o RUC con dígito errado (CP-04, CP-05, CP-08). Credenciales: válidas, clave errada, usuario inexistente o vacías (CP-01, CP-02) |
| Valores límite | Cantidad 0 (CP-05); boleta de más de S/ 700 sin DNI (CP-09); período de más de 366 días (CP-12); fecha de compra futura (CP-13) |
| Tabla de decisión | Tipo de comprobante × cliente: Boleta, Con DNI, Factura con y sin RUC (CP-07 a CP-09) |
| Transición de estados | Proforma VIGENTE → CONVERTIDA, y nueva conversión rechazada (CP-10) |
| Casos de uso (escenarios) | Los tres procesos completos: PN-01 en CP-07, PN-02 en CP-10 y PN-03 en CP-13 |

En una prueba de aceptación automatizada la **técnica basada en casos de uso** marca la estructura: cada caso de Selenium sigue un escenario del usuario. Las particiones y los límites eligen los datos de cada escenario.

## b) Variables de configuración de Selenium para una aplicación simple

Son las de `02_Suite/config.ini` y `comun.crear_driver()`:

| Variable | Valor en Cóndor | Para qué |
|---|---|---|
| URL base | `http://localhost:5080/` (`CONDOR_URL`) | Dónde está la aplicación bajo prueba |
| Navegador | `chrome` o `edge` (`CONDOR_NAVEGADOR`) | Qué `webdriver.*` se crea |
| Controlador | Lo resuelve Selenium Manager (sin `executable_path`) | Compatibilidad entre controlador y navegador |
| Modo headless | `--headless=new` (`CONDOR_HEADLESS=1`); `--ventana` para verlo | Regresión sin pantalla o depuración visual |
| Tamaño de ventana | `--window-size=1440,900` | Diseño estable; evita elementos fuera de la vista |
| Idioma | `--lang=es-PE` e `intl.accept_languages` | Fechas y textos como los ve el usuario de Majes |
| Espera explícita | `WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,))` | Sincronizar con la aplicación sin `sleep` |
| Tiempo de carga de página | `set_page_load_timeout(30)` | No colgar la suite si el servidor no responde |
| Carpeta de evidencias | `CONDOR_CARPETA_EJECUCION` (la fija el ejecutor) | Dónde van las capturas y los reportes |
| Credenciales y datos | `datos.py` | Usuarios de prueba y datos aislados por ejecución |

## c) Un inconveniente de Selenium y su solución

Se presentaron tres en el producto:

1. **Sincronización con contenido dinámico.** El portal vuelve a pintar las tablas con JavaScript. Una referencia a un elemento viejo produce `StaleElementReferenceException`, y CP-10 falló de forma intermitente (DEF-06).
   - **Solución:** esperas explícitas que reintentan y que ignoran ese error (`ignored_exceptions`). Se vuelve a buscar el elemento en cada intento, sin `time.sleep` ni `implicitly_wait`; la guía Selenium desaconseja mezclar los dos tipos de espera.
   - **Resultado:** cuatro ejecuciones seguidas sin fallos.
2. **Selenium solo automatiza navegadores.** La app del cliente es de escritorio (WPF) y no había nada que automatizar.
   - **Solución:** CC-03, un portal web con los mismos `id` (AutomationId) que la app.
   - La alternativa era Appium con WinAppDriver, que se descartó porque no se mantiene.
3. **Versión del controlador.** En los ejercicios originales del repositorio de la guía el chromedriver se fijaba con una ruta, y deja de funcionar cuando Chrome se actualiza (Chrome 156 en este equipo).
   - **Solución:** **Selenium Manager** (Selenium 4.6 o superior), que descarga el controlador que corresponde. Así la suite corrió en Chrome y Edge sin tocar el código.

Un inconveniente que la automatización **no** resuelve sola: las aserciones solo comprueban lo que se les pidió. La primera ejecución pasó 14/14 con dos defectos visibles en las capturas (DEF-03 y DEF-04). Se encontraron al revisar las evidencias y entonces se agregaron las aserciones. Por eso el dictamen se apoya en reportes **y** en capturas.
