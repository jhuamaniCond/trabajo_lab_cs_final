# Cambios

## 1.2.0 – CC-03: portal web del mostrador

Solicitud de cambio CC-03 (aprobada): el trabajo del curso exige una interfaz
web automatizable con Selenium WebDriver (G09) y el producto solo tenía la app
de escritorio WPF. Desarrollada en la rama SVN `branches/CC-03-portal-web`.

### Portal web (`src/Condor.Api/wwwroot`)
- `Condor.Api` sirve el portal en `http://<PC principal>:5080/` (archivos
  estáticos). Es HTML, CSS y JavaScript sin dependencias externas y usa las
  mismas rutas `/api` con el token JWT: no tiene reglas propias.
- Replica las pantallas de la app de escritorio: ventana Ingresar, menú
  lateral con la marca, la greca y el Misti, pie con usuario, rol y conexión,
  y la paleta «Majes» de `Estilos/Tema.xaml`. Los `id` de los controles son
  los mismos AutomationId de la app (`CampoUsuario`, `CampoClave`,
  `BotonIngresar`, `TextoError`, `MenuVenta`... `MenuCerrarSesion`,
  `TextoUsuario`, `TextoMensaje`).
- Módulos: Nueva venta (búsqueda con sugerencias, cantidad, detalle, cliente
  por DNI o RUC, boleta, boleta con DNI, factura, nota de venta y proforma,
  totales con IGV, F10 emite), Catálogo y Nuevo producto, Clientes y Nuevo
  cliente, Historial con filtros y total del período, Proformas con su estado
  y Convertir en venta, y, solo para el Encargado general, Compras y Nueva
  compra, Proveedores y Nuevo proveedor, Reporte consolidado de ventas y
  Respaldos. Las Guías de remisión siguen solo en la app de escritorio.
- Permisos por rol como en la app (`PermisosModulo`): el Vendedor no ve los
  módulos del Encargado y, si los pide por la dirección o con su tecla, se queda
  en Nueva venta con «Acceso denegado: el módulo … es solo para el Encargado
  general». La API vuelve a responder 403.

### Rutas nuevas
- `GET /api/proformas?texto=` (todos): proformas con su estado `VIGENTE`,
  `VENCIDA` o `CONVERTIDA` y el comprobante en que se convirtió.
- `POST /api/proformas/{id}/convertir` (todos) con `{tipo, documentoCliente}`:
  convierte la proforma en boleta, boleta con DNI, factura o nota de venta con
  las líneas y precios cotizados (HU-09). Las reglas son las de
  `EmisionComprobante`: 400 si ya se convirtió o si se pide otra proforma, 404
  si no es una proforma y 409 si la base la rechaza por vencida.
- `GET /api/compras?desde=&hasta=&proveedor=` y `POST /api/compras`
  (**Encargado**): compras a proveedores (HU-11) con las reglas de
  `ValidadorCompra`; el servidor toma la descripción del catálogo y recalcula
  importes e IGV. 400 si no cumple las reglas, 409 si el comprobante del
  proveedor ya está registrado, 403 al Vendedor.
- Versión de `Condor.Api` y `Condor.Escritorio` en 1.2.0.

### Correcciones halladas por la suite Selenium (G09)
- DEF-03: la lista de Compras mostraba 0 en la columna Líneas porque la
  búsqueda trae solo las cabeceras. Ahora muestra Op. gravada, IGV y Total, y
  `CompraDto.lineas` es null cuando no se cargó el detalle.
- DEF-04: al convertir una proforma en venta quedaba a la vista el aviso verde
  de la emisión anterior. Ahora se oculta al cargar la proforma.

### Pruebas
- `Api/PortalWebTests` (11): el portal se sirve sin token, la lista de
  proformas, la conversión (número, total, usuario y estado CONVERTIDA), la
  doble conversión, la conversión en otra proforma, un comprobante que no es
  proforma, la ruta sin token, la compra con totales recalculados, la compra
  repetida (409), la compra inválida (400) y el Vendedor (403).
  Suite: 944 aprobadas, 0 fallidas, 5 omitidas.
- Pruebas de aceptación y regresión web con Selenium WebDriver en
  `G09_Gestion_Calidad`.

