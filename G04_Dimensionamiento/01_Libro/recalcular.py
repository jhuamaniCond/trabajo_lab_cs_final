"""Abre estimacion_condor.xlsx en Excel (sin ventana), recalcula todas las
fórmulas, guarda y lista cualquier celda con error.

    python recalcular.py
"""
from pathlib import Path

import win32com.client as win32

LIBRO = Path(__file__).resolve().parent / "estimacion_condor.xlsx"

excel = win32.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(LIBRO))
    excel.CalculateFull()
    errores = 0
    for ws in wb.Worksheets:
        usado = ws.UsedRange
        for celda in usado:
            if celda.HasFormula and isinstance(celda.Value, int) and celda.Text.startswith("#"):
                print(f"{ws.Name}!{celda.Address}: {celda.Text}  {celda.Formula}")
                errores += 1
            elif celda.HasFormula and str(celda.Text).startswith("#"):
                print(f"{ws.Name}!{celda.Address}: {celda.Text}  {celda.Formula}")
                errores += 1
    wb.Save()
    wb.Close()
    print("errores:", errores)
finally:
    excel.Quit()
