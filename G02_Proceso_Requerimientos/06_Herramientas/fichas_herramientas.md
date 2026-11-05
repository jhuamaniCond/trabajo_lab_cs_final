# Fichas de herramientas — G02

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## Redmine — gestor de requisitos y cambios

| Campo | Contenido |
|---|---|
| Versión exacta | Redmine **7.0.1** (Rails 8.1.3.1, Ruby 4.0.6, SQLite) sobre Debian 13. Imagen `redmine:latest`, digest `sha256:6129b73568e1…` (26-08-2026) |
| Finalidad | Registrar requisitos y solicitudes de cambio, imponer el flujo registrado → analizado → aprobado/rechazado → implementado → verificado → cerrado por rol, conservar el historial (fecha, usuario, nota, adjuntos) y emitir reportes de seguimiento |
| Requisitos de instalación | Windows 10/11 con Docker Desktop 29.x (WSL 2), unos 1.1 GB para la imagen y el puerto 3010 libre |
| Procedencia | Imagen oficial de Docker Hub (`docker.io/library/redmine`), proyecto https://www.redmine.org |
| Licencia | GNU GPL v2, gratuita |
| Configuración | `01_Redmine/configurar_redmine.rb` (se ejecuta con `rails runner`): idioma español, zona horaria de Lima, API REST activa, 7 estados, tipos *Requisito* y *Solicitud de cambio*, 5 roles (Analista, CCB, Desarrollador, Evaluador de calidad, Responsable de configuración), 14 transiciones por rol, 13 campos personalizados, 5 usuarios, proyecto `condor` con versiones 1.0.0 y 1.1.0 |
| Ejecución | Ver el procedimiento debajo de esta tabla |
| Archivos generados | `01_Redmine/exportaciones/peticiones_condor.csv` y `.pdf` (lista de peticiones), `peticion_N_ID.pdf` (cada petición con su historial), `01_Redmine/respaldo/redmine.db` (base completa) y `redmine_files.tgz` (adjuntos), capturas en `01_Redmine/capturas/` |
| Credenciales de demostración | `admin`, `jhuamani`, `jpayehuanca`, `rcondo`, `achaisa` y `gerente`, todos con la clave `Condor2026!` |

Procedimiento de ejecución:

```
docker run -d --name redmine-condor -p 3010:3000 -v redmine-condor-files:/usr/src/redmine/files -v redmine-condor-db:/usr/src/redmine/sqlite redmine:latest
docker exec -e REDMINE_LANG=es -e RAILS_ENV=production redmine-condor bundle exec rake redmine:load_default_data
docker cp configurar_redmine.rb redmine-condor:/tmp/
docker exec -e RAILS_ENV=production redmine-condor bundle exec rails runner /tmp/configurar_redmine.rb
python cargar_redmine.py http://localhost:3010 <clave API del admin>
```

Después se abre http://localhost:3010 en el navegador.

**Restaurar el respaldo** (sin repetir la carga): crear el contenedor con el comando anterior, `docker cp respaldo/redmine.db redmine-condor:/usr/src/redmine/sqlite/redmine.db`, descomprimir `redmine_files.tgz` en `/usr/src/redmine` y reiniciar el contenedor.

## Scripts de carga y reporte (Python)

| Campo | Contenido |
|---|---|
| Versión exacta | Python 3.12.0; solo biblioteca estándar (`urllib`, `json`, `xml.etree`) |
| Finalidad | `cargar_redmine.py`: crea los 24 requisitos desde `G01_Requerimientos/03_REMUS/condor_datos.json` (la misma fuente de la ERS) y las dos solicitudes de cambio, y las hace recorrer el flujo. Cada transición se hace como el integrante que tiene el rol (cabecera `X-Redmine-Switch-User`), así que Redmine valida el flujo de su perfil. `generar_informe_seguimiento.py`: arma el informe de seguimiento con los datos que devuelve la API |
| Requisitos de instalación | Python 3.10 o superior |
| Procedencia | Escritos por el equipo |
| Licencia | Uso académico |
| Configuración | URL de Redmine y clave API del administrador como argumentos (la clave se lee en *Mi cuenta → Clave de acceso a la API*) |
| Ejecución | `python cargar_redmine.py http://localhost:3010 <clave>` · `python generar_informe_seguimiento.py http://localhost:3010 <clave>` |
| Archivos generados | Peticiones e historial en Redmine; `05_Seguimiento/informe_seguimiento.md` |

