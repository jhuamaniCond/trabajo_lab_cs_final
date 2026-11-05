"""Genera estimacion_condor.xlsx: frontera y línea base, conteo NESMA (detallado,
estimado e indicativo), medición COSMIC, COCOMO II.2000, escenarios de 1 y 3
personas, sensibilidad ±20 %, horas reales y cuadro comparativo.

    python generar_libro.py

Todos los resultados son fórmulas de Excel: cambie un dato de entrada (celdas
amarillas) y el libro se recalcula. Los nombres definidos (Tarifa, LocPorPF...)
están en la hoja Parámetros.
"""
import json
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "estimacion_condor.xlsx"

FINO = Side(style="thin", color="808080")
BORDE = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
CAB = PatternFill("solid", fgColor="1F3864")
ENTRADA = PatternFill("solid", fgColor="FFF2CC")   # dato editable
RESULT = PatternFill("solid", fgColor="E2EFDA")    # resultado clave
TOTAL = PatternFill("solid", fgColor="D9D9D9")
PEND = Font(color="C00000", bold=True)

wb = Workbook()
wb.remove(wb.active)


def hoja(nombre, titulo, nota=None, anchos=()):
    ws = wb.create_sheet(nombre)
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=13)
    if nota:
        ws["A2"] = nota
        ws["A2"].font = Font(italic=True, color="555555")
    for i, w in enumerate(anchos, start=1):
        ws.column_dimensions[chr(64 + i)].width = w
    ws.sheet_view.showGridLines = False
    return ws


def cab(ws, fila, textos, col=1):
    for i, t in enumerate(textos):
        c = ws.cell(row=fila, column=col + i, value=t)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = CAB
        c.border = BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[fila].height = 48


def c(ws, fila, col, valor, fmt=None, fondo=None, negrita=False, envolver=False):
    x = ws.cell(row=fila, column=col, value=valor)
    x.border = BORDE
    if fmt:
        x.number_format = fmt
    if fondo:
        x.fill = fondo
    if negrita:
        x.font = Font(bold=True)
    x.alignment = Alignment(vertical="top", wrap_text=envolver)
    return x


def nombre(n, ref):
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


# =============================================================================
# 1. Parámetros
# =============================================================================
ws = hoja("Parámetros", "Parámetros de la estimación (celdas amarillas = datos editables)",
          "Unidades explícitas en cada fila. Cambie un valor y todo el libro se recalcula.", (42, 16, 12, 70))
cab(ws, 4, ["Parámetro", "Valor", "Unidad", "Fuente / justificación"])
PARAM = [
    ("Tarifa", "Tarifa por hora del equipo", 25, "S/ por hora",
     "Tarifa de referencia usada en los análisis de impacto de G02 (CC-01, CC-02); desarrollador junior en Arequipa, 2026."),
    ("HorasPM", "Horas por persona-mes (COCOMO II)", 152, "h / PM",
     "COCOMO II.2000 Model Definition Manual: 1 PM = 152 horas de trabajo."),
    ("HorasMesCompleto", "Dedicación a tiempo completo", 152, "h / mes / persona", "Igual a la hora-mes de COCOMO."),
    ("HorasSemanaParcial", "Dedicación parcial del equipo (estudiantes)", 20, "h / semana / persona",
     "Carga real disponible junto a los demás cursos del semestre."),
    ("SemanasMes", "Semanas por mes", 4.33, "semanas", "52 semanas / 12 meses."),
    ("HorasMesParcial", "Dedicación parcial mensual", "=HorasSemanaParcial*SemanasMes", "h / mes / persona", "Fórmula."),
    ("SobrecostoCanal", "Sobrecosto de coordinación por canal de comunicación", 0.05, "fracción del esfuerzo",
     "Supuesto: 5 % por canal; canales = n(n−1)/2 (Brooks). 3 personas → 3 canales → +15 %."),
    ("CompresionMax", "Duración mínima respecto de la nominal de COCOMO", 0.75, "fracción de TDEV",
     "COCOMO II: con SCED muy bajo el plazo no baja del 75 % de TDEV nominal."),
    ("LocPorPF", "Factor de conversión PF → SLOC para C#", 54, "SLOC / PF",
     "QSM Function Point Languages Table v5.0: C# promedio 54 (mediana 59, bajo 29, alto 70). Ver hoja Sensibilidad."),
    ("A_coc", "COCOMO II.2000 constante A", 2.94, "—", "Model Definition Manual (calibración 2000, 161 proyectos)."),
    ("B_coc", "COCOMO II.2000 constante B", 0.91, "—", "Ídem."),
    ("C_coc", "COCOMO II.2000 constante C", 3.67, "—", "Ídem."),
    ("D_coc", "COCOMO II.2000 constante D", 0.28, "—", "Ídem."),
]
for i, (n, desc, val, uni, fuente) in enumerate(PARAM, start=5):
    c(ws, i, 1, desc)
    x = c(ws, i, 2, val, fondo=None if str(val).startswith("=") else ENTRADA)
    if isinstance(val, float) and val < 1:
        x.number_format = "0%"
    c(ws, i, 3, uni)
    c(ws, i, 4, fuente, envolver=True)
    nombre(n, f"'Parámetros'!$B${i}")

# Tamaño real del producto (SLOC lógicas contadas en la versión 1.1.0)
f0 = 5 + len(PARAM) + 2
ws.cell(row=f0, column=1, value="Tamaño real del producto 1.1.0 (líneas lógicas: sin blancos ni comentarios)").font = Font(bold=True)
cab(ws, f0 + 1, ["Proyecto / lenguaje", "SLOC", "¿Entra en COCOMO?", "Observación"])
REAL = [
    ("Condor.Dominio (C#)", 1742, "Sí", "Lógica de negocio"),
    ("Condor.Presentacion (C#)", 4072, "Sí", "ViewModels"),
    ("Condor.Datos (C#)", 2136, "Sí", "Repositorios SQL"),
    ("Condor.Sunat (C#)", 1222, "Sí", "XML UBL, firma, SOAP"),
    ("Condor.Escritorio (C#)", 989, "Sí", "Code-behind WPF"),
    ("Condor.Api (C#)", 624, "Sí", "Backend REST"),
    ("Condor.ClienteApi (C#)", 429, "Sí", "Cliente HTTP"),
    ("Condor.Impresion (C#)", 295, "Sí", "ESC/POS"),
    ("Migraciones V001–V014 (SQL)", 320, "Sí", "Esquema y reglas en la base"),
    ("Vistas XAML (marcado)", 2844, "No", "Marcado declarativo de la interfaz; se excluye del SLOC (regla de COCOMO: código entregado escrito a mano)"),
    ("Pruebas (C#)", 12603, "No", "Código de pruebas, no entregable funcional"),
]
for j, (p, n, entra, obs) in enumerate(REAL, start=f0 + 2):
    c(ws, j, 1, p)
    c(ws, j, 2, n, fmt="#,##0", fondo=ENTRADA)
    c(ws, j, 3, entra, fondo=ENTRADA)
    c(ws, j, 4, obs, envolver=True)
