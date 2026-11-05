# Revisión del SDD contra IEEE 1016-2009

| Campo | Valor |
|---|---|
| Documento revisado | `01_SDD/SDD_Condor_v1.0.md` (borrador 0.9 → versión 1.0) |
| Referencia | IEEE Std 1016-2009: cláusula 4 (contenido del SDD) y cláusula 5 (puntos de vista) |
| Fecha | 2026-10-30 |
| Revisores | Integrante 1 — Huamani Condori, Jeanpiero Sixto · Integrante 2 — Payehuanca Riquelme, Jhastyn Jefferson (no redactaron el SDD) |
| Método | Lista de comprobación por criterio y contraste del diseño con el código de la versión 1.1.0 (`Sistema_Logistico_Condor_final/src`) y con las migraciones `db/migraciones` |
| Resultado | 7 observaciones: 6 corregidas en la 1.0 y 1 que es un defecto del producto (DEF-01, **corregido en el producto 1.1.1**, revisión SVN r11). 3 criterios quedan pendientes o no aplican, con justificación. |

## 1. Criterios de contenido (IEEE 1016, cláusula 4)

| N.º | Criterio | Estado | Evidencia en el SDD |
|---|---|---|---|
| C1 | Identificación del SDD: fecha, estado, alcance, organización, autoría, referencias, notación e historial de cambios | Cumplido | Cabecera, control de versiones, secciones 1.1 a 1.4 |
| C2 | Interesados identificados | Cumplido | Sección 2 (6 interesados, los mismos de la ERS: PAR-01 a PAR-06) |
| C3 | Preocupaciones de diseño de cada interesado | Cumplido | Sección 2, columna *Preocupaciones* |
| C4 | Puntos de vista seleccionados, con las preocupaciones que atiende cada uno y su lenguaje | Cumplido | Sección 3 (8 puntos de vista) |
| C5 | Una vista por cada punto de vista, conforme a él | Cumplido | Secciones 4.1 a 4.8 |
| C6 | Cada preocupación queda atendida al menos por una vista | Cumplido | La tabla de la sección 2 relaciona cada preocupación con sus vistas |
| C7 | Elementos de diseño con nombre, tipo y propósito | Cumplido | Tabla de componentes (4.2), clases (4.3), tablas (4.4) |
| C8 | Relaciones entre elementos | Cumplido | Diagramas de clases, componentes y ER |
| C9 | Restricciones de diseño | Cumplido | Vista de información (tabla de restricciones) y despliegue (la clave de la base solo en la API) |
| C10 | Justificación del diseño (*design rationale*): decisiones, alternativas y motivos | Cumplido | Sección 6 (DD-01 a DD-08) |
| C11 | Superposiciones de diseño (*design overlays*) | No aplica | No se usaron; las notas de los diagramas cumplen esa función. |
| C12 | Coherencia de nombres entre requisitos, diseño, código, tablas y pantallas | Cumplido tras OS-02 y OS-03 | Sección 7, contrastada con el código (ver observaciones) |

## 2. Criterios de los puntos de vista (IEEE 1016, cláusula 5)

| Punto de vista | Elementos que exige la norma | Estado | Evidencia |
|---|---|---|---|
| Contexto (5.2) | Actores, servicios, límites del sistema | Cumplido | `01_casos_uso`; contexto ASCII de la ERS 2.1 |
| Composición (5.3) | Partes, responsabilidades, dependencias | Cumplido | `07_componentes`, tabla 4.2 |
| Lógico (5.4) | Clases, atributos, operaciones, asociaciones | Cumplido tras OS-01 | `02a_clases_entidades`, `02b_clases_reglas` |
| Dependencias (5.5) | Dependencias entre componentes | Cumplido | `07_componentes` (flechas de uso e implementación) |
| Información (5.6) | Datos persistentes, claves, restricciones | Cumplido tras OS-02 | `09_modelo_datos`, tabla de restricciones 4.4 |
| Uso de patrones (5.7) | Patrones aplicados y su papel | **Parcial** | MVVM, Repositorio y Puertos se nombran en 1.3, 4.2 y DD-04, sin una vista propia de patrones. Se acepta: el diagrama de componentes ya muestra la separación. |
| Interfaz (5.8) | Interfaces externas e internas | Cumplido | Tabla de rutas HTTP (4.7.1) y mockups (4.7.2) |
| Estructura (5.9) | Estructura interna de los elementos | Cumplido | Diagramas de clases |
| Interacción (5.10) | Colaboración entre elementos en un escenario | Cumplido | `03_secuencia_emitir_comprobante` (proceso crítico) |
| Estado dinámico (5.11) | Estados, transiciones, eventos | Cumplido | `04_estados_comprobante`; actividades `05` y `06` |
| Algoritmos (5.12) | Detalle de algoritmos importantes | **Pendiente** | El cálculo del IGV y del redondeo está en CRQ-01 y en `CalculadoraVenta`, sin pseudocódigo en el SDD. Se completará en el informe final con el código de `CalculadoraVenta.Totales`. |
| Recursos (5.13) | Uso de recursos y despliegue | Cumplido | `08_despliegue` |

