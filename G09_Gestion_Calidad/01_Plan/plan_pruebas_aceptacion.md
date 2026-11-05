# Plan de pruebas de aceptación y regresión web — G09

| Campo | Valor |
|---|---|
| Producto | Sistema de Ventas y Facturación Cóndor, **versión 1.2.0** (portal web CC-03) |
| Objeto de prueba | Portal web del mostrador servido por `Condor.Api` en `http://localhost:5080/` |
| Herramienta | Selenium WebDriver 4.52.0 (Python 3.12.0, `unittest`), Chrome 156 y Edge 156 con Selenium Manager |
| Suite | `02_Suite` — 14 casos (CP-01 a CP-14) |
| Responsable de la suite | Integrante 2 — Payehuanca Riquelme, Jhastyn Jefferson |
| Responsable del dictamen | Integrante 1 — Huamani Condori, Jeanpiero Sixto |
| Revisó | Integrante 4 — Chaisa Fernández, Anthony Leonel |

## 1. Objetivo

Comprobar en la interfaz web, con resultados observables, que el producto cumple los criterios de aceptación de los requisitos de la línea base (ERS 1.2) en los tres procesos de negocio. La misma suite se usa como regresión de la versión final.

## 2. Alcance

| Incluido | Excluido (y dónde se verifica) |
|---|---|
| Ingreso, credenciales inválidas, roles y cierre de sesión (RF-01 a RF-03) | Ticketera e impresión, RF-09: `Aceptacion/HU12_*` y `Impresion/*` (xUnit) |
| Registro de clientes y productos con datos válidos e inválidos (RF-04 a RF-06) | Envío a la SUNAT, RF-10: `Aceptacion/HU07_*`, `HU17_*` (xUnit) |
| Venta con boleta, factura y sus reglas (RF-05, RF-07) | Guías de remisión, RF-13: solo en la app; `Aceptacion/HU10_*` (xUnit) |
| Proforma y su conversión en venta (RF-08) | Generación del respaldo, RF-16: G06 control S3 y `Aceptacion/HU15_*` |
| Proveedores y compras (RF-11, RF-12) | Concurrencia de tres PC, RNF-04: `Aceptacion/HU16_*`, `Datos/MEJ01_*` |
| Historial y reporte consolidado (RF-14, RF-15) | Capacidad de la API, RNF-02: G08 (JMeter) |
| RNF-01 (sugerencias < 1 s) y RNF-06 (venta solo con teclado ≤ 60 s) | Cobertura, RNF-08: G07 |

## 3. Técnicas de diseño de casos

| Técnica | Dónde se aplica |
|---|---|
| **Casos de uso / escenarios de negocio** | CP-07, CP-10 y CP-13 recorren de principio a fin PN-01, PN-02 y PN-03 |
| **Partición de equivalencia** | Documento válido (DNI 8 dígitos, RUC con dígito correcto) frente a corto, no registrado o con dígito errado (CP-04, CP-05, CP-08); usuario válido, clave errada o usuario inexistente (CP-02) |
| **Valores límite** | Cantidad 0 (CP-05); boleta de más de S/ 700 sin DNI (CP-09); período de más de 366 días en el reporte (CP-12); fecha de compra futura (CP-13) |
| **Tabla de decisión** | Tipo de comprobante × cliente: boleta sin cliente, con DNI, factura con RUC y factura sin RUC (CP-07 a CP-09) |
| **Transición de estados** | Proforma VIGENTE → CONVERTIDA, y CONVERTIDA → nueva conversión rechazada (CP-10) |
| **Pruebas negativas de autorización** | Vendedor contra los módulos del Encargado, por menú, por dirección y por tecla (CP-03) |

## 4. Casos de prueba