fin = f0 + 1 + len(REAL)
c(ws, fin + 1, 1, "KSLOC real que entra en COCOMO", negrita=True, fondo=TOTAL)
c(ws, fin + 1, 2, f'=SUMIF(C{f0 + 2}:C{fin},"Sí",B{f0 + 2}:B{fin})/1000', fmt="0.000", fondo=RESULT, negrita=True)
c(ws, fin + 1, 3, "KSLOC", fondo=TOTAL)
c(ws, fin + 1, 4, "Conteo con el script de 01_Libro/contar_sloc.py sobre Sistema_Logistico_Condor_final (versión 1.1.0).",
  envolver=True)
nombre("KslocReal", f"'Parámetros'!$B${fin + 1}")

# =============================================================================
# 2. Frontera y línea base
# =============================================================================
ws = hoja("Frontera", "Frontera del sistema y línea base de requisitos medida",
          "Línea base: ERS 1.1 (2026-10-30), producto 1.1.0. Propósito del conteo: estimar el desarrollo completo del producto.",
          (16, 46, 16, 60))
FRONT = [
    ("Dentro", "Aplicación WPF CondorVentas.exe, backend Condor.Api y base PostgreSQL de Cóndor (los tres se miden como una sola aplicación)."),
    ("Fuera", "SUNAT (servicio sendBill/getStatusCdr y API de guías), ticketera, lector de código de barras (emula teclado), sistema operativo, pg_dump."),
    ("Usuarios", "Vendedor y Encargado general (y la SUNAT como usuario funcional que envía el CDR)."),
    ("Tipo de conteo", "NESMA detallado (equivalente a IFPUG 4.3 en la identificación y la complejidad), más NESMA estimado e indicativo como comparación."),
    ("Ajuste", "Se informan puntos de función SIN ajustar (NESMA 2.x recomienda no aplicar el factor de ajuste; el entorno se modela en COCOMO)."),
]
cab(ws, 4, ["Aspecto", "Definición"])
for i, (a, b) in enumerate(FRONT, start=5):
    c(ws, i, 1, a, negrita=True)
    ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=4)
    c(ws, i, 2, b, envolver=True)
    ws.row_dimensions[i].height = 32
LB = [
    ("RF-01", "Iniciar sesión", "T01"), ("RF-02", "Cerrar sesión", "No se cuenta: no cruza datos ni mantiene archivos"),
    ("RF-03", "Restringir módulos según el rol", "No se cuenta: control dentro de cada función"),
    ("RF-04", "Registrar producto en el catálogo", "T02–T05"), ("RF-05", "Buscar producto para la venta", "T06, T07"),
    ("RF-06", "Registrar y buscar cliente", "T08, T09"), ("RF-07", "Emitir comprobante de venta", "T10, T34"),
    ("RF-08", "Emitir proforma y convertirla", "T12–T14"), ("RF-09", "Imprimir y reimprimir el ticket", "T11"),
    ("RF-10", "Enviar a la SUNAT y reenviar pendientes", "T15–T17"), ("RF-11", "Registrar proveedor", "T18, T19"),
    ("RF-12", "Registrar compra a proveedor", "T20–T22"), ("RF-13", "Emitir guía de remisión", "T23–T27"),
    ("RF-14", "Consultar historial de ventas", "T28, T29"), ("RF-15", "Reporte consolidado de ventas", "T30"),
    ("RF-16", "Generar respaldo", "T31–T33"),
    ("RNF-01 a RNF-08", "Requisitos no funcionales", "No suman PF: se reflejan en los factores de COCOMO (RELY, CPLX, TIME...)"),
]
r0 = 5 + len(FRONT) + 1
cab(ws, r0, ["Requisito", "Nombre", "Funciones NESMA", "Observación"])
for i, (a, b, d) in enumerate(LB, start=r0 + 1):
    c(ws, i, 1, a)
    c(ws, i, 2, b)
    c(ws, i, 3, d if d.startswith("T") else "—")
    c(ws, i, 4, "" if d.startswith("T") else d, envolver=True)

# =============================================================================
# 3. Pesos NESMA
# =============================================================================
ws = hoja("Pesos NESMA", "Pesos y matrices de complejidad (NESMA = IFPUG 4.3)", None, (10, 10, 10, 10, 4, 52))
cab(ws, 3, ["Tipo", "Baja", "Media", "Alta"])
PESOS = {"ALI": (7, 10, 15), "AIE": (5, 7, 10), "EI": (3, 4, 6), "EO": (4, 5, 7), "EQ": (3, 4, 6)}
for i, (t, p) in enumerate(PESOS.items(), start=4):
    c(ws, i, 1, t, negrita=True)
    for j, v in enumerate(p, start=2):
        c(ws, i, j, v)
MATRIZ = [
    "ALI/AIE: RET 1 → DET ≤ 50 Baja, > 50 Media | RET 2–5 → ≤ 19 Baja, 20–50 Media, > 50 Alta | RET ≥ 6 → ≤ 19 Media, > 19 Alta",
    "EI: FTR ≤ 1 → DET ≤ 15 Baja, > 15 Media | FTR 2 → ≤ 4 Baja, 5–15 Media, > 15 Alta | FTR ≥ 3 → ≤ 4 Media, > 4 Alta",
    "EO/EQ: FTR ≤ 1 → DET ≤ 19 Baja, > 19 Media | FTR 2–3 → ≤ 5 Baja, 6–19 Media, > 19 Alta | FTR ≥ 4 → ≤ 5 Media, > 5 Alta",
    "NESMA indicativo: PF = 35 × ALI + 15 × AIE.  NESMA estimado: ALI y AIE Baja; EI, EO y EQ Media.",
]
for i, t in enumerate(MATRIZ, start=10):
    ws.cell(row=i, column=1, value=t)
nombre("TablaPesos", "'Pesos NESMA'!$B$4:$D$8")
nombre("TiposPesos", "'Pesos NESMA'!$A$4:$A$8")
nombre("NivelesPesos", "'Pesos NESMA'!$B$3:$D$3")

# =============================================================================
# 4. NESMA detallado
# =============================================================================
ws = hoja("NESMA detallado", "Conteo NESMA detallado — Sistema Cóndor 1.1.0 (línea base ERS 1.1)",
          "DET = datos elementales reconocibles por el usuario; RET = subgrupos de registro; FTR = archivos referenciados. Complejidad y PF son fórmulas.",
          (6, 44, 7, 7, 8, 13, 7, 16, 62))