## 3. Criterios propios del enunciado (G03)

| Exigencia del enunciado | Estado | Evidencia |
|---|---|---|
| Diagrama de casos de uso | Cumplido | `02_UML/01_casos_uso` |
| Diagrama de clases | Cumplido | `02_UML/02a_…`, `02b_…` |
| Al menos un diagrama de comportamiento de un proceso crítico | Cumplido | Secuencia de la emisión (crítico), más estados y 2 actividades |
| Al menos 3 casos de uso con precondiciones, flujo principal, alternativas, excepciones y poscondiciones | Cumplido | SDD, sección 5: CU-01, CU-02 y CU-03 (uno por proceso de negocio) |
| Mockups de las pantallas de esos casos | Cumplido | `03_Mockups/M01` a `M05` (M02, M03 y M04 corresponden a CU-01, CU-02 y CU-03) |
| Arquitectura y modelo de datos | Cumplido | Vistas 4.2, 4.4 y 4.8 |
| Coherencia de nombres, reglas, clases, tablas y pantallas | Cumplido | Sección 7 y observaciones OS-02 a OS-06 |
| Tabla de utilidad de los diagramas UML | Cumplido | SDD, sección 8 |
| El diseño explica los tres procesos y se puede rastrear hacia requisitos y código | Cumplido | Vista de contexto (4.1), casos de uso (5) y trazabilidad (7) |
| Validación de los mockups con el usuario | **Pendiente** | La validó el gerente representado (Integrante 2). Falta mostrarlos al docente en el primer entregable (11-11-2026). |

## 4. Observaciones de la revisión y su corrección

