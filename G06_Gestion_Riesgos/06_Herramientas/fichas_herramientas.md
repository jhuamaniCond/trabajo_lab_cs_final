# Fichas de herramientas — G06

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## PILAR Basic

| Campo | Contenido |
|---|---|
| Versión exacta | **PILAR Basic 2026.1.1** (28/5/2026), biblioteca `[std] Biblioteca INFOSEC (22.7.2023)` y `std_20251.pl5`, configuración `BASIC_es.car` |
| Finalidad | Análisis y gestión de riesgos con MAGERIT v3: activos, dependencias, valoración, amenazas, salvaguardas e impacto y riesgo en fases potencial, actual y objetivo |
| Requisitos de instalación | Windows 10/11; entorno de ejecución Java 8 o superior (se usó Java SE 26.0.2.1); instalador Inno Setup en `C:\Program Files (x86)\PilarBasic_2026.1` |
| Procedencia | Portal del CCN-CERT: https://pilar.ccn-cert.cni.es/ (desarrollador A.L.H. J. Mañas S.L.) |
| Licencia o restricciones | Licencia de evaluación `test` (`03_PILAR/capturas/01_pilar_licencia_evaluacion.png`). **Restricciones observadas**: la exportación a CSV, HTML y XML está deshabilitada y el mapa de riesgos y los informes R.x salen con la marca «modo evaluación» (`12_pilar_mapa_riesgos_modo_evaluacion.png`). Por eso las evidencias son el proyecto `.mgr` y capturas de la interfaz. |
| Configuración | Proyecto `[CONDOR]` con dominio `[base]`, fases potencial, current, target y PILAR; perfil de amenazas `tsv_last.xlsx` y `ext_tsv_pi.xlsx`; escala de valoración 0–10 |
| Ejecución | Abrir `pilarbasic.exe` con su carpeta de instalación como directorio de trabajo → *Análisis y Gestión de Riesgos* → *Proyecto › Recientes* → `CONDOR.mgr`. Fases usadas: A.1 activos, A.2 valoración, A.4 amenazas, A.5.1 salvaguardas, A.6 riesgo. La carga se automatizó con los scripts de `03_PILAR/scripts` (Java Access Bridge), que no usan el ratón ni el teclado del usuario. |
| Archivos generados | `03_PILAR/CONDOR.mgr` (proyecto vigente), `CONDOR_1.mgr` (copia de seguridad automática que deja PILAR al guardar) y capturas `03_PILAR/capturas/01` a `12` |

## Microsoft Excel (matriz y plan de tratamiento)

| Campo | Contenido |
|---|---|
| Versión exacta | Microsoft Excel **16.0, compilación 14334** (formato `.xlsx`); los libros se crean con Python 3 y openpyxl 3.1.5 y Excel los recalcula |
| Finalidad | Matriz MAGERIT con fórmulas de impacto y riesgo, priorización, plan de tratamiento con costos y la plantilla docente P × I |
| Requisitos de instalación | Excel 2016 o superior, o LibreOffice Calc 7 o superior; para regenerar: Python 3.10 o superior con `pip install openpyxl` |
| Procedencia | Microsoft Office · https://pypi.org/project/openpyxl/ · plantilla `Plan_Riesgo_Guia_6_Alumnos.xlsx` entregada por el docente |
| Licencia | Excel: licencia comercial de Microsoft Office · openpyxl: MIT · LibreOffice: MPL 2.0 |
| Configuración | Cálculo automático; las tablas de MAGERIT están en la hoja *Escalas* y las fórmulas usan `INDEX/MATCH`; la tarifa (S/ 25/h) está en una celda de entrada |
| Ejecución | `python 02_Matriz_y_Tratamiento/generar_matrices.py` y abrir los libros en Excel |
| Archivos generados | `matriz_riesgos_magerit.xlsx`, `Plan_Riesgo_Condor.xlsx`, `02_Matriz_y_Tratamiento/capturas/*.png` |

## Verificación de controles (Python y xUnit)

| Campo | Contenido |
|---|---|
| Versión exacta | Python 3 (biblioteca estándar: `urllib`, `subprocess`); PostgreSQL 16 (`pg_dump`, `pg_restore` dentro del contenedor `Cas_condor`); suite xUnit del producto ejecutada con .NET SDK 8.0 en Docker (`mcr.microsoft.com/dotnet/sdk:8.0`) |
| Finalidad | Prueba de funcionamiento de S1, S2 y S3 contra la API 1.1.1 en ejecución y la base real, y repetición de las pruebas automatizadas relacionadas |
| Requisitos | API en `http://localhost:5080` (`Sistema_Logistico_Condor_final\ejecutar.ps1 -Api`) y Docker Desktop con el contenedor de PostgreSQL |
| Procedencia | Scripts propios del equipo |
| Licencia | Python: PSF · PostgreSQL: licencia PostgreSQL · .NET: MIT |
| Ejecución | `python 04_Controles/verificar_controles.py http://localhost:5080` |
| Archivos generados | `04_Controles/verificacion_controles.md` (18 de 18 cumplen) y `pruebas_controles_S1_S2_S3.trx` (122 de 122 pasaron) |
