# Especificación de Requisitos de Software (ERS)

## Sistema de Ventas y Facturación Cóndor — Ferretería Cóndor Majes S.A.C.

| Campo | Valor |
|---|---|
| Versión | **1.1** (línea base vigente) |
| Fecha | 2026-10-30 |
| Estado | Aprobada — línea base final para G02 a G09 |
| Norma de referencia | IEEE Std 830-1998 (referencia académica de estructura) |
| Preparado para | Ferretería Cóndor Majes S.A.C. (Gerente general) |
| Preparado por | Equipo de desarrollo — Calidad de Software 2026-B, EPIS UNSA |
| Herramienta de gestión | REMUS 1.3 (Universidad de Sevilla) — `03_REMUS/condor.rem` |
| Fuente única | `03_REMUS/condor_datos.json` (este documento se genera con `generar_ers.py`) |

### Control de versiones

| Versión | Fecha | Autor | Cambios | Estado |
|---|---|---|---|---|
| 0.9 | 2026-10-29 | Equipo (analistas) | Borrador: requisitos derivados del Product Backlog (HU-01 a HU-18) y de la elicitación ENT-01, CUE-01 y OBS-01. | Revisado (ver `07_Revision`) |
| 1.0 | 2026-10-29 | Equipo | Corrección de las 14 observaciones de la revisión. Línea base inicial: acceso con el perfil único MAESTRO, sin credenciales (HU-14). | Línea base |
| 1.1 | 2026-10-30 | Equipo | Solicitud de cambio **CC-01** aprobada: ingreso con usuario, contraseña y roles, backend REST y reporte consolidado (ver Apéndice B). | **Línea base vigente** |

## 1. Introducción

### 1.1 Propósito

El presente documento especifica los requisitos del **Sistema de Ventas y Facturación Cóndor** para la **Ferretería Cóndor Majes S.A.C.** (Majes, Arequipa).

Sirve de acuerdo entre la ferretería y el equipo de desarrollo sobre lo que el sistema debe hacer, y de línea base para el diseño (G03), la estimación (G04), la gestión de cambios (G02) y las pruebas (G07 a G09). Se redacta tomando como referencia académica la norma _IEEE Std 830-1998_ y las plantillas de requisitos de REMUS.

Está dirigido al gerente general (aprobación del alcance), al encargado general y a los vendedores (validación), al contador externo (reglas tributarias), al equipo de desarrollo (diseño, construcción y pruebas) y al docente (validación del alcance académico).

### 1.2 Alcance

Cóndor registra las ventas del mostrador en las tres PC del local, emite boletas, facturas, notas de venta y proformas, imprime el ticket en la ticketera térmica, envía los comprobantes electrónicos a la SUNAT, registra proveedores, compras y guías de remisión, ofrece el historial y un reporte consolidado de ventas, y genera respaldos de la base de datos.

Todas las PC trabajan sobre una base de datos PostgreSQL central a través de un backend REST (_Condor.Api_) instalado en la PC principal, con ingreso por usuario y contraseña y dos roles: **Vendedor** y **Encargado general**.

**Queda fuera de esta versión:** control de stock e inventario valorizado, cuentas por cobrar y crédito a clientes, notas de crédito y débito, pagos con tarjeta integrados, venta por internet y pantalla de administración de usuarios.

**Beneficios esperados:** atender una venta en menos de un minuto, eliminar los errores de cálculo del IGV, informar a tiempo todos los comprobantes a la SUNAT, saber qué usuario y qué terminal emitió cada comprobante, y disponer de un reporte consolidado de ventas.

**Procesos de negocio cubiertos:**

* **PN-01 Venta y facturación electrónica:** buscar productos, identificar al cliente, emitir boleta, factura o nota de venta, imprimir el ticket y enviar el comprobante a la SUNAT (RF-05, RF-06, RF-07, RF-09, RF-10; opcionalmente RF-13).
* **PN-02 Cotización y conversión en venta:** emitir una proforma con vigencia de 7 días y convertirla en boleta o factura una sola vez (RF-08, RF-07).
* **PN-03 Abastecimiento:** registrar al proveedor y registrar sus compras sin duplicar comprobantes (RF-11, RF-12).

Los procesos se apoyan en el ingreso y los roles (RF-01 a RF-03), el catálogo (RF-04), las consultas (RF-14, RF-15) y el respaldo (RF-16).

### 1.3 Definiciones, acrónimos y abreviaturas

* **SUNAT:** Superintendencia Nacional de Aduanas y de Administración Tributaria.
* **CDR:** Constancia de Recepción que devuelve la SUNAT por cada comprobante electrónico.
* **IGV:** Impuesto General a las Ventas, 18 % incluido en el precio de venta.
* **DNI / RUC:** documento de identidad (8 dígitos) / Registro Único de Contribuyentes (11 dígitos).
* **Boleta, factura:** comprobantes electrónicos de venta (series B001 y F001).
* **Nota de venta:** documento interno de control, sin valor tributario (serie NV01).
* **Proforma:** cotización sin valor tributario con vigencia de 7 días (serie PR01).
* **Guía de remisión:** documento electrónico que sustenta el traslado de bienes (serie T001).
* **Ticketera:** impresora térmica de 80 mm que recibe comandos ESC/POS.
* **JWT:** token firmado que identifica al usuario ante la API.
* **RF / RNF:** requisito funcional / no funcional.

### 1.4 Referencias

* IEEE Std 830-1998, _IEEE Recommended Practice for Software Requirements Specifications_.
* Guía de laboratorio PRAC01 Requerimientos, Calidad de Software, J. M. Silva Fernández.
* Product Backlog del proyecto Cóndor: historias HU-01 a HU-18 (CHANGELOG.md del repositorio).
* Solicitud de cambio CC-01 (G02_Proceso_Requerimientos).
* SUNAT, Resolución de Superintendencia N.° 097-2012/SUNAT y modificatorias (comprobantes electrónicos).

### 1.5 Visión general del documento

La sección 2 describe el producto en su contexto; la sección 3 especifica los requisitos funcionales, no funcionales, reglas de negocio y requisitos de información; la sección 4 reúne los indicadores medibles; la sección 5 los conflictos y su resolución, y la sección 6 la trazabilidad con objetivos, procesos y pruebas. Los apéndices dan la correspondencia con los identificadores de REMUS y el detalle del cambio de la versión 1.0 a la 1.1.

## 2. Descripción general

### 2.1 Perspectiva del producto

La ferretería vende al público y a obras de construcción. Hoy las ventas se anotan en un cuaderno y las boletas se llenan a mano en talonarios; los precios se consultan en una lista impresa que se desactualiza, y la facturación electrónica se hace aparte en el portal de la SUNAT al final del día.

Esto provoca colas en horas punta, errores de precio y de cálculo del IGV, comprobantes que no se informan a tiempo a la SUNAT, compras a proveedores sin registro ordenado y ninguna información consolidada para el gerente. Tampoco se sabe qué vendedor emitió cada comprobante.

Cóndor reemplaza el cuaderno de ventas, los talonarios y la facturación manual en el portal de la SUNAT. Es un sistema nuevo e independiente que se relaciona con tres sistemas o dispositivos externos:

```
  PC-1 / PC-2 / PC-3 (CondorVentas.exe, WPF)        Ticketera térmica 80 mm (PC de caja)
            │  HTTP + JWT                                  ▲ ESC/POS por el spooler
            ▼                                              │
  PC principal: Condor.Api (ASP.NET Core 8, :5080) ───────┘
            │  Npgsql                        │  HTTPS (sendBill, getStatusCdr, API de guías)
            ▼                                ▼
  PostgreSQL 16 (base central)        SUNAT (ambiente beta; simulada en las pruebas)
```

### 2.2 Funciones del producto

| Proceso | Requisitos funcionales |
|---|---|
| PN-01 Venta y facturación electrónica | RF-05 Buscar producto para la venta; RF-06 Registrar y buscar cliente por DNI o RUC; RF-07 Emitir comprobante de venta; RF-09 Imprimir y reimprimir el ticket; RF-10 Enviar comprobantes a la SUNAT y reenviar pendientes; RF-13 Emitir guía de remisión electrónica |
| PN-02 Cotización y conversión en venta | RF-08 Emitir proforma y convertirla en venta |
| PN-03 Abastecimiento | RF-11 Registrar proveedor; RF-12 Registrar compra a proveedor |
| Consultas e información consolidada | RF-14 Consultar historial de ventas; RF-15 Generar reporte consolidado de ventas |
| Soporte (acceso, catálogo y respaldo) | RF-01 Iniciar sesión; RF-02 Cerrar sesión; RF-03 Restringir módulos según el rol; RF-04 Registrar producto en el catálogo; RF-16 Generar respaldo de la base de datos |

### 2.3 Características de los usuarios

| Usuario | Rol en el sistema | Perfil | Frecuencia de uso |
|---|---|---|---|
| Vendedores de mostrador (2 a 3 por turno) | Vendedor | Secundaria completa, manejo básico de PC, conocen los productos; trabajan de pie y con prisa en horas punta. | Todo el turno |
| Encargado general | Encargado general | Técnico o experiencia administrativa; maneja compras, proveedores y guías. | Diaria |
| Gerente general | Encargado general (consulta) | Dueño del negocio; usa el reporte consolidado. | Semanal |
| Contador externo | Sin cuenta | Revisa comprobantes y estados ante la SUNAT a través del encargado. | Mensual |

### 2.4 Restricciones

- **Plataforma:** Windows 10/11 en las tres PC; .NET 8; PostgreSQL 16 en la PC principal; red local (LAN) del local.
- **Hardware:** ticketera térmica de 80 mm compatible ESC/POS (página de códigos 850); lector de código de barras que emula teclado.
- **Normativa:** comprobantes electrónicos en formato UBL 2.1 firmados con certificado digital, según la normativa de la SUNAT.
- **Seguridad:** solo la API conoce la clave de la base de datos; las PC acceden a los datos únicamente a través de la API.
- **Académicas:** rutas HTTP evaluables con JMeter, interfaz automatizable para las pruebas de aceptación (G09) y pruebas unitarias con una herramienta equivalente a JUnit (xUnit), aprobada por el docente.
- **Plazo:** entregas el 11-11-2026, el 25-11-2026 y el 02-12-2026.

