# Usuarios, roles y permisos (CC-01)

Desde la versión 1.1.0 el sistema pide **usuario y contraseña** al abrirse,
en la app de escritorio y en la API. Reemplaza el perfil único `MAESTRO` sin
credenciales de HU-14 (solicitud de cambio CC-01).

## Usuarios de demostración

Los crea la migración `V014__usuarios_y_roles.sql` la primera vez que se
abre el programa o se arranca la API.

| Usuario | Contraseña | Rol |
|---|---|---|
| `encargado` | `Encargado2026!` | Encargado general |
| `vendedor1` | `Vendedor2026!` | Vendedor |
| `vendedor2` | `Vendedor2026!` | Vendedor |

> Son datos de prueba. Antes de usar el sistema en el local hay que cambiar
> las contraseñas (ver más abajo).

## Qué puede hacer cada rol

| Módulo / ruta | Vendedor | Encargado general |
|---|:---:|:---:|
| F1 Nueva venta: boleta, factura, nota de venta, proforma | ✔ | ✔ |
| F2 Catálogo · F3 Clientes · F5 Historial · F7 Proformas | ✔ | ✔ |
| F4 Compras · F6 Proveedores · F8 Guías · F9 Respaldo | ✘ | ✔ |
| API: `/api/productos`, `/api/clientes`, `/api/comprobantes` | ✔ | ✔ |
| API: `/api/proveedores`, `/api/reportes/ventas`, `/api/respaldos` | ✘ (403) | ✔ |

- En la app, el Vendedor **no ve** los botones de Compras, Proveedores, Guías
  ni Respaldo, ni el aviso de respaldo vencido. Si pulsa su tecla (F4, F6,
  F8, F9), se queda en Nueva venta y el pie muestra «Acceso denegado: el
  módulo … es solo para el Encargado general».
- La app ya no se conecta a la base: cada operación pasa por la API, que
  vuelve a comprobar el rol. Aunque alguien modificara la app, el servidor
  respondería 403 en esas rutas. La regla está en
  `src/Condor.Presentacion/ViewModels/PermisosModulo.cs` y la aplica
  `MainViewModel.IrA`, por donde pasan el menú y las teclas F1 a F9.
- En la API, las rutas del Encargado exigen la política `Encargado`
  (`RequireRole("ENCARGADO")`) y responden 403 a un Vendedor.
- Cada comprobante guarda en `comprobante.usuario` el nombre de usuario de
  quien lo emitió y la terminal. Los emitidos antes de CC-01 conservan `MAESTRO`.

## Reglas del ingreso

Están en `src/Condor.Dominio/Seguridad/ServicioAutenticacion.cs` y son las
mismas para la app y la API:

1. Si falta el usuario o la contraseña, no se consulta la base de datos.
2. Un usuario que no existe, una cuenta inactiva y una contraseña equivocada
   dan el **mismo mensaje**: «Usuario o contraseña incorrectos.».
3. **5 contraseñas equivocadas seguidas** bloquean la cuenta **15 minutos**.
   Mientras dura el bloqueo no se entra ni con la contraseña correcta. La API
   responde 423.
4. Un ingreso correcto pone en cero los intentos fallidos.
5. Cada intento, correcto o fallido, queda en la tabla `acceso_usuario` con la
   terminal (o `API <ip>`), la fecha y el motivo.

Las contraseñas se guardan con **PBKDF2-SHA256, 100 000 iteraciones y sal
aleatoria de 16 bytes**, en el formato `pbkdf2-sha256$iteraciones$sal$hash`
(`HashClave.cs`). La contraseña nunca se guarda ni se muestra.

## Cerrar sesión

El botón **Cerrar sesión** del menú hace lo siguiente:

1. Descarta la venta en curso y vuelve a Nueva venta.
2. Oculta la ventana principal y muestra otra vez **Ingresar**.
3. Con **Salir**, el programa se cierra.

No se puede cerrar sesión mientras se genera un respaldo.

## Administración (sin pantalla)

La versión 1.1.0 no tiene una pantalla de usuarios. El Encargado los
administra con `psql` en la PC principal.

```sql
-- Desbloquear una cuenta antes de los 15 minutos
UPDATE usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE nombre_usuario = 'vendedor1';

-- Dar de baja a un vendedor (conserva sus comprobantes)
UPDATE usuario SET activo = false WHERE nombre_usuario = 'vendedor2';

-- Últimos accesos
SELECT fecha, nombre_usuario, terminal, exitoso, detalle FROM acceso_usuario ORDER BY fecha DESC LIMIT 20;
```

Para crear un usuario o cambiar una contraseña hace falta su hash:

1. Generarlo con `Condor.Dominio.Seguridad.HashClave.Generar("NuevaClave")`,
   por ejemplo desde una prueba unitaria temporal.
2. Ponerlo en el `INSERT` o en el `UPDATE usuario SET hash_clave = '…'`.

## Relación con la gestión de riesgos (G6)

| Control | Riesgo que reduce | Dónde se prueba |
|---|---|---|
| Autorización por roles (app y API) | Uso indebido de compras, respaldos y proveedores | `Aceptacion/CC01_IngresoConRolesTests`, `Api/ApiTests` (403) |
| Contraseñas con hash y bloqueo por intentos | Acceso no autorizado, fuerza bruta | `Dominio/HashClaveTests`, `Dominio/ServicioAutenticacionTests`, `Datos/UsuarioRepositorioTests` |
| Bitácora de accesos | Falta de trazabilidad | `Datos/UsuarioRepositorioTests` |
| Validación de entradas en la API | Datos corruptos o manipulados (precio enviado por el cliente) | `Api/ApiTests` (400) |
| Respaldo manual (HU-15) | Pérdida de datos | `Aceptacion/HU15_RespaldoTests` |
