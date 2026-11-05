# CC-03 · Portal web del mostrador (interfaz automatizable con Selenium)

| Campo | Valor |
|---|---|
| ID | CC-03 (Redmine: petición **#28**, tipo *Solicitud de cambio*; ver `08_Redmine`) |
| Fecha de registro | 2026-11-04 |
| Solicitante | Docente del curso (enunciado, sección 2 y Guía 9) y evaluador de calidad del equipo |
| Registró | Integrante 2 — Payehuanca Riquelme, Jhastyn Jefferson (responsable de la suite de G09) |
| Analizó | Integrante 3 — Condo Zamata, Richard Alberto (diseño) |
| Decidió | Comité de cambios (CCB): gerente general, Integrante 1 e Integrante 2 |
| Prioridad | Alta (bloquea G09) |
| Línea base afectada | ERS 1.1 → **ERS 1.2** (interfaz INT-07, Apéndice C) · SDD 1.0 → **SDD 1.1** (DD-09) |
| Versión del producto afectada | 1.1.2 → **1.2.0** |
| Decisión | **Aprobada** |
| Estado final | **Cerrado** (implementado, verificado con xUnit y Selenium, integrado en trunk r32) |

## 1. Descripción del cambio

Agregar al producto una interfaz web, el **portal web del mostrador**, que `Condor.Api` sirva en `http://<PC principal>:5080/`. Debe cumplir tres condiciones:

- Reproduce las pantallas de la app de escritorio, con la misma paleta, menú, atajos y textos: Ingresar, Nueva venta, Catálogo, Clientes, Historial y Proformas, y para el Encargado general Compras, Proveedores, Reporte y Respaldo.
- Usa las mismas rutas `/api` con el token JWT y no tiene reglas de negocio propias.
- Tiene `id` estables en cada control (los mismos AutomationId de la app WPF) para Selenium WebDriver.

Para que el portal cubra los tres procesos de negocio se agregan cuatro rutas públicas, con las mismas reglas de `Condor.Dominio`:

| Ruta | Rol | Regla que reutiliza |
|---|---|---|
| `GET /api/proformas?texto=` | todos | Estado VIGENTE / VENCIDA / CONVERTIDA (`Comprobante.Vencida`, `Convertida`) |
| `POST /api/proformas/{id}/convertir` | todos | `EmisionComprobante.Preparar` con la proforma (HU-09, CRQ-06) |
| `GET /api/compras?desde=&hasta=&proveedor=` | Encargado | `ICompraRepositorio.BuscarAsync` |
| `POST /api/compras` | Encargado | `ValidadorCompra.Preparar` (HU-11) |

## 2. Motivo

1. **Del curso.** El enunciado pide una «interfaz automatizable con Selenium», y la Guía 9 pide configurar «Selenium WebDriver, navegador y mecanismo compatible de gestión del controlador». El producto solo tenía la app WPF y la API, así que no había ninguna página web que automatizar.
2. **Alternativa descartada.** Se podía automatizar la app WPF con Appium y WinAppDriver, que también usan el protocolo WebDriver, aprovechando los AutomationId que dejó CC-01. Se descartó por tres razones:
   - WinAppDriver no se mantiene desde la versión 1.2.1 (2020).
   - Exige activar el Modo de desarrollador de Windows.
   - No cumple «navegador» como pide la guía.

   El usuario representado del equipo pidió que el portal fuera lo más parecido posible a la app de C#.
3. **Del cliente.** El Encargado general puede consultar ventas, proformas y el reporte desde cualquier PC del local sin instalar la app. Es un beneficio secundario, no el motivo principal.

## 3. Análisis de impacto

### 3.1 Requisitos (ERS)

| Elemento | Impacto |
|---|---|
| Interfaces externas | Nueva **INT-07 Portal web** (ERS 1.2, 3.1). |
| RF-01 a RF-08, RF-11, RF-12, RF-14, RF-15 | Sin cambio en su texto ni en sus criterios. Se verifican además en el portal (CP-01 a CP-14). |
| RF-09, RF-10, RF-13, RF-16 | Sin cambio: ticketera, SUNAT, guías y generación del respaldo siguen solo en la app. El portal muestra Guías como «use la app de escritorio» y Respaldo solo como consulta. |
| RNF-01, RNF-06 | Se miden también en el portal (CP-07). |
| RNF-03 | El portal no cambia la seguridad: el token se guarda en `sessionStorage`, que se borra al cerrar la pestaña o la sesión, y la API vuelve a comprobar el rol en cada ruta. |

### 3.2 Diseño (SDD)

- **Decisión DD-09:** portal estático (HTML, CSS y JavaScript sin dependencias) en `src/Condor.Api/wwwroot`.
- **Componentes:** «Portal web» y `wwwroot` en el diagrama de componentes, y nodo «PC con navegador» en el de despliegue (`G03_Analisis_Sistemas/02_UML/07_componentes`, `08_despliegue`).
- **Vista de interfaz:** las cuatro rutas nuevas y `GET /` en 4.7.1.

### 3.3 Código

| Archivo | Cambio |
|---|---|
| `src/Condor.Api/Program.cs` | `UseDefaultFiles()` y `UseStaticFiles()` |
| `src/Condor.Api/Endpoints.cs` | Rutas de proformas y compras |
| `src/Condor.Api/Modelos.cs` | `ProformaDto`, `ConvertirPedido`, `NuevaCompraPedido`, `CompraDto`, `ComprasDto` |
| `src/Condor.Api/wwwroot/` | `index.html`, `css/portal.css`, `js/portal.js`, `img/` (los recursos de la app) |
| `Condor.Api.csproj`, `Condor.Escritorio.csproj` | Versión 1.2.0 |

No cambian `Condor.Dominio`, `Condor.Datos` ni la base de datos (no hay migración nueva).

### 3.4 Costo y plazo

| Actividad | Responsable | Estimado | Real |
|---|---|---|---|
| Análisis de impacto y diseño (DD-09) | Condo Z., R. A. | 1 h | 1 h |
| Portal web (HTML, CSS, JS) | Condo Z., R. A. | 6 h | 6,5 h |
| Rutas de proformas y compras + 11 pruebas xUnit | Condo Z., R. A. | 2 h | 2 h |
| Suite Selenium (14 casos), reportes y defectos | Payehuanca R., J. J. | 6 h | 6 h |
| Dictamen | Huamani C., J. S. | 2 h | 2 h |
| **Total** | | **17 h** | **17,5 h** |

A S/ 25 la hora (tarifa de G04): unos **S/ 440**. El plazo es de un día y no mueve el segundo entregable (25-11-2026).

### 3.5 Riesgos (MAGERIT, G06)

- **Activo nuevo.** El portal se agrega como servicio [S] dependiente de `Condor.Api`.
- **R12 (interceptación en la LAN).** Es el riesgo que más aumenta: ahora cualquier navegador de la red puede abrir el portal por HTTP, así que la salvaguarda propuesta **S10 (HTTPS en la API)** sube de prioridad. Queda como observación del dictamen.
- **XSS.** Todo texto que viene de la API se escapa (`escapar()` en `portal.js`).
- **Autorización.** No se debilita, porque la API repite el control de rol (S1). CP-03 lo verifica en la interfaz y `ApiTests`/`PortalWebTests` en el servidor (403).

### 3.6 Pruebas

| Nivel | Prueba | Resultado |
|---|---|---|
| Unitarias / integración (xUnit) | `Api/PortalWebTests` (11 casos nuevos) + la suite completa del producto | 944 aprobadas, 0 fallidas, 5 omitidas (r31 y r32) |
| Aceptación y regresión web (Selenium) | CP-01 a CP-14 (`02_Suite`) | 14/14 en Chrome (dos corridas) y en Edge sobre trunk r32 (`r32_final-3`, `r32_final-4`, `r32_edge-2`) |
| Regresión de la app de escritorio | Las pruebas de aceptación de la app (`Aceptacion/*`, `Presentacion/*`) dentro de la misma suite xUnit | Sin fallos |

## 4. Decisión

**Aprobada** por el CCB el 2026-11-04. Condiciones:

1. El portal no puede tener reglas propias: toda validación la hace la API.
2. El aspecto debe seguir el de la app (pedido del usuario representado).
3. Se implementa en una rama SVN y se integra solo con la suite xUnit en verde.

## 5. Implementación y cierre

| Paso | Fecha | Responsable | Evidencia |
|---|---|---|---|
| Rama `branches/CC-03-portal-web` | 2026-11-04 | Condo Z., R. A. | SVN r28 |
| Portal web, rutas de proformas, `PortalWebTests` (7) | 2026-11-04 | Condo Z., R. A. | SVN r29 |
| Módulo Compras, rutas de compras, 4 pruebas más | 2026-11-04 | Condo Z., R. A. | SVN r30 |
| La suite Selenium detecta DEF-03 y DEF-04 | 2026-11-04 | Payehuanca R., J. J. | `04_Reportes/20261104_1851_1.2.0-r30_defectos` |
| Corrección de DEF-03 y DEF-04 | 2026-11-04 | Condo Z., R. A. | SVN r31 |
| Regresión Selenium 14/14 sobre la rama | 2026-11-04 | Payehuanca R., J. J. | `04_Reportes/20261104_1856_1.2.0-r31_regresion` |
| Integración en trunk (sin conflictos) | 2026-11-04 | Integración hecha con la cuenta `rcondo` (ver nota) | SVN r32 |
| Regresión final xUnit + Selenium (Chrome ×2, Edge) | 2026-11-04 | Payehuanca R., J. J. | `04_Reportes/xunit_1.2.0-r32`; Selenium `r32_final-3`, `r32_final-4`, `r32_edge-2`. Las tres primeras ejecuciones r32 se anularon por DEF-07 (defecto de la suite) |
| ERS 1.2 y SDD 1.1 | 2026-11-04 | Huamani C., J. S. y Condo Z., R. A. | `G01_Requerimientos/01_ERS/ERS_Condor_v1.2.md`, `G03_Analisis_Sistemas/01_SDD` |
| Verificación y cierre en Redmine (petición #28) | 2026-11-04 | Chaisa F., A. L. verifica; Payehuanca R., J. J. cierra | `08_Redmine/actualizar_redmine.py`, `08_Redmine/capturas` |

> **Nota de configuración.** Los commits r28 a r32 y el de G09 se hicieron con la cuenta SVN `rcondo`, la única con credencial guardada en el equipo de trabajo, por decisión del equipo. En G05 se registró que la integración en trunk la hace el responsable de configuración: esta vez la regla no se cumplió en el historial, aunque sí en la revisión del merge.

## 6. Comparación visual app / portal

Las capturas de `capturas/` muestran la misma pantalla en la app WPF (`0N_app_*.png`) y en el portal (`0N_portal_*.png`):

1. Ingresar
2. Nueva venta
3. Historial
4. Proformas
5. Clientes
6. Compras (solo portal: en la app es una ventana aparte)