| ID | Elemento | Criterio | Observación (versión 0.9) | Corrección en la 1.0 | Estado |
|---|---|---|---|---|---|
| OS-01 | Diagrama de clases | Legibilidad (5.4) | Un solo diagrama de 4096 px de ancho, recortado por el límite de PlantUML: no se veían `EmisionComprobante` ni `CalculadoraVenta`. | Se dividió en `02a` (entidades) y `02b` (reglas y contratos). | Cerrada |
| OS-02 | Modelo de datos | Coherencia con el código (C12) | Columnas que no existen: `comprobante_sunat.cdr`, `guia_remision.peso_bruto`, `respaldo.tamano` y `resultado`; faltaban los `id` de `compra_detalle` y `guia_detalle`. | Se corrigieron con las migraciones V001–V014: `cdr_zip`, `peso_bruto_kg`, `bytes`, `iniciado_en`, `terminado_en`, `carpeta`; se agregó la relación `producto`–`guia_detalle`. | Cerrada |
| OS-03 | Clases: `GuiaRemision`, `ValidadorCompra` | Coherencia con el código (C12) | `PesoBruto` en lugar de `PesoBrutoKg`; `ValidadorCompra` sin operaciones. | Se cambió a `PesoBrutoKg` y `FechaTraslado`, y se agregaron `Errores()` y `Preparar()`. | Cerrada |
| OS-04 | Mockup M02 | Coherencia con las reglas (CRQ-01) | Los totales no cuadraban: subtotales que suman 118.01 con un TOTAL de 119.01. | TOTAL S/ 118.01 = op. gravada 100.01 + IGV 18.00. | Cerrada |
| OS-05 | Mockup M02 | Coherencia con RF-03 | Mostraba al Vendedor los botones F4, F6, F8 y F9 en gris, pero la versión 1.1.0 los oculta. | Se retiraron de M02; la restricción se muestra en M05. | Cerrada |
| OS-06 | Actividad PN-03 y diagrama de casos de uso | Claridad | La actividad sugería registrar el proveedor dentro de Nueva compra (en la aplicación se hace en Proveedores, F6); el título del diagrama de casos de uso tapaba el nombre del sistema. | Se indicó «Proveedores (F6)»; el título pasó a pie de figura. | Cerrada |
| OS-07 | Vista de interfaz e interacción: `POST /api/escritorio/comprobantes` | Diseño frente a requisito (CRQ-07) | La ruta pública `/api/comprobantes` toma el precio y la descripción **del catálogo**. La ruta que usa la aplicación (`EndpointsEscritorio.EmitirAsync`) **guarda el precio unitario y la descripción enviados por la PC** y solo recalcula los totales. La base solo exige `precio_unitario > 0`. Un usuario con token de Vendedor puede emitir por HTTP una boleta a cualquier precio. Contradice CRQ-07 («no se acepta el precio enviado por la terminal»). | El SDD documenta el comportamiento real (secuencia, paso 9: «recalcula importes y totales», sin afirmar que toma el precio del catálogo). Se registra como **defecto DEF-01** del producto para corregirlo con trazabilidad (ver sección 5). | **Cerrada** (DEF-01 corregido en 1.1.1, r11) |

## 5. Defecto encontrado en la revisión

| Campo | Valor |
|---|---|
| ID | DEF-01 |
| Fecha | 2026-10-30 |
| Versión | 1.1.0 |
| Requisito | CRQ-07 (y RF-07, RNF-03) |
| Pasos de reproducción | 1) `POST /api/auth/login` con `vendedor1`. 2) `POST /api/escritorio/comprobantes` con una línea del cemento (precio de catálogo S/ 32.50) y `precioUnitario: 0.10`. |
| Resultado esperado | El servidor usa S/ 32.50 del catálogo (o rechaza la petición) |
| Resultado obtenido (por inspección del código) | Se guarda la boleta con precio S/ 0.10 |
| Severidad | **Mayor**: afecta una función importante y la integridad de los importes, aunque exige un token válido |
| Prioridad | Alta: antes de la versión final |
| Responsable | Integrante 1 (desarrollo en la rama), Integrante 2 (integración) |
| Corrección propuesta | En `EndpointsEscritorio.EmitirAsync`, leer los productos con `IConsultaProductos` y reemplazar `Descripcion` y `PrecioUnitario` por los del catálogo, como ya hace `Endpoints.EmitirAsync`. Agregar una prueba en `Api/ClienteApiTests` que envíe un precio distinto y verifique el del catálogo. |
| Prueba de cierre | La nueva prueba en verde y la regresión de emisión (HU05, HU06, HU08, HU09) en verde |
| Estado | **Cerrado** el 2026-10-30. Rama `branches/DEF-01-precio-catalogo` (r8), corrección r10, integración en trunk r11 con conflicto resuelto frente a CRQ-14 (r9). Las 3 pruebas nuevas fallan con el código 1.1.0 y pasan con 1.1.1; suite integrada: 930 aprobadas, 0 fallidas (`G05_Gestion_Configuracion/04_Evidencias/pruebas/`). Producto **1.1.1**. Se llevará al registro de defectos y es candidato a control de G06 (validación de entradas). |

## 6. Conclusión

El SDD 1.0 cumple los criterios de contenido de IEEE 1016 y las exigencias de G03. Quedan dos puntos parciales o pendientes justificados (vista de patrones y vista de algoritmos) y la validación de los mockups con el docente.

La revisión contra el código encontró un defecto real del producto (DEF-01, CRQ-07). Se corrigió con trazabilidad en una rama SVN, con pruebas que detectan el defecto, y se integró en el producto 1.1.1 (G05, r11).
