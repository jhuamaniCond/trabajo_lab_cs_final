# -*- coding: utf-8 -*-
"""
generar_manual_tecnico.py
Manual breve técnico del Sistema Cóndor 1.2.0: arquitectura, instalación,
configuración, base de datos, API, seguridad, respaldo, pruebas y SVN.
Antes ejecutar generar_codigo.py.

    python Docs/generar_manual_tecnico.py
"""

import os

from comun import (Documento, SALIDA, VERSION, ETIQUETA, portada, indice,
                   pie_paginado, figura, informar)

FIGURAS = {
    "t_componentes": ("G03_Analisis_Sistemas/02_UML/07_componentes.png",
                      "Componentes del producto (proyectos de la solución CondorVentas.sln).", 16),
    "t_despliegue": ("G03_Analisis_Sistemas/02_UML/08_despliegue.png",
                     "Despliegue en el local: PC principal y PC de mostrador en la LAN.", 15),
    "cod_condor_json": ("Docs/figuras/cod_condor_json.png",
                        "Inicio de condor.ejemplo.json (src/Condor.Escritorio): secciones Api y Ticketera. Las líneas 22 a 48 (sección Sunat) se describen en la tabla siguiente.", 16),
    "cod_ejecutar_ps1": ("Docs/figuras/cod_ejecutar_ps1.png",
                         "Parámetros del script ejecutar.ps1 (raíz del producto).", 15),
    "t_modelo": ("G03_Analisis_Sistemas/02_UML/09_modelo_datos.png",
                 "Modelo de datos de PostgreSQL (migraciones V001 a V014).", 16),
    "cod_admin_sql": ("Docs/figuras/cod_admin_sql.png",
                      "Administración de cuentas con psql, tomada de docs/seguridad.md.", 16),
    "cod_restaurar": ("Docs/figuras/cod_restaurar.png",
                      "Restauración de un respaldo, tomada de docs/respaldo.md. La línea 79 termina con el acento grave de continuación de PowerShell.", 16),
}
ORDEN = list(FIGURAS)
PASOS = {k: ["Ejecutar `python Docs/generar_codigo.py`."] for k in FIGURAS if k.startswith("cod_")}


def fig(doc, clave):
    figura(doc, clave, FIGURAS, PASOS)