DATOS = [
    ("D01", "Producto", "ALI", 6, 1, "RF-04, RF-05", "Nombre, precio, unidad, código de barras, activo, fecha de registro."),
    ("D02", "Cliente", "ALI", 4, 1, "RF-06", "Tipo y número de documento, nombre, dirección."),
    ("D03", "Comprobante", "ALI", 28, 3, "RF-07 a RF-10, RF-14", "RET: cabecera (14 DET), detalle (7) y envío SUNAT (7). Boleta, factura, nota de venta y proforma son el mismo archivo lógico."),
    ("D04", "Serie y correlativos", "ALI", 3, 1, "RF-07, RF-13", "Código, tipo, último correlativo; la aplicación lo actualiza en cada emisión."),
    ("D05", "Proveedor", "ALI", 8, 1, "RF-11", "RUC, razón social, nombre comercial, dirección, teléfono, correo, contacto, activo."),
    ("D06", "Compra", "ALI", 18, 2, "RF-12", "RET: cabecera y detalle."),
    ("D07", "Guía de remisión", "ALI", 33, 2, "RF-13", "RET: cabecera (destinatario, traslado, transporte, SUNAT) y detalle."),
    ("D08", "Usuario y bitácora de accesos", "ALI", 12, 2, "RF-01, RF-03", "RET: cuenta (8 DET) y acceso (4 DET)."),
    ("D09", "Terminal", "ALI", 3, 1, "RF-07", "Nombre del equipo, registro, último acceso."),
    ("D10", "Respaldo", "ALI", 6, 1, "RF-16", "Archivo, carpeta, bytes, inicio, fin, terminal."),
]
TRANS = [
    ("T01", "Iniciar sesión (actualiza intentos y bitácora)", "EI", 5, 2, "RF-01"),
    ("T02", "Registrar producto", "EI", 6, 1, "RF-04"),
    ("T03", "Asignar código de barras a un producto", "EI", 3, 1, "RF-04"),
    ("T04", "Importar lista de precios (CSV)", "EI", 5, 1, "RF-04 (SUP-04)"),
    ("T05", "Consultar catálogo", "EQ", 6, 1, "RF-04"),
    ("T06", "Buscar producto por nombre", "EQ", 5, 1, "RF-05"),
    ("T07", "Buscar producto por código de barras", "EQ", 5, 1, "RF-05"),
    ("T08", "Registrar cliente", "EI", 5, 1, "RF-06"),
    ("T09", "Buscar cliente por DNI o RUC", "EQ", 5, 1, "RF-06"),
    ("T10", "Emitir comprobante (boleta, factura, nota de venta)", "EI", 16, 5, "RF-07"),
    ("T11", "Imprimir / reimprimir ticket (monto en letras, IGV)", "EO", 22, 4, "RF-09"),
    ("T12", "Emitir proforma (vigencia calculada)", "EI", 13, 4, "RF-08"),
    ("T13", "Listar proformas con estado derivado", "EO", 7, 2, "RF-08"),
    ("T14", "Convertir proforma en venta", "EI", 6, 3, "RF-08"),
    ("T15", "Enviar comprobante a la SUNAT (XML UBL firmado)", "EO", 25, 4, "RF-10"),
    ("T16", "Registrar respuesta de la SUNAT (CDR)", "EI", 5, 1, "RF-10"),
    ("T17", "Resumen de pendientes y aviso de plazo", "EO", 3, 1, "RF-10"),
    ("T18", "Registrar proveedor", "EI", 8, 1, "RF-11"),
    ("T19", "Consultar proveedores", "EQ", 8, 1, "RF-11"),
    ("T20", "Registrar compra", "EI", 14, 4, "RF-12"),
    ("T21", "Consultar compras con totales", "EO", 9, 2, "RF-12"),
    ("T22", "Ver detalle de compra", "EQ", 12, 3, "RF-12"),
    ("T23", "Emitir guía de remisión", "EI", 30, 4, "RF-13"),
    ("T24", "Enviar guía a la SUNAT", "EO", 28, 3, "RF-13"),
    ("T25", "Registrar respuesta de la guía", "EI", 5, 1, "RF-13"),
    ("T26", "Imprimir guía", "EO", 28, 3, "RF-13"),
    ("T27", "Consultar guías", "EQ", 8, 1, "RF-13"),
    ("T28", "Consultar historial de ventas con total", "EO", 9, 2, "RF-14"),
    ("T29", "Ver detalle de comprobante", "EQ", 15, 3, "RF-14"),
    ("T30", "Reporte consolidado de ventas", "EO", 8, 2, "RF-15"),
    ("T31", "Generar respaldo", "EI", 4, 2, "RF-16"),
    ("T32", "Aviso de respaldo vencido (> 24 h)", "EO", 3, 1, "RF-16"),
    ("T33", "Consultar respaldos", "EQ", 6, 1, "RF-16"),
    ("T34", "Registrar terminal", "EI", 2, 1, "RF-07 (CRQ-11)"),
]
tipos_dv = DataValidation(type="list", formula1='"ALI,AIE,EI,EO,EQ"', allow_blank=False)
ws.add_data_validation(tipos_dv)

ws["A4"] = "Funciones de datos"
ws["A4"].font = Font(bold=True)
cab(ws, 5, ["ID", "Archivo lógico", "Tipo", "DET", "RET", "Complejidad", "PF", "Requisitos", "Hipótesis / detalle"])
r = 6
for fid, nom, t, det, ret, rf, hip in DATOS:
    c(ws, r, 1, fid); c(ws, r, 2, nom)
    c(ws, r, 3, t, fondo=ENTRADA); tipos_dv.add(f"C{r}")
    c(ws, r, 4, det, fondo=ENTRADA); c(ws, r, 5, ret, fondo=ENTRADA)
    c(ws, r, 6, f'=IF(E{r}=1,IF(D{r}<=50,"Baja","Media"),IF(E{r}<=5,IF(D{r}<=19,"Baja",IF(D{r}<=50,"Media","Alta")),IF(D{r}<=19,"Media","Alta")))')
    c(ws, r, 7, f"=INDEX(TablaPesos,MATCH(C{r},TiposPesos,0),MATCH(F{r},NivelesPesos,0))")
    c(ws, r, 8, rf); c(ws, r, 9, hip, envolver=True)
    r += 1
d_ini, d_fin = 6, r - 1
c(ws, r, 6, "Subtotal", negrita=True, fondo=TOTAL)
c(ws, r, 7, f"=SUM(G{d_ini}:G{d_fin})", negrita=True, fondo=TOTAL)
fila_sub_datos = r
r += 2
ws.cell(row=r, column=1, value="Funciones transaccionales").font = Font(bold=True)
r += 1
cab(ws, r, ["ID", "Función", "Tipo", "DET", "FTR", "Complejidad", "PF", "Requisitos", "Observación"])
r += 1
t_ini = r
for fid, nom, t, det, ftr, rf in TRANS:
    c(ws, r, 1, fid); c(ws, r, 2, nom)
    c(ws, r, 3, t, fondo=ENTRADA); tipos_dv.add(f"C{r}")
    c(ws, r, 4, det, fondo=ENTRADA); c(ws, r, 5, ftr, fondo=ENTRADA)
    c(ws, r, 6, f'=IF(C{r}="EI",IF(E{r}<=1,IF(D{r}<=15,"Baja","Media"),IF(E{r}=2,IF(D{r}<=4,"Baja",IF(D{r}<=15,"Media","Alta")),IF(D{r}<=4,"Media","Alta"))),'
                f'IF(E{r}<=1,IF(D{r}<=19,"Baja","Media"),IF(E{r}<=3,IF(D{r}<=5,"Baja",IF(D{r}<=19,"Media","Alta")),IF(D{r}<=5,"Media","Alta"))))')
    c(ws, r, 7, f"=INDEX(TablaPesos,MATCH(C{r},TiposPesos,0),MATCH(F{r},NivelesPesos,0))")
    c(ws, r, 8, rf); c(ws, r, 9, "")
    r += 1
