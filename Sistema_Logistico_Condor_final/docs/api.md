# Backend REST – Condor.Api (CC-01)

`src/Condor.Api` es un servicio ASP.NET Core 8 (Minimal API) que corre en la
**PC principal**, junto a PostgreSQL. Expone en HTTP las mismas reglas de
`Condor.Dominio` y los mismos repositorios de `Condor.Datos` que usa la app
de escritorio:

- el cálculo del IGV y las series;
- el correlativo con bloqueo de fila;
- las validaciones de DNI, RUC y productos.

```
PC-1, PC-2, PC-3 (CondorVentas.exe) ──HTTP──► Condor.Api (:5080, PC principal) ──Npgsql──► PostgreSQL 16
                     JMeter, integraciones ──HTTP──┘
```

Desde la versión 1.1.0 **las PC no se conectan a PostgreSQL**: la app de
escritorio usa el cliente `src/Condor.ClienteApi`, que implementa los mismos
repositorios de `Condor.Dominio.Contratos` llamando a las rutas
`/api/escritorio/*`. Solo la API tiene la clave de la base. Los ViewModels no
cambiaron. Los errores llegan como las mismas excepciones:

- API caída o base caída (503): `SinConexionException`, el aviso de conexión
  con Reintentar.
- Reglas de negocio (400/409): la excepción de `Condor.Dominio` con su mensaje.
- 403: acceso denegado.
- 401: sesión vencida.

Otros cambios en la app:

- El aviso de cambios del catálogo (T-13) se consulta cada 3 s en
  `GET /api/escritorio/catalogo/version`.
- El respaldo (HU-15) lo genera la API en la PC principal.

Las rutas públicas (`/api/productos`, `/api/comprobantes`...) son las que usan
JMeter y las integraciones; trabajan con DTO y con las mismas reglas.

**Arranque:** `CondorApi.exe` y `CondorVentas.exe` son dos programas. En la PC
principal, si `condor.json` tiene `Api > Backend` (la ruta de `CondorApi.exe`)
y la API no responde al abrir la app, la app la arranca en segundo plano.
`ejecutar.ps1` ya lo configura así.

## Arrancar

Con la base ya levantada (`.\ejecutar.ps1` la crea):

```powershell
.\ejecutar.ps1 -Api                                  # compila y arranca la API en http://localhost:5080
# o, con el SDK de .NET:
dotnet run --project src/Condor.Api
```

La configuración está en `src/Condor.Api/appsettings.json`. Cada valor se
puede cambiar con una variable de entorno de doble guion bajo:

| Clave | Para qué |
|---|---|
| `BaseDatos:*` | Igual que `condor.json`. `MaxConexiones` es el tamaño del pool de conexiones (20 por defecto). |
| `Jwt:Clave` | Firma de los tokens, de 32 caracteres o más. **Cambiarla en el local:** `$env:Jwt__Clave = "..."`. |
| `Jwt:MinutosValidez` | Duración del token (480 = un turno). |
| `Urls` | Dirección y puerto (`http://0.0.0.0:5080`). |

Al arrancar, la API aplica las migraciones y se registra como la terminal
`API-<equipo>`. Si la base no responde, reintenta cada 10 s, y
`GET /api/salud` responde 503 hasta que esté lista.

## Autenticación

1. `POST /api/auth/login` con `{"usuario":"vendedor1","clave":"Vendedor2026!"}`.
2. Enviar el `token` recibido en cada petición:
   `Authorization: Bearer <token>`.

Los usuarios, los roles y el bloqueo por intentos se explican en
[seguridad.md](seguridad.md).

## Rutas de la app de escritorio (`/api/escritorio`)

Las usa `Condor.ClienteApi` y envían como JSON las mismas entidades de
`Condor.Dominio`. Hay una ruta por cada método de los repositorios: productos,
clientes, comprobantes, envío a la SUNAT, guías, terminales, empresa y
respaldos para todos los roles; proveedores, compras, emitir y buscar guías,
y generar respaldos **solo para el Encargado**.

Controles en el servidor:

- `POST /api/escritorio/comprobantes` recalcula importes y totales.
- El usuario del comprobante sale del token, no de la petición
  (`Api/ClienteApiTests`).

## Rutas públicas

