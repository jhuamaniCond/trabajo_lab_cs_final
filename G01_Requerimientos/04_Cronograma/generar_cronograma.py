"""Genera el cronograma del Trabajo Grupal: cronograma.xlsx (editable) y cronograma.png.

    python generar_cronograma.py

El Excel no tiene valores calculados a mano: la duración, las horas totales y las
barras del Gantt son fórmulas y formato condicional, de modo que al cambiar una
fecha de inicio o de fin todo se recalcula.
"""
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
D = lambda m, d: date(2026, m, d)

# Modelo de proceso: incremental en tres incrementos, uno por entrega (hito).
# (id, incremento, actividad, guía, responsable, inicio, fin, horas plan, entregable)
ACTIVIDADES = [
    ("A01", "Inc. 1", "Leer el enunciado y elegir el producto (Cóndor)", "—", "Todos", D(10, 26), D(10, 27), 6, "Propuesta de alcance"),
    ("A02", "Inc. 1", "Elicitación: entrevista, cuestionario y observación", "G01", "Integrante 1, Integrante 3", D(10, 28), D(10, 29), 10, "02_Elicitacion"),
    ("A03", "Inc. 1", "ERS 0.9, revisión y línea base 1.0 en REMUS", "G01", "Integrante 1", D(10, 29), D(10, 29), 8, "ERS 1.0, lista de revisión"),
    ("A04", "Inc. 1", "Solicitud de cambio CC-01 y ERS 1.1", "G01/G02", "Integrante 2", D(10, 30), D(10, 30), 4, "ERS 1.1"),
    ("A05", "Inc. 1", "Cronograma, organigrama y comparación de herramientas", "G01", "Integrante 1", D(10, 30), D(10, 31), 5, "04, 05, 06"),
    ("A06", "Inc. 1", "Gestor de requisitos: flujo e historial de 5 requisitos", "G02", "Integrante 2", D(11, 2), D(11, 5), 10, "Exportación del gestor"),
    ("A07", "Inc. 1", "SDD, UML, casos de uso y mockups", "G03", "Integrante 3", D(11, 2), D(11, 8), 18, "SDD y fuentes UML"),
    ("A08", "Inc. 1", "Conteo NESMA, medición COSMIC y COCOMO", "G04", "Integrante 4", D(11, 3), D(11, 9), 14, "Libro de cálculo"),
    ("A09", "Inc. 1", "Repositorio SVN, política de configuración e importación", "G05", "Integrante 2", D(11, 2), D(11, 4), 8, "Repositorio y política"),
    ("H1", "Hito", "Primer entregable sustentado (alcance validado)", "—", "Todos", D(11, 11), D(11, 11), 2, "Avance 1"),
    ("A10", "Inc. 2", "Análisis de riesgos MAGERIT en PILAR y dos controles", "G06", "Integrante 4", D(11, 10), D(11, 18), 16, "Proyecto PILAR"),
    ("A11", "Inc. 2", "Pruebas unitarias, cobertura y defecto controlado", "G07", "Integrante 1", D(11, 10), D(11, 17), 16, "Suite y reportes"),
    ("A12", "Inc. 2", "Plan JMeter: carga, estrés, pico, estabilidad y mejora", "G08", "Integrante 3", D(11, 12), D(11, 22), 18, ".jmx, .jtl, HTML"),
    ("A13", "Inc. 2", "Suite de aceptación automatizada (8 casos)", "G09", "Integrante 2", D(11, 16), D(11, 23), 18, "Suite y reportes"),
    ("A14", "Inc. 2", "Solicitud de cambio CC-02: impacto y decisión", "G02", "Integrante 2", D(11, 16), D(11, 19), 6, "CC-02"),
    ("H2", "Hito", "Segundo entregable", "—", "Todos", D(11, 25), D(11, 25), 2, "Avance 2"),
    ("A15", "Inc. 3", "Regresión final y dictamen de liberación", "G09", "Integrante 1", D(11, 26), D(11, 28), 8, "Dictamen"),
    ("A16", "Inc. 3", "Etiqueta v1.0.0 y recuperación en SVN", "G05", "Integrante 2", D(11, 26), D(11, 27), 4, "Tag v1.0.0"),
    ("A17", "Inc. 3", "Informe final, manuales, matriz de trazabilidad", "Todas", "Todos", D(11, 26), D(12, 1), 24, "Informe final"),
    ("A18", "Inc. 3", "Ensayo de la sustentación", "—", "Todos", D(12, 1), D(12, 1), 3, "—"),
    ("H3", "Hito", "Entrega final y sustentación", "—", "Todos", D(12, 2), D(12, 2), 2, "Paquete final"),
]
INICIO, FIN = D(10, 26), D(12, 2)

# ------------------------------------------------------------------ Excel
wb = Workbook()
ws = wb.active
ws.title = "Cronograma"
fina = Side(style="thin", color="000000")
borde = Border(left=fina, right=fina, top=fina, bottom=fina)
neg = Font(name="Calibri", bold=True)

ws["A1"] = "Cronograma del Trabajo Grupal — Sistema Cóndor (Calidad de Software 2026-B)"
ws["A1"].font = Font(name="Calibri", bold=True, size=13)
ws["A2"] = "Modelo de proceso: incremental, un incremento por entrega. Duración, horas y Gantt son fórmulas: cambie Inicio/Fin y se recalcula."

cab = ["ID", "Incremento", "Actividad", "Guía", "Responsable", "Inicio", "Fin", "Días", "Horas plan", "Horas reales", "Entregable"]
F0 = 4
for c, t in enumerate(cab, 1):
    x = ws.cell(row=F0, column=c, value=t)
    x.font = neg
    x.border = borde
    x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