t_fin = r - 1
c(ws, r, 6, "Subtotal", negrita=True, fondo=TOTAL)
c(ws, r, 7, f"=SUM(G{t_ini}:G{t_fin})", negrita=True, fondo=TOTAL)
fila_sub_trans = r
r += 2
c(ws, r, 6, "PF sin ajustar", negrita=True, fondo=RESULT)
c(ws, r, 7, f"=G{fila_sub_datos}+G{fila_sub_trans}", negrita=True, fondo=RESULT)
c(ws, r, 8, "PF NESMA", negrita=True, fondo=RESULT)
nombre("PF_Detallado", f"'NESMA detallado'!$G${r}")
r += 2
ws.cell(row=r, column=1, value="Resumen por tipo y complejidad").font = Font(bold=True)
r += 1
cab(ws, r, ["", "Tipo", "Baja", "Media", "Alta", "Cantidad", "PF"])
r += 1
for t in PESOS:
    c(ws, r, 2, t, negrita=True)
    for j, niv in enumerate(["Baja", "Media", "Alta"], start=3):
        c(ws, r, j, f'=COUNTIFS($C${d_ini}:$C${t_fin},$B{r},$F${d_ini}:$F${t_fin},"{niv}")')
    c(ws, r, 6, f"=SUM(C{r}:E{r})")
    c(ws, r, 7, f'=SUMIF($C${d_ini}:$C${t_fin},$B{r},$G${d_ini}:$G${t_fin})')
    r += 1
r += 1
EXCL = [
    "No se cuentan: RF-02 Cerrar sesión (no cruza datos de negocio), RF-03 Restricción por rol (control dentro de cada función),",
    "el reenvío automático de pendientes (reutiliza la lógica de T15), menús y navegación, ni la configuración Empresa",
    "(datos de cabecera cargados por migración, sin función que los mantenga). No hay AIE: la aplicación no lee archivos",
    "mantenidos por otro sistema (la SUNAT se comunica por transacciones, no por un archivo lógico consultado).",
]
for t in EXCL:
    ws.cell(row=r, column=1, value=t).font = Font(italic=True)
    r += 1
ws.freeze_panes = "A6"

# =============================================================================
# 5. NESMA estimado e indicativo
# =============================================================================
ws = hoja("NESMA rápido", "NESMA estimado e indicativo (mismo alcance)",
          "Se calculan a partir de las funciones identificadas en el conteo detallado.", (40, 14, 14, 14, 50))
cab(ws, 4, ["Tipo", "Cantidad", "Peso", "PF", "Regla"])
ND = "'NESMA detallado'"
RAP = [("ALI", 7, "Estimado: ALI siempre Baja"), ("AIE", 5, "Estimado: AIE siempre Baja"),
       ("EI", 4, "Estimado: EI siempre Media"), ("EO", 5, "Estimado: EO siempre Media"),
       ("EQ", 4, "Estimado: EQ siempre Media")]
for i, (t, p, regla) in enumerate(RAP, start=5):
    c(ws, i, 1, t, negrita=True)
    c(ws, i, 2, f"=COUNTIF({ND}!$C$6:$C${t_fin},A{i})")
    c(ws, i, 3, p)
    c(ws, i, 4, f"=B{i}*C{i}")
    c(ws, i, 5, regla)
c(ws, 10, 1, "PF NESMA estimado", negrita=True, fondo=RESULT)
c(ws, 10, 4, "=SUM(D5:D9)", negrita=True, fondo=RESULT)
nombre("PF_Estimado", "'NESMA rápido'!$D$10")
c(ws, 12, 1, "PF NESMA indicativo = 35 × ALI + 15 × AIE", negrita=True, fondo=RESULT)
c(ws, 12, 4, "=35*B5+15*B6", negrita=True, fondo=RESULT)
nombre("PF_Indicativo", "'NESMA rápido'!$D$12")
c(ws, 14, 1, "Desviación del estimado respecto del detallado")
c(ws, 14, 4, "=PF_Estimado/PF_Detallado-1", fmt="0.0%")
c(ws, 15, 1, "Desviación del indicativo respecto del detallado")
c(ws, 15, 4, "=PF_Indicativo/PF_Detallado-1", fmt="0.0%")

# =============================================================================
# 6. COSMIC
# =============================================================================
ws = hoja("COSMIC", "Medición COSMIC (ISO/IEC 19761) — mismo alcance, unidades CFP",
          "E = entrada, X = salida, R = lectura, W = escritura. 1 movimiento de datos = 1 CFP. Los CFP NO se convierten a PF.",
          (6, 50, 22, 6, 6, 6, 6, 8, 14))
COSMIC = [
    ("P01", "Iniciar sesión", "Vendedor / Encargado", 1, 2, 1, 2, "RF-01"),
    ("P02", "Cerrar sesión", "Usuario", 1, 1, 0, 0, "RF-02"),
    ("P03", "Registrar producto", "Usuario", 1, 1, 1, 1, "RF-04"),
    ("P04", "Asignar código de barras", "Usuario", 1, 1, 1, 1, "RF-04"),
    ("P05", "Importar lista de precios", "Encargado", 1, 1, 1, 1, "RF-04"),
    ("P06", "Consultar catálogo", "Usuario", 1, 1, 1, 0, "RF-04"),
    ("P07", "Buscar producto por nombre", "Vendedor", 1, 2, 1, 0, "RF-05"),
    ("P08", "Buscar producto por código", "Vendedor (lector)", 1, 2, 1, 0, "RF-05"),
    ("P09", "Registrar cliente", "Vendedor", 1, 1, 1, 1, "RF-06"),
    ("P10", "Buscar cliente por documento", "Vendedor", 1, 2, 1, 0, "RF-06"),
    ("P11", "Emitir comprobante", "Vendedor", 2, 2, 3, 3, "RF-07"),
    ("P12", "Imprimir ticket", "Vendedor", 1, 1, 4, 1, "RF-09"),
    ("P13", "Reimprimir ticket", "Vendedor", 1, 2, 3, 1, "RF-09"),
    ("P14", "Emitir proforma", "Vendedor", 2, 2, 3, 3, "RF-08"),
    ("P15", "Listar proformas", "Vendedor", 1, 1, 2, 0, "RF-08"),
    ("P16", "Convertir proforma en venta", "Vendedor", 1, 2, 2, 0, "RF-08"),
    ("P17", "Enviar comprobante a la SUNAT", "Sistema (al emitir)", 2, 2, 4, 1, "RF-10"),
    ("P18", "Reenviar pendientes", "Reloj (cada ReenvioMinutos)", 2, 1, 1, 2, "RF-10"),
    ("P19", "Resumen de pendientes", "Reloj / pantalla", 1, 1, 1, 0, "RF-10"),
    ("P20", "Registrar proveedor", "Encargado", 1, 1, 1, 1, "RF-11"),
    ("P21", "Consultar proveedores", "Encargado", 1, 1, 1, 0, "RF-11"),
    ("P22", "Registrar compra", "Encargado", 2, 2, 3, 2, "RF-12"),
    ("P23", "Consultar compras", "Encargado", 1, 1, 2, 0, "RF-12"),
    ("P24", "Ver detalle de compra", "Encargado", 1, 1, 2, 0, "RF-12"),
    ("P25", "Emitir guía de remisión", "Encargado", 2, 2, 3, 3, "RF-13"),
    ("P26", "Enviar guía a la SUNAT", "Sistema", 2, 2, 3, 1, "RF-13"),
    ("P27", "Imprimir guía", "Encargado", 1, 1, 3, 1, "RF-13"),
    ("P28", "Consultar guías", "Encargado", 1, 1, 1, 0, "RF-13"),
    ("P29", "Consultar historial de ventas", "Usuario", 1, 2, 2, 0, "RF-14"),
    ("P30", "Ver detalle de comprobante", "Usuario", 1, 1, 3, 0, "RF-14"),
    ("P31", "Reporte consolidado de ventas", "Encargado (API)", 1, 5, 1, 0, "RF-15"),
    ("P32", "Generar respaldo", "Encargado", 1, 2, 1, 1, "RF-16"),
    ("P33", "Aviso de respaldo vencido", "Sistema (al abrir)", 1, 1, 1, 0, "RF-16"),
    ("P34", "Consultar respaldos", "Encargado", 1, 1, 1, 0, "RF-16"),
    ("P35", "Registrar terminal", "Sistema (al iniciar)", 1, 1, 1, 1, "RF-07"),
]
cab(ws, 4, ["ID", "Proceso funcional", "Usuario funcional / disparador", "E", "X", "R", "W", "CFP", "Requisito"])
r = 5
for pid, nom, usr, e, x, rr, w, rf in COSMIC:
    c(ws, r, 1, pid); c(ws, r, 2, nom); c(ws, r, 3, usr)
    for j, v in enumerate([e, x, rr, w], start=4):
        c(ws, r, j, v, fondo=ENTRADA)
    c(ws, r, 8, f"=SUM(D{r}:G{r})", negrita=True)
    c(ws, r, 9, rf)
    r += 1
