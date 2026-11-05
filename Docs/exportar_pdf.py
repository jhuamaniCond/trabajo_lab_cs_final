# -*- coding: utf-8 -*-
"""
exportar_pdf.py
Abre cada .docx de Docs/salida en Microsoft Word (COM, sin ventana), actualiza
el índice y los campos, guarda el .docx con el índice ya relleno y exporta el PDF.

    python Docs/exportar_pdf.py
"""

import glob
import os

import win32com.client

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
WD_PDF = 17


def main():
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for ruta in sorted(glob.glob(os.path.join(SALIDA, "*.docx"))):
            if os.path.basename(ruta).startswith("~$"):
                continue
            doc = word.Documents.Open(os.path.abspath(ruta))
            for toc in doc.TablesOfContents:
                toc.Update()
            doc.Fields.Update()
            doc.Save()
            pdf = os.path.splitext(ruta)[0] + ".pdf"
            doc.ExportAsFixedFormat(pdf, WD_PDF)
            print("PDF:", pdf, "· páginas:", doc.ComputeStatistics(2))
            doc.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    main()