### 2.5 Supuestos y dependencias

- **SUP-01** La PC principal permanece encendida durante el horario de atención (aloja la API y la base de datos).
- **SUP-02** La ferretería obtiene su certificado digital y su usuario SOL antes de pasar a producción; mientras tanto se usa el ambiente beta de la SUNAT.
- **SUP-03** En las pruebas, la SUNAT y la API de guías se sustituyen por **servicios simulados** (`SunatFalsa`, API de guías falsa), documentados en el código de pruebas.
- **SUP-04** El catálogo inicial se carga desde la lista de precios en CSV que entrega la ferretería (`db/datos/lista_precios.csv`).
- **SUP-05** Existe un disco externo conectado a la PC principal para los respaldos.
- **DEP-01** Bibliotecas de terceros: Npgsql, ASP.NET Core, xUnit; la generación del XML UBL se basa en el modelo de Greenter / sunat-manager.

### 2.6 Fuentes de elicitación

Se aplicaron tres técnicas, cuyos instrumentos y resultados están en _G01_Requerimientos/02_Elicitacion_:

* **ENT-01 Entrevista semiestructurada** al gerente general y al encargado general.
* **CUE-01 Cuestionario** a los vendedores de mostrador.
* **OBS-01 Observación directa** del proceso de venta actual, con toma de tiempos.

**Declaración:** las sesiones se realizaron con **usuarios representados**: integrantes del equipo asumieron los roles de gerente, encargado y vendedores a partir del conocimiento del negocio recogido en el Product Backlog del proyecto.

## 3. Requisitos específicos

### 3.1 Interfaces externas

| ID | Tipo | Descripción |
|---|---|---|
| INT-01 | Usuario | Aplicación de escritorio WPF: ventana Ingresar, ventana principal con Nueva venta y módulos F2 a F9 en el panel derecho; operable solo con teclado (atajos F1 a F11, Enter, Esc). |
| INT-02 | Usuario / software | API REST `Condor.Api` (HTTP + JSON, JWT Bearer) con las rutas públicas de `docs/api.md`; la usan JMeter y las integraciones. |
| INT-03 | Hardware | Ticketera térmica de 80 mm por el spooler de Windows (comandos ESC/POS); lector de código de barras como teclado. |
| INT-04 | Software | PostgreSQL 16 mediante Npgsql; migraciones SQL versionadas en `db/migraciones`. |
| INT-05 | Comunicaciones | Servicios web de la SUNAT: `sendBill` y `getStatusCdr` (SOAP) para comprobantes y API REST de guías (OAuth2). |
| INT-06 | Software | `pg_dump` / `pg_restore` para el respaldo y la restauración de la base de datos. |

### 3.2 Requisitos funcionales

Cada requisito funcional se modela en REMUS como un caso de uso (RF-xx = UC-00xx). Prioridad: Alta = imprescindible para liberar; Media = necesaria, puede diferirse un incremento.

| ID | Nombre | Descripción | Fuente | Prioridad | Origen |
|---|---|---|---|---|---|
| **RF-01** | Iniciar sesión | El sistema deberá autenticar al usuario con su nombre de usuario y contraseña antes de permitir cualquier operación, bloquear la cuenta 15 minutos tras 5 intentos fallidos seguidos y registrar cada intento en la bitácora. | Gerente general, Encargado general de tienda (Entrevista) | Alta | CC-01 |
| **RF-02** | Cerrar sesión | El sistema deberá permitir al usuario cerrar su sesión, descartando la venta en curso y volviendo a la ventana de ingreso. | Encargado general de tienda (Entrevista, Observación) | Media | CC-01 |
| **RF-03** | Restringir módulos según el rol | El sistema deberá restringir el acceso a los módulos de la aplicación y a las rutas de la API según el rol del usuario (Vendedor o Encargado general). | Gerente general, Encargado general de tienda (Entrevista) | Alta | CC-01 |
| **RF-04** | Registrar producto en el catálogo | El sistema deberá registrar productos en el catálogo central con nombre, precio con IGV, unidad y código de barras, sin nombres ni códigos repetidos. | Encargado general de tienda, Vendedores de mostrador (Entrevista, Cuestionario) | Alta | HU-01, HU-13 |
| **RF-05** | Buscar producto para la venta | El sistema deberá buscar productos por nombre desde la tercera letra, sin distinguir mayúsculas ni tildes, o por código de barras, y agregarlos al detalle de la venta. | Vendedores de mostrador (Cuestionario, Observación) | Alta | HU-02, HU-13 |
| **RF-06** | Registrar y buscar cliente por DNI o RUC | El sistema deberá buscar al cliente por su DNI o RUC validado y registrarlo si no existe. | Vendedores de mostrador, Contador externo (Cuestionario, Observación) | Alta | HU-03 |
| **RF-07** | Emitir comprobante de venta | El sistema deberá emitir boletas, facturas y notas de venta con número correlativo por serie, cálculo del IGV y las reglas de identificación del cliente. | Gerente general, Vendedores de mostrador, Contador externo (Entrevista, Cuestionario, Observación) | Alta | HU-05, HU-06, HU-08 |
| **RF-08** | Emitir proforma y convertirla en venta | El sistema deberá emitir proformas con vigencia de 7 días y convertirlas en venta una sola vez. | Gerente general, Vendedores de mostrador (Entrevista, Cuestionario) | Media | HU-09 |
| **RF-09** | Imprimir y reimprimir el ticket | El sistema deberá imprimir el ticket de cada comprobante en la ticketera térmica y permitir reimprimirlo marcado como copia. | Vendedores de mostrador (Observación) | Alta | HU-12, HU-18 |
| **RF-10** | Enviar comprobantes a la SUNAT y reenviar pendientes | El sistema deberá enviar las boletas y facturas a la SUNAT, guardar el CDR y reenviar automáticamente los comprobantes pendientes. | Gerente general, Contador externo (Entrevista) | Alta | HU-07, HU-17 |
| **RF-11** | Registrar proveedor | El sistema deberá permitir al Encargado general registrar proveedores con RUC único. | Encargado general de tienda (Entrevista) | Media | HU-04 |
| **RF-12** | Registrar compra a proveedor | El sistema deberá permitir al Encargado general registrar las compras a proveedores sin duplicar el comprobante del proveedor. | Encargado general de tienda, Contador externo (Entrevista) | Media | HU-11 |
| **RF-13** | Emitir guía de remisión electrónica | El sistema deberá permitir al Encargado general emitir guías de remisión electrónicas y enviarlas a la SUNAT. | Encargado general de tienda, Contador externo (Entrevista) | Media | HU-10 |
| **RF-14** | Consultar historial de ventas | El sistema deberá consultar el historial de comprobantes por período, tipo, cliente o número, con el total de ventas del período. | Encargado general de tienda, Vendedores de mostrador (Entrevista, Cuestionario) | Media | HU-18 |
| **RF-15** | Generar reporte consolidado de ventas | El sistema deberá generar para el Encargado general un reporte consolidado de ventas por día, tipo de comprobante, terminal y usuario. | Gerente general (Entrevista) | Media | CC-01 |
| **RF-16** | Generar respaldo de la base de datos | El sistema deberá permitir al Encargado general generar un respaldo de la base de datos en un disco externo. | Gerente general, Encargado general de tienda (Entrevista) | Media | HU-15 |

#### RF-01 Iniciar sesión

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá autenticar al usuario con su nombre de usuario y contraseña antes de permitir cualquier operación, bloquear la cuenta 15 minutos tras 5 intentos fallidos seguidos y registrar cada intento en la bitácora. |
| Proceso | Soporte (acceso, catálogo y respaldo) |
| Fuente | Gerente general, Encargado general de tienda (Entrevista) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: media) |
| Objetivos | OBJ-03 Controlar el acceso y la trazabilidad |
| Origen | CC-01 — REMUS UC-0001 |
| Evento | Cuando una persona del local abre el sistema o necesita identificarse para trabajar. |
| Precondición | La persona tiene una cuenta activa y la API de la PC principal está disponible. |
| Frecuencia | 12 veces por día(s) |

**Flujo principal**

1. El actor **Usuario** escribe su usuario y su contraseña en la ventana Ingresar y pulsa Ingresar.
2. El sistema verifica la contraseña contra el hash PBKDF2-SHA256 guardado de la cuenta.
3. El sistema pone en cero los intentos fallidos y registra el acceso exitoso con la terminal, la fecha y la hora.
4. El sistema abre la pantalla Nueva venta mostrando solo los módulos permitidos para el rol del usuario.

**Excepciones**

- Paso 1: si falta el usuario o la contraseña, el sistema mantiene deshabilitado el botón Ingresar y no consulta la base de datos; el caso de uso continúa.
- Paso 2: si el usuario no existe, está inactivo o la contraseña es incorrecta, el sistema muestra el mensaje «Usuario o contraseña incorrectos.», suma un intento fallido y lo registra en la bitácora; el caso de uso queda sin efecto.
- Paso 2: si la cuenta acumula 5 intentos fallidos seguidos, el sistema bloquea la cuenta durante 15 minutos e informa el bloqueo, aunque después se escriba la contraseña correcta; el caso de uso queda sin efecto.
- Paso 2: si la API no responde, el sistema muestra el aviso de conexión con la opción Reintentar; el caso de uso queda sin efecto.

**Postcondición:** La sesión queda abierta con el rol del usuario, el pie de la pantalla muestra su nombre y rol, y el intento queda en la bitácora de accesos.

**Criterios de aceptación**