c(ws, r, 3, "Total", negrita=True, fondo=TOTAL)
for j, col in enumerate("DEFGH", start=4):
    c(ws, r, j, f"=SUM({col}5:{col}{r - 1})", negrita=True, fondo=RESULT if col == "H" else TOTAL)
nombre("CFP_Total", f"COSMIC!$H${r}")
r += 2
for t in [
    "Grupos de datos (objetos de interés): Producto, Cliente, Comprobante, Detalle, Serie, Envío SUNAT, Proveedor, Compra, Guía, Usuario, Bitácora, Terminal, Respaldo, Empresa, Mensajes.",
    "Regla aplicada: cada proceso cuenta 1 X de mensajes de error o confirmación cuando los emite (COSMIC Measurement Manual 5.0, 3.5.11).",
    "El reporte consolidado cuenta 5 X: un grupo por día, por tipo, por terminal, por usuario y el mensaje de período inválido.",
    "La SUNAT es un usuario funcional: el XML enviado es una X y el CDR recibido una E en los procesos P17, P18 y P26.",
]:
    ws.cell(row=r, column=1, value=t).font = Font(italic=True)
    r += 1

# =============================================================================
# 7. COCOMO II
# =============================================================================
ws = hoja("COCOMO II", "COCOMO II.2000, modelo post-arquitectura",
          "PM = A × KSLOC^E × ΠEM ;  E = B + 0.01 × ΣSF ;  TDEV = C × PM^F ;  F = D + 0.2 × (E − B)",
          (34, 26, 26, 64))
SF = [  # nombre, nivel elegido, valores VL..XH, justificación
    ("PREC  Precedentes", "N", [6.20, 4.96, 3.72, 2.48, 1.24, 0.00], "Sistema de ventas conocido, pero primera facturación electrónica del equipo."),
    ("FLEX  Flexibilidad de desarrollo", "H", [5.07, 4.05, 3.04, 2.03, 1.01, 0.00], "Requisitos negociables con el cliente; la norma SUNAT es rígida."),
    ("RESL  Arquitectura / resolución de riesgos", "N", [7.07, 5.65, 4.24, 2.83, 1.41, 0.00], "Riesgos identificados (G06) pero resueltos solo en parte al iniciar."),
    ("TEAM  Cohesión del equipo", "H", [5.48, 4.38, 3.29, 2.19, 1.10, 0.00], "Cuatro compañeros que ya trabajaron juntos."),
    ("PMAT  Madurez del proceso", "N", [7.80, 6.24, 4.68, 3.12, 1.56, 0.00], "Proceso definido por las guías (requisitos, cambios, SVN, pruebas): equivalente a CMM 2."),
]
EM = [
    ("RELY  Fiabilidad requerida", "H", {"VL": .82, "L": .92, "N": 1.00, "H": 1.10, "VH": 1.26}, "Un error de IGV o de numeración tiene consecuencias tributarias."),
    ("DATA  Tamaño de la base de datos", "N", {"L": .90, "N": 1.00, "H": 1.14, "VH": 1.28}, "≈ 100 000 filas al año frente a 12 KSLOC: relación D/P entre 10 y 100."),
    ("CPLX  Complejidad del producto", "H", {"VL": .73, "L": .87, "N": 1.00, "H": 1.17, "VH": 1.34, "XH": 1.74}, "Concurrencia de 3 PC, firma XML, SOAP, transacciones."),
    ("RUSE  Reutilización requerida", "N", {"L": .95, "N": 1.00, "H": 1.07, "VH": 1.15, "XH": 1.24}, "Dominio reutilizado por la app y la API dentro del mismo producto."),
    ("DOCU  Documentación", "N", {"VL": .81, "L": .91, "N": 1.00, "H": 1.11, "VH": 1.23}, "Documentación acorde con el ciclo de vida."),
    ("TIME  Restricción de tiempo de ejecución", "N", {"N": 1.00, "H": 1.11, "VH": 1.29, "XH": 1.63}, "Uso de CPU bajo."),
    ("STOR  Restricción de almacenamiento", "N", {"N": 1.00, "H": 1.05, "VH": 1.17, "XH": 1.46}, "Sin restricción."),
    ("PVOL  Volatilidad de la plataforma", "L", {"L": .87, "N": 1.00, "H": 1.15, "VH": 1.30}, ".NET 8 LTS y PostgreSQL 16 estables."),
    ("ACAP  Capacidad de los analistas", "N", {"VL": 1.42, "L": 1.19, "N": 1.00, "H": .85, "VH": .71}, "Estudiantes de 8.º semestre."),
    ("PCAP  Capacidad de los programadores", "N", {"VL": 1.34, "L": 1.15, "N": 1.00, "H": .88, "VH": .76}, "Ídem."),
    ("PCON  Continuidad del personal", "N", {"VL": 1.29, "L": 1.12, "N": 1.00, "H": .90, "VH": .81}, "Mismo equipo todo el semestre."),
    ("APEX  Experiencia en aplicaciones", "L", {"VL": 1.22, "L": 1.10, "N": 1.00, "H": .88, "VH": .81}, "Poca experiencia en facturación electrónica."),
    ("PLEX  Experiencia en la plataforma", "N", {"VL": 1.19, "L": 1.09, "N": 1.00, "H": .91, "VH": .85}, "Un año con .NET y PostgreSQL."),
    ("LTEX  Experiencia en lenguaje y herramientas", "N", {"VL": 1.20, "L": 1.09, "N": 1.00, "H": .91, "VH": .84}, "C# del curso de programación."),
    ("TOOL  Uso de herramientas", "H", {"VL": 1.17, "L": 1.09, "N": 1.00, "H": .90, "VH": .78}, "IDE moderno, pruebas automatizadas, Docker."),
    ("SITE  Desarrollo multisitio", "H", {"VL": 1.22, "L": 1.09, "N": 1.00, "H": .93, "VH": .86, "XH": .80}, "Misma ciudad, comunicación diaria por chat y reuniones."),
    ("SCED  Compresión del calendario", "N", {"VL": 1.43, "L": 1.14, "N": 1.00, "H": 1.00, "VH": 1.00}, "Plazo nominal (se analiza aparte en Escenarios)."),
]
NIV = ["VL", "L", "N", "H", "VH", "XH"]
nivel_dv = DataValidation(type="list", formula1='"VL,L,N,H,VH,XH"')
ws.add_data_validation(nivel_dv)
cab(ws, 4, ["Factor de escala", "Nivel", "Valor", "Justificación"] + NIV, col=1)
r = 5
for n, niv, vals, just in SF:
    c(ws, r, 1, n); c(ws, r, 2, niv, fondo=ENTRADA); nivel_dv.add(f"B{r}")
    for j, v in enumerate(vals, start=5):
        c(ws, r, j, v, fmt="0.00")
    c(ws, r, 3, f"=INDEX(E{r}:J{r},MATCH(B{r},$E$4:$J$4,0))", fmt="0.00")
    c(ws, r, 4, just, envolver=True)
    r += 1
