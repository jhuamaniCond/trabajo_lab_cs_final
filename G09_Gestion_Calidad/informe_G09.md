# G09 · Gestión de calidad con Selenium — Sistema Cóndor

| Campo | Valor |
|---|---|
| Guía | PRAC09 Gestión de Calidad (Selenium) |
| Producto | Sistema de Ventas y Facturación Cóndor **1.2.0**, SVN trunk r32 |
| Herramientas | Selenium WebDriver 4.52.0 (Python 3.12.0, `unittest`), Selenium Manager, Chrome 156.0.8078.80, Edge 156.0.4314.58 |
| Requisitos vinculados | RF-01 a RF-08, RF-11, RF-12, RF-14, RF-15, RNF-01, RNF-03, RNF-06 (verificados en la web); los 24 requisitos en el dictamen |
| Responsables | Suite: Payehuanca R., J. J. · Portal (CC-03): Condo Z., R. A. · Dictamen: Huamani C., J. S. · Verificación: Chaisa F., A. L. |

## I. Objetivo

Automatizar con Selenium WebDriver las pruebas de aceptación y regresión web del producto, en los tres procesos de negocio, y combinar sus resultados con los de requisitos, riesgos, pruebas unitarias y rendimiento en un dictamen de liberación.

## II. Procedimiento realizado

1. **Impedimento y cambio (CC-03).** Cóndor es una app WPF con una API REST; no tenía ninguna página web para Selenium. Se registró la solicitud **CC-03** para agregar un portal web con el aspecto y los `id` de la app, servido por `Condor.Api`.
   - Se aprobó y se desarrolló en `branches/CC-03-portal-web` (r28–r31), y se integró en trunk r32.
   - Se actualizaron la ERS (1.2, INT-07), el SDD (1.1, DD-09) y los diagramas de componentes y despliegue.
   - Documento: `00_Solicitud_Cambio/CC-03_portal_web.md`.
2. **Configuración.**
   - `pip install selenium==4.52.0`.
   - Selenium Manager resuelve chromedriver y msedgedriver sin rutas fijas, a diferencia de los ejercicios del Lab 9.
   - Modo headless para la regresión y `--ventana` para depurar.
   - Fichas en `07_Herramientas`.
3. **Diseño.** El plan está en `01_Plan`. Tiene 14 casos (CP-01 a CP-14) que cubren los ocho casos que pide la guía y los tres procesos: PN-01 en CP-07, PN-02 en CP-10 (cambio de estado) y PN-03 en CP-13. Se aplicaron particiones de equivalencia, valores límite, tabla de decisión y transición de estados.
4. **Automatización.** Está en `02_Suite`:
   - Page Objects con selectores por `id` y esperas explícitas.
   - Datos aislados por ejecución: DNI, RUC con dígito verificador y nombres únicos (`03_Datos`).
   - Captura automática de cada fallo, sin ocultarlo.
   - Reporte HTML, JUnit XML y JSON por ejecución.
5. **Ejecución y defectos.** Se hicieron 10 ejecuciones (`04_Reportes/indice_ejecuciones.md`). Revisar las capturas, no solo las aserciones, permitió hallar defectos del portal (DEF-03, DEF-04) y de la propia suite (DEF-06, DEF-07). Se corrigieron y se repitió la regresión (`05_Defectos`).
6. **Regresión final y dictamen.** Se corrieron xUnit y Selenium sobre trunk r32 y se emitió el dictamen (`06_Dictamen`). La actualización de Redmine queda lista en `08_Redmine`.

## III. Resultados obtenidos

| Ejecución | Producto | Resultado |
|---|---|---|
| `r30_primera` | rama r30 | 14/14, pero las capturas muestran DEF-03 y DEF-04 |
| `r30_defectos` | rama r30 | 12/14: CP-10 y CP-13 fallan con las aserciones nuevas (captura del fallo) |
| `r31_correccion` | rama r31 | 13/14: CP-10 en ERROR intermitente (DEF-06, de la suite) |
| `r31_regresion` | rama r31 | 14/14 |
| `r32_final-1`, `-2`, `edge` | trunk r32 | 14/14, anuladas por DEF-07 (CP-13 registraba dos veces cemento) |
| **`r32_final-3`, `r32_final-4`, `r32_edge-2`** | **trunk r32** | **14/14 en Chrome (dos ejecuciones) y en Edge** |
| xUnit del producto | trunk r32 | 944 aprobadas, 0 fallidas, 5 omitidas |