col_g = len(cab) + 1  # primera columna del Gantt
dias = (FIN - INICIO).days + 1
for i in range(dias):
    dia = INICIO + timedelta(days=i)
    x = ws.cell(row=F0, column=col_g + i, value=dia)
    x.number_format = "dd"
    x.font = Font(name="Calibri", bold=True, size=8)
    x.alignment = Alignment(horizontal="center", text_rotation=90)
    x.border = borde
    ws.column_dimensions[get_column_letter(col_g + i)].width = 3.2
    m = ws.cell(row=F0 - 1, column=col_g + i, value=dia.strftime("%b").capitalize() if i == 0 or dia.day == 1 else None)
    m.font = Font(name="Calibri", bold=True, size=9)

for r, a in enumerate(ACTIVIDADES, F0 + 1):
    id_, inc, act, guia, resp, ini, fin, horas, ent = a
    vals = [id_, inc, act, guia, resp, ini, fin, f"=G{r}-F{r}+1", horas, None, ent]
    for c, v in enumerate(vals, 1):
        x = ws.cell(row=r, column=c, value=v)
        x.border = borde
        x.alignment = Alignment(vertical="center", wrap_text=(c in (3, 5, 11)))
        if c in (6, 7):
            x.number_format = "dd/mm/yyyy"
    if inc == "Hito":
        for c in range(1, len(cab) + 1):
            ws.cell(row=r, column=c).font = neg
    for i in range(dias):
        ws.cell(row=r, column=col_g + i).border = borde

ultima = F0 + len(ACTIVIDADES)
tot = ultima + 1
ws.cell(row=tot, column=3, value="Total").font = neg
ws.cell(row=tot, column=9, value=f"=SUM(I{F0 + 1}:I{ultima})").font = neg
ws.cell(row=tot, column=10, value=f"=SUM(J{F0 + 1}:J{ultima})").font = neg

# Barras del Gantt: formato condicional sobre la fecha de la cabecera
rango = f"{get_column_letter(col_g)}{F0 + 1}:{get_column_letter(col_g + dias - 1)}{ultima}"
c0 = get_column_letter(col_g)
ws.conditional_formatting.add(rango, FormulaRule(
    formula=[f'AND($B{F0 + 1}="Hito",{c0}${F0}>=$F{F0 + 1},{c0}${F0}<=$G{F0 + 1})'],
    fill=PatternFill(fill_type="solid", start_color="C00000", end_color="C00000"), stopIfTrue=True))
ws.conditional_formatting.add(rango, FormulaRule(
    formula=[f"AND({c0}${F0}>=$F{F0 + 1},{c0}${F0}<=$G{F0 + 1})"],
    fill=PatternFill(fill_type="solid", start_color="595959", end_color="595959")))

for col, ancho in zip("ABCDEFGHIJK", [5, 9, 46, 8, 22, 11, 11, 6, 8, 8, 22]):
    ws.column_dimensions[col].width = ancho
ws.freeze_panes = ws.cell(row=F0 + 1, column=col_g)
ws.row_dimensions[F0].height = 34
ws.sheet_view.zoomScale = 70

# Hoja de hitos
h = wb.create_sheet("Hitos")
for c, t in enumerate(["Hito", "Fecha", "Qué se entrega", "Días desde el inicio"], 1):
    h.cell(row=1, column=c, value=t).font = neg
hitos = [("H1", D(11, 11), "Alcance validado: G01 completo, G02 a G05 en curso"),
         ("H2", D(11, 25), "G02 a G09 con evidencias de avance"),
         ("H3", D(12, 2), "Paquete final, informe y sustentación de 20 minutos")]
h.cell(row=6, column=1, value="Inicio del trabajo")
h.cell(row=6, column=2, value=INICIO).number_format = "dd/mm/yyyy"
for r, (n, f, q) in enumerate(hitos, 2):
    h.cell(row=r, column=1, value=n)
    h.cell(row=r, column=2, value=f).number_format = "dd/mm/yyyy"
    h.cell(row=r, column=3, value=q)
    h.cell(row=r, column=4, value=f"=B{r}-$B$6")
h.column_dimensions["C"].width = 55
h.column_dimensions["B"].width = 12

wb.save(AQUI / "cronograma.xlsx")

# ------------------------------------------------------------------ PNG
fig, ax = plt.subplots(figsize=(13, 7.2))
plt.rcParams["font.family"] = "DejaVu Sans"
ys = list(range(len(ACTIVIDADES)))[::-1]
for y, a in zip(ys, ACTIVIDADES):
    id_, inc, act, guia, resp, ini, fin = a[:7]
    if inc == "Hito":
        ax.plot(mdates.date2num(ini) + 0.5, y, marker="D", color="#C00000", markersize=9)
    else:
        ax.barh(y, (fin - ini).days + 1, left=mdates.date2num(ini), height=0.6,
                color="#595959", edgecolor="black", linewidth=0.5)
ax.set_yticks(ys)
ax.set_yticklabels([f"{a[0]}  {a[2]}  [{a[3]}]" for a in ACTIVIDADES], fontsize=8)
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.set_xlim(mdates.date2num(INICIO) - 0.5, mdates.date2num(FIN) + 1.5)
ax.grid(axis="x", color="#BBBBBB", linewidth=0.5)
for f in (D(11, 11), D(11, 25), D(12, 2)):
    ax.axvline(mdates.date2num(f) + 0.5, color="#C00000", linewidth=0.8, linestyle="--")
ax.set_title("Cronograma del Trabajo Grupal — Sistema Cóndor (modelo incremental, 3 incrementos)", fontsize=11)
ax.set_xlabel("Semana (lunes)")
plt.tight_layout()
plt.savefig(AQUI / "cronograma.png", dpi=150)
print("cronograma.xlsx y cronograma.png generados")