## 1.1.2 – MEJ-01: el correlativo de la serie se reserva al final de la emisión

Mejora de rendimiento hallada en las pruebas de rendimiento (G08). En la prueba
de capacidad sin pausas, desde 25 usuarios, las boletas se encolaban en el
bloqueo de la fila de la serie B001 (19 de las 20 conexiones del pool esperando
ese bloqueo) y, al ocupar el pool, también hacían esperar a las consultas de
productos. Desarrollada en la rama SVN `branches/MEJ-01-correlativo-al-final`.

### Cambios
- `ComprobanteRepositorio.EmitirAsync` guarda primero la cabecera (con un número
  provisional `-id`, invisible fuera de la transacción) y las líneas, y recién
  al final numera con `SerieRepositorio.NumerarComprobanteAsync` (una sola
  sentencia: incrementa la serie y pone el número). La fila de la serie queda
  bloqueada solo durante esa sentencia y el COMMIT. Se mantienen las reglas de
  HU-16: ningún número repetido ni saltado; un error deshace también el número.
- Versión de los ensamblados de `Condor.Api` y `Condor.Escritorio` en 1.1.2
  (seguían en 1.1.0 desde CC-01).

### Pruebas
- `Datos/MEJ01_CorrelativoAlFinalTests`: tres PC emitiendo a la vez con el
  repositorio real (90 boletas, números 1 a 90), una emisión fallida que no
  consume número ni deja el provisional, y que la serie solo se bloquea al
  numerar.
- G08: prueba de capacidad y los cuatro escenarios repetidos antes y después
  (`G08_Pruebas_Rendimiento/04_Resultados`).

## 1.1.1 – DEF-01 y CRQ-14 en la ruta de escritorio

Corrección del defecto DEF-01, encontrado en la revisión del SDD (G03), y
validación de CRQ-14 en el servidor. Desarrollado en la rama SVN
`branches/DEF-01-precio-catalogo` e integrado en trunk en la revisión r11 (G05).

### Correcciones
- DEF-01 (CRQ-07): `POST /api/escritorio/comprobantes` ya no guarda el precio
  ni la descripción que envía la PC. Toma los del catálogo o, si la venta sale
  de una proforma, los de la proforma guardada (el precio cotizado se respeta
  mientras esté vigente, HU-09). Un producto que no está en el catálogo se
  rechaza con 400.
- CRQ-14: la misma ruta rechaza con 400 más de 100 líneas y cantidades fuera de
  rango (≤ 0, > 99 999 o con más de 3 decimales), igual que la ruta pública.

### Pruebas
- `Api/ClienteApiTests`: 3 pruebas de DEF-01 (fallan con el código 1.1.0) y 4
  de CRQ-14. Suite: 930 aprobadas, 0 fallidas, 5 omitidas.

## 1.1.0 – CC-01: ingreso con usuario, contraseña y roles; backend REST

Solicitud de cambio CC-01 (aprobada): el trabajo del curso exige
autenticación, autorización según roles y rutas HTTP evaluables con JMeter.
Cambia el criterio de HU-14 («sin pedir usuario ni contraseña»).

### Ingreso y roles
- Migración V014: tablas `usuario` (hash PBKDF2-SHA256, rol, intentos
  fallidos, bloqueo) y `acceso_usuario` (bitácora de accesos). Crea tres
  usuarios de demostración (docs/seguridad.md).
- `ServicioAutenticacion`: el mismo mensaje para usuario inexistente y clave
  equivocada; 5 intentos fallidos bloquean la cuenta 15 minutos; cada intento
  queda en la bitácora.
- Ventana **Ingresar** antes de Nueva venta y botón **Cerrar sesión** en el menú.
- Roles Vendedor y Encargado general: el Vendedor no abre Compras (F4),
  Proveedores (F6), Guías (F8) ni Respaldo (F9) y se le muestra «Acceso denegado».
- El pie muestra el usuario y su rol; cada comprobante guarda el usuario que
  lo emitió (antes, siempre MAESTRO).
- AutomationId estables en la ventana Ingresar, el menú y el pie, para las
  pruebas automáticas de interfaz.

### Backend REST (`src/Condor.Api`)
- ASP.NET Core 8 con tokens JWT y la política `Encargado`; usa las mismas
  reglas de Condor.Dominio y los mismos repositorios de Condor.Datos.
