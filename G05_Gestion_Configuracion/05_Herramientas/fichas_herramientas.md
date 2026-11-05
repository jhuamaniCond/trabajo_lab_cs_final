# Fichas de herramientas — G05

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## Apache Subversion (servidor y línea de comandos)

| Campo | Contenido |
|---|---|
| Versión exacta | Subversion **1.14.5** (`svn`, `svnadmin`, `svnserve`, `svnlook`), instalado con las herramientas de línea de comandos de TortoiseSVN |
| Finalidad | Repositorio centralizado de los elementos de configuración; servidor `svnserve` con usuarios y permisos por ruta |
| Requisitos de instalación | Windows 10/11, 64 bits; al instalar TortoiseSVN, marcar *command line client tools* |
| Procedencia | https://tortoisesvn.net/downloads.html (incluye los binarios de Apache Subversion) |
| Licencia | Apache License 2.0 |
| Configuración | Repositorio FSFS en `02_Repositorio/condor`. Archivos `conf/svnserve.conf` (sin acceso anónimo, base de usuarios y de permisos), `conf/passwd` (5 usuarios), `conf/authz` (grupos `equipo` y `configuracion`; `/tags` solo para el responsable de configuración) y `hooks/pre-commit.bat` (mensaje de 10 caracteres como mínimo). Copia versionada en `06_Scripts/config_repositorio`, sin el archivo de claves. |
| Ejecución | Ver los comandos debajo de esta tabla |
| Archivos generados | El repositorio, `03_Respaldo/condor_r*.dump.gz`, `04_Evidencias/historial_svn.txt` y `.xml` |

Comandos de ejecución:

```
svnadmin create --fs-type fsfs condor
svnserve -d --foreground -r 02_Repositorio --listen-port 3690 --listen-host 127.0.0.1
svn checkout svn://127.0.0.1/condor/trunk "Trabajo Grupal" --force
```

## TortoiseSVN (cliente gráfico)

| Campo | Contenido |
|---|---|
| Versión exacta | TortoiseSVN **1.14.9.29743**, 64 bits (Subversion 1.14.5) |
| Finalidad | Operar el repositorio desde el Explorador de Windows: *Log*, *Repo-browser*, *Revision graph*, *Edit conflicts* (TortoiseMerge), *Branch/tag*, *Merge*, *Update to revision* |
| Requisitos de instalación | Windows 10/11; instalador MSI; reiniciar el Explorador para ver los iconos superpuestos |
| Procedencia | https://tortoisesvn.net/downloads.html |
| Licencia | GPL v2 |
| Configuración | Idioma inglés (el paquete de idioma español es opcional); credenciales de cada integrante en el diálogo de autenticación |
| Ejecución | Clic derecho sobre la copia de trabajo → *TortoiseSVN* → la operación. Desde la línea de comandos: `TortoiseProc.exe /command:log /path:"<ruta>"` |
| Archivos generados | Capturas en `04_Evidencias/capturas/` |

## Script de pruebas en Docker

| Campo | Contenido |
|---|---|
| Versión exacta | `06_Scripts/probar_en_docker.sh` (Bash); imagen `mcr.microsoft.com/dotnet/sdk:8.0` |
| Finalidad | Ejecutar la suite del producto de cualquier copia de trabajo (trunk, rama o integración) y dejar el reporte `.trx`, como condición para fusionar y etiquetar |
| Ejecución | `./probar_en_docker.sh <Sistema_Logistico_Condor_final> <salida> <nombre> [filtro]` |
| Archivos generados | `04_Evidencias/pruebas/*.trx` y `04_Evidencias/recuperacion/reconstruccion_producto_r2.trx` |