- **CA-01.1** Dado `vendedor1` con la contraseña correcta, cuando pulsa Ingresar, entonces se abre Nueva venta y el pie muestra el usuario `vendedor1` y el rol «Vendedor».
- **CA-01.2** Dado un usuario inexistente o una contraseña equivocada, cuando pulsa Ingresar, entonces se muestra exactamente «Usuario o contraseña incorrectos.» en ambos casos.
- **CA-01.3** Dado 5 intentos fallidos seguidos, cuando se intenta con la contraseña correcta antes de 15 minutos, entonces el ingreso se rechaza (la API responde 423).
- **CA-01.4** Cada intento, correcto o fallido, aparece en la tabla `acceso_usuario` con terminal, fecha y motivo.

**Pruebas vinculadas:** `Dominio/ServicioAutenticacionTests`, `Presentacion/LoginViewModelTests`, `Datos/UsuarioRepositorioTests`, `Api/ApiTests`, `G09: acceso correcto y credenciales inválidas`

#### RF-02 Cerrar sesión

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá permitir al usuario cerrar su sesión, descartando la venta en curso y volviendo a la ventana de ingreso. |
| Proceso | Soporte (acceso, catálogo y respaldo) |
| Fuente | Encargado general de tienda (Entrevista, Observación) |
| Prioridad | Media (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-03 Controlar el acceso y la trazabilidad |
| Origen | CC-01 — REMUS UC-0002 |
| Evento | Cuando el usuario termina su turno o deja la PC. |
| Precondición | El usuario tiene una sesión abierta y no se está generando un respaldo. |
| Frecuencia | 12 veces por día(s) |

**Flujo principal**

1. El actor **Usuario** pulsa Cerrar sesión en el menú.
2. El sistema descarta la venta en curso y vuelve a Nueva venta.
3. El sistema oculta la ventana principal y muestra la ventana Ingresar vacía.

**Excepciones**

- Paso 1: si se está generando un respaldo, el sistema no permite cerrar la sesión hasta que el respaldo termine; el caso de uso queda sin efecto.

**Postcondición:** La sesión queda cerrada, la venta en curso se descarta y se muestra otra vez la ventana Ingresar.

**Criterios de aceptación**

- **CA-02.1** Dado un usuario con sesión abierta, cuando pulsa Cerrar sesión, entonces se muestra la ventana Ingresar con los campos vacíos.
- **CA-02.2** Después de cerrar sesión, la venta que estaba en pantalla no se conserva y el siguiente usuario empieza con una venta vacía.

**Pruebas vinculadas:** `Aceptacion/CC01_IngresoConRolesTests`, `G09: cierre de sesión`

#### RF-03 Restringir módulos según el rol

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá restringir el acceso a los módulos de la aplicación y a las rutas de la API según el rol del usuario (Vendedor o Encargado general). |
| Proceso | Soporte (acceso, catálogo y respaldo) |
| Fuente | Gerente general, Encargado general de tienda (Entrevista) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: media) |
| Objetivos | OBJ-03 Controlar el acceso y la trazabilidad |
| Origen | CC-01 — REMUS UC-0003 |
| Evento | Cuando un usuario intenta abrir un módulo desde el menú, con su tecla de función o mediante una ruta de la API. |
| Precondición | El usuario tiene una sesión abierta con el rol Vendedor o Encargado general. |
| Frecuencia | 50 veces por día(s) |

**Flujo principal**

1. El actor **Usuario** elige un módulo (F2 a F9) o invoca una ruta de la API.
2. El sistema comprueba el rol de la sesión contra los permisos del módulo, en la aplicación y otra vez en la API.
3. El sistema abre el módulo en el panel derecho de la ventana principal.

**Excepciones**

- Paso 2: si un Vendedor elige Compras, Proveedores, Guías o Respaldo, el sistema se queda en Nueva venta y muestra «Acceso denegado: el módulo … es solo para el Encargado general»; el caso de uso queda sin efecto.
- Paso 2: si un Vendedor invoca una ruta exclusiva del Encargado en la API, el sistema responde 403 sin ejecutar la operación; el caso de uso queda sin efecto.
- Paso 2: si la petición a la API no trae token o el token está alterado o vencido, el sistema responde 401; el caso de uso queda sin efecto.

**Postcondición:** El usuario solo accede a los módulos de su rol; los intentos no permitidos se rechazan sin cambiar los datos.

**Criterios de aceptación**

- **CA-03.1** Dado `vendedor1`, la ventana principal no muestra los botones Compras, Proveedores, Guías ni Respaldo.
- **CA-03.2** Dado `vendedor1`, cuando pulsa F4, entonces permanece en Nueva venta y el pie muestra «Acceso denegado».
- **CA-03.3** Dado un token de Vendedor, `GET /api/proveedores`, `GET /api/reportes/ventas` y `GET /api/respaldos` responden 403; sin token responden 401.
- **CA-03.4** Dado `encargado`, los cuatro módulos se abren normalmente.

**Pruebas vinculadas:** `Aceptacion/CC01_IngresoConRolesTests`, `Api/ApiTests`, `G09: restricción por rol`

#### RF-04 Registrar producto en el catálogo

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá registrar productos en el catálogo central con nombre, precio con IGV, unidad y código de barras, sin nombres ni códigos repetidos. |
| Proceso | Soporte (acceso, catálogo y respaldo) |
| Fuente | Encargado general de tienda, Vendedores de mostrador (Entrevista, Cuestionario) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador |
| Origen | HU-01, HU-13 — REMUS UC-0004 |
| Evento | Cuando llega un producto nuevo o hay que asignar el código de barras a uno existente. |
| Precondición | El usuario tiene una sesión abierta. |
| Frecuencia | 5 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** abre Nuevo producto (Ctrl+N o desde el Catálogo F2).
2. El actor **Vendedor** escribe el nombre, el precio con IGV, la unidad y, si tiene, lee el código de barras con el lector.
3. El sistema valida los datos contra las reglas del producto y la unicidad de nombre y código de barras.
4. El sistema guarda el producto en la base central y avisa a las demás PC del cambio en el catálogo.

**Excepciones**

- Paso 3: si el nombre está vacío, el precio no es mayor que 0, pasa de S/ 99 999.99 o tiene más de dos decimales, el sistema señala cada campo con su mensaje y no guarda; el caso de uso continúa.
- Paso 3: si ya existe un producto con el mismo nombre o el mismo código de barras, el sistema informa el duplicado y no guarda; el caso de uso continúa.

**Postcondición:** El producto queda en el catálogo central y las demás PC lo ven en sus búsquedas en 3 segundos como máximo.

**Criterios de aceptación**

- **CA-04.1** Dado «Cemento Sol 42.5 kg» a S/ 32.50, cuando se guarda, entonces aparece al buscar «cem» en otra PC en 3 s o menos.
- **CA-04.2** Dado un precio 0 o 12.345, cuando se guarda, entonces se rechaza con el mensaje de la regla correspondiente.
- **CA-04.3** Dado un nombre que ya existe escrito con otras mayúsculas o tildes, cuando se guarda, entonces se rechaza como duplicado (la API responde 409).

**Pruebas vinculadas:** `Aceptacion/HU01_RegistrarProductoTests`, `Aceptacion/HU13_LectorCodigoBarrasTests`, `Dominio/ValidadorProducto`, `G09: registro válido y datos inválidos`

#### RF-05 Buscar producto para la venta

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá buscar productos por nombre desde la tercera letra, sin distinguir mayúsculas ni tildes, o por código de barras, y agregarlos al detalle de la venta. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Vendedores de mostrador (Cuestionario, Observación) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador |
| Origen | HU-02, HU-13 — REMUS UC-0005 |
| Evento | Cuando el vendedor necesita agregar un producto al detalle de la venta. |
| Precondición | El vendedor está en la pantalla Nueva venta. |
| Frecuencia | 400 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** escribe al menos tres letras del nombre del producto o lo pasa por el lector de código de barras.
2. El sistema muestra hasta 15 sugerencias que contienen el texto, sin distinguir mayúsculas ni tildes, con su precio.
3. El actor **Vendedor** elige la sugerencia con Enter y escribe la cantidad.
4. El sistema agrega la línea al detalle y recalcula la operación gravada, el IGV y el total.

**Excepciones**

- Paso 1: si el código leído no pertenece a ningún producto, el sistema avisa que el código no está en el catálogo y ofrece registrarlo; el caso de uso queda sin efecto.
- Paso 2: si ningún producto coincide con el texto, el sistema no muestra sugerencias y el vendedor puede corregir el texto; el caso de uso continúa.
- Paso 3: si la cantidad no es mayor que 0, pasa de 99 999 o tiene más de tres decimales, el sistema no agrega la línea y señala la cantidad; el caso de uso continúa.

**Postcondición:** El producto queda agregado al detalle con su precio del catálogo y los totales se recalculan.

**Criterios de aceptación**

- **CA-05.1** Dado un catálogo de 3 000 productos, cuando se escribe «tub», entonces las sugerencias aparecen en menos de 1 s.
- **CA-05.2** Dado «tuberia» sin tilde, entonces se sugiere «Tubería PVC 1/2"».
- **CA-05.3** Dado un código de barras leído con el lector, entonces el producto se agrega con cantidad 1 sin tocar el mouse.

**Pruebas vinculadas:** `Aceptacion/HU02_BuscarProductoTests`, `Aceptacion/HU13_LectorCodigoBarrasTests`, `Presentacion/BuscadorProductoViewModel`, `G08: consultar productos`, `G09: consulta`

#### RF-06 Registrar y buscar cliente por DNI o RUC

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá buscar al cliente por su DNI o RUC validado y registrarlo si no existe. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Vendedores de mostrador, Contador externo (Cuestionario, Observación) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador, OBJ-02 Cumplir con la facturación electrónica |
| Origen | HU-03 — REMUS UC-0006 |
| Evento | Cuando el cliente pide un comprobante a su nombre. |
| Precondición | El usuario tiene una sesión abierta. |
| Frecuencia | 80 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** escribe el DNI o el RUC en el campo Cliente (Alt+D) y pulsa Enter.
2. El sistema valida el documento y busca al cliente en la base central.
3. El sistema completa el nombre o la razón social y la dirección en la venta.