- Rutas de salud, ingreso, productos, clientes, comprobantes (emitir,
  historial y detalle), proveedores, respaldos y **reporte consolidado de
  ventas** (por día, tipo, terminal y usuario). docs/api.md.
- El precio de cada línea sale del catálogo, no de la petición. Los errores
  de las reglas responden 400, los duplicados 409 y la base caída 503.
- `ejecutar.ps1 -Api` compila y arranca la API. `MaxConexiones` en la
  configuración de la conexión (pool de Npgsql).

### La app usa el backend (ya no se conecta a PostgreSQL)
- `src/Condor.ClienteApi`: repositorios que llaman a `/api/escritorio/*`. Los
  errores llegan como las mismas excepciones de antes: sin conexión, reglas
  de negocio, acceso denegado y sesión vencida.
- `condor.json` de cada PC: sección `Api` (`Url`, `Backend`). Ya no lleva la
  clave de la base. El aviso de cambios del catálogo se consulta a la API
  cada 3 s y el respaldo lo genera la API en la PC principal.
- En la PC principal la app arranca `CondorApi.exe` si no está corriendo.
- `POST /api/escritorio/comprobantes` recalcula los totales y toma el usuario del token.

### Interfaz
- El Vendedor ya no ve los botones de Compras, Proveedores, Guías ni Respaldo
  ni el aviso de respaldo vencido.
- Resumen de venta más compacto: TOTAL y monto en una línea, siempre visibles.
- Columnas más anchas en Compras (fecha, RUC, terminal), Guías (traslado),
  Proformas (documento) e Historial (tipo); los filtros del Historial caben
  en una línea.

### Datos de demostración
- `herramientas/Condor.DatosDemo`: 32 clientes, 26 proveedores, 45 ventas,
  26 proformas (6 convertidas), 28 compras y 26 guías en los últimos 30 días,
  con usuarios y terminales repartidos. Cada sección se carga solo si tiene
  menos de 25 registros. `ejecutar.ps1` la ejecuta al crear la base.

### Pruebas
- Cliente y API juntos: `Api/ClienteApiTests` y `Api/ConfiguracionApiTests`.
- Unitarias: `HashClaveTests`, `ServicioAutenticacionTests`,
  `ReporteVentasTests` y `LoginViewModelTests`.
- Aceptación: `CC01_IngresoConRolesTests`.
- API en memoria: `ApiTests`.
- Integración con PostgreSQL: `UsuarioRepositorioTests`.
- Cobertura con coverlet (docs/pruebas.md).

### Documentación
- `docs/modelo_datos.md`: tablas `usuario` y `acceso_usuario` y columna
  `comprobante.usuario` actualizadas al cerrar CC-01 (antes seguían diciendo
  «siempre MAESTRO»).

## 1.0.0 – Sprint 5, entrega final (18 al 24 de noviembre de 2026)

Objetivo del sprint: terminar el backlog del producto en la última semana —
notas de venta, proformas que se convierten en venta, historial de ventas,
compras a proveedores, guías de remisión electrónicas y lector de código de
barras—, cerrar el pendiente del código 1033 de la SUNAT y dejar el sistema
listo para la puesta en producción. Sprint de una semana.

### HU-08 · Emitir notas de venta
- Reglas de la nota de venta: serie NV01, cliente opcional, sin el tope de
  S/ 700 de la boleta; `Comprobante.EsElectronico` distingue lo que va a la
  SUNAT (T-66).
- Ticket de la nota de venta con el total y la leyenda «Documento interno de
  control», sin desglosar el IGV (T-67).
- Opción Nota venta en el resumen de venta; no se envía a la SUNAT ni cuenta
  como pendiente (T-68).
- Pruebas de aceptación, incluidas notas de venta desde tres PC a la vez (T-69).

### HU-09 · Emitir proformas y convertirlas en venta
- Migración V011: vigencia de la proforma (7 días contando el de emisión) y
  enlace de la venta con su proforma; la base central admite una sola
  conversión por proforma y rechaza las vencidas (T-70).
