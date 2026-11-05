# Fichas de herramientas — G04

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

## Microsoft Excel — libro de estimación

| Campo | Contenido |
|---|---|
| Versión exacta | Microsoft Excel 16.0 (compilación 14334) |
| Finalidad | Libro editable con fórmulas: NESMA, COSMIC, COCOMO II, escenarios, sensibilidad, horas reales y comparación |
| Requisitos de instalación | Windows 10/11 con Microsoft Office. El libro se abre también en LibreOffice Calc 7 o superior (usa funciones estándar: `IF`, `INDEX`, `MATCH`, `COUNTIFS`, `SUMIF`, `PRODUCT` y nombres definidos) |
| Procedencia | Licencia institucional de Microsoft Office |
| Licencia | Comercial (licencia de la universidad) |
| Configuración | Nombres definidos en la hoja *Parámetros* (`Tarifa`, `LocPorPF`, `HorasPM`, `A_coc`…); celdas amarillas editables; listas desplegables para el tipo NESMA y los niveles de COCOMO |
| Ejecución | Abrir `01_Libro/estimacion_condor.xlsx` y cambiar cualquier celda amarilla: el libro se recalcula. Para regenerarlo desde cero, ver los comandos debajo de esta tabla. |
| Archivos generados | `01_Libro/estimacion_condor.xlsx`; capturas en `03_Capturas/` |

Para regenerar el libro desde cero:

```
python generar_libro.py
python recalcular.py
python capturar_excel.py
```

## Scripts de apoyo (Python)

| Campo | Contenido |
|---|---|
| Versión exacta | Python 3.12.0; openpyxl 3.1.5 (escribe el libro con fórmulas); pywin32 (automatiza Excel por COM, sin ventana) |
| Finalidad | `generar_libro.py`: construye el libro. `recalcular.py`: Excel recalcula y se listan las celdas con error (resultado: 0 errores). `capturar_excel.py`: exporta imágenes de los rangos tal como los dibuja Excel (`Range.CopyPicture`), con valores y con fórmulas, sin tomar el control del teclado ni de la pantalla. `contar_sloc.py`: mide el tamaño real del código. |
| Requisitos de instalación | `pip install openpyxl pywin32`; Excel instalado para recalcular y capturar |
| Procedencia | Escritos por el equipo |
| Licencia | Uso académico |
| Ejecución | `python contar_sloc.py ..\..\Sistema_Logistico_Condor_final` |
| Archivos generados | Libro, capturas y conteo de SLOC por proyecto |