**Excepciones**

- Paso 2: si el documento no tiene 8 u 11 dígitos o el RUC no cumple el dígito verificador, el sistema indica que el documento no es válido; el caso de uso continúa.
- Paso 2: si el cliente no está registrado, el sistema abre Nuevo cliente con el documento escrito; al guardarlo queda registrado y elegido en la venta; el caso de uso continúa.
- Paso 2: si otra PC registra el mismo documento al mismo tiempo, el sistema conserva un solo cliente y usa el ya registrado; el caso de uso continúa.

**Postcondición:** El cliente queda identificado en la venta y, si era nuevo, registrado en la base central.

**Criterios de aceptación**

- **CA-06.1** Dado el DNI de un cliente registrado, cuando se pulsa Enter, entonces se completa su nombre.
- **CA-06.2** Dado el RUC 20123456780 con dígito verificador incorrecto, entonces se rechaza (la API responde 400).
- **CA-06.3** Dado un documento ya registrado, cuando se intenta registrarlo otra vez, entonces no se crea un duplicado (409).

**Pruebas vinculadas:** `Aceptacion/HU03_ClienteTests`, `Dominio/ValidadorDocumento`, `G09: registro válido y datos inválidos`

#### RF-07 Emitir comprobante de venta

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá emitir boletas, facturas y notas de venta con número correlativo por serie, cálculo del IGV y las reglas de identificación del cliente. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Gerente general, Vendedores de mostrador, Contador externo (Entrevista, Cuestionario, Observación) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador, OBJ-02 Cumplir con la facturación electrónica, OBJ-03 Controlar el acceso y la trazabilidad |
| Origen | HU-05, HU-06, HU-08 — REMUS UC-0007 |
| Evento | Cuando el cliente confirma la compra y pide su comprobante. |
| Precondición | La venta en pantalla tiene al menos una línea y el usuario tiene una sesión abierta. |
| Frecuencia | 150 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** elige el tipo de comprobante (Boleta, Con DNI, Factura o Nota de venta) y pulsa Emitir e imprimir (F10).
2. El sistema valida las reglas del tipo elegido y recalcula los importes con los precios del catálogo.
3. El sistema asigna el siguiente número de la serie y guarda la cabecera y el detalle en una sola transacción.
4. Se realiza **RF-09 Imprimir y reimprimir el ticket**.
5. Se realiza **RF-10 Enviar comprobantes a la SUNAT y reenviar pendientes**.
6. El sistema deja la pantalla lista para la siguiente venta.

**Excepciones**

- Paso 2: si es una boleta de más de S/ 700.00 sin DNI del cliente, el sistema pide el DNI y no emite; el caso de uso continúa.
- Paso 2: si es una factura sin un cliente con RUC, el sistema pasa el foco al campo RUC y no emite; el caso de uso continúa.
- Paso 3: si se pierde la conexión con la API o la base de datos, el sistema no guarda nada, no consume número y conserva la venta en pantalla para reintentar; el caso de uso queda sin efecto.

**Postcondición:** El comprobante queda guardado con su serie y número correlativo, el usuario y la terminal; las boletas y facturas quedan pendientes de envío a la SUNAT.

**Criterios de aceptación**

- **CA-07.1** Dada una venta de S/ 118.00, cuando se emite boleta, entonces queda B001 con el siguiente número, operación gravada 100.00 e IGV 18.00.
- **CA-07.2** Dada una boleta de S/ 700.01 sin DNI, entonces no se emite y se pide el DNI; con S/ 700.00 sí se emite.
- **CA-07.3** Dada una factura sin RUC, entonces no se emite.
- **CA-07.4** Dada una nota de venta, entonces se emite con serie NV01, sin cliente obligatorio, y no queda pendiente para la SUNAT.
- **CA-07.5** Dado `vendedor1`, el comprobante guarda `usuario = vendedor1` aunque la petición diga otro usuario.

**Pruebas vinculadas:** `Aceptacion/HU05_EmitirBoletaTests`, `Aceptacion/HU06_EmitirFacturaTests`, `Aceptacion/HU08_NotasVentaTests`, `Dominio/EmisionComprobante`, `Dominio/CalculadoraVenta`, `Api/ClienteApiTests`, `G08: registrar boleta`, `G09: cambio de estado (emitir)`

#### RF-08 Emitir proforma y convertirla en venta

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá emitir proformas con vigencia de 7 días y convertirlas en venta una sola vez. |
| Proceso | PN-02 Cotización y conversión en venta |
| Fuente | Gerente general, Vendedores de mostrador (Entrevista, Cuestionario) |
| Prioridad | Media (urgencia: hay presión; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador |
| Origen | HU-09 — REMUS UC-0008 |
| Evento | Cuando un cliente pide una cotización o regresa a comprar lo cotizado. |
| Precondición | El usuario tiene una sesión abierta. |
| Frecuencia | 20 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** arma el detalle, elige Proforma y pulsa Emitir e imprimir.
2. El sistema emite la proforma con serie PR01 y la fecha «Válida hasta» de 7 días contando el de emisión, e imprime el ticket con la leyenda de cotización.
3. El actor **Vendedor** cuando el cliente regresa, busca la proforma en Proformas (F7) por número, DNI, RUC o nombre y pulsa Convertir en venta.
4. El sistema lleva el detalle y el cliente a Nueva venta y propone factura si el cliente tiene RUC o boleta en otro caso.
5. Se realiza **RF-07 Emitir comprobante de venta**.

**Excepciones**

- Paso 3: si la proforma está vencida, el sistema informa la fecha de vencimiento y no la convierte; el caso de uso queda sin efecto.
- Paso 3: si la proforma ya fue convertida, incluso desde otra PC al mismo tiempo, el sistema informa el comprobante que la convirtió y no la convierte otra vez; el caso de uso queda sin efecto.

**Postcondición:** La proforma queda emitida con su vigencia; al convertirla, la venta queda enlazada a la proforma y la proforma ya no se puede volver a convertir.

**Criterios de aceptación**

- **CA-08.1** Dada una proforma emitida el 2026-11-02, entonces su «Válida hasta» es 2026-11-08.
- **CA-08.2** Dada una proforma vigente, cuando se convierte, entonces la venta emitida queda enlazada a ella y la proforma figura como convertida.
- **CA-08.3** Dada la misma proforma convertida desde dos PC a la vez, entonces solo una conversión prospera.

**Pruebas vinculadas:** `Aceptacion/HU09_ProformasTests`, `Dominio/EmisionComprobante`, `G09: cambio de estado (convertir proforma)`

#### RF-09 Imprimir y reimprimir el ticket

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá imprimir el ticket de cada comprobante en la ticketera térmica y permitir reimprimirlo marcado como copia. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Vendedores de mostrador (Observación) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: alta) |
| Objetivos | OBJ-01 Agilizar la venta en mostrador |
| Origen | HU-12, HU-18 — REMUS UC-0009 |
| Evento | Cuando se emite un comprobante o el cliente pide una copia. |
| Precondición | El comprobante está emitido. |
| Frecuencia | 160 veces por día(s) |

**Flujo principal**

1. El sistema arma el ticket de 80 mm con el RUC de la empresa, tipo y número, cliente, detalle, operación gravada, IGV, total e importe en letras.
2. El sistema envía el ticket a la Ticketera térmica en comandos ESC/POS por el spooler de Windows.
3. El actor **Ticketera térmica** imprime el ticket.
4. El sistema suma una impresión al comprobante.

**Excepciones**

- Paso 2: si la PC no tiene ticketera configurada, el sistema muestra el ticket en pantalla como vista previa; el caso de uso continúa.
- Paso 3: si la ticketera está apagada o sin papel, el sistema avisa del problema y permite reimprimir con F11 sin volver a emitir; el caso de uso continúa.
- Paso 1: si es una reimpresión desde el Historial o con F11, el sistema marca el ticket con «*** COPIA - REIMPRESIÓN ***»; el caso de uso continúa.

**Postcondición:** El ticket queda impreso y el comprobante registra el número de impresiones.

**Criterios de aceptación**

- **CA-09.1** El ticket de una boleta de S/ 118.00 muestra «SON: CIENTO DIECIOCHO CON 00/100 SOLES».
- **CA-09.2** Una reimpresión lleva la marca «COPIA - REIMPRESIÓN» y suma una impresión.
- **CA-09.3** Con la ticketera apagada, el comprobante queda emitido igual y se avisa del fallo de impresión.

**Pruebas vinculadas:** `Aceptacion/HU12_ImprimirTicketTests`, `Aceptacion/HU18_HistorialTests`, `Impresion/*`, `Dominio/MontoEnLetras`

#### RF-10 Enviar comprobantes a la SUNAT y reenviar pendientes

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá enviar las boletas y facturas a la SUNAT, guardar el CDR y reenviar automáticamente los comprobantes pendientes. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Gerente general, Contador externo (Entrevista) |
| Prioridad | Alta (urgencia: inmediatamente; estabilidad: media) |
| Objetivos | OBJ-02 Cumplir con la facturación electrónica |
| Origen | HU-07, HU-17 — REMUS UC-0010 |
| Evento | Cuando se emite una boleta o factura, o vence el intervalo de reenvío de pendientes. |
| Precondición | La PC tiene configurada la sección Sunat (certificado y usuario SOL) y el comprobante es electrónico. |
| Frecuencia | 140 veces por día(s) |

**Flujo principal**

1. El sistema genera el XML UBL 2.1 del comprobante y lo firma con el certificado digital.
2. El sistema envía el ZIP a la SUNAT por sendBill en paralelo con la impresión.
3. El actor **SUNAT** devuelve el CDR con el código de respuesta.
4. El sistema guarda el XML, el CDR y el estado, y lo muestra bajo el botón Emitir y en el Historial.
5. El sistema cada ReenvioMinutos aparta los pendientes y los reenvía del más antiguo al más reciente.

