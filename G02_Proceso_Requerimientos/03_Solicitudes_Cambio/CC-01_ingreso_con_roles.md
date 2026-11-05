# CC-01 · Ingreso con usuario, contraseña y roles; backend REST

| Campo | Valor |
|---|---|
| ID | CC-01 (Redmine: petición «CC-01», tipo *Solicitud de cambio*) |
| Fecha de registro | 2026-10-30 |
| Solicitante | Gerente general (representado por Integrante 2) y docente del curso |
| Registró | Gerente general (usuario `gerente` en Redmine) |
| Analizó | Integrante 2 — Payehuanca Riquelme, Jhastyn Jefferson |
| Decidió | Comité de cambios (CCB): gerente general, Integrante 1 e Integrante 2 |
| Prioridad | Alta |
| Línea base afectada | ERS 1.0 (2026-10-29) → ERS 1.1 (2026-10-30) |
| Versión del producto afectada | 1.0.0 → **1.1.0** |
| Decisión | **Aprobada** |
| Estado final | **Cerrado** (implementado y verificado) |

## 1. Descripción del cambio

Reemplazar el acceso con el perfil único MAESTRO, que abre Nueva venta sin pedir usuario ni contraseña (RF-01 de la ERS 1.0, criterio de HU-14), por:

- ingreso con usuario y contraseña, con bloqueo tras 5 intentos fallidos y bitácora de accesos;
- dos roles, Vendedor y Encargado general, que limitan los módulos de la aplicación y las rutas de la API;
- un backend REST (Condor.Api) que concentra el acceso a PostgreSQL y ofrece un reporte consolidado de ventas.

## 2. Motivo

1. **Del cliente.** El gerente necesita saber quién emitió cada comprobante. Con MAESTRO todos los comprobantes dicen lo mismo (ENT-01, pregunta A5). Además, no quiere que los vendedores vean costos, compras ni respaldos (CFL-06).
2. **Del curso.** El enunciado exige autenticación, autorización según roles, un reporte consolidado y rutas HTTP evaluables con JMeter (G08). La ERS 1.0 no cumplía ninguna de las cuatro exigencias.
3. **Conflicto CFL-01.** Los vendedores pedían rapidez sin contraseña. El cuestionario CUE-01 mostró que el 100 % rechaza escribir la contraseña en cada venta, pero el 75 % la acepta una vez por turno. El cambio se diseñó con esa condición.

## 3. Análisis de impacto

### 3.1 Requisitos (ERS)

| Elemento | Impacto |
|---|---|
| RF-01 | Se reescribe: «Acceder con el perfil MAESTRO» pasa a «Iniciar sesión», con 4 criterios de aceptación nuevos. |
| RF-02 Cerrar sesión | Nuevo. |
| RF-03 Restringir módulos según el rol | Nuevo. |
| RF-07 | Se agrega CA-07.5: el comprobante guarda el usuario de la sesión, no el que envía la terminal. |
| RF-15 Reporte consolidado de ventas | Nuevo. |
| RNF-02 Capacidad de la API | Nuevo: p95 ≤ 2 s con 10 usuarios. |
| RNF-03 Protección de credenciales | Nuevo: PBKDF2, bloqueo y 100 % de rutas protegidas. |
| CRQ-11, CRQ-12, IRQ-08 | Nuevas reglas de autoría y de funciones exclusivas, y la información de usuarios. |
| CFL-01 | Pasa de abierto a resuelto. |

Total: **1 requisito reescrito, 1 ampliado y 5 nuevos.** La ERS pasa de 13 RF y 6 RNF a 16 RF y 8 RNF.

### 3.2 Diseño

| Componente | Cambio |
|---|---|
| Base de datos | Migración `V014__usuarios_y_roles.sql`: tablas `usuario` (hash, rol, intentos, bloqueo) y `acceso_usuario` (bitácora); `comprobante.usuario` guarda el usuario real. |
| Condor.Dominio | `Seguridad/HashClave`, `Seguridad/ServicioAutenticacion`, `Seguridad/Roles`, `Reportes/ReporteVentas`. |
| Condor.Api (nuevo) | ASP.NET Core 8 con JWT y la política `Encargado`; rutas de ingreso, productos, clientes, comprobantes, proveedores, respaldos y `/api/reportes/ventas`. |
| Condor.ClienteApi (nuevo) | La aplicación WPF deja de conectarse a PostgreSQL y llama a la API. |
| Condor.Presentacion / Escritorio | Ventana Ingresar (`LoginWindow`), botón Cerrar sesión, `PermisosModulo` por rol y pie con usuario y rol. |
| Arquitectura | De cliente pesado contra la base a **cliente – API – base**. El SDD de G03 debe describirse con esta arquitectura. |
| Documentos de diseño del producto | `docs/seguridad.md`, `docs/api.md` (nuevos) y `docs/modelo_datos.md` (actualizado). |

### 3.3 Costo

Tarifa de referencia: **S/ 25.00 por hora**, la misma tarifa que debe usar G04.

