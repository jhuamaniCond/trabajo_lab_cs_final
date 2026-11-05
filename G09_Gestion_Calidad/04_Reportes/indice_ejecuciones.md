# Ejecuciones de la suite Selenium

Cada carpeta tiene `reporte.html` (abrir en el navegador), `resultados.xml` (JUnit), `resultados.json`, `ejecucion.log`, `entorno.json` y `capturas/`.

| Ejecución | Producto | Navegador | Aprobados | Fallidos | CP-07: RNF-01 / RNF-06 | Duración | Motivo |
|---|---|---|---|---|---|---|---|
| `20261104_1847_1.2.0-r30_primera` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 572 ms / 1.7 s | 77 s | Primera ejecución sobre la rama CC-03 (r30) |
| `20261104_1851_1.2.0-r30_defectos` | 1.2.0 | chrome 156.0.8078.80 | **12/14** | CP-10 (fallido), CP-13 (fallido) | 578 ms / 1.2 s | 71 s | Aserciones nuevas para DEF-03 y DEF-04 (vistos en la revisión de capturas): la suite los detecta |
| `20261104_1855_1.2.0-r31_correccion` | 1.2.0 | chrome 156.0.8078.80 | **13/14** | CP-10 (error) | 576 ms / 1.8 s | 78 s | Tras corregir DEF-03 y DEF-04 (r31): pasan; falla intermitente de la suite en CP-10 (DEF-06) |
| `20261104_1856_1.2.0-r31_regresion` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 585 ms / 1.3 s | 77 s | Regresión en la rama tras corregir DEF-06 en la suite |
| `20261104_1903_1.2.0-r32_final-1` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 573 ms / 1.8 s | 78 s | Trunk r32, Chrome — anulada para el dictamen: la suite tenía DEF-07 (CP-13 compraba dos veces cemento) |
| `20261104_1904_1.2.0-r32_final-2` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 575 ms / 1.2 s | 76 s | Trunk r32, Chrome — anulada para el dictamen (DEF-07) |
| `20261104_1906_1.2.0-r32_edge` | 1.2.0 | MicrosoftEdge 156.0.4314.58 | **14/14** | — | 570 ms / 1.3 s | 81 s | Trunk r32, Edge — anulada para el dictamen (DEF-07) |
| `20261104_1919_1.2.0-r32_final-3` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 575 ms / 1.4 s | 82 s | **Regresión final** sobre trunk r32 con la suite corregida — Chrome (1.ª) |
| `20261104_1921_1.2.0-r32_final-4` | 1.2.0 | chrome 156.0.8078.80 | **14/14** | — | 576 ms / 1.3 s | 79 s | **Regresión final** sobre trunk r32 — Chrome (2.ª, repetibilidad) |
| `20261104_1922_1.2.0-r32_edge-2` | 1.2.0 | MicrosoftEdge 156.0.4314.58 | **14/14** | — | 572 ms / 1.3 s | 84 s | **Regresión final** sobre trunk r32 — Edge |

`xunit_1.2.0-r32/`: suite xUnit del producto sobre trunk r32 (`.trx` y `.html`): 944 aprobadas, 0 fallidas, 5 omitidas.