**Excepciones**

- Paso 2: si no hay internet o la SUNAT no responde, el sistema deja el comprobante PENDIENTE sin frenar la venta y lo reintenta en el siguiente ciclo; el caso de uso continúa.
- Paso 3: si la SUNAT responde que el comprobante ya fue recibido (código 1033), el sistema consulta el CDR con getStatusCdr y lo guarda; el caso de uso continúa.
- Paso 5: si el pendiente más antiguo está por vencer el plazo de 3 días, el sistema muestra un aviso en rojo en el pie de Nueva venta; el caso de uso continúa.

**Postcondición:** El comprobante queda ACEPTADO, OBSERVADO o RECHAZADO con su CDR guardado, o PENDIENTE para un nuevo intento.

**Criterios de aceptación**

- **CA-10.1** Con la SUNAT simulada aceptando, una boleta emitida queda ACEPTADO con su CDR guardado.
- **CA-10.2** Sin internet, la boleta se emite e imprime igual y queda PENDIENTE; al volver internet se reenvía sola y queda ACEPTADO.
- **CA-10.3** Dos PC nunca reenvían el mismo comprobante a la vez.

**Pruebas vinculadas:** `Aceptacion/HU07_EnviarSunatTests`, `Aceptacion/HU17_ReenvioAutomaticoTests`, `Sunat/*`, `Dominio/ReenvioSunat`

#### RF-11 Registrar proveedor

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá permitir al Encargado general registrar proveedores con RUC único. |
| Proceso | PN-03 Abastecimiento |
| Fuente | Encargado general de tienda (Entrevista) |
| Prioridad | Media (urgencia: hay presión; estabilidad: alta) |
| Objetivos | OBJ-04 Ordenar el abastecimiento |
| Origen | HU-04 — REMUS UC-0011 |
| Evento | Cuando la ferretería empieza a comprar a un proveedor nuevo. |
| Precondición | El usuario tiene una sesión abierta con el rol Encargado general. |
| Frecuencia | 2 veces por semana(s) |

**Flujo principal**

1. El actor **Encargado general** abre Proveedores (F6) y pulsa Nuevo proveedor (Alt+N).
2. El actor **Encargado general** escribe el RUC, la razón social, el nombre comercial, la dirección, el teléfono, el correo y el contacto.
3. El sistema valida el RUC y los formatos de teléfono y correo.
4. El sistema guarda al proveedor y lo muestra en la lista.

**Excepciones**

- Paso 3: si el RUC no es válido, falta la razón social o el correo no tiene un formato válido, el sistema señala cada campo con su mensaje y no guarda; el caso de uso continúa.
- Paso 4: si ya existe un proveedor con el mismo RUC, el sistema informa el duplicado y no guarda; el caso de uso continúa.

**Postcondición:** El proveedor queda registrado una sola vez por RUC y disponible para registrar compras.

**Criterios de aceptación**

- **CA-11.1** Dado un RUC válido y la razón social, cuando se guarda, entonces aparece al buscar por RUC o por razón social sin tildes.
- **CA-11.2** Dado un correo «ventas@», entonces se rechaza con «El correo no es válido».
- **CA-11.3** Dado un RUC ya registrado, entonces la API responde 409.

**Pruebas vinculadas:** `Aceptacion/HU04_ProveedoresTests`, `Dominio/ValidadorProveedor`

#### RF-12 Registrar compra a proveedor

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá permitir al Encargado general registrar las compras a proveedores sin duplicar el comprobante del proveedor. |
| Proceso | PN-03 Abastecimiento |
| Fuente | Encargado general de tienda, Contador externo (Entrevista) |
| Prioridad | Media (urgencia: hay presión; estabilidad: alta) |
| Objetivos | OBJ-04 Ordenar el abastecimiento |
| Origen | HU-11 — REMUS UC-0012 |
| Evento | Cuando llega mercadería de un proveedor con su factura o boleta. |
| Precondición | El usuario tiene una sesión abierta con el rol Encargado general y el proveedor está registrado. |
| Frecuencia | 3 veces por día(s) |

**Flujo principal**

1. El actor **Encargado general** abre Compras (F4) y pulsa Nueva compra (Alt+N).
2. El actor **Encargado general** busca al proveedor por RUC, indica el tipo, la serie, el número y la fecha de su comprobante y agrega los productos con cantidad y costo.
3. El sistema valida la compra y que el comprobante del proveedor no esté ya registrado.
4. El sistema guarda la compra y actualiza el total de egresos del período.

**Excepciones**

- Paso 3: si la serie no tiene 4 caracteres, el número no está entre 1 y 99999999, la fecha es futura o de hace más de un año, o una línea no tiene cantidad y costo mayores que cero, el sistema señala el campo con su mensaje y no guarda; el caso de uso continúa.
- Paso 3: si el mismo comprobante del proveedor ya está registrado, aunque lo intente otra PC a la vez, el sistema informa el duplicado y no lo registra otra vez; el caso de uso queda sin efecto.

**Postcondición:** La compra queda registrada con su detalle y suma al total de egresos del período.

**Criterios de aceptación**

- **CA-12.1** Dada la factura F001-123 del proveedor con RUC 20100070970, cuando se registra, entonces suma al total de egresos del mes.
- **CA-12.2** Dada la misma F001-123 otra vez, entonces se rechaza como duplicada.
- **CA-12.3** Dada una fecha de mañana, entonces se rechaza con «La fecha del comprobante no puede ser posterior a hoy».

**Pruebas vinculadas:** `Aceptacion/HU11_ComprasTests`, `Dominio/ValidadorCompra`

#### RF-13 Emitir guía de remisión electrónica

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá permitir al Encargado general emitir guías de remisión electrónicas y enviarlas a la SUNAT. |
| Proceso | PN-01 Venta y facturación electrónica |
| Fuente | Encargado general de tienda, Contador externo (Entrevista) |
| Prioridad | Media (urgencia: puede esperar; estabilidad: media) |
| Objetivos | OBJ-02 Cumplir con la facturación electrónica |
| Origen | HU-10 — REMUS UC-0013 |
| Evento | Cuando hay que trasladar la mercadería vendida a una obra o a otro establecimiento. |
| Precondición | El usuario tiene una sesión abierta con el rol Encargado general. |
| Frecuencia | 2 veces por día(s) |

**Flujo principal**

1. El actor **Encargado general** abre Guías (F8) y crea una guía desde una factura o boleta, o a mano.
2. El actor **Encargado general** completa el destinatario, el motivo y la fecha de traslado, el peso, los puntos de partida y llegada y el transporte.
3. El sistema valida los datos obligatorios según la modalidad de transporte.
4. El sistema emite la guía, la imprime y la envía a la SUNAT por la API de guías.
5. El actor **SUNAT** devuelve el ticket y luego el CDR de la guía.

**Excepciones**

- Paso 3: si falta un dato obligatorio o el punto de llegada es igual al de partida, el sistema señala el campo con su mensaje y no emite; el caso de uso continúa.
- Paso 4: si la SUNAT no responde, el sistema deja la guía pendiente y la reenvía o consulta sola más tarde; el caso de uso continúa.

**Postcondición:** La guía queda emitida con serie T001, impresa y enviada a la SUNAT, o pendiente de envío.

**Criterios de aceptación**

- **CA-13.1** Dada una guía con transporte privado sin placa, entonces se rechaza con el mensaje de la placa.
- **CA-13.2** Dada una guía creada desde una factura, entonces hereda el destinatario y el detalle de la factura.
- **CA-13.3** Con la API de guías simulada, la guía queda aceptada con su CDR.

**Pruebas vinculadas:** `Aceptacion/HU10_GuiasRemisionTests`, `Dominio/ValidadorGuia`

#### RF-14 Consultar historial de ventas

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá consultar el historial de comprobantes por período, tipo, cliente o número, con el total de ventas del período. |
| Proceso | Consultas e información consolidada |
| Fuente | Encargado general de tienda, Vendedores de mostrador (Entrevista, Cuestionario) |
| Prioridad | Media (urgencia: hay presión; estabilidad: alta) |
| Objetivos | OBJ-05 Disponer de información consolidada |
| Origen | HU-18 — REMUS UC-0014 |
| Evento | Cuando el usuario necesita ubicar un comprobante o conocer las ventas de un período. |
| Precondición | El usuario tiene una sesión abierta. |
| Frecuencia | 30 veces por día(s) |

**Flujo principal**

1. El actor **Vendedor** abre Historial (F5) y elige el período (Hoy, Este mes, Todo o fechas), el tipo, el cliente o el número.
2. El sistema lista los comprobantes con su estado ante la SUNAT, usando los días de la hora de Perú.
3. El sistema muestra el total de ventas del período sin contar proformas ni rechazados.

**Excepciones**

- Paso 2: si ningún comprobante cumple los filtros, el sistema muestra la lista vacía con total S/ 0.00; el caso de uso continúa.

**Postcondición:** Se muestran los comprobantes que cumplen los filtros y el total del período.

**Criterios de aceptación**

- **CA-14.1** Dadas 2 boletas de S/ 50.00 y 1 proforma de S/ 30.00 hoy, cuando se filtra Hoy, entonces el total es S/ 100.00.
- **CA-14.2** Las notas de venta muestran «No aplica» en la columna SUNAT.

**Pruebas vinculadas:** `Aceptacion/HU18_HistorialTests`, `G09: consulta`

#### RF-15 Generar reporte consolidado de ventas

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá generar para el Encargado general un reporte consolidado de ventas por día, tipo de comprobante, terminal y usuario. |
| Proceso | Consultas e información consolidada |
| Fuente | Gerente general (Entrevista) |
| Prioridad | Media (urgencia: hay presión; estabilidad: media) |
| Objetivos | OBJ-05 Disponer de información consolidada |
| Origen | CC-01 — REMUS UC-0015 |
| Evento | Cuando el gerente o el encargado necesitan analizar las ventas de un período. |
| Precondición | El usuario tiene una sesión abierta con el rol Encargado general. |
| Frecuencia | 1 veces por día(s) |

