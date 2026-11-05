# Sistema de Ventas y Facturación – Ferretería Cóndor Majes S.A.C.

Sistema (C# .NET 8) para registrar las ventas de la ferretería y emitir sus
comprobantes electrónicos. Trabaja en la red local: la app de escritorio (WPF)
y el portal web del mostrador hablan con el backend `Condor.Api` de la PC
principal, que es el único que se conecta a la base PostgreSQL 16.

## Versión actual: 1.2.0 (entrega final, etiqueta SVN `tags/v1.0.1`)

| Versión | Cambio | Qué agrega |
|---|---|---|
| **1.2.0** | CC-03: portal web del mostrador | `Condor.Api` sirve en `http://localhost:5080/` un portal web con el mismo aspecto y los mismos módulos de la app (venta, catálogo, clientes, historial, proformas y, para el Encargado, compras, proveedores, reporte consolidado y respaldos). Lo usan las pruebas de aceptación con Selenium (G09). Corrige DEF-03 y DEF-04. Ver [docs/api.md](docs/api.md#portal-web-cc-03). |
| 1.1.2 | MEJ-01 (G08) | Correlativo del comprobante asignado al final de la transacción: mejora del cuello de botella hallado con JMeter. |
| 1.1.1 | DEF-01 | Corrige el precio del catálogo en la ruta de escritorio. |
| 1.1.0 | CC-01: ingreso con roles y backend REST | Usuario y contraseña con dos roles, Vendedor y Encargado general ([docs/seguridad.md](docs/seguridad.md)); backend REST con tokens JWT y reporte consolidado de ventas ([docs/api.md](docs/api.md)). Las PC ya no se conectan directo a PostgreSQL. |
| 1.0.0 | Línea base del producto | Catálogo con autocompletado y lector de código de barras; clientes y proveedores; boletas, facturas, notas de venta y proformas que se convierten en venta; ticketera; envío, reenvío y consulta del CDR en la SUNAT; guías de remisión; historial con reimpresión; compras y respaldo de la base. |

Detalle en el [CHANGELOG](CHANGELOG.md); para pasar a producción,
[docs/produccion.md](docs/produccion.md).

> La etiqueta SVN numera la **entrega del trabajo** y la versión del producto
> numera **el software**: `tags/v1.0.1` (entrega final) contiene el producto
> **1.2.0**. Ver `G05_Gestion_Configuracion/01_Politica/politica_configuracion.md`.

### Servicios externos simulados

- **SUNAT:** sin la sección `Sunat` en `condor.json` no se envía nada; los
  comprobantes se emiten igual y quedan `PENDIENTE` (así corren las pruebas y
  la demostración). Con ella se usa el ambiente **beta** de la SUNAT.
- **Ticketera:** sin impresora configurada el ticket se muestra en pantalla.

### Credenciales de demostración

| Usuario | Contraseña | Rol |
|---|---|---|
| `encargado` | `Encargado2026!` | Encargado general (todos los módulos) |
| `vendedor1` | `Vendedor2026!` | Vendedor (venta, catálogo, clientes, historial, proformas) |
| `vendedor2` | `Vendedor2026!` | Vendedor |

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/Condor.Escritorio` | Aplicación WPF: ventanas y arranque. |
| `src/Condor.Presentacion` | ViewModels (MVVM) sin dependencias de WPF. |
| `src/Condor.Dominio` | Entidades, reglas (validación, IGV) y contratos. |
| `src/Condor.Datos` | Acceso a PostgreSQL (Npgsql), migraciones, repositorios y respaldo con pg_dump. |
| `src/Condor.Impresion` | Ticketera térmica: comandos ESC/POS y envío directo al spooler de Windows. |
| `src/Condor.ClienteApi` | Cliente HTTP de la app: implementa los repositorios llamando a la API (CC-01). |
| `herramientas/Condor.DatosDemo` | Datos de demostración: 25 o más clientes, proveedores, ventas, proformas, compras y guías. |
| `src/Condor.Api` | Backend REST (ASP.NET Core 8): ingreso con JWT, permisos por rol, productos, clientes, comprobantes, proformas, proveedores, reporte consolidado y respaldos. En `wwwroot`, el portal web (CC-03). |
| `src/Condor.Sunat` | Facturación electrónica: XML UBL 2.1 de comprobantes y guías, firma digital, envío a la SUNAT (sendBill y API de guías), lectura y consulta del CDR, reenvío de pendientes y chequeo de producción. |
| `db/migraciones` | Scripts SQL versionados; se aplican solos al abrir el programa. |
| `db/servidor` | Instalación de la base central en la PC principal. |
| `db/datos` | Lista de precios para la carga inicial del catálogo. |
| `herramientas/Condor.CargaCatalogo` | Programa de consola para la carga inicial. |
| `tests/Condor.Pruebas` | Pruebas unitarias, de integración y de aceptación (xUnit). |
| `docs/` | Modelo de datos, instalación, ticketera, SUNAT, respaldo, puesta en producción, pruebas, seguridad (usuarios y roles) y API. |

## Puesta en marcha

1. **PC principal:** instalar PostgreSQL 16 y abrirlo a la LAN según
   [docs/instalacion_postgresql.md](docs/instalacion_postgresql.md).
2. **Cada PC:** copiar `condor.ejemplo.json` como `condor.json` junto al
   ejecutable y poner la IP de la PC principal y la clave.
3. **Catálogo inicial:** ver [db/datos/README.md](db/datos/README.md).
4. **Datos de la ferretería** (RUC, razón social y dirección del ticket):
   ver [docs/modelo_datos.md](docs/modelo_datos.md#datos-de-la-empresa).
5. **PC con ticketera:** instalarla y poner su nombre en `condor.json`
   según [docs/ticketera.md](docs/ticketera.md). Sin ticketera, el ticket se
   muestra en pantalla.
6. **PC con internet:** completar la sección `Sunat` de `condor.json` según
   [docs/sunat.md](docs/sunat.md) (ambiente beta). Sin ella, los comprobantes
   se emiten igual y quedan pendientes; se reenvían solos cada
   `ReenvioMinutos` desde la PC que sí la tiene.
7. **PC principal:** completar la sección `Respaldo` de `condor.json` con la
   carpeta del disco externo según [docs/respaldo.md](docs/respaldo.md).
8. **Producción:** datos de la empresa, certificado digital, usuario SOL y
   credenciales de la API de guías según [docs/produccion.md](docs/produccion.md).

## Atajos de la pantalla Nueva venta

| Tecla | Acción |
|---|---|
| Enter | Elegir el producto sugerido y, en Cantidad, agregarlo al detalle. |
| Lector | Pasar el producto por el lector de código de barras lo agrega con una unidad. |
| Alt+D | Ir al campo DNI o RUC del cliente (Enter busca). |
| Ctrl+N | Nuevo producto. |
| Alt+L | Nuevo cliente. |
| F10 | Emitir e imprimir: boleta, con DNI, factura, nota de venta o proforma. |
| F11 | Reimprimir el último ticket. |
| F2 | Catálogo: buscar productos, registrar uno nuevo y asignarle su código de barras. |
| F3 | Clientes: buscar por DNI, RUC o nombre, registrar y usar en la venta. |
| F4 | Compras a proveedores y egresos del período; Alt+N registra una compra. |
| F5 | Historial de ventas: filtros por fecha, tipo, cliente o número, total del período, estado ante la SUNAT, reimpresión (como copia) y reenvío de pendientes. |
| F6 | Proveedores: buscar por RUC o razón social; Alt+N registra uno nuevo. |
| F7 | Proformas: buscarlas y convertirlas en venta (Enter). |
| F8 | Guías de remisión: emitir (desde una factura o a mano), imprimir y enviar a la SUNAT. |
| F9 | Respaldo de la base de datos en el disco externo (PC principal). |
| Esc | Cancelar la venta en curso; dentro de un módulo, volver a Nueva venta. |

Los módulos F2 a F9 se muestran en el panel derecho de la ventana principal,
en lugar de la pantalla de venta; F1, Esc o el menú vuelven a Nueva venta sin
perder la venta en curso.

## Desarrollo

Requisitos: .NET 8 SDK (o Visual Studio 2022) en Windows 10/11.

```powershell
dotnet build CondorVentas.sln
dotnet run --project src/Condor.Escritorio
dotnet run --project src/Condor.Api          # backend REST en http://localhost:5080
dotnet test        # ver docs/pruebas.md para las pruebas con base de datos y la cobertura
```

Sin el SDK de .NET instalado, `.\ejecutar.ps1` compila dentro de Docker y
abre la app; `.\ejecutar.ps1 -Api` arranca el backend.

`.\ejecutar.ps1` hace todo: base de datos, datos de demostración (la
primera vez), API y app. `-DatosDemo` vuelve a cargar los datos de demostración.

`ejecutar.ps1` usa su propio contenedor de PostgreSQL, **`Cas_condor`**
(volumen `cas_condor_datos`, puerto **5433** de esta PC), para no mezclarse
con otros PostgreSQL de la PC. Base `condor`, usuario `condor_app`, clave
`condor_local`. `.\ejecutar.ps1 -Detener` lo detiene y `-BorrarDatos` borra
su volumen.

Los registros se guardan en ese volumen de PostgreSQL y se conservan al
reiniciar la API, la app o el contenedor.

## Portal web (1.2.0)

```powershell
.\ejecutar.ps1 -Api      # base de datos + API; el portal queda en http://localhost:5080/
```

Se ingresa con las credenciales de demostración de arriba. Los menús que ve
cada usuario dependen de su rol; las rutas `/api` rechazan con 403 lo que el
rol no permite.

## Pruebas

| Tipo (guía) | Herramienta | Comando | Evidencias |
|---|---|---|---|
| Unitarias, integración y aceptación del producto (G07) | xUnit + coverlet | `dotnet test` (detalle y filtros en [docs/pruebas.md](docs/pruebas.md)) | `G07_Pruebas_Unitarias/` |
| Suite de negocio y cobertura (G07) | xUnit + coverlet | `..\G07_Pruebas_Unitarias\01_Suite\ejecutar_suite.ps1` | `G07_Pruebas_Unitarias/03_Reportes/` |
| Rendimiento (G08) | Apache JMeter (modo no gráfico) | `..\G08_Pruebas_Rendimiento\02_Scripts\ejecutar_todos.ps1` | `G08_Pruebas_Rendimiento/04_Resultados/` |
| Aceptación y regresión web (G09) | Selenium WebDriver 4.52.0 (Python) | con la API arrancada: `..\G09_Gestion_Calidad\02_Suite\ejecutar_suite.ps1 -Etiqueta <nombre>` | `G09_Gestion_Calidad/04_Reportes/` |

Los requisitos de cada suite (SDK, JMeter, Python y navegador) están en el
README o la ficha de herramientas de su carpeta.

## Gestión de configuración (SVN)

El proyecto se versiona en Apache Subversion (G05), con la estructura
`trunk/`, `branches/` y `tags/`:

- `trunk`: línea principal; contiene el producto y las carpetas G01 a G09.
- `branches/<ID>-<descripcion>`: una rama por cambio o defecto
  (`CC-03-portal-web`, `DEF-01-precio-catalogo`, `MEJ-01-correlativo-al-final`).
- `tags/vX.Y.Z`: líneas base de solo lectura que crea únicamente el
  responsable de configuración: `v0.1.0` (avance 1), `v0.2.0` (avance 2),
  `v1.0.0` (entrega final) y **`v1.0.1` (entrega final corregida, la que se entrega)**;
  `v1.0.1` solo añade documentación y evidencias, el código es el de `v1.0.0`.

Política, permisos y manifiesto en
`G05_Gestion_Configuracion/01_Politica/politica_configuracion.md`; historial
en `G05_Gestion_Configuracion/04_Evidencias/historial_svn.txt`.

> Durante los sprints 1 a 5 (versiones 0.1.0 a 1.0.0) el equipo usó Git y
> GitHub (`main`, `develop` y ramas `feature/T-XX`, tablero
> <https://github.com/users/ianthony4/projects/6>); desde la importación a SVN
> (r1–r2) la línea de control es el repositorio SVN.