Mediciones de CP-07 en las 10 ejecuciones:

- **RNF-01:** las sugerencias aparecen en **570–585 ms** (umbral: < 1 000 ms).
- **RNF-06:** la venta completa se hace solo con teclado en **1,2–1,8 s** de sistema.

**Dictamen: APTO CON OBSERVACIONES.** Detalle en `06_Dictamen/dictamen_liberacion.md`. Las observaciones son:

- **HTTPS** (S10): pendiente.
- **Etiqueta `v0.2.0`**: pendiente.
- **Salvaguardas S4–S11**: siguen propuestas.
- **Medición humana de RNF-06**: falta cronometrar a un vendedor.

## IV. Análisis de resultados

- **La suite verifica resultados del producto y se puede repetir.**
  - Dos ejecuciones seguidas en Chrome y una en Edge dieron el mismo resultado, sin fallos intermitentes después de DEF-06.
  - Cada caso crea sus propios datos, así que el orden no influye.
- **La automatización no reemplaza la revisión.** Dos veces la suite pasó 14/14 con defectos a la vista: DEF-03 y DEF-04 en r30, y DEF-07 en r32. Las aserciones solo comprueban lo que se les pide. Revisar las capturas de cada regresión antes del dictamen es parte del procedimiento.
- **Una prueba defectuosa también invalida la evidencia.**
  - DEF-06 hacía fallar un caso correcto.
  - DEF-07 hacía pasar un caso con datos que no eran los del plan.

  Ambos se registraron y se corrigieron igual que los defectos del producto. Por DEF-07 se anularon y repitieron las ejecuciones finales.
- **El portal no agrega reglas: las prueba.** Los mensajes que comprueba la suite son los de `Condor.Dominio`, que aplica la API: DNI y RUC, IGV, boleta de más de S/ 700, factura con RUC, una sola conversión por proforma, compra repetida, roles. Por eso un caso web aprobado también confirma la regla del servidor.
- **Riesgo.** El portal aumenta la exposición de R12 (HTTP en la LAN), así que la salvaguarda S10 de G06 sube de prioridad.

## V. Conclusiones

1. Se configuró Selenium WebDriver con Selenium Manager, Chrome y Edge, y se automatizaron 14 casos web sobre el producto real. Cubren los ocho casos de la guía y los tres procesos de negocio, con aserciones observables, selectores estables, esperas explícitas y datos aislados.
2. Para tener una interfaz automatizable fue necesario un cambio controlado (CC-03). Se hizo con todo el ciclo de G02 y G05: solicitud, análisis de impacto, rama, pruebas, integración y actualización de la ERS y el SDD.
3. La suite encontró y ayudó a cerrar dos defectos reales del portal. Su propia calidad también se controló (DEF-06 y DEF-07).
4. La versión 1.2.0 (trunk r32) es **apta con observaciones**. Ningún defecto crítico o mayor está abierto, y todos los requisitos de la línea base tienen una prueba aprobada.

## Ubicación de evidencias

| Carpeta | Contenido |
|---|---|
| `00_Solicitud_Cambio` | CC-03 y capturas comparativas app / portal |
| `01_Plan` | Plan de pruebas de aceptación y regresión |
| `02_Suite` | Código de la suite, configuración, ejecutores y README |
| `03_Datos` | Datos fijos, generados e inválidos |
| `04_Reportes` | 10 ejecuciones (HTML, JUnit XML, JSON, log, capturas), xUnit r32 e índice |
| `05_Defectos` | Registro DEF-03 a DEF-07 y evidencias antes / después |
| `06_Dictamen` | Dictamen de liberación y matriz de trazabilidad |
| `07_Herramientas` | Fichas y comparación de herramientas |
| `08_Redmine` | Scripts para registrar CC-03 y las verificaciones (requieren la clave de Redmine) |
| `09_Cuestionario_guia.md` | Cuestionario de la guía aplicado al producto |

## Limitaciones

- Las pruebas se hicieron contra la base de demostración, que guarda los registros «G09».
- Hubo una sola PC y no se hicieron pruebas de seguridad dedicadas del portal.
- RF-09, RF-10, RF-13 y RF-16 se verifican con xUnit y G06, no por la web.
- RNF-06 se midió con automatización: falta cronometrar a un vendedor real.
- Los commits se hicieron con la cuenta `rcondo`.
- Uso de IA: la suite, el portal y los documentos se prepararon con asistencia de Claude (Anthropic) y el equipo los revisó. Las cifras salen de los archivos de resultados.