**Flujo principal**

1. El actor **Encargado general** solicita el reporte de ventas indicando la fecha inicial y la final.
2. El sistema valida el período.
3. El sistema agrupa las ventas por día, tipo, terminal y usuario, sin proformas, y muestra los rechazados aparte.

**Excepciones**

- Paso 2: si la fecha final es anterior a la inicial o el período pasa de 366 días, el sistema rechaza la consulta con el motivo (400); el caso de uso queda sin efecto.
- Paso 1: si el usuario tiene el rol Vendedor, el sistema responde 403; el caso de uso queda sin efecto.

**Postcondición:** Se obtiene el reporte con los totales por día, por tipo de comprobante, por terminal y por usuario.

**Criterios de aceptación**

- **CA-15.1** Dadas ventas de `vendedor1` y `vendedor2` en dos terminales, el reporte suma correctamente por usuario y por terminal y el total general coincide con el Historial.
- **CA-15.2** Un período de 400 días se rechaza con 400.

**Pruebas vinculadas:** `Dominio/ReporteVentasTests`, `Api/ApiTests`, `Datos/UsuarioRepositorioTests`

#### RF-16 Generar respaldo de la base de datos

| Campo | Contenido |
|---|---|
| Descripción | El sistema deberá permitir al Encargado general generar un respaldo de la base de datos en un disco externo. |
| Proceso | Soporte (acceso, catálogo y respaldo) |
| Fuente | Gerente general, Encargado general de tienda (Entrevista) |
| Prioridad | Media (urgencia: hay presión; estabilidad: alta) |
| Objetivos | OBJ-06 Proteger la información del negocio |
| Origen | HU-15 — REMUS UC-0016 |
| Evento | Cuando termina el día de trabajo o el sistema avisa que el último respaldo tiene más de 24 horas. |
| Precondición | El usuario tiene una sesión abierta con el rol Encargado general y el disco externo está conectado a la PC principal. |
| Frecuencia | 1 veces por día(s) |

**Flujo principal**

1. El actor **Encargado general** abre Respaldo (F9), confirma la carpeta del disco externo y pulsa Generar respaldo.
2. El sistema ejecuta pg_dump en formato personalizado y muestra el avance tabla por tabla.
3. El sistema registra el respaldo con su tamaño y confirma el resultado.

**Excepciones**

- Paso 2: si falla pg_dump o el disco se desconecta, el sistema borra el archivo incompleto, registra el error y lo informa; el caso de uso queda sin efecto.

**Postcondición:** Queda un archivo .backup con la fecha y la hora en el nombre y el respaldo registrado en la base.

**Criterios de aceptación**

- **CA-16.1** Al generar el respaldo queda un archivo `condor_AAAAMMDD_HHMM.backup` que pg_restore puede restaurar en una base vacía.
- **CA-16.2** Si falla a la mitad, no queda ningún archivo a medias.
- **CA-16.3** Si el último respaldo tiene más de 24 h, el Encargado ve un aviso al abrir el sistema; el Vendedor no.

**Pruebas vinculadas:** `Aceptacion/HU15_RespaldoTests`, `G06: control respaldo y restauración`

### 3.3 Requisitos no funcionales

| ID | Atributo | Descripción | Fuente | Prioridad |
|---|---|---|---|---|
| **RNF-01** | Rendimiento | El sistema deberá mostrar las sugerencias de productos en **menos de 1 segundo** desde que se escribe la tercera letra, con un catálogo de **3 000 productos**. | Vendedores de mostrador (Cuestionario, Observación) | Alta |
| **RNF-02** | Rendimiento | El sistema deberá atender las transacciones críticas consultar productos y emitir boleta con un **percentil 95 menor o igual a 2 segundos** y una **tasa de error menor o igual a 1 %**, con **10 usuarios concurrentes durante 5 minutos**. | Gerente general, Docente del curso (Entrevista) | Media |
| **RNF-03** | Seguridad | El sistema deberá guardar las contraseñas solo como hash **PBKDF2-SHA256 con 100 000 iteraciones y sal de 16 bytes**, bloquear la cuenta **15 minutos tras 5 intentos fallidos seguidos** y rechazar el **100 %** de los accesos a funciones del Encargado general por usuarios sin ese rol. | Gerente general, Docente del curso (Entrevista) | Alta |
| **RNF-04** | Fiabilidad (integridad) | El sistema deberá permitir que **3 terminales** emitan comprobantes al mismo tiempo sin producir **ningún** número de comprobante repetido ni saltado. | Encargado general de tienda, Contador externo (Entrevista, Observación) | Alta |
| **RNF-05** | Disponibilidad | El sistema deberá seguir emitiendo e imprimiendo comprobantes sin internet y reenviar automáticamente el **100 %** de los pendientes cuando vuelva la conexión, avisando cuando el más antiguo esté por vencer el plazo de **3 días**. | Gerente general, Contador externo (Entrevista) | Alta |
| **RNF-06** | Usabilidad | El sistema deberá permitir completar una venta de **3 productos con boleta** usando **solo el teclado** (atajos F1 a F11, Enter y Esc) en **60 segundos o menos** para un vendedor con una hora de capacitación. | Vendedores de mostrador (Observación, Cuestionario) | Media |
| **RNF-07** | Fiabilidad (recuperabilidad) | El sistema deberá conservar el **100 %** de los registros tras reiniciar la aplicación, la API o la PC principal, y permitir **restaurar un respaldo** en una base vacía; avisar al Encargado si el último respaldo tiene **más de 24 horas**. | Gerente general, Encargado general de tienda (Entrevista) | Alta |
| **RNF-08** | Mantenibilidad | El sistema deberá mantener una cobertura de líneas de **al menos 80 %** en el paquete de lógica de negocio `Condor.Dominio`, con la suite automatizada en verde. | Docente del curso | Media |

**Criterios de aceptación de los RNF**

- **CA-RNF-01.1** La prueba HU02 con 3 000 productos registra un tiempo menor que 1 s. Verificación: `Aceptacion/HU02_BuscarProductoTests`.
- **CA-RNF-02.1** El reporte HTML de JMeter del escenario de carga esperada cumple ambos umbrales por transacción. Verificación: `G08: escenario de carga esperada`.
- **CA-RNF-03.1** Las pruebas de hash, autenticación y API pasan; ninguna contraseña aparece en texto plano en la base ni en la bitácora. Verificación: `Dominio/HashClaveTests`, `Dominio/ServicioAutenticacionTests`, `Api/ApiTests`.
- **CA-RNF-04.1** La prueba de concurrencia con tres terminales emitiendo a la vez obtiene la serie completa sin huecos ni repetidos. Verificación: `Aceptacion/HU16_ConcurrenciaTests`, `Aceptacion/HU05_EmitirBoletaTests`.
- **CA-RNF-05.1** Con la SUNAT simulada sin internet a mitad del envío, todas las ventas se emiten y, al restablecerse, todos los pendientes quedan aceptados. Verificación: `Aceptacion/HU07_EnviarSunatTests`, `Aceptacion/HU17_ReenvioAutomaticoTests`.
- **CA-RNF-06.1** En 5 ventas cronometradas con la ficha de observación, la mediana es de 60 s o menos sin usar el mouse. Verificación: `G01: ficha OBS-01 (línea base manual)`, `G09: prueba de aceptación cronometrada`.
- **CA-RNF-07.1** Tras reiniciar la API, los comprobantes emitidos siguen en el Historial. Verificación: `Aceptacion/HU15_RespaldoTests`, `Datos/* ([FactConBD])`, `G06: control de respaldo`.
- **CA-RNF-07.2** Un respaldo generado se restaura con pg_restore y conserva los mismos conteos por tabla. Verificación: `Aceptacion/HU15_RespaldoTests`, `Datos/* ([FactConBD])`, `G06: control de respaldo`.
- **CA-RNF-08.1** El reporte de cobertura de G07 muestra 80 % o más de líneas en Condor.Dominio. Verificación: `G07: reporte de cobertura`.

### 3.4 Reglas de negocio y restricciones