c(ws, r, 1, "ΣSF", negrita=True, fondo=TOTAL); c(ws, r, 3, f"=SUM(C5:C{r - 1})", fmt="0.00", negrita=True, fondo=TOTAL)
nombre("SumaSF", f"'COCOMO II'!$C${r}")
r += 2
cab(ws, r, ["Multiplicador de esfuerzo", "Nivel", "Valor", "Justificación"] + NIV, col=1)
r += 1
em_ini = r
for n, niv, vals, just in EM:
    c(ws, r, 1, n); c(ws, r, 2, niv, fondo=ENTRADA); nivel_dv.add(f"B{r}")
    for j, k in enumerate(NIV, start=5):
        c(ws, r, j, vals.get(k, "—"), fmt="0.00")
    c(ws, r, 3, f"=INDEX(E{r}:J{r},MATCH(B{r},$E${em_ini - 1}:$J${em_ini - 1},0))", fmt="0.00")
    c(ws, r, 4, just, envolver=True)
    r += 1
c(ws, r, 1, "EAF = ΠEM", negrita=True, fondo=TOTAL); c(ws, r, 3, f"=PRODUCT(C{em_ini}:C{r - 1})", fmt="0.000", negrita=True, fondo=TOTAL)
nombre("EAF", f"'COCOMO II'!$C${r}")
r += 2
ws.cell(row=r, column=1, value="Resultados").font = Font(bold=True, size=12)
r += 1
cab(ws, r, ["Magnitud", "A) Tamaño desde NESMA", "B) Tamaño real 1.1.0", "Unidad / fórmula"])
r += 1
filas_res = {}
RES = [
    ("Tamaño funcional (entrada)", "=PF_Detallado", "—", "PF NESMA (no es esfuerzo ni código)"),
    ("Factor SLOC/PF", "=LocPorPF", "=KslocReal*1000/PF_Detallado", "SLOC/PF (B = factor real del producto)"),
    ("Tamaño en KSLOC", "=PF_Detallado*LocPorPF/1000", "=KslocReal", "KSLOC"),
    ("Exponente E", "=B_coc+0.01*SumaSF", "=B_coc+0.01*SumaSF", "E = B + 0.01·ΣSF"),
    ("Esfuerzo nominal", None, None, "PM = A·KSLOC^E·EAF"),
    ("Esfuerzo en horas", None, None, "h = PM × 152"),
    ("Exponente F", "=D_coc+0.2*(B{e}-B_coc)", "=D_coc+0.2*(C{e}-B_coc)", "F = D + 0.2·(E − B)"),
    ("Duración nominal TDEV", None, None, "meses = C·PM^F"),
    ("Personal promedio", None, None, "personas a tiempo completo = PM / TDEV"),
    ("Costo del esfuerzo nominal", None, None, "S/ = horas × Tarifa"),
]
for nombre_fila, fa, fb, uni in RES:
    filas_res[nombre_fila] = r
    c(ws, r, 1, nombre_fila, negrita=True)
    c(ws, r, 4, uni)
    r += 1
F = filas_res
k, e, pm, h, f_, td = F["Tamaño en KSLOC"], F["Exponente E"], F["Esfuerzo nominal"], F["Esfuerzo en horas"], F["Exponente F"], F["Duración nominal TDEV"]
for col in "BC":
    ws[f"{col}{F['Tamaño funcional (entrada)']}"] = "=PF_Detallado" if col == "B" else "=PF_Detallado"
    ws[f"{col}{F['Factor SLOC/PF']}"] = "=LocPorPF" if col == "B" else "=KslocReal*1000/PF_Detallado"
    ws[f"{col}{k}"] = "=PF_Detallado*LocPorPF/1000" if col == "B" else "=KslocReal"
    ws[f"{col}{e}"] = "=B_coc+0.01*SumaSF"
    ws[f"{col}{pm}"] = f"=A_coc*{col}{k}^{col}{e}*EAF"
    ws[f"{col}{h}"] = f"={col}{pm}*HorasPM"
    ws[f"{col}{f_}"] = f"=D_coc+0.2*({col}{e}-B_coc)"
    ws[f"{col}{td}"] = f"=C_coc*{col}{pm}^{col}{f_}"
    ws[f"{col}{F['Personal promedio']}"] = f"={col}{pm}/{col}{td}"
    ws[f"{col}{F['Costo del esfuerzo nominal']}"] = f"={col}{h}*Tarifa"
FMT = {F["Tamaño funcional (entrada)"]: "0", F["Factor SLOC/PF"]: "0.0", k: "0.00", e: "0.0000", pm: "0.0",
       h: "#,##0", f_: "0.0000", td: "0.0", F["Personal promedio"]: "0.0", F["Costo del esfuerzo nominal"]: '"S/" #,##0'}
for fila, fmt in FMT.items():
    for col in "BC":
        x = ws[f"{col}{fila}"]
        x.number_format = fmt
        x.border = BORDE
        if fila in (pm, td, F["Costo del esfuerzo nominal"]):
            x.fill = RESULT
            x.font = Font(bold=True)
nombre("KSLOC_Nesma", f"'COCOMO II'!$B${k}")
nombre("E_coc", f"'COCOMO II'!$B${e}")
nombre("PM_Nesma", f"'COCOMO II'!$B${pm}")
nombre("TDEV_Nesma", f"'COCOMO II'!$B${td}")
nombre("PM_Real", f"'COCOMO II'!$C${pm}")
nombre("TDEV_Real", f"'COCOMO II'!$C${td}")
r += 1
ws.cell(row=r, column=1, value="Comparación: COCOMO 81 básico, modo orgánico (PM = 2.4·KLOC^1.05 ; TDEV = 2.5·PM^0.38)").font = Font(bold=True)
r += 1
c(ws, r, 1, "Esfuerzo COCOMO 81 (PM)"); c(ws, r, 2, f"=2.4*B{k}^1.05", fmt="0.0"); c(ws, r, 3, f"=2.4*C{k}^1.05", fmt="0.0")
nombre("PM_81", f"'COCOMO II'!$B${r}")
r += 1
c(ws, r, 1, "Duración COCOMO 81 (meses)"); c(ws, r, 2, f"=2.5*B{r - 1}^0.38", fmt="0.0"); c(ws, r, 3, f"=2.5*C{r - 1}^0.38", fmt="0.0")
nombre("TDEV_81", f"'COCOMO II'!$B${r}")