| ID | Caso (exigido por la guía) | Proceso | Requisitos | Datos | Resultado esperado observable |
|---|---|---|---|---|---|
| CP-01 | Acceso correcto | — | RF-01 | `encargado` | Pie con «encargado · Encargado general»; Nueva venta activa; la ventana Ingresar desaparece |
| CP-02 | Credenciales inválidas | — | RF-01, RNF-03 | `vendedor2` con clave errada; usuario inexistente; campos vacíos | «Usuario o contraseña incorrectos.» para clave errada y para usuario inexistente; la clave se borra; «Ingrese su usuario y su contraseña.» con campos vacíos |
| CP-03 | Restricción por rol | — | RF-03, RNF-03 | `vendedor1` | Sin Compras, Proveedores, Guías, Respaldo ni Reporte en el menú; `#/proveedores` y F4 lo dejan en Nueva venta con «Acceso denegado: el módulo … es solo para el Encargado general» |
| CP-04 | Registro válido (cliente) | PN-01 | RF-06 | DNI nuevo, nombre con sufijo de la ejecución | Mensaje «Cliente … registrado.», fila en Clientes; en Nueva venta el DNI lo encuentra y elige «Con DNI» |
| CP-05 | Datos inválidos | PN-01 | RF-04, RF-05, RF-06 | DNI de 4 dígitos, DNI no registrado, cantidad 0, RUC con dígito errado, precio 0, nombre vacío | Cada mensaje de la regla de `Condor.Dominio`; no se agrega la línea; el diálogo queda abierto |
| CP-06 | Registro válido (producto) | PN-01 | RF-04, RF-05 | Producto nuevo S/ 12.35 KG | Fila en Catálogo; en la venta se encuentra y 2 × 12.35 = S/ 24.70 |
| CP-07 | Registro y consulta: venta con boleta | PN-01 | RF-05, RF-07, RF-14, RNF-01, RNF-06 | «cemento», cantidad 2 | Sugerencias < 1 000 ms; total = 2 × precio; op. gravada = total / 1,18; «Boleta B001-######## emitida · Total … · SUNAT: PENDIENTE»; pantalla limpia; el número aparece en Historial con su total y usuario; venta completa ≤ 60 s solo con teclado |
| CP-08 | Registro válido: factura | PN-01 | RF-06, RF-07 | RUC nuevo con dígito válido | Con RUC se elige Factura; «Factura F001-######## emitida» |
| CP-09 | Datos inválidos: reglas de emisión | PN-01 | RF-07 | Factura sin cliente; boleta de 40 bolsas sin DNI | «La factura requiere un cliente con RUC…»; «… deben llevar el DNI del cliente…»; la venta no se pierde; Esc la cancela |
| CP-10 | **Cambio de estado** | PN-02 | RF-08, RF-07 | Proforma de 5 bolsas para un cliente nuevo | «Vigente hasta el dd/mm/aaaa» (7 días) → Convertir lleva detalle, total y cliente a la venta → boleta → «Convertida en B001-########»; no se puede convertir otra vez |
| CP-11 | Consulta: historial | PN-01 | RF-14 | Todo; Facturas; desde > hasta | Solo filas de Factura, menos que el total; «Total del período S/ …»; «La fecha final no puede ser anterior a la inicial.» |
| CP-12 | Consulta consolidada: reporte | — | RF-15, RF-03 | `encargado`, 01/10/2026 a hoy | La suma por tipo coincide con el total y la cantidad; hay filas por usuario; período > 366 días rechazado |
| CP-13 | Registro: proveedor y compra | PN-03 | RF-11, RF-12, RF-03 | RUC nuevo, factura F### con número aleatorio, 10 × 15.50 + 2 × 25.00 | Proveedor en la lista; RUC repetido rechazado; compra con total S/ 205.00 y op. gravada S/ 173.73; compra repetida «ya está registrada»; fecha futura rechazada |
| CP-14 | Cierre de sesión | — | RF-02 | `vendedor1` | Vuelve a Ingresar con campos vacíos; `sessionStorage` sin token; recargar o abrir `#/historial` no reabre la sesión |