| ID | Regla | Fuente | Objetivos |
|---|---|---|---|
| **CRQ-01** | El sistema deberá respetar: el precio de venta incluye el IGV del 18 %; la operación gravada es el total dividido entre 1.18, el IGV es la diferencia, todo redondeado a dos decimales, y operación gravada más IGV debe ser igual al total. | Contador externo | OBJ-02 |
| **CRQ-02** | El sistema deberá respetar: una boleta cuyo total sea mayor que S/ 700.00 exige el DNI del cliente. | Contador externo | OBJ-02 |
| **CRQ-03** | El sistema deberá respetar: una factura solo se emite a un cliente registrado con RUC válido, razón social y dirección. | Contador externo | OBJ-02 |
| **CRQ-04** | El sistema deberá respetar: el DNI tiene 8 dígitos; el RUC tiene 11 dígitos, empieza con 10, 15, 16, 17 o 20 y su último dígito cumple el verificador módulo 11 de la SUNAT. | Contador externo | OBJ-02 |
| **CRQ-05** | El sistema deberá respetar: cada serie (B001, F001, NV01, PR01, T001) numera sus documentos de uno en uno, sin números repetidos ni saltados, aunque emitan varias PC a la vez o falle una emisión. | Contador externo | OBJ-02, OBJ-06 |
| **CRQ-06** | El sistema deberá respetar: una proforma vale 7 días contando el de su emisión y se convierte en venta una sola vez; una proforma vencida o ya convertida no se convierte. | Gerente general | OBJ-01 |
| **CRQ-07** | El sistema deberá respetar: el precio y la descripción de cada línea de venta se toman del catálogo y el servidor recalcula los importes y totales; no se acepta el precio enviado por la terminal. | Gerente general | OBJ-03, OBJ-06 |
| **CRQ-08** | El sistema deberá respetar: no pueden existir dos productos con el mismo nombre (sin distinguir mayúsculas ni tildes) ni dos productos con el mismo código de barras. | Encargado general de tienda | OBJ-01 |
| **CRQ-09** | El sistema deberá respetar: un mismo comprobante de proveedor (RUC, tipo, serie y número) no se registra dos veces. | Contador externo | OBJ-04 |
| **CRQ-10** | El sistema deberá respetar: las boletas, facturas y guías se envían a la SUNAT como máximo 3 días después de su emisión; las notas de venta y las proformas no se envían. | Contador externo | OBJ-02 |
| **CRQ-11** | El sistema deberá respetar: cada comprobante guarda el usuario que lo emitió, tomado de su sesión y no de los datos enviados, y la terminal desde donde se emitió. | Gerente general | OBJ-03 |
| **CRQ-12** | El sistema deberá respetar: solo el Encargado general accede a proveedores, compras, guías de remisión, respaldos y al reporte consolidado de ventas, tanto en la aplicación como en la API. | Gerente general, Encargado general de tienda | OBJ-03 |
| **CRQ-13** | El sistema deberá respetar: la guía exige motivo, fecha de traslado no anterior a hoy, peso bruto, ubigeos de 6 dígitos, punto de llegada distinto del de partida y los datos del transporte según su modalidad (RUC y razón social del transportista, o placa, DNI, nombre y licencia del conductor). | Encargado general de tienda, Contador externo | OBJ-02 |
| **CRQ-14** | El sistema deberá respetar: cada línea tiene una cantidad mayor que 0 y hasta 99 999, con tres decimales como máximo, y un comprobante tiene como máximo 100 líneas. | Encargado general de tienda | OBJ-01 |
| **CRQ-15** | El sistema deberá respetar: la fecha final del reporte no es anterior a la inicial y el período no pasa de 366 días; las proformas no suman ventas y los rechazados se muestran aparte. | Gerente general | OBJ-05 |

### 3.5 Requisitos de información

| ID | Concepto | Datos específicos | Ocurrencias (media / máx.) | Vida (media / máx.) |
|---|---|---|---|---|
| **IRQ-01** | Información sobre productos | Nombre del producto (único  hasta 150 caracteres); Precio de venta con IGV (mayor que 0 y hasta S/ 99 999.99  dos decimales); Unidad de medida (UND  KG  M  GAL...); Código de barras (único  de 4 a 30 caracteres  opcional); Indicador de producto activo; Fecha y hora de registro | 3 000 / 5 000 | 3 / 10 año(s) |
| **IRQ-02** | Información sobre clientes | Tipo de documento (1 = DNI  6 = RUC); Número de documento (único); Nombre o razón social (hasta 200 caracteres); Dirección (hasta 250 caracteres; obligatoria para factura) | 2 000 / 8 000 | 5 / 10 año(s) |
| **IRQ-03** | Información sobre comprobantes de venta | Serie (B001  F001  NV01  PR01) y número correlativo; Fecha y hora de emisión; Cliente (opcional en boleta hasta S/ 700 y en nota de venta); Terminal y usuario que lo emitió; Operación gravada  IGV y total; Detalle: ítem  producto  descripción  cantidad  precio unitario e importe; Estado ante la SUNAT (PENDIENTE  ACEPTADO  OBSERVADO  RECHAZADO); Número de impresiones y fecha de la última; Vigencia (proforma) y proforma de origen (venta convertida) | 40 000 / 60 000 | 5 / 10 año(s) |
| **IRQ-04** | Información sobre envíos a la SUNAT | XML UBL 2.1 firmado; CDR recibido (ZIP) y código de respuesta; Descripción del motivo de observación o rechazo; Número de intentos y fecha del último; Reserva de reenvío (terminal y vencimiento) | 35 000 / 55 000 | 5 / 10 año(s) |
| **IRQ-05** | Información sobre proveedores | RUC (único); Razón social y nombre comercial; Dirección; Teléfono y correo electrónico; Persona de contacto | 60 / 300 | 5 / 10 año(s) |
| **IRQ-06** | Información sobre compras | Proveedor; Tipo  serie y número del comprobante del proveedor (únicos por proveedor); Fecha del comprobante (no futura ni de más de un año); Terminal y usuario que la registró; Detalle: producto  cantidad y costo unitario; Total de la compra | 600 / 1 500 | 5 / 10 año(s) |
| **IRQ-07** | Información sobre guías de remisión | Serie T001 y número; Destinatario (DNI o RUC y nombre); Motivo y fecha de traslado  peso bruto; Punto de partida y de llegada (ubigeo y dirección); Modalidad de transporte: transportista (RUC y razón social) o vehículo y conductor; Comprobante que la sustenta (opcional); Detalle de productos y cantidades; Estado ante la SUNAT | 500 / 1 200 | 5 / 10 año(s) |
| **IRQ-08** | Información sobre usuarios y accesos | Nombre de usuario (único) y nombre completo; Hash de la contraseña (PBKDF2-SHA256 con sal); Rol (VENDEDOR o ENCARGADO); Indicador de cuenta activa; Intentos fallidos seguidos y bloqueo hasta; Bitácora: fecha  usuario  terminal o IP  resultado y motivo de cada intento | 5 / 20 | 2 / 5 año(s) |
| **IRQ-09** | Información sobre respaldos | Fecha y hora; Terminal que lo generó; Ruta y nombre del archivo (.backup); Tamaño en bytes; Resultado (correcto o error y su motivo) | 300 / 1 000 | 1 / 3 año(s) |

## 4. Indicadores medibles