- Búsqueda de proformas por número, DNI, RUC o nombre del cliente (T-71).
- Ticket de la proforma con «Válida hasta» y la leyenda de cotización (T-72).
- Opción Proforma y módulo Proformas (F7): Convertir en venta lleva el
  detalle y el cliente a la pantalla y propone factura o boleta. Los módulos
  del menú (F1 a F9) se abren en el panel derecho de la ventana principal en
  lugar de ventanas aparte; Esc o F1 vuelven a Nueva venta (T-73).
- Pruebas de aceptación, incluida la misma proforma convertida desde dos PC (T-74).

### HU-18 · Historial de ventas y reimpresión
- Búsqueda de comprobantes por fechas (días de Perú), tipo, cliente o número,
  con el total de ventas del período sin proformas ni rechazados (T-75).
- Historial (F5) con filtros, botones Hoy, Este mes y Todo, el total sobre la
  lista y «No aplica» en la columna SUNAT de los documentos internos (T-76).
- El ticket reimpreso sale marcado «COPIA - REIMPRESIÓN» (T-77).
- Pruebas de aceptación (T-78).

### HU-11 · Registrar compras a proveedores
- Migración V012 y repositorio de compras: un mismo comprobante del proveedor
  no se registra dos veces aunque dos PC lo intenten a la vez (T-79).
- Entidad Compra y sus reglas (T-80); diálogo Nueva compra (T-81); módulo
  Compras (F4) con el total de egresos del período (T-82).
- Pruebas de aceptación (T-83).

### HU-13 · Ingreso con lector de código de barras
- Búsqueda y asignación del código de barras en el catálogo; un código no
  puede ser de dos productos (T-86).
- Pasar un producto por el lector en Nueva venta lo agrega con una unidad;
  campo Código de barras en Nuevo producto (T-87).
- Módulo Catálogo (F2): buscar por nombre o leyendo el código y asignar el
  código a los productos que ya estaban (T-88).
- Pruebas de aceptación (T-89).

### HU-10 · Emitir guías de remisión electrónicas
- Migración V013: serie T001 y tablas de guías con su respuesta de la SUNAT;
  la base central exige los datos del transporte según la modalidad (T-90).
- Entidad GuiaRemision y sus reglas: motivo, fechas, ubigeos, peso,
  transportista o vehículo y conductor; guía desde una factura o boleta (T-91).
- XML UBL 2.1 DespatchAdvice firmado (T-92).
- Envío por la API REST de guías: token OAuth2, ticket y CDR; credenciales
  `ClientId` y `ClientSecret` en condor.json (T-93).
- Módulo Guías (F8) y diálogo Nueva guía: se imprime y se envía al emitir;
  las pendientes se reenvían o consultan solas (T-94).
- Representación impresa de la guía en la ticketera (T-95).
- Pruebas de aceptación (T-96).

### Transversales
- Consulta del CDR con getStatusCdr cuando la SUNAT responde 1033 (T-84).
- Datos de prueba de notas de venta, proformas y compras (T-85) y de guías y
  códigos de barras con la API de guías falsa (T-98).
- Módulo Clientes (F3): ningún módulo del menú queda «para un próximo
  sprint» (T-97).
- Puesta en producción: aviso al abrir el sistema de lo que falta (datos de
  la empresa, certificado y su vencimiento, usuario SOL, credenciales de la
  API de guías) y guía docs/produccion.md (T-99).

## 0.4.0 – Sprint 4 (11 al 17 de noviembre de 2026)

Objetivo del sprint: atender a las empresas y obras con factura, que ningún
comprobante se quede sin llegar a la SUNAT cuando se cae internet y no perder
la información ante un corte de energía. Sprint de una semana.

### HU-06 · Emitir factura electrónica con RUC
- Opción Factura en el resumen de venta: el campo del cliente pasa a pedir el
  RUC y recibe el foco; sin un cliente con RUC no se emite (T-51).
- Ticket de la factura con razón social, RUC y dirección del cliente y forma
  de pago Contado (T-52).
- Migración V008: la base central rechaza una factura sin cliente con RUC,
  aunque venga de una PC con una versión vieja (T-53).
- Pruebas de aceptación, incluidas facturas desde tres PC a la vez (T-54).

### HU-17 · Reenvío automático de pendientes a SUNAT
- Migración V009: cada PC aparta los pendientes antes de reenviarlos; dos PC
  nunca envían el mismo comprobante y la reserva vence si la PC se apaga (T-55).