# =============================================================================
# 8. Escenarios de 1 y 3 personas
# =============================================================================
ws = hoja("Escenarios", "Costo y plazo con 1 y 3 personas (esfuerzo ≠ duración)",
          "Base: esfuerzo COCOMO II con tamaño desde NESMA. La duración NO se divide entre tres: se suma la coordinación y se respeta el plazo mínimo.",
          (34, 11, 13, 13, 10, 12, 13, 11, 13, 13, 13, 15))
cab(ws, 4, ["Escenario", "Personas", "h/mes por persona", "Esfuerzo base (h)", "Canales n(n−1)/2",
            "Sobrecosto coordinación", "Esfuerzo total (h)", "Esfuerzo (PM)", "Duración por capacidad (meses)",
            "Duración mínima COCOMO (meses)", "Duración resultante (meses)", "Costo (S/)"])
ESC = [("1 persona, tiempo completo", 1, "=HorasMesCompleto"), ("3 personas, tiempo completo", 3, "=HorasMesCompleto"),
       ("1 persona, dedicación parcial", 1, "=HorasMesParcial"), ("3 personas, dedicación parcial", 3, "=HorasMesParcial")]
for i, (n, p, hm) in enumerate(ESC, start=5):
    c(ws, i, 1, n, negrita=True)
    c(ws, i, 2, p, fondo=ENTRADA)
    c(ws, i, 3, hm, fmt="0.0")
    c(ws, i, 4, "=PM_Nesma*HorasPM", fmt="#,##0")
    c(ws, i, 5, f"=B{i}*(B{i}-1)/2")
    c(ws, i, 6, f"=E{i}*SobrecostoCanal", fmt="0%")
    c(ws, i, 7, f"=D{i}*(1+F{i})", fmt="#,##0")
    c(ws, i, 8, f"=G{i}/HorasPM", fmt="0.0")
    c(ws, i, 9, f"=G{i}/(B{i}*C{i})", fmt="0.0")
    c(ws, i, 10, "=CompresionMax*TDEV_Nesma", fmt="0.0")
    c(ws, i, 11, f"=MAX(I{i},J{i})", fmt="0.0", fondo=RESULT, negrita=True)
    c(ws, i, 12, f"=G{i}*Tarifa", fmt='"S/" #,##0', fondo=RESULT, negrita=True)
for i, t in enumerate([
    "Esfuerzo (h, PM) = trabajo total; Duración (meses) = calendario; Costo (S/) = esfuerzo × tarifa. Son magnitudes distintas.",
    "Con 3 personas el esfuerzo SUBE (coordinación) y la duración baja menos que 1/3; no puede bajar del 75 % del TDEV nominal.",
    "El tamaño funcional (PF, CFP) no cambia con el número de personas.",
], start=10):
    ws.cell(row=i, column=1, value=t).font = Font(italic=True)

# =============================================================================
# 9. Sensibilidad ±20 %
# =============================================================================
ws = hoja("Sensibilidad", "Sensibilidad: variación de ±20 % en parámetros relevantes",
          "Cada fila recalcula COCOMO II cambiando solo el parámetro indicado (los demás quedan en su valor base).",
          (34, 12, 12, 12, 12, 12, 14, 14))
cab(ws, 4, ["Parámetro variado", "Variación", "Valor usado", "KSLOC", "Esfuerzo (PM)", "TDEV (meses)",
            "Costo 3 personas (S/)", "Δ costo vs. base"])
r = 5
bloques = [("Factor SLOC/PF", "=LocPorPF*(1+{v})", "=PF_Detallado*C{r}/1000", "=A_coc*D{r}^E_coc*EAF"),
           ("Tamaño en PF", "=PF_Detallado*(1+{v})", "=C{r}*LocPorPF/1000", "=A_coc*D{r}^E_coc*EAF"),
           ("Multiplicador CPLX (complejidad)", "=1.17*(1+{v})", "=KSLOC_Nesma", "=A_coc*D{r}^E_coc*EAF/1.17*C{r}")]
base_cost = None
for titulo, val, ksloc, pmf in bloques:
    for v in (-0.2, 0, 0.2):
        c(ws, r, 1, titulo, negrita=(v == 0))
        c(ws, r, 2, v, fmt="+0%;-0%;0%")
        c(ws, r, 3, val.format(v=v), fmt="0.00")
        c(ws, r, 4, ksloc.format(r=r), fmt="0.00")
        c(ws, r, 5, pmf.format(r=r), fmt="0.0")
        c(ws, r, 6, f"=C_coc*E{r}^(D_coc+0.2*(E_coc-B_coc))", fmt="0.0")
        c(ws, r, 7, f"=E{r}*HorasPM*(1+3*SobrecostoCanal)*Tarifa", fmt='"S/" #,##0')
        c(ws, r, 8, f"=G{r}/$G$6-1", fmt="+0.0%;-0.0%;0.0%")
        r += 1
    r += 1
ws.cell(row=r, column=1, value="Factor SLOC/PF alternativo: rango de la tabla QSM para C# (29 bajo, 70 alto) y factor real medido (hoja COCOMO II, columna B).").font = Font(italic=True)

# =============================================================================
# 10. Horas reales
# =============================================================================
ws = hoja("Horas reales", "Horas reales del desarrollo del producto frente a la estimación",
          "Registro diario del equipo hasta la versión 1.1.1 (01_Libro/horas_reales_desarrollo.json).",
          (14, 40, 16, 16, 16, 16))
r = 4
ws.cell(row=r, column=1, value="Desarrollo del producto Cóndor hasta la versión 1.1.1: registro diario del equipo (01_Libro/horas_reales_desarrollo.json)").font = Font(bold=True)
r += 1
registro = json.loads((AQUI / "horas_reales_desarrollo.json").read_text(encoding="utf-8"))
INTEGR = [("Condo", "Integrante 3\nCondo Zamata"), ("Chaisa", "Integrante 4\nChaisa Fernández"),
          ("Huamani", "Integrante 1\nHuamani Condori"), ("Payehuanca", "Integrante 2\nPayehuanca Riquelme")]
cab(ws, r, ["Fecha"] + [t for _, t in INTEGR] + ["Total del día (h)"])
r += 1
s_ini = r
for dia in registro["registros"]:
    c(ws, r, 1, date.fromisoformat(dia["fecha"]), fmt='dd"/"mm"/"yyyy')
    for j, (clave, _) in enumerate(INTEGR, start=2):
        h_ = next(x["horas"] for x in dia["integrantes"] if x["nombre"].startswith(clave))
        c(ws, r, j, h_, fondo=ENTRADA)
    c(ws, r, 6, f"=SUM(B{r}:E{r})", negrita=True)
    r += 1