## Selenium WebDriver + Google Chrome (capturas de la interfaz)

| Campo | Contenido |
|---|---|
| Versión exacta | Selenium 4.52.0 (Python); Google Chrome 156.0.8078.79, sin ventana; el controlador lo resuelve Selenium Manager |
| Finalidad | Tomar capturas de página completa de la interfaz web de Redmine (`01_Redmine/capturar_redmine.py`). Antes de capturar reemplaza el texto relativo «hace 2 minutos» por la fecha y hora exactas, que Redmine guarda en el atributo `title` |
| Requisitos de instalación | `pip install selenium` y Chrome instalado |
| Procedencia | PyPI (`selenium`) y Google |
| Licencia | Apache 2.0 (Selenium); Chrome es gratuito |
| Configuración | Ventana de 1440 × 900 px, idioma español |
| Ejecución | `python capturar_redmine.py http://localhost:3010` |
| Archivos generados | `01_Redmine/capturas/01_estados.png` a `22_hoja_de_ruta_1.1.0.png` |

## SDK de .NET 8 en Docker (pruebas del producto)

| Campo | Contenido |
|---|---|
| Versión exacta | Imagen `mcr.microsoft.com/dotnet/sdk:8.0`; xUnit 2.9.2 y Microsoft.NET.Test.Sdk 17.11.1 (`tests/Condor.Pruebas`) |
| Finalidad | Ejecutar la suite del producto 1.1.0 y la regresión de CC-01, que son la evidencia de las transiciones a Verificado |
| Requisitos de instalación | Docker Desktop; PostgreSQL 16 del producto (contenedor `Cas_condor`, puerto 5433) con la base `condor_pruebas` |
| Procedencia | Microsoft Container Registry |
| Licencia | MIT |
| Configuración | Variable `CONDOR_TEST_CONN=Host=host.docker.internal;Port=5433;Database=condor_pruebas;Username=condor_app;Password=…` para las pruebas `[FactConBD]` |
| Ejecución | Ver el comando debajo de esta tabla |
| Archivos generados | `04_Pruebas/suite_completa_v1.1.0.trx` y `.html`; `04_Pruebas/regresion_CC-01.trx` y `.html` |

Comando de ejecución (desde `Trabajo Grupal`):

```
docker run --rm -v "<ruta>/Sistema_Logistico_Condor_final:/repo:ro" -v "<ruta>/G02_Proceso_Requerimientos/04_Pruebas:/out" -e CONDOR_TEST_CONN=... mcr.microsoft.com/dotnet/sdk:8.0 sh -c 'cp -r /repo /src && cd /src && dotnet test tests/Condor.Pruebas/Condor.Pruebas.csproj --logger "trx;LogFileName=suite_completa_v1.1.0.trx" --logger "html;LogFileName=suite_completa_v1.1.0.html" --results-directory /out'
```

El filtro de la regresión está en `03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md`.

## Diagrama del flujo (matplotlib)

| Campo | Contenido |
|---|---|
| Versión exacta | matplotlib (Python 3.12.0) |
| Finalidad | Dibujar el flujo de estados, con el rol de cada transición y la evidencia que se exige |
| Ejecución | `python 02_Flujo/generar_flujo.py` |
| Archivos generados | `02_Flujo/flujo_requerimientos.png` (la fuente editable es el mismo `.py`) |
| Impedimento | Se pensaba usar PlantUML, pero no se pudo descargar su `.jar` en este equipo. Se usó matplotlib, como en el organigrama de G01. El diagrama equivalente de la herramienta es la matriz de *Flujo de trabajo* de Redmine (`01_Redmine/capturas/05_flujo_resumen.png` a `09_flujo_evaluador.png`). |