- Reenvío en segundo plano del más antiguo al más reciente, con espera
  creciente entre intentos; si se corta internet se detiene sin gastar
  intentos (T-56).
- `ReenvioMinutos` en la sección Sunat de condor.json (T-57).
- Pie de la pantalla de venta con los pendientes y aviso en rojo si el más
  antiguo está por vencer el plazo de 3 días; botón Reenviar a la SUNAT en el
  Historial (T-58).
- Pruebas de aceptación (T-59).

### HU-15 · Respaldo manual de la base de datos
- Migración V010 y registro de los respaldos en la base central (T-60).
- Respaldo con pg_dump (formato personalizado) en el disco externo, con la
  fecha y la hora en el nombre y el avance tabla por tabla; sin archivos a
  medias si algo falla (T-61).
- Ventana Respaldo (F9) con la carpeta del disco, barra de progreso y
  confirmación (T-62).
- Aviso al abrir el sistema si el último respaldo tiene más de 24 horas
  (`AvisoHoras` de la sección Respaldo) (T-63).
- Pruebas de aceptación, también con el pg_dump real, y guía de respaldo y
  restauración docs/respaldo.md (T-64).

### Transversales
- Datos de prueba de facturas, respaldos y pendientes; SUNAT falsa que se
  queda sin internet a mitad y admite varios hilos; corrección de una prueba
  de HU-07 que fallaba a veces (T-65).

### Pendiente para el Sprint 5
- Consultar el CDR con getStatusCdr cuando la SUNAT dice que el comprobante ya
  fue recibido (código 1033).
- Notas de venta, proformas, compras a proveedores e historial completo
  (HU-08, HU-09, HU-11, HU-18).
- Pasar a producción con el certificado digital y el usuario SOL de la ferretería.

## 0.3.0 – Sprint 3 (4 al 10 de noviembre de 2026)

Objetivo del sprint: que cada boleta emitida llegue sola a la SUNAT y quede
guardada su constancia (CDR), sin frenar la venta cuando falla el internet;
y tener registrados a los proveedores para las compras. Sprint de una semana.

### HU-04 · Registrar proveedores
- Entidad Proveedor y sus reglas: RUC válido, razón social, teléfono y correo
  (T-36).
- Migración V006 y repositorio de proveedores, un solo proveedor por RUC aunque
  dos PC lo registren a la vez; búsqueda por RUC o razón social sin tildes
  (T-37).
- Diálogo Nuevo proveedor con los datos comerciales (T-38).
- Ventana Proveedores (F6) con búsqueda y + Nuevo proveedor (T-39).
- Pruebas de aceptación (T-40).

### HU-07 · Enviar a SUNAT y guardar el CDR
- Proyecto Condor.Sunat, basado en Greenter / sunat-manager: XML UBL 2.1 de la
  boleta y la factura (T-41), firma digital XMLDSig con el certificado (T-42),
  lectura del CDR y estados aceptado, observado, rechazado o pendiente (T-43)
  y envío del ZIP por sendBill con la clave SOL (T-44).
- Migración V007: domicilio fiscal de la empresa y tabla comprobante_sunat con
  el XML firmado, el CDR y los intentos (T-45).
- Sección Sunat de condor.json: ambiente beta o producción, usuario y clave
  SOL y certificado (T-46).
- Envío al emitir, en paralelo con la impresión: el resultado se ve bajo
  Emitir; sin internet el ticket sale igual y queda pendiente (T-47).
- Columna SUNAT en el Historial (F5) con el motivo de los pendientes y
  rechazados (T-48).
- Pruebas de aceptación con la SUNAT simulada y contra el ambiente beta real,
  y guía docs/sunat.md (T-49).

### Transversales
- Datos de prueba de proveedores, SUNAT falsa y repositorios en memoria (T-50).

### Pendiente para el Sprint 4
- Reenvío automático de los comprobantes pendientes (HU-17).
- Factura con RUC desde la pantalla de venta (HU-06); el XML ya la soporta.
- Pasar a producción con el certificado digital y el usuario SOL de la ferretería.

## 0.2.0 – Sprint 2 (21 de octubre al 3 de noviembre de 2026)

