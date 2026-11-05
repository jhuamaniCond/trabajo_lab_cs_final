"""Exporta imágenes de las hojas de estimacion_condor.xlsx tal como las dibuja
Excel (Range.CopyPicture → gráfico → PNG), sin mostrar ventanas ni usar el
teclado o el mouse. Genera cada hoja con valores y algunas con fórmulas.

    python capturar_excel.py
"""
import time
from pathlib import Path

import win32com.client as win32

AQUI = Path(__file__).resolve().parent
LIBRO = AQUI / "estimacion_condor.xlsx"
SALIDA = AQUI.parent / "03_Capturas"
SALIDA.mkdir(exist_ok=True)

# (hoja, rango, archivo, mostrar fórmulas)
CAPTURAS = [
    ("Parámetros", "A1:D33", "01_parametros.png", False),
    ("Frontera", "A1:D28", "02_frontera_linea_base.png", False),
    ("NESMA detallado", "A1:I17", "03_nesma_funciones_datos.png", False),
    ("NESMA detallado", "A18:H56", "04_nesma_transacciones.png", False),
    ("NESMA detallado", "A19:G30", "05_nesma_formulas.png", True),
    ("NESMA detallado", "A58:G69", "06_nesma_resumen.png", False),
    ("NESMA rápido", "A1:E15", "07_nesma_estimado_indicativo.png", False),
    ("COSMIC", "A1:I45", "08_cosmic.png", False),
    ("COCOMO II", "A1:J30", "09_cocomo_factores.png", False),
    ("COCOMO II", "A32:D47", "10_cocomo_resultados.png", False),
    ("COCOMO II", "A33:C47", "11_cocomo_formulas.png", True),
    ("Escenarios", "A1:L12", "12_escenarios_1_y_3_personas.png", False),
    ("Escenarios", "A4:L8", "13_escenarios_formulas.png", True),
    ("Sensibilidad", "A1:H17", "14_sensibilidad.png", False),
    ("Horas reales", "A1:F35", "15_horas_reales.png", False),
    ("Comparación", "A1:D24", "16_cuadro_comparativo.png", False),
]

excel = win32.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(LIBRO), ReadOnly=True)
    for hoja, rango, archivo, formulas in CAPTURAS:
        ws = wb.Worksheets(hoja)
        ws.Activate()
        wb.Windows(1).DisplayFormulas = formulas
        rng = ws.Range(rango)
        rng.CopyPicture(Appearance=1, Format=2)       # xlScreen, xlBitmap
        graf = ws.ChartObjects().Add(0, 0, rng.Width + 4, rng.Height + 4)
        graf.Activate()
        for _ in range(5):                            # el portapapeles puede tardar
            try:
                graf.Chart.Paste()
                break
            except Exception:
                time.sleep(0.5)
        graf.Chart.ChartArea.Format.Line.Visible = False
        graf.Chart.Export(str(SALIDA / archivo), "PNG")
        graf.Delete()
        print(archivo)
    wb.Windows(1).DisplayFormulas = False
    wb.Close(SaveChanges=False)
finally:
    excel.Quit()