| RNF | Atributo | Indicador | Meta | Cómo se mide |
|---|---|---|---|---|
| RNF-01 | Rendimiento | Tiempo entre la tercera letra y la lista de sugerencias (ms), medido en la prueba automatizada | **< 1 000 ms** | Aceptacion/HU02_BuscarProductoTests |
| RNF-02 | Rendimiento | p95 por transacción (s) y porcentaje de respuestas con error en JMeter | **p95 ≤ 2 s; error ≤ 1 %** | G08: escenario de carga esperada |
| RNF-03 | Seguridad | Iteraciones y longitud de sal del hash; intentos hasta el bloqueo; porcentaje de rutas exclusivas que responden 403 al Vendedor y 401 sin token | **100 000 iteraciones; bloqueo al 5.º intento; 100 % de rutas protegidas** | Dominio/HashClaveTests, Dominio/ServicioAutenticacionTests, Api/ApiTests |
| RNF-04 | Fiabilidad (integridad) | Números repetidos o saltados en la serie tras la emisión simultánea | **0 repetidos y 0 saltados** | Aceptacion/HU16_ConcurrenciaTests, Aceptacion/HU05_EmitirBoletaTests |
| RNF-05 | Disponibilidad | Ventas emitidas sin internet; porcentaje de pendientes aceptados tras recuperar la conexión | **100 % de ventas emitidas; 100 % de pendientes reenviados** | Aceptacion/HU07_EnviarSunatTests, Aceptacion/HU17_ReenvioAutomaticoTests |
| RNF-06 | Usabilidad | Tiempo cronometrado por venta en la observación; uso del mouse durante la venta | **≤ 60 s; 0 clics** | G01: ficha OBS-01 (línea base manual), G09: prueba de aceptación cronometrada |
| RNF-07 | Fiabilidad (recuperabilidad) | Registros antes y después del reinicio; restauración correcta de un respaldo | **0 registros perdidos; restauración exitosa** | Aceptacion/HU15_RespaldoTests, Datos/* ([FactConBD]), G06: control de respaldo |
| RNF-08 | Mantenibilidad | Porcentaje de líneas cubiertas de Condor.Dominio (coverlet + ReportGenerator) | **≥ 80 %** | G07: reporte de cobertura |

Línea base de la situación actual (ficha OBS-01): una venta de 3 productos con boleta manual toma una mediana de 2 min 50 s y en 2 de 12 boletas observadas hubo error en el cálculo del IGV. Las metas de RNF-01 y RNF-06 se fijaron contra esa línea base.

## 5. Conflictos identificados y su resolución

| ID | Conflicto | Partes | Resolución | Estado |
|---|---|---|---|---|
| **CFL-01** | **Rapidez del ingreso frente a control de acceso.** Los vendedores pidieron que el sistema abra **directo en Nueva venta, sin usuario ni contraseña** (HU-14, perfil único MAESTRO). El gerente necesita saber **quién emitió cada comprobante** y que los vendedores no vean compras ni respaldos; el curso exige autenticación y roles. | Gerente general, Vendedores de mostrador | Se aprobó la solicitud de cambio **CC-01**: ingreso con usuario y contraseña **una vez por turno** (el token dura 480 minutos) y dos roles. Se mantiene la apertura directa en Nueva venta tras el ingreso, de modo que el vendedor no pierde rapidez. | Resuelto |
| **CFL-02** | **Venta sin internet frente a la obligación de informar a la SUNAT.** El internet del local se corta con frecuencia y los vendedores **no pueden dejar de vender**; el contador exige que **todo comprobante llegue a la SUNAT** dentro del plazo. | Vendedores de mostrador, Contador externo | El comprobante se emite e imprime sin esperar a la SUNAT y queda PENDIENTE; un proceso en segundo plano lo reenvía solo y el pie avisa en rojo cuando el más antiguo está por vencer el plazo de 3 días (RF-10, RNF-05). | Resuelto |
| **CFL-03** | **Ajuste de precio por el vendedor frente al control de precios.** Algunos vendedores quieren **cambiar el precio en la venta** para hacer descuentos; el gerente quiere que **los precios los fije solo el catálogo**. | Gerente general, Vendedores de mostrador | El precio de cada línea sale del catálogo y el servidor recalcula los totales (CRQ-07). Los descuentos quedan fuera del alcance de esta versión y se registran como posible cambio futuro. | Resuelto |
| **CFL-04** | **Boleta rápida sin datos frente a la norma de identificación.** Los vendedores prefieren **no pedir el DNI** para no demorar; la norma de la SUNAT obliga a identificar al comprador en boletas desde cierto monto. | Vendedores de mostrador, Contador externo | Se pide el DNI **solo en boletas de más de S/ 700.00** (CRQ-02); por debajo, la boleta se emite sin cliente. | Resuelto |
| **CFL-05** | **Respaldo automático frente a la infraestructura disponible.** El gerente quiere **respaldos automáticos en la nube**; la ferretería no tiene servidor dedicado ni presupuesto para un servicio en la nube y solo cuenta con un disco externo. | Gerente general, Encargado general de tienda | Respaldo **manual** con pg_dump en el disco externo desde la PC principal y **aviso si el último tiene más de 24 horas** (RF-16, RNF-07). El respaldo automático queda como mejora futura. | Resuelto |
| **CFL-06** | **Visibilidad de compras para todos frente a confidencialidad.** El encargado propuso que todos vean las compras para consultar costos; el gerente no quiere que los vendedores conozcan **costos ni egresos**. | Gerente general, Encargado general de tienda | Compras, proveedores, guías, respaldos y el reporte consolidado son exclusivos del Encargado general (CRQ-12, RF-03). | Resuelto |

## 6. Trazabilidad

### 6.1 Requisitos frente a objetivos

| Requisito | OBJ-01 | OBJ-02 | OBJ-03 | OBJ-04 | OBJ-05 | OBJ-06 |
|---|---|---|---|---|---|---|
| RF-01 |  |  | ✔ |  |  |  |
| RF-02 |  |  | ✔ |  |  |  |
| RF-03 |  |  | ✔ |  |  |  |
| RF-04 | ✔ |  |  |  |  |  |
| RF-05 | ✔ |  |  |  |  |  |
| RF-06 | ✔ | ✔ |  |  |  |  |
| RF-07 | ✔ | ✔ | ✔ |  |  |  |
| RF-08 | ✔ |  |  |  |  |  |
| RF-09 | ✔ |  |  |  |  |  |
| RF-10 |  | ✔ |  |  |  |  |
| RF-11 |  |  |  | ✔ |  |  |
| RF-12 |  |  |  | ✔ |  |  |
| RF-13 |  | ✔ |  |  |  |  |
| RF-14 |  |  |  |  | ✔ |  |
| RF-15 |  |  |  |  | ✔ |  |
| RF-16 |  |  |  |  |  | ✔ |
| RNF-01 | ✔ |  |  |  |  |  |
| RNF-02 | ✔ |  |  |  |  |  |
| RNF-03 |  |  | ✔ |  |  |  |
| RNF-04 |  |  |  |  |  | ✔ |
| RNF-05 |  | ✔ |  |  |  |  |
| RNF-06 | ✔ |  |  |  |  |  |
| RNF-07 |  |  |  |  |  | ✔ |
| RNF-08 |  |  |  |  |  | ✔ |

### 6.2 Requisitos frente a pruebas

La matriz de trazabilidad final del trabajo amplía esta tabla con los identificadores de las pruebas de G07, G08 y G09 y su resultado.

| Requisito | Criterios | Pruebas existentes en el producto | Pruebas previstas en las guías |
|---|---|---|---|
| RF-01 | 4 | `Dominio/ServicioAutenticacionTests`, `Presentacion/LoginViewModelTests`, `Datos/UsuarioRepositorioTests`, `Api/ApiTests` | G09: acceso correcto y credenciales inválidas |
| RF-02 | 2 | `Aceptacion/CC01_IngresoConRolesTests` | G09: cierre de sesión |
| RF-03 | 4 | `Aceptacion/CC01_IngresoConRolesTests`, `Api/ApiTests` | G09: restricción por rol |
| RF-04 | 3 | `Aceptacion/HU01_RegistrarProductoTests`, `Aceptacion/HU13_LectorCodigoBarrasTests`, `Dominio/ValidadorProducto` | G09: registro válido y datos inválidos |
| RF-05 | 3 | `Aceptacion/HU02_BuscarProductoTests`, `Aceptacion/HU13_LectorCodigoBarrasTests`, `Presentacion/BuscadorProductoViewModel` | G08: consultar productos; G09: consulta |
| RF-06 | 3 | `Aceptacion/HU03_ClienteTests`, `Dominio/ValidadorDocumento` | G09: registro válido y datos inválidos |
| RF-07 | 5 | `Aceptacion/HU05_EmitirBoletaTests`, `Aceptacion/HU06_EmitirFacturaTests`, `Aceptacion/HU08_NotasVentaTests`, `Dominio/EmisionComprobante`, `Dominio/CalculadoraVenta`, `Api/ClienteApiTests` | G08: registrar boleta; G09: cambio de estado (emitir) |
| RF-08 | 3 | `Aceptacion/HU09_ProformasTests`, `Dominio/EmisionComprobante` | G09: cambio de estado (convertir proforma) |
| RF-09 | 3 | `Aceptacion/HU12_ImprimirTicketTests`, `Aceptacion/HU18_HistorialTests`, `Impresion/*`, `Dominio/MontoEnLetras` | G07 (regresión unitaria) |
| RF-10 | 3 | `Aceptacion/HU07_EnviarSunatTests`, `Aceptacion/HU17_ReenvioAutomaticoTests`, `Sunat/*`, `Dominio/ReenvioSunat` | G07 (regresión unitaria) |
| RF-11 | 3 | `Aceptacion/HU04_ProveedoresTests`, `Dominio/ValidadorProveedor` | G07 (regresión unitaria) |
| RF-12 | 3 | `Aceptacion/HU11_ComprasTests`, `Dominio/ValidadorCompra` | G07 (regresión unitaria) |
| RF-13 | 3 | `Aceptacion/HU10_GuiasRemisionTests`, `Dominio/ValidadorGuia` | G07 (regresión unitaria) |
| RF-14 | 2 | `Aceptacion/HU18_HistorialTests` | G09: consulta |
| RF-15 | 2 | `Dominio/ReporteVentasTests`, `Api/ApiTests`, `Datos/UsuarioRepositorioTests` | G07 (regresión unitaria) |
| RF-16 | 3 | `Aceptacion/HU15_RespaldoTests` | G06: control respaldo y restauración |
| RNF-01 | 1 | `Aceptacion/HU02_BuscarProductoTests` | G07 (regresión unitaria) |
| RNF-02 | 1 | — | G08: escenario de carga esperada |
| RNF-03 | 1 | `Dominio/HashClaveTests`, `Dominio/ServicioAutenticacionTests`, `Api/ApiTests` | G07 (regresión unitaria) |
| RNF-04 | 1 | `Aceptacion/HU16_ConcurrenciaTests`, `Aceptacion/HU05_EmitirBoletaTests` | G07 (regresión unitaria) |
| RNF-05 | 1 | `Aceptacion/HU07_EnviarSunatTests`, `Aceptacion/HU17_ReenvioAutomaticoTests` | G07 (regresión unitaria) |
| RNF-06 | 1 | — | G01: ficha OBS-01 (línea base manual); G09: prueba de aceptación cronometrada |
| RNF-07 | 2 | `Aceptacion/HU15_RespaldoTests`, `Datos/* ([FactConBD])` | G06: control de respaldo |
| RNF-08 | 1 | — | G07: reporte de cobertura |

## Apéndice A. Correspondencia con los identificadores de REMUS

| ERS | REMUS | ERS | REMUS |
|---|---|---|---|
| RF-01 | UC-0001 | RF-13 | UC-0013 |
| RF-02 | UC-0002 | RF-14 | UC-0014 |
| RF-03 | UC-0003 | RF-15 | UC-0015 |
| RF-04 | UC-0004 | RF-16 | UC-0016 |
| RF-05 | UC-0005 | RNF-01 | NFR-0001 |
| RF-06 | UC-0006 | RNF-02 | NFR-0002 |
| RF-07 | UC-0007 | RNF-03 | NFR-0003 |
| RF-08 | UC-0008 | RNF-04 | NFR-0004 |
| RF-09 | UC-0009 | RNF-05 | NFR-0005 |
| RF-10 | UC-0010 | RNF-06 | NFR-0006 |
| RF-11 | UC-0011 | RNF-07 | NFR-0007 |
| RF-12 | UC-0012 | RNF-08 | NFR-0008 |

Objetivos (OBJ), requisitos de información (IRQ), reglas (CRQ), actores (ACT) y conflictos (CFL) conservan su número con cuatro dígitos en REMUS (OBJ-01 = OBJ-0001).

## Apéndice B. Cambios de la versión 1.0 a la 1.1 (CC-01)

| Elemento | Versión 1.0 | Versión 1.1 |
|---|---|---|
| RF-01 | Acceder con el perfil único MAESTRO: el sistema abre Nueva venta sin usuario ni contraseña (HU-14). | **Iniciar sesión** con usuario y contraseña, bloqueo tras 5 intentos y bitácora. |
| RF-02 | — | **Cerrar sesión** (nuevo). |
| RF-03 | — | **Restringir módulos según el rol** (nuevo). |
| RF-07 | El comprobante guarda el usuario MAESTRO. | El comprobante guarda el usuario de la sesión (CRQ-11). |
| RF-15 | — | **Reporte consolidado de ventas** (nuevo, en la API). |
| CRQ-11, CRQ-12 | — | Nuevas reglas de autoría y de funciones exclusivas del Encargado general. |
| RNF-02, RNF-03 | — | Nuevos: capacidad de la API y protección de credenciales. |
| IRQ-08 | — | Nueva información de usuarios y accesos. |
| CFL-01 | Abierto | Resuelto con CC-01. |

El análisis de impacto, la decisión y el cierre de CC-01 están en `G02_Proceso_Requerimientos`.