Objetivo del sprint: que el vendedor emita la boleta de la venta, con o sin
DNI, y la entregue impresa en la ticketera sin pasos adicionales.

### HU-03 · Registrar o buscar cliente por DNI/RUC
- Validación del DNI (8 dígitos) y del RUC (11 dígitos, prefijo y dígito
  verificador módulo 11) (T-21).
- Repositorio de clientes en la base central, sin documentos repetidos (T-22).
- Panel Cliente en Nueva venta: un solo campo DNI o RUC; Buscar completa el
  nombre o la razón social y la dirección (T-23).
- Diálogo Nuevo cliente: el cliente queda registrado y elegido en la venta (T-24).
- Pruebas de aceptación (T-25).

### HU-05 · Emitir boleta con o sin DNI
- Migración V005: datos de la empresa, impresiones por comprobante y control
  de que gravada + IGV = total (T-26).
- Reglas de emisión: serie B001, boleta con DNI y DNI obligatorio en boletas
  de más de S/ 700.00 (T-27).
- Emisión en una sola transacción: correlativo, cabecera y detalle; si algo
  falla no queda nada a medias ni números saltados (T-28).
- Botón Emitir e imprimir (F10) con el tipo Boleta / Con DNI; sin conexión,
  la venta se conserva para reintentar (T-29).
- Pruebas de aceptación y emisión simultánea desde tres PC (T-30).

### HU-12 · Imprimir en la ticketera térmica
- Ticket de 80 mm con RUC, tipo y número, cliente, detalle, op. gravada,
  IGV, total y el importe en letras (T-31).
- Proyecto Condor.Impresion: comandos ESC/POS en la página de códigos 850 y
  envío directo al spooler de Windows, con aviso si la ticketera está
  apagada o sin papel (T-32).
- Impresión al emitir, aviso si falla, reimpresión con F11 y desde
  Historial (F5); vista previa en las PC sin ticketera (T-33).
- Pruebas de aceptación y guía de instalación de la ticketera (T-34).

### Transversales
- Datos de prueba de clientes, repositorios en memoria y ticketera falsa (T-35).

### Pendiente para el Sprint 3
- Enviar las boletas a la SUNAT por el PSE y guardar el CDR (HU-07): hoy
  quedan con estado PENDIENTE.

## 0.1.0 – Sprint 1 (7 al 20 de octubre de 2026)

Objetivo del sprint: que las tres PC trabajen sobre una base de datos central
en la LAN y que el vendedor pueda registrar productos y buscarlos por nombre
para armar el detalle de una venta.

### HU-14 · Acceso con el perfil único de Usuario Maestro
- El programa abre directamente la pantalla Nueva venta con el perfil MAESTRO,
  sin usuario ni contraseña (T-08, T-09).
- Cada PC queda registrada como terminal con el nombre del equipo (T-09).

### HU-16 · Base de datos central y trabajo simultáneo en LAN
- Modelo de datos y migraciones automáticas de PostgreSQL 16 (T-01, T-03).
- Instalación y apertura de la base central a la red del local (T-02).
- Capa de datos con conexión configurable en `condor.json` (T-04).
- Correlativo por serie con bloqueo de fila: sin números repetidos ni saltados (T-05).
- Aviso de pérdida de conexión con Reintentar, sin perder lo que hay en pantalla (T-06).
- Prueba de concurrencia con tres terminales (T-07).

### HU-01 · Registrar producto en el catálogo
- Diálogo Nuevo producto (T-11), repositorio con validaciones y control de
  duplicados (T-12).
- Integración con la base central y aviso inmediato a las otras PC (T-13).
- Pruebas de aceptación (T-14).

### HU-02 · Buscar producto por nombre al vender
- Búsqueda con índice de trigramas, sin distinguir mayúsculas ni tildes (T-15).
- Autocompletado desde la tercera letra, manejable solo con teclado (T-16).
- Detalle de la venta con operación gravada, IGV (18 %) y total (T-17).
- Pruebas de aceptación y de tiempo de respuesta: menos de 1 s con 3 000 productos (T-18).

### Transversales
- Proyecto de pruebas xUnit y datos de prueba (T-20).
- Carga inicial del catálogo desde la lista de precios (T-19).
- Integración continua en GitHub Actions.
