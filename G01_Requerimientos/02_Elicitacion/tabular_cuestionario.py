"""Tabula CUE-01_respuestas.csv y escribe CUE-01_tabulacion.md.

    python tabular_cuestionario.py
"""
import csv
from collections import Counter
from pathlib import Path
from statistics import mean, median

AQUI = Path(__file__).resolve().parent
filas = list(csv.DictReader((AQUI / "CUE-01_respuestas.csv").open(encoding="utf-8")))
n = len(filas)

CERRADAS = {
    "P1": ("Antigüedad como vendedor", {"a": "< 6 meses", "b": "6 a 12 meses", "c": "1 a 3 años", "d": "> 3 años"}),
    "P2": ("Clientes esperando en hora punta", {"a": "0 a 1", "b": "2 a 3", "c": "4 a 5", "d": "más de 5"}),
    "P3": ("Lo que más demora una venta", {"a": "Buscar el precio", "b": "Calcular el total y el IGV",
                                           "c": "Llenar la boleta o factura", "d": "Pedir los datos del cliente"}),
    "P4": ("Frecuencia de errores de precio o cálculo", {"a": "Nunca", "b": "Una vez al mes",
                                                         "c": "Una vez a la semana", "d": "Casi todos los días"}),
}
LIKERT = {
    "P5": ("Encontrar el producto con parte del nombre", "RF-05, RNF-01"),
    "P6": ("Usaría el lector de código de barras", "RF-04, RF-05"),
    "P7": ("Trabajar solo con el teclado", "RNF-06"),
    "P8": ("Ticket impreso al emitir", "RF-09"),
    "P9": ("Usuario y contraseña al inicio del turno no molesta", "RF-01, CFL-01"),
    "P10": ("Usuario y contraseña en cada venta retrasaría", "RF-01, CFL-01"),
    "P11": ("Consultar las ventas del día", "RF-14"),
    "P12": ("Cambiar el precio para hacer descuentos", "CFL-03"),
    "P13": ("Pedir DNI en todas las boletas demoraría", "CRQ-02, CFL-04"),
}

L = ["# CUE-01 · Tabulación del cuestionario", "",
     f"Generado con `tabular_cuestionario.py` a partir de `CUE-01_respuestas.csv` (n = {n}). "
     "**Usuario representado:** las respuestas las dieron integrantes del equipo en el rol de vendedor.", "",
     "## Preguntas cerradas", ""]
for p, (titulo, op) in CERRADAS.items():
    c = Counter(f[p] for f in filas)
    L.append(f"**{p}. {titulo}**")
    L.append("")
    L.append("| Opción | Respuestas | % |")
    L.append("|---|---|---|")
    for k, v in op.items():
        L.append(f"| {v} | {c.get(k, 0)} | {100 * c.get(k, 0) / n:.0f} % |")
    L.append("")

L += ["## Escala de 1 a 5", "",
      "| N.º | Afirmación | Media | Mediana | % de acuerdo (4 o 5) | Requisito |",
      "|---|---|---|---|---|---|"]
for p, (titulo, req) in LIKERT.items():
    v = [int(f[p]) for f in filas]
    acuerdo = 100 * sum(x >= 4 for x in v) / n
    L.append(f"| {p} | {titulo} | {mean(v):.2f} | {median(v):g} | {acuerdo:.0f} % | {req} |")
L.append("")

L += ["## Preguntas abiertas", "", "| Vendedor | P14 · Lo que más molesta | P15 · Lo que debe hacer bien |", "|---|---|---|"]
for f in filas:
    L.append(f"| {f['vendedor']} ({f['turno']}) | {f['P14']} | {f['P15']} |")
L.append("")

L += ["## Interpretación y requisitos derivados", "",
      "- **Buscar el precio** es la principal demora (P3) y la búsqueda por parte del nombre tiene 100 % de acuerdo (P5): "
      "confirma **RF-05** y la meta de **RNF-01** (sugerencias en menos de 1 s).",
      "- El **lector de código de barras** sería usado por todos (P6): se incluye en **RF-04** y **RF-05**.",
      "- Trabajar **solo con el teclado** tiene 100 % de acuerdo (P7): **RNF-06** con atajos F1 a F11.",
      "- El ingreso **una vez por turno** es aceptado (P9, 75 %), pero en **cada venta** sería rechazado (P10, 100 %): "
      "sustenta la resolución de **CFL-01** (token válido por 480 minutos).",
      "- Tres de cuatro quieren **cambiar el precio** (P12): choca con el gerente; se registra **CFL-03**.",
      "- Pedir el **DNI en todas las boletas** demoraría (P13, 100 %): se exige solo desde S/ 700 (**CRQ-02**, **CFL-04**).",
      "- Errores semanales o diarios en 3 de 4 vendedores (P4): justifica el cálculo automático del IGV (**CRQ-01**).", ""]

(AQUI / "CUE-01_tabulacion.md").write_text("\n".join(L), encoding="utf-8")
print("CUE-01_tabulacion.md generado")