| Método y ruta | Rol | Respuestas |
|---|---|---|
| `GET /api/salud` | — | 200 `{estado:"OK"}` · 503 sin base o preparando |
| `POST /api/auth/login` | — | 200 token · 400 faltan datos · 401 incorrecto · 423 bloqueada |
| `GET /api/auth/yo` | todos | 200 usuario, nombre y rol |
| `GET /api/productos?texto=cem&limite=20` | todos | 200 lista (sin `texto`, el catálogo) |
| `GET /api/productos/codigo/{codigo}` | todos | 200 · 404 |
| `POST /api/productos` | todos | 201 · 400 con `errores` · 409 nombre o código repetido |
| `GET /api/clientes?texto=` | todos | 200 lista |
| `GET /api/clientes/{dni-o-ruc}` | todos | 200 · 404 · 400 si no tiene 8 u 11 dígitos |
| `POST /api/clientes` | todos | 201 · 400 (p. ej. RUC con dígito verificador inválido) · 409 |
| `POST /api/comprobantes` | todos | 201 comprobante emitido · 400 reglas · 503 base caída |
| `GET /api/comprobantes?desde=2026-11-20&hasta=2026-11-20&tipo=03&texto=` | todos | 200 `{cantidad,total,comprobantes}` |
| `GET /api/comprobantes/{id}` | todos | 200 con detalle · 404 |
| `GET /api/proformas?texto=` | todos | 200 lista con `estado` VIGENTE, VENCIDA o CONVERTIDA (CC-03) |
| `POST /api/proformas/{id}/convertir` | todos | 201 comprobante · 400 ya convertida u otra proforma · 404 no es proforma · 409 vencida (CC-03) |
| `GET /api/proveedores?texto=` · `POST /api/proveedores` | **Encargado** | 200/201 · 400 · 409 · 403 al Vendedor |
| `GET /api/compras?desde=&hasta=&proveedor=` · `POST /api/compras` | **Encargado** | 200/201 · 400 reglas de la compra · 409 comprobante repetido · 403 al Vendedor (CC-03) |
| `GET /api/reportes/ventas?desde=&hasta=` | **Encargado** | 200 reporte consolidado · 400 período inválido · 403 |
| `GET /api/respaldos` | **Encargado** | 200 últimos 10 respaldos · 403 |

Sin token, o con uno alterado o vencido, la respuesta es **401**. Los errores
vienen en formato `application/problem+json`, con `title` y, en las
validaciones, la lista `errores`.

### Emitir un comprobante

```http
POST /api/comprobantes
Authorization: Bearer <token>
Content-Type: application/json

{ "tipo": "BOLETA", "documentoCliente": null,
  "detalle": [ { "productoId": 1, "cantidad": 2 }, { "productoId": 5, "cantidad": 0.5 } ] }
```

- `tipo` puede ser `BOLETA`, `BOLETA_DNI`, `FACTURA`, `NOTA_VENTA` o `PROFORMA`.
- `documentoCliente` es el DNI o RUC de un cliente **ya registrado**. Es
  obligatorio en `BOLETA_DNI` y `FACTURA`, y también en la boleta de más de
  S/ 700.
- El **precio y la descripción salen del catálogo**. El cliente HTTP solo
  manda el Id del producto y la cantidad: cantidad mayor que 0, hasta 99 999,
  con 3 decimales como máximo y 100 líneas como máximo.
- El comprobante queda con el usuario del token y la terminal `API-<equipo>`.
  Las boletas y facturas quedan `PENDIENTE` de envío a la SUNAT.

## Portal web (CC-03)

`GET /` devuelve el portal web del mostrador (`src/Condor.Api/wwwroot`):
`index.html`, `css/portal.css`, `js/portal.js` e `img/` (los mismos recursos
de la app de escritorio). No necesita token para cargarse; al ingresar guarda
el JWT en `sessionStorage` y llama a las rutas de esta página. No tiene reglas
propias: el IGV, las series, las validaciones y los permisos los aplica la API.

Los controles tienen `id` estables (los mismos AutomationId de la app WPF)
para las pruebas Selenium de G09. Teclas: F1 a F9 y F12 abren los módulos, F10
emite y Esc cancela la venta o vuelve a Nueva venta.

## Ejemplos y pruebas

- `src/Condor.Api/Condor.Api.http`: peticiones listas para VS Code (REST
  Client) o Visual Studio.
- Pruebas automáticas en `tests/Condor.Pruebas/Api/ApiTests.cs`. Levantan la
  API en memoria con repositorios de prueba, sin PostgreSQL.

## Notas para JMeter (G8)

Transacciones críticas sugeridas:

1. `GET /api/productos?texto=…` (consultar).
2. `POST /api/comprobantes` (registrar una boleta).

Mezcla de operaciones sugerida: 70 % consulta y 30 % registro.

En cada hilo:

1. Hacer `POST /api/auth/login` una sola vez, en un *Once Only Controller*.
2. Extraer el token con un *JSON Extractor* (`$.token`).
3. Enviarlo en un *HTTP Header Manager* (`Authorization: Bearer ${token}`).

Validación de las respuestas: código 200 o 201 y una *JSON Assertion* sobre
`$.numero`. Cuentan como error un 4xx inesperado, un 5xx o un tiempo de espera
superado.

Parámetros que influyen en el rendimiento y conviene registrar:

- `BaseDatos:MaxConexiones`, el pool de conexiones. Con 50 usuarios y 20
  conexiones las peticiones esperan turno; subirlo es una mejora medible.
- Las 100 000 iteraciones de PBKDF2. Hacen el login deliberadamente lento,
  así que el login no debe ir dentro del bucle.
- El bloqueo de fila de la serie `B001`. Todas las boletas se numeran en
  serie, a propósito, para no repetir ni saltar números.

Para no ensuciar la base del local, ejecutar JMeter contra una base de
pruebas: definir `BaseDatos__BaseDatos=condor_pruebas` al arrancar la API.