def construir():
    doc = Documento(figuras=ORDEN)
    portada(doc, "MANUAL TÉCNICO", "Instalación, configuración, operación y mantenimiento")
    indice(doc)

    doc.titulo(1, "1. Propósito y alcance")
    doc.parrafo(
        "Este manual está dirigido al responsable técnico que instala, configura, opera y mantiene el "
        "Sistema Cóndor %s, y al docente que necesita reconstruir y ejecutar el producto y sus pruebas. "
        "Resume y ordena la documentación del repositorio (`Sistema_Logistico_Condor_final/README.md` y "
        "`docs/`), que es la referencia detallada." % VERSION)
    doc.tabla([
        ["Dato", "Valor"],
        ["Versión del producto", VERSION],
        ["Etiqueta SVN entregada", "%s, copia de trunk@43; código idéntico a `tags/v1.0.0`" % ETIQUETA],
        ["Lenguaje y plataforma", "C# .NET 8 (WPF, ASP.NET Core 8), PostgreSQL 16"],
        ["Repositorio", "`svn://127.0.0.1/condor` (portable en `G05_Gestion_Configuracion/02_Repositorio/condor`)"],
    ], anchos_cm=[4.5, 11.5])

    doc.titulo(1, "2. Arquitectura")
    doc.parrafo("Arquitectura cliente – API – base. Solo `Condor.Api` conoce la clave de la base de datos; la app de escritorio y el portal web hablan con la API por HTTP con un token JWT. Las reglas de negocio están en `Condor.Dominio` y no dependen de infraestructura.")
    fig(doc, "t_componentes")
    doc.tabla([
        ["Carpeta", "Contenido"],
        ["`src/Condor.Escritorio`", "Aplicación WPF: ventanas, estilos y arranque (`CondorVentas.exe`)"],
        ["`src/Condor.Presentacion`", "ViewModels MVVM sin dependencias de WPF"],
        ["`src/Condor.Dominio`", "Entidades, reglas (validación, IGV, emisión, autenticación, reporte) y contratos"],
        ["`src/Condor.Datos`", "Npgsql, repositorios, migrador y respaldo con `pg_dump`"],
        ["`src/Condor.ClienteApi`", "Repositorios de la app que llaman a `/api/escritorio/*`"],
        ["`src/Condor.Api`", "Backend REST (`CondorApi.exe`) y portal web en `wwwroot`"],
        ["`src/Condor.Sunat`", "XML UBL 2.1, firma, envío a la SUNAT, guías y reenvío de pendientes"],
        ["`src/Condor.Impresion`", "Comandos ESC/POS y envío al spooler de Windows"],
        ["`db/migraciones`", "Scripts SQL versionados V001 a V014, aplicados al arrancar"],
        ["`herramientas/`", "`Condor.CargaCatalogo` (carga inicial) y `Condor.DatosDemo` (datos de demostración)"],
        ["`tests/Condor.Pruebas`", "Pruebas xUnit unitarias, de integración y de aceptación"],
    ], anchos_cm=[5.0, 11.0])
    fig(doc, "t_despliegue")

    doc.titulo(1, "3. Requisitos de instalación")
    doc.tabla([
        ["Elemento", "PC principal", "PC de mostrador"],
        ["Sistema operativo", "Windows 10/11 de 64 bits", "Windows 10/11 de 64 bits"],
        ["Programas", "`CondorApi.exe`, `CondorVentas.exe`, PostgreSQL 16 (nativo o en Docker)", "`CondorVentas.exe`"],
        ["Red", "IP fija en la LAN; puerto 5080 abierto", "Acceso a la IP de la PC principal"],
        ["Periféricos", "Disco externo para respaldos", "Ticketera ESC/POS de 80 mm y lector de código de barras (opcionales)"],
        ["Internet", "Opcional (una PC con internet envía a la SUNAT)", "Opcional"],
        ["Desarrollo", ".NET 8 SDK o Visual Studio 2022; sin SDK, Docker Desktop", "—"],
    ], anchos_cm=[3.4, 6.6, 6.0])

    doc.titulo(1, "4. Instalación en el local")
    doc.numerada([
        "**PC principal — base de datos:** instalar PostgreSQL 16, fijar la IP y crear la base `condor` y el usuario `condor_app` (`docs/instalacion_postgresql.md`, `db/servidor/crear_bd.sql`).",
        "**PC principal — API:** copiar `CondorApi.exe` y su `appsettings.json`; poner los datos de la base, la carpeta de respaldos y una clave JWT propia de 32 caracteres o más (sección 5.2).",
        "**Cada PC:** copiar `condor.ejemplo.json` como `condor.json` junto a `CondorVentas.exe` y poner la URL de la API (en la PC principal, `http://localhost:5080` y la ruta de `CondorApi.exe` en `Backend`, para que la app la arranque si no corre).",
        "**Catálogo inicial:** cargar `db/datos/lista_precios.csv` con `Condor.CargaCatalogo` (`db/datos/README.md`).",
        "**Datos de la empresa:** RUC, razón social y dirección del ticket (`docs/modelo_datos.md`).",
        "**Ticketera:** instalarla en Windows y poner su nombre en `condor.json` (`docs/ticketera.md`).",
        "**SUNAT:** en la PC con internet, completar la sección `Sunat` (ambiente beta) según `docs/sunat.md`; para producción, certificado digital, usuario SOL y credenciales de la API de guías (`docs/produccion.md`).",
        "**Antes de instalar en el local:** implantar HTTPS en la LAN (salvaguarda S10 de G06, observación O-2 del dictamen).",
    ])
    doc.parrafo("Las migraciones se aplican solas al arrancar la API; no hay que ejecutar los scripts SQL a mano.")

    doc.titulo(1, "5. Configuración")
    doc.titulo(2, "5.1 condor.json (cada PC)")
    fig(doc, "cod_condor_json")
    doc.tabla([
        ["Sección y clave", "Uso"],
        ["`Api.Url`", "URL de la API en la PC principal"],
        ["`Api.Backend`", "Solo en la PC principal: ruta de `CondorApi.exe` para arrancarla si no responde"],
        ["`Ticketera.Nombre`", "Nombre de la impresora en Windows; vacío = ticket en pantalla"],
        ["`Sunat.Ambiente`, `UsuarioSol`, `ClaveSol`, `Certificado`", "Envío a la SUNAT (Beta o Produccion); sin la sección los comprobantes quedan PENDIENTE"],
        ["`Sunat.ReenvioMinutos`", "Cada cuántos minutos se reenvían los pendientes (0 = esta PC no reenvía)"],
        ["`Sunat.ClientId`, `ClientSecret`", "Credenciales de la API de guías de remisión"],
    ], anchos_cm=[6.0, 10.0])
    doc.titulo(2, "5.2 appsettings.json (Condor.Api)")
    doc.tabla([
        ["Sección", "Claves", "Uso"],
        ["`Urls`", "`http://0.0.0.0:5080`", "Puerto del backend y del portal web"],
        ["`BaseDatos`", "`Servidor`, `Puerto`, `BaseDatos`, `Usuario`, `Clave`, `MaxConexiones` (20)", "Conexión a PostgreSQL y tamaño del pool de Npgsql"],
        ["`Respaldo`", "`Carpeta`, `PgDump`, `AvisoHoras` (24)", "Carpeta del disco externo y aviso de respaldo vencido"],
        ["`Jwt`", "`Emisor`, `Audiencia`, `Clave`, `MinutosValidez` (480)", "Firma de los tokens; **cambiar la clave en el local** o definir la variable `Jwt__Clave`"],
    ], anchos_cm=[3.0, 7.0, 6.0])

    doc.titulo(1, "6. Ejecución en un equipo de desarrollo o de evaluación")
    doc.parrafo("El script `ejecutar.ps1` hace todo: levanta PostgreSQL en el contenedor Docker **`Cas_condor`** (volumen `cas_condor_datos`, puerto **5433**, base `condor`, usuario `condor_app`), carga los datos de demostración la primera vez, compila y arranca la API y abre la app. Si PowerShell bloquea scripts: `powershell -ExecutionPolicy Bypass -File .\\ejecutar.ps1`.")
    fig(doc, "cod_ejecutar_ps1")
    doc.tabla([
        ["Comando", "Efecto"],
        ["`.\\ejecutar.ps1`", "Base, datos de demostración (la primera vez), API y app de escritorio"],
        ["`.\\ejecutar.ps1 -Api`", "Base y API; el portal queda en `http://localhost:5080/`"],
        ["`.\\ejecutar.ps1 -SinCompilar`", "Arranca lo ya publicado en `.ejecutar\\app` y `.ejecutar\\api`"],
        ["`.\\ejecutar.ps1 -DatosDemo`", "Vuelve a cargar los datos de demostración"],
        ["`.\\ejecutar.ps1 -Detener` / `-BorrarDatos`", "Detiene el contenedor / borra su volumen"],
        ["`dotnet build CondorVentas.sln`", "Compila la solución con el SDK de .NET 8"],
        ["`dotnet run --project src/Condor.Api`", "Arranca solo el backend"],
    ], anchos_cm=[6.5, 9.5])
    doc.parrafo("Credenciales de demostración: `encargado` / `Encargado2026!` (Encargado general) y `vendedor1`, `vendedor2` / `Vendedor2026!` (Vendedor). Comprobación rápida: `http://localhost:5080/api/salud` debe responder con la versión 1.2.0.")

    doc.titulo(1, "7. Base de datos")
    doc.parrafo("PostgreSQL 16. Las migraciones están en `db/migraciones` y el migrador de `Condor.Datos` aplica las que falten al arrancar. La persistencia está en el volumen del contenedor (o en el clúster nativo), así que los registros se conservan al reiniciar la API, la app o la PC (RNF-07).")
    doc.tabla([
        ["Migración", "Contenido"],
        ["V001–V004", "Esquema inicial, series, índice de búsqueda de productos (trigram), aviso de cambios del catálogo"],
        ["V005, V008", "Emisión de comprobantes; factura con RUC"],
        ["V006", "Proveedores"],
        ["V007, V009", "Envío y reenvío a la SUNAT"],
        ["V010", "Respaldos"],
        ["V011", "Proformas"],
        ["V012", "Compras"],
        ["V013", "Guías de remisión"],
        ["V014", "Usuarios, roles y bitácora de accesos (CC-01)"],
    ], anchos_cm=[3.0, 13.0])
    fig(doc, "t_modelo")

    doc.titulo(1, "8. API REST")
    doc.parrafo("Todas las rutas, salvo `/api/salud`, `/api/auth/login` y el portal (`/`), exigen el token JWT (`Authorization: Bearer`). Las marcadas **E** exigen el rol Encargado general. Detalle en `docs/api.md`; ejemplos en `src/Condor.Api/Condor.Api.http`.")
    doc.tabla([
        ["Ruta", "Rol", "Uso"],
        ["`GET /api/salud`", "—", "Disponibilidad de la API y de la base"],
        ["`POST /api/auth/login`", "—", "Ingreso; devuelve el JWT (480 min); 423 si la cuenta está bloqueada"],
        ["`GET /api/productos?texto=`", "V", "Buscar productos"],
        ["`GET/POST /api/clientes`", "V", "Buscar y registrar clientes"],
        ["`POST /api/comprobantes`, `GET /api/comprobantes`", "V", "Emitir (precio del catálogo) e historial"],
        ["`GET /api/proformas`, `POST /api/proformas/{id}/convertir`", "V", "Proformas y conversión en venta (CC-03)"],
        ["`GET/POST /api/proveedores`", "E", "Proveedores"],
        ["`GET/POST /api/compras`", "E", "Compras a proveedores (CC-03)"],
        ["`GET /api/reportes/ventas?desde=&hasta=`", "E", "Reporte consolidado"],
        ["`GET /api/respaldos`", "E", "Respaldos generados"],
        ["`/api/escritorio/*` (41 rutas)", "V / E", "Contrato interno de la app WPF"],
    ], anchos_cm=[7.0, 1.4, 7.6])
    doc.tabla([
        ["Código", "Significado"],
        ["400", "Regla de negocio incumplida (mensaje de `Condor.Dominio`)"],
        ["401 / 403", "Sin token o token vencido / rol sin permiso"],
        ["409", "Duplicado (cliente, producto, proveedor o compra ya registrados)"],
        ["423", "Cuenta bloqueada 15 minutos tras 5 intentos fallidos"],
        ["503", "Base de datos no disponible"],
    ], anchos_cm=[3.0, 13.0])

    doc.titulo(1, "9. Seguridad y administración de usuarios")
    doc.vinetas([
        "Contraseñas con PBKDF2-SHA256, 100 000 iteraciones y sal de 16 bytes (`HashClave`); nunca se guardan ni se muestran en claro.",
        "Bloqueo de 15 minutos al quinto intento fallido; cada intento queda en `acceso_usuario` con terminal o IP, fecha y motivo.",
        "Roles VENDEDOR y ENCARGADO: la app oculta los módulos y la API responde 403 aunque la app se modificara.",
        "Cada comprobante guarda el usuario del token y la terminal, no los datos que envía la PC.",
        "El precio de cada línea lo pone el servidor desde el catálogo (CRQ-07, defecto DEF-01 corregido en 1.1.1).",
        "El portal escapa todo texto que viene de la API para evitar XSS.",
    ])
    doc.parrafo("La versión 1.2.0 no tiene pantalla de usuarios: se administran con `psql` en la PC principal. Para crear un usuario o cambiar una contraseña se genera el hash con `HashClave.Generar` y se pone en el `INSERT` o `UPDATE`.")
    fig(doc, "cod_admin_sql")

    doc.titulo(1, "10. Respaldo y restauración")
    doc.parrafo("El respaldo lo genera la API en la PC principal con `pg_dump -Fc` hacia la carpeta del disco externo (`Respaldo.Carpeta`), desde el módulo F9. Se avisa si el último tiene más de 24 horas. Para restaurar, con el programa cerrado en las tres PC, se crea una base vacía y se carga el respaldo con `pg_restore`; si los conteos son correctos se renombran las bases (`docs/respaldo.md`). La salvaguarda S3 de G06 verificó este procedimiento con conteos idénticos en 8 tablas.")
    fig(doc, "cod_restaurar")
    doc.parrafo("Se recomienda un ensayo de restauración mensual. Los comprobantes emitidos después del respaldo no están en él y deben volver a registrarse desde sus tickets o los CDR de la SUNAT.")

    doc.titulo(1, "11. Pruebas")
    doc.tabla([
        ["Tipo (guía)", "Herramienta", "Comando", "Evidencias"],
        ["Unitarias, integración y aceptación (G07)", "xUnit 2.9.2 + coverlet", "`dotnet test` (con `CONDOR_TEST_CONN` para las de base de datos)", "`G09/04_Reportes/xunit_1.2.0-r32`"],
        ["Suite de negocio y cobertura (G07)", "xUnit + ReportGenerator", "`G07_Pruebas_Unitarias\\01_Suite\\ejecutar_suite.ps1`", "`G07/03_Reportes`"],
        ["Defecto controlado (G07)", "xUnit", "`G07_Pruebas_Unitarias\\04_Defecto_Controlado\\reproducir_defecto.ps1`", "`G07/04_Defecto_Controlado`"],
        ["Rendimiento (G08)", "Apache JMeter 5.6.3, modo no gráfico", "`G08_Pruebas_Rendimiento\\02_Scripts\\ejecutar_todos.ps1`", "`G08/04_Resultados`"],
        ["Aceptación y regresión web (G09)", "Selenium 4.52.0 (Python)", "Con la API arrancada: `G09_Gestion_Calidad\\02_Suite\\ejecutar_suite.ps1 -Etiqueta <nombre>`", "`G09/04_Reportes`"],
    ], anchos_cm=[3.6, 3.4, 5.6, 3.4])
    doc.parrafo("Las pruebas marcadas `[FactConBD]` aparecen como omitidas si no hay base de pruebas configurada; nunca se debe apuntar `CONDOR_TEST_CONN` a la base `condor` de producción. Resultado de referencia en la versión entregada: 944 aprobadas, 0 fallidas, 5 omitidas; Selenium 14/14.")

    doc.titulo(1, "12. Gestión de configuración")
    doc.vinetas([
        "Estructura `trunk/`, `branches/<ID>-<descripción>` y `tags/vX.Y.Z` (solo lectura; solo el responsable de configuración crea etiquetas).",
        "Para reconstruir la versión entregada: `svn export svn://127.0.0.1/condor/tags/v1.0.1 condor_v1.0.1` y compilar `Sistema_Logistico_Condor_final`.",
        "Para restaurar el repositorio en otro equipo: `svnadmin create` y `svnadmin load` con `G05_Gestion_Configuracion/03_Respaldo/condor_r44.dump.gz` descomprimido; luego `svnserve -d -r <carpeta>`.",
        "Cada cambio se desarrolla en su rama y se integra al trunk con la suite en verde; los mensajes de commit empiezan con el ID (CC, DEF, MEJ o requisito).",
        "Política completa, permisos y manifiesto: `G05_Gestion_Configuracion/01_Politica/politica_configuracion.md`.",
    ])

    doc.titulo(1, "13. Solución de problemas")
    doc.tabla([
        ["Síntoma", "Causa probable", "Solución"],
        ["`ejecutar.ps1 -Api` dice que la API no respondió", "Primer arranque del .exe recién publicado tarda más de 1 min", "Esperar y abrir `/api/salud`, o repetir con `-SinCompilar`"],
        ["La app muestra el aviso de conexión", "API detenida o IP incorrecta en `condor.json`", "Arrancar `CondorApi.exe`; revisar `Api.Url` y el firewall (puerto 5080)"],
        ["`/api/salud` responde 503", "PostgreSQL detenido o credenciales erradas", "Arrancar el servicio o el contenedor `Cas_condor`; revisar `BaseDatos` en appsettings.json"],
        ["Comprobantes siempre PENDIENTE", "Sección `Sunat` vacía o sin internet", "Configurar la SUNAT en la PC con internet (`docs/sunat.md`)"],
        ["Ticket no se imprime", "Nombre de la ticketera distinto al de Windows, sin papel o apagada", "Corregir `Ticketera.Nombre`; reimprimir con F11"],
        ["Usuario bloqueado", "5 intentos fallidos", "Esperar 15 min o desbloquear con el `UPDATE` de la sección 9"],
        ["Puerto 5433 ocupado", "Otro PostgreSQL en el equipo", "`.\\ejecutar.ps1 -Puerto <otro>`"],
    ], anchos_cm=[4.6, 5.4, 6.0])

    doc.titulo(1, "14. Limitaciones y componentes de terceros")
    doc.vinetas([
        "La API y el portal funcionan por HTTP: implantar HTTPS antes de instalar en el local (O-2).",
        "Guías de remisión, ticketera y generación del respaldo solo están en la app de escritorio.",
        "No hay pantalla de administración de usuarios.",
        "La SUNAT se simula en las pruebas; el ambiente beta requiere configurarse.",
        "Terceros: .NET 8, ASP.NET Core, WPF, Npgsql, PostgreSQL 16, xUnit, coverlet; el XML UBL se basa en el modelo de Greenter / sunat-manager.",
    ])

    pie_paginado(doc, "Manual técnico — Sistema Cóndor %s" % VERSION)
    os.makedirs(SALIDA, exist_ok=True)
    salida = os.path.join(SALIDA, "Manual_Tecnico_Condor.docx")
    doc.guardar(salida)
    informar(salida)


if __name__ == "__main__":
    construir()