Los ocho casos mínimos de la guía están cubiertos: acceso correcto (CP-01), credenciales inválidas (CP-02), restricción por rol (CP-03), registro válido (CP-04, CP-06, CP-08, CP-13), datos inválidos (CP-05, CP-09), consulta (CP-07, CP-11, CP-12), cambio de estado (CP-10) y cierre de sesión (CP-14). Los tres procesos de negocio se recorren completos en CP-07 (PN-01), CP-10 (PN-02) y CP-13 (PN-03).

## 5. Reglas de automatización

- **Aserciones sobre resultados observables:** textos que ve el usuario (mensajes, números de comprobante, totales, estados), visibilidad de pantallas y del menú, y contenido de las tablas. No se inspecciona la base de datos.
- **Selectores estables:** los `id` del portal, que repiten los AutomationId de la app (`CampoUsuario`, `BotonIngresar`, `MenuVenta`, `TextoMensaje`…). No hay XPath por posición; solo hay selectores CSS por `id`, clase de estado o `data-numero`.
- **Esperas explícitas:** `WebDriverWait` con `expected_conditions`, que ignora `StaleElementReferenceException` porque las tablas se vuelven a pintar (ver DEF-06). No se usa `implicit_wait` ni `time.sleep` para sincronizar.
- **Datos aislados:** cada caso abre su propio navegador e ingresa de nuevo. Los DNI, RUC (con dígito verificador válido), nombres y series de compra se generan para cada ejecución (`datos.py`). Los casos no dependen del orden ni de otra ejecución, y `vendedor2` solo se usa en CP-02 para que su intento fallido no afecte a los demás.
- **Fallos visibles:** la aserción fallida se propaga a `unittest`. `PruebaWeb._callTestMethod` toma la captura `CP-xx_NN_FALLO.png` y vuelve a lanzar la excepción. Nunca se captura `AssertionError` para solo imprimirla (precaución de la guía 7).
- **Modo de ejecución:** sin ventana (headless) para la regresión, y `--ventana` para mirar la prueba.

## 6. Entorno

| Elemento | Valor |
|---|---|
| Equipo | LAPTOP-JPHC, Windows 11 Home 10.0.26300 |
| Producto | `CondorApi.exe` 1.2.0 (trunk r32), publicado por `ejecutar.ps1 -Api` |
| Base de datos | PostgreSQL 16 en Docker (`Cas_condor`, base `condor`, con los datos de demostración) |
| Navegadores | Chrome 156.0.8078.80 y Edge 156.0.4314.58; controladores ubicados por Selenium Manager |
| Ejecutor | `python ejecutar_suite.py --etiqueta <versión>_<motivo>` |

## 7. Criterios

| Criterio | Valor |
|---|---|
| Entrada | `GET /api/salud` responde `OK` con la versión a probar; suite xUnit del producto en verde |
| Salida para el dictamen | 14/14 casos aprobados en la versión final, dos ejecuciones seguidas sin fallos intermitentes y ningún defecto crítico ni mayor abierto |
| Definición de defecto | Un resultado observable distinto del esperado del caso o del criterio de la ERS. Un fallo de la propia suite (sincronización, selector) se registra como defecto de la prueba, no del producto |
| Severidad | **Crítico:** impide un proceso esencial o expone información. **Mayor:** afecta una función importante. **Menor:** impacto limitado (enunciado, sección 13). La prioridad (alta, media o baja) se registra aparte |

## 8. Ejecuciones previstas

1. Primera ejecución sobre la rama CC-03 (r30).
2. Ejecución con aserciones nuevas para los defectos hallados en la revisión de evidencias.
3. Regresión tras la corrección (r31).
4. Regresión final sobre trunk r32: dos veces en Chrome y una en Edge. Se repitió (`r32_final-3`, `r32_final-4`, `r32_edge-2`) después de corregir DEF-07 en la suite.

Todas quedan en `04_Reportes` con su HTML, JUnit XML, JSON, log y capturas.