| Actividad | Horas |
|---|---|
| Análisis, actualización de la ERS 1.1 y de REMUS | 6 |
| Migración V014 y repositorio de usuarios | 4 |
| Hash, autenticación y bloqueo (dominio) | 5 |
| Ventana Ingresar, cierre de sesión y permisos por rol | 6 |
| Backend REST con JWT, políticas y reporte consolidado | 14 |
| Cliente HTTP de la aplicación (Condor.ClienteApi) | 8 |
| Pruebas unitarias, de aceptación, de API y de integración | 10 |
| Documentación (seguridad, API, modelo de datos) | 3 |
| **Total** | **56 h ≈ S/ 1 400.00** |

### 3.4 Plazo

56 horas-persona. Con los 4 integrantes a unas 4 h por día, son unos 4 días hábiles. Se absorbe dentro del incremento 1 y **no mueve el hito del 11-11-2026**. A cambio, G03 (SDD) y G04 (estimación) arrancan con la línea base 1.1 en lugar de la 1.0.

### 3.5 Riesgos

| Riesgo | Tratamiento |
|---|---|
| El ingreso hace más lenta la venta en hora punta (CFL-01). | El token dura 480 minutos: se ingresa una vez por turno y la aplicación abre directamente Nueva venta. |
| Si la API se cae, ninguna PC puede vender. | La aplicación arranca `CondorApi.exe` en la PC principal y muestra un aviso con Reintentar. Este riesgo pasa a G06. |
| Exposición de contraseñas. | Solo se guarda el hash PBKDF2-SHA256 con sal. El mismo mensaje para un usuario inexistente o una clave equivocada. Bloqueo a los 5 intentos. |
| Regresión en la emisión, que ahora pasa por la API. | Se repite la suite completa y la regresión específica de CC-01 (sección 3.6). |
| Un vendedor llama a una ruta del Encargado directamente por HTTP. | Política `Encargado` en el servidor: responde 403. Se prueba en `Api/ApiTests`. |

### 3.6 Pruebas afectadas

- **Nuevas:** `Dominio/HashClaveTests`, `Dominio/ServicioAutenticacionTests`, `Dominio/ReporteVentasTests`, `Presentacion/LoginViewModelTests`, `Aceptacion/CC01_IngresoConRolesTests`, `Api/ApiTests`, `Api/ClienteApiTests`, `Datos/UsuarioRepositorioTests`.
- **A repetir:** la suite completa, porque la emisión, el historial y el respaldo ahora pasan por la API.
- **Previstas en otras guías:** G08 (consultar productos y emitir boleta por HTTP) y G09 (acceso correcto, credenciales inválidas, restricción por rol y cierre de sesión).

## 4. Decisión

**Aprobada por el CCB el 2026-10-30.** El cambio responde a una necesidad del cliente y a una exigencia del curso, su costo es moderado (56 h) y no mueve el hito. El riesgo principal, la rapidez en el mostrador, queda mitigado con la sesión por turno. La versión objetivo es la **1.1.0**.

## 5. Implementación y verificación

| Elemento | Evidencia |
|---|---|
| ERS | ERS 1.1 (`G01_Requerimientos/01_ERS/ERS_Condor_v1.1.md`, apéndice B) y `condor.rem` regenerado en REMUS. |
| Diseño | `docs/seguridad.md`, `docs/api.md` y `docs/modelo_datos.md`. Al cerrar el cambio se encontró que `modelo_datos.md` seguía diciendo «usuario siempre MAESTRO» y le faltaban las tablas de V014; se corrigió y quedó anotado en el `CHANGELOG`. |
| Código | Versión **1.1.0** del producto (`CHANGELOG.md`, sección 1.1.0): V014, Condor.Api, Condor.ClienteApi, `ServicioAutenticacion`, `LoginWindow`, `PermisosModulo`. |
| Pruebas: regresión de CC-01 | `04_Pruebas/regresion_CC-01.trx` y `.html`: **130 de 130 aprobadas**, incluidas las de PostgreSQL (`UsuarioRepositorioTests`). |
| Pruebas: suite completa | `04_Pruebas/suite_completa_v1.1.0.trx` y `.html`: **923 aprobadas, 0 fallidas, 5 omitidas.** Las omitidas necesitan la SUNAT beta real o el `pg_dump` real del servidor. |
| Cierre | Redmine: CC-01 pasa por Registrado → Analizado → Aprobado → Implementado → Verificado → Cerrado. Las pruebas se ejecutaron el 2026-10-30. |

Comando de la regresión (desde `Sistema_Logistico_Condor_final`, con el SDK de .NET 8 o dentro del contenedor `mcr.microsoft.com/dotnet/sdk:8.0`):

```
dotnet test tests/Condor.Pruebas/Condor.Pruebas.csproj --filter "FullyQualifiedName~CC01|FullyQualifiedName~Api|FullyQualifiedName~Autenticacion|FullyQualifiedName~HashClave|FullyQualifiedName~LoginViewModel|FullyQualifiedName~ReporteVentas|FullyQualifiedName~UsuarioRepositorio" --logger "trx;LogFileName=regresion_CC-01.trx"
```

Pendiente para G05: registrar esta versión en SVN y etiquetarla, para que el cambio quede vinculado a una revisión.
