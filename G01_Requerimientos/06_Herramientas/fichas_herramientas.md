# Fichas de herramientas — G01

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## REMUS — REquirements Manager, Universidad de Sevilla

| Campo | Contenido |
|---|---|
| Versión exacta | 1.3.0.0 (`remus.exe`); repositorio en el commit `4d6bb0d` (03-10-2022) |
| Finalidad | Elaborar la ERS: objetivos, requisitos de información, reglas, actores, casos de uso, RNF, matrices de trazabilidad y conflictos |
| Requisitos de instalación | Windows 10/11; Internet Explorer 11 / componente WebBrowser (vista HTML); para generar por script, *Microsoft Access Database Engine* (ACE OLEDB 12.0 o 16.0) |
| Procedencia | `git clone https://github.com/amador-duran-toro/remus.git` |
| Licencia | Gratuita, distribución binaria para beta testers (uso académico) |
| Configuración | `remus/bin/remus.ini`: idioma `Spanish`, plantilla base `remus_base_empty_spanish.rem`, hojas XSLT `REMUS_Spanish.xsl`. Copia incluida en `03_REMUS/remus/` para que la carpeta sea portable. |
| Ejecución | 1) `powershell -ExecutionPolicy Bypass -File 03_REMUS\generar_rem.ps1` crea `condor.rem` desde `condor_datos.json`. 2) Abrir `condor.rem` con `remus\bin\remus.exe`: al abrirlo genera el HTML y el log. |
| Archivos generados | `condor.rem` (documento), `condor.xml`, `condor__CRS.html` (ERS navegable), `condor__DRS/CFS/CHS.html` (documentos vacíos de análisis, defectos y cambios), `condor.log.xml` (vacío = sin errores), `condor_ERS_REMUS.pdf` (impresión del HTML) |
| Impedimento registrado | REM (la herramienta nombrada en la guía) no se puede descargar: el enlace oficial devuelve 404 (evidencia: `impedimento_REM_404.png`). Se usa REMUS, del mismo autor y con el mismo modelo. **Sustitución por validar con el docente.** |

## Generador de la ERS (`01_ERS/generar_ers.py`)

| Campo | Contenido |
|---|---|
| Versión | Python 3.12.0; solo usa la biblioteca estándar |
| Finalidad | Producir la ERS en Markdown con la estructura IEEE 830 desde la misma fuente que REMUS, para no tener dos versiones distintas |
| Ejecución | `python 01_ERS\generar_ers.py` |
| Archivos generados | `01_ERS/ERS_Condor_v1.1.md` |

## Microsoft Excel + openpyxl + matplotlib (cronograma)

| Campo | Contenido |
|---|---|
| Versión | Microsoft Excel (Microsoft 365, Office16); Python 3.12.0, openpyxl 3.1.5, matplotlib 3.11.2 |
| Finalidad | Cronograma editable con fórmulas (duración = Fin − Inicio + 1; horas totales; Gantt por formato condicional) y su imagen |
| Ejecución | `python 04_Cronograma\generar_cronograma.py` y abrir `cronograma.xlsx` en Excel |
| Archivos generados | `cronograma.xlsx`, `cronograma.png`, `captura_excel_cronograma.png` |

## Tabulación del cuestionario y organigrama

| Campo | Contenido |
|---|---|
| Herramienta | Python 3.12.0 (csv, statistics) y matplotlib 3.11.2 |
| Ejecución | `python 02_Elicitacion\tabular_cuestionario.py` · `python 05_Organizacion\generar_organigrama.py` |
| Archivos generados | `CUE-01_tabulacion.md` · `organigrama.png` |

## Google Chrome sin interfaz (exportación del HTML de REMUS a PDF)

| Campo | Contenido |
|---|---|
| Finalidad | Imprimir `condor__CRS.html` a PDF para entregarlo y revisarlo sin abrir REMUS |
| Ejecución | `chrome --headless=new --no-pdf-header-footer --print-to-pdf=condor_ERS_REMUS.pdf condor__CRS.html` |
| Archivos generados | `03_REMUS/condor_ERS_REMUS.pdf` y las capturas `capturas/10_…` a `17_…` |