s_fin = r - 1
c(ws, r, 1, "Total", negrita=True, fondo=TOTAL)
for j, col in enumerate("BCDEF", start=2):
    c(ws, r, j, f"=SUM({col}{s_ini}:{col}{s_fin})", negrita=True, fondo=RESULT if col == "F" else TOTAL)
nombre("HorasRealesDesarrollo", f"'Horas reales'!$F${r}")
r += 2
ws.cell(row=r, column=1, value="Confrontación con la estimación").font = Font(bold=True)
r += 1
cab(ws, r, ["Magnitud", "", "", "", "Valor", "Unidad"])
CONF = [
    ("Esfuerzo real", "=HorasRealesDesarrollo", "h", "#,##0"),
    ("Esfuerzo real en persona-mes", "=HorasRealesDesarrollo/HorasPM", "PM", "0.00"),
    ("Personas", f"=COUNTA(B{s_ini - 1}:E{s_ini - 1})", "personas", "0"),
    ("Duración real", f"=A{s_fin}-A{s_ini}+1", "días de calendario", "0"),
    ("Duración real en meses", f"=(A{s_fin}-A{s_ini}+1)/30.4", "meses", "0.00"),
    ("Horas por persona y día (promedio)", f"=HorasRealesDesarrollo/((A{s_fin}-A{s_ini}+1)*4)", "h / persona / día", "0.0"),
    ("Horas estimadas: COCOMO II con tamaño NESMA", "=PM_Nesma*HorasPM", "h", "#,##0"),
    ("Horas estimadas: COCOMO II con tamaño real", "=PM_Real*HorasPM", "h", "#,##0"),
    ("Error relativo MRE = |estimado − real| / real (NESMA)", "=ABS(PM_Nesma*HorasPM-HorasRealesDesarrollo)/HorasRealesDesarrollo", "—", "0%"),
    ("Error relativo MRE (tamaño real)", "=ABS(PM_Real*HorasPM-HorasRealesDesarrollo)/HorasRealesDesarrollo", "—", "0%"),
    ("Factor de calibración local = real / estimado (NESMA)", "=HorasRealesDesarrollo/(PM_Nesma*HorasPM)", "—", "0.000"),
    ("Constante A calibrada = A × factor", "=A_coc*HorasRealesDesarrollo/(PM_Nesma*HorasPM)", "—", "0.000"),
    ("Productividad real", "=KslocReal*1000/HorasRealesDesarrollo", "SLOC / h", "0.0"),
    ("Productividad implícita en COCOMO II", "=KslocReal*1000/(PM_Real*HorasPM)", "SLOC / h", "0.0"),
    ("Costo real del esfuerzo (a la tarifa del trabajo)", "=HorasRealesDesarrollo*Tarifa", "S/", '"S/" #,##0'),
]
r += 1
for m, f, u, fmt in CONF:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    c(ws, r, 1, m, negrita=True)
    c(ws, r, 5, f, fmt=fmt, fondo=RESULT)
    c(ws, r, 6, u)
    r += 1
r += 1

# =============================================================================
# 11. Comparación
# =============================================================================
ws = hoja("Comparación", "Cuadro comparativo de métodos y magnitudes",
          "Cada magnitud con su unidad. Los PF NESMA y los CFP COSMIC no se suman ni se convierten entre sí.",
          (40, 18, 16, 60))
cab(ws, 4, ["Método / magnitud", "Valor", "Unidad", "Lectura"])
COMP = [
    ("NESMA indicativo", "=PF_Indicativo", "PF", "Solo cuenta archivos lógicos; útil al inicio, antes de conocer las transacciones.", "0"),
    ("NESMA estimado", "=PF_Estimado", "PF", "Identifica todas las funciones con complejidad por defecto.", "0"),
    ("NESMA detallado", "=PF_Detallado", "PF", "Complejidad medida con DET, RET y FTR: tamaño de referencia.", "0"),
    ("COSMIC", "=CFP_Total", "CFP", "Movimientos de datos; otra unidad, no comparable 1:1 con PF.", "0"),
    ("Relación CFP / PF (solo informativa)", "=CFP_Total/PF_Detallado", "CFP por PF", "No es un factor de conversión: describe este producto.", "0.00"),
    ("Tamaño en código desde NESMA", "=KSLOC_Nesma", "KSLOC", "PF × factor QSM para C#.", "0.00"),
    ("Tamaño real medido (1.1.0)", "=KslocReal", "KSLOC", "Código C# y SQL entregado, sin XAML ni pruebas.", "0.00"),
    ("Esfuerzo COCOMO II (NESMA)", "=PM_Nesma", "persona-mes", "Esfuerzo total del desarrollo.", "0.0"),
    ("Esfuerzo COCOMO II (tamaño real)", "=PM_Real", "persona-mes", "Con el tamaño que efectivamente se construyó.", "0.0"),
    ("Esfuerzo COCOMO 81 orgánico (NESMA)", "=PM_81", "persona-mes", "Modelo antiguo, sin factores de escala.", "0.0"),
    ("Duración nominal COCOMO II", "=TDEV_Nesma", "meses", "Calendario con el equipo óptimo de COCOMO.", "0.0"),
    ("Duración COCOMO 81", "=TDEV_81", "meses", "", "0.0"),
    ("Costo 1 persona (tiempo completo)", "=Escenarios!L5", "S/", "", '"S/" #,##0'),
    ("Duración 1 persona (tiempo completo)", "=Escenarios!K5", "meses", "", "0.0"),
    ("Costo 3 personas (tiempo completo)", "=Escenarios!L6", "S/", "Mayor que con 1 persona por la coordinación.", '"S/" #,##0'),
    ("Duración 3 personas (tiempo completo)", "=Escenarios!K6", "meses", "No es la tercera parte del plazo de 1 persona.", "0.0"),
    ("Duración 3 personas (dedicación parcial)", "=Escenarios!K8", "meses", "Escenario real del equipo de estudiantes.", "0.0"),
    ("Horas reales de desarrollo (20 al 30-10-2026)", "=HorasRealesDesarrollo", "h", "Registro diario de los 4 integrantes hasta la versión 1.1.1.", "#,##0"),
    ("Error relativo de COCOMO II frente a lo real", "=ABS(PM_Nesma*HorasPM-HorasRealesDesarrollo)/HorasRealesDesarrollo", "MRE", "COCOMO sin calibrar sobreestima este proyecto (ver hoja Horas reales).", "0%"),
    ("Constante A calibrada con el proyecto", "=A_coc*HorasRealesDesarrollo/(PM_Nesma*HorasPM)", "—", "A local para estimar los próximos incrementos de este equipo.", "0.000"),
]
for i, (m, v, u, lec, fmt) in enumerate(COMP, start=5):
    c(ws, i, 1, m, negrita=True); c(ws, i, 2, v, fmt=fmt, fondo=RESULT); c(ws, i, 3, u); c(ws, i, 4, lec, envolver=True)

wb.move_sheet("Comparación", offset=-(len(wb.sheetnames) - 1))
wb.active = 0
wb.save(SALIDA)
print("generado", SALIDA)
