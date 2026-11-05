"""Genera los dos libros de G06 a partir de los mismos datos:

    python generar_matrices.py

1. matriz_riesgos_magerit.xlsx  — escenarios activo-amenaza con frecuencia, degradación,
   impacto y riesgo (tablas de MAGERIT v3, Libro III §2.1), en tres situaciones:
   potencial (sin salvaguardas), actual (producto 1.1.1) y objetivo (con el plan).
   Impacto y riesgo se calculan con fórmulas INDEX/MATCH sobre la hoja Escalas.
2. Plan_Riesgo_Condor.xlsx      — plantilla docente Plan_Riesgo_Guia_6_Alumnos.xlsx
   completada con el mismo caso (matriz simplificada P x I, complemento del análisis).

Los datos salen de 01_Inventario/inventario_activos.md y de 04_Controles.
"""
import shutil
from pathlib import Path

import openpyxl
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = Path(__file__).resolve().parent
PLANTILLA = AQUI.parents[2] / "6" / "enunciado" / "Plan_Riesgo_Guia_6_Alumnos.xlsx"

NIVELES = ["MB", "B", "M", "A", "MA"]
NOMBRE_NIVEL = {"MB": "muy bajo", "B": "bajo", "M": "medio", "A": "alto", "MA": "muy alto"}
# MAGERIT v3 Libro III, 2.1.1: impacto = f(valor, degradación)  (filas valor MB..MA; columnas degradación B, M, A)
IMPACTO = {"MA": ["M", "A", "MA"], "A": ["B", "M", "A"], "M": ["MB", "B", "M"], "B": ["MB", "MB", "B"], "MB": ["MB", "MB", "MB"]}
# MAGERIT v3 Libro III, 2.1.2: riesgo = f(impacto, frecuencia)  (filas impacto; columnas frecuencia MB..MA)
RIESGO = {"MA": ["A", "MA", "MA", "MA", "MA"], "A": ["M", "A", "A", "MA", "MA"], "M": ["B", "M", "M", "A", "MA"],
          "B": ["MB", "B", "B", "M", "A"], "MB": ["MB", "MB", "MB", "B", "B"]}
DEGR = ["B", "M", "A"]


def nivel_valor(v):
    """Escala 0-10 de MAGERIT (Libro II, cap. 4) a los cinco niveles de las tablas."""
    return "MA" if v >= 9 else "A" if v >= 6 else "M" if v >= 3 else "B" if v >= 1 else "MB"


def impacto(valor, d):
    return IMPACTO[nivel_valor(valor)][DEGR.index(d)]


def riesgo(imp, f):
    return RIESGO[imp][NIVELES.index(f)]


# ---------------------------------------------------------------- activos
ACTIVOS = [
    # id, nombre, tipo plantilla, propietario, depende de, C, I, D, A (escala 1-5 de la plantilla), justificación
    ("A01", "Servicio de venta y facturación (PN-01, PN-02)", "Servicio", "Gerente general", "A05, A08, A10", 1, 1, 5, 1,
     "~150 ventas/día y colas en hora punta (ENT-01); MAGERIT [D]=8"),
    ("A02", "Datos de ventas y comprobantes electrónicos", "Datos", "Gerente general / contador", "A04, A05, A06, A09", 3, 5, 4, 5,
     "Valor tributario 5 años (CRQ-01, CRQ-05); MAGERIT [I]=9 [A]=8 [T]=8 [D]=7 [C]=5"),
    ("A03", "Datos de compras, costos y proveedores (PN-03)", "Datos", "Encargado general", "A05, A06, A09", 4, 3, 2, 3,
     "Costos ocultos al vendedor (CFL-06, CRQ-12); MAGERIT [C]=7 [I]=6"),
    ("A04", "Certificado digital y credenciales SOL", "Recuperación", "Gerente general", "A07", 5, 4, 3, 5,
     "Permite emitir comprobantes a nombre de la ferretería; MAGERIT [C]=9 [A]=9"),
    ("A05", "Aplicación Cóndor 1.1.1 (WPF + Condor.Api)", "Software", "Equipo de desarrollo", "A06, A07, A08", 4, 5, 5, 5,
     "Valor acumulado de A01-A03 (PILAR propaga por dependencias)"),
    ("A06", "Base de datos PostgreSQL 16", "Software", "Encargado general", "A07", 4, 5, 4, 5, "Valor acumulado de A02 y A03"),
    ("A07", "PC principal (API, base de datos y caja 1)", "Infraestructura", "Encargado general", "A08", 5, 5, 5, 5,
     "Soporta todos los activos esenciales y el certificado"),
    ("A08", "Red local e Internet (enlace a la SUNAT)", "Infraestructura", "Encargado general", "", 4, 4, 5, 4,
     "Une las 3 PC con la API; sin ella no se vende desde las cajas 2 y 3"),
    ("A09", "Disco externo de respaldos", "Recuperación", "Encargado general", "A07", 4, 5, 4, 1, "Contiene copia completa de A02 y A03"),
    ("A10", "Personal y cuentas de usuario", "Personas", "Gerente general", "", 3, 4, 5, 5, "Vendedores y encargado operan PN-01 a PN-03"),
]

# Valor acumulado MAGERIT (0-10) por activo y dimensión, propagado desde los esenciales.
VALOR = {
    "A01": {"D": 8}, "A02": {"D": 7, "I": 9, "C": 5, "A": 8, "T": 8}, "A03": {"D": 4, "I": 6, "C": 7, "A": 5, "T": 5},
    "A04": {"D": 6, "I": 8, "C": 9, "A": 9, "T": 6},
    "A05": {"D": 8, "I": 9, "C": 7, "A": 8, "T": 8}, "A06": {"D": 7, "I": 9, "C": 7, "A": 8, "T": 8},
    "A07": {"D": 8, "I": 9, "C": 9, "A": 9, "T": 8}, "A08": {"D": 8, "I": 9, "C": 7, "A": 8, "T": 8},
    "A09": {"D": 7, "I": 9, "C": 7, "A": 8, "T": 8}, "A10": {"D": 8, "I": 9, "C": 7, "A": 8, "T": 8},
}

# ---------------------------------------------------------------- escenarios
# id, activo, amenaza MAGERIT, código local de la plantilla, dimensión, vulnerabilidad,
# (frecuencia, degradación) potencial / actual / objetivo, controles actuales, salvaguardas, justificación
ESCENARIOS = [
    ("R01", "A03", "[A.11] Acceso no autorizado", "T6", "C",
     "Un vendedor abre compras, costos o proveedores desde su caja o llamando a la API",
     ("A", "A"), ("B", "M"), ("MB", "M"),
     "S1: rutas del Encargado responden 403 al Vendedor (6/6 verificadas)", "S1 (implantado) · revisión mensual de bitácora",
     "2-3 vendedores por turno usan la misma aplicación cada día (OBS-01); si entran ven todo el módulo"),
    ("R02", "A02", "[A.5] Suplantación de la identidad del usuario", "T2", "A",
     "Contraseña adivinada o compartida entre vendedores del mismo turno",
     ("A", "A"), ("M", "A"), ("B", "M"),
     "S1: PBKDF2 100 000 iter., bloqueo 15 min al 5.º intento, usuario en cada comprobante", "S1 (implantado) · S9 política y capacitación",
     "CUE-01: los vendedores se turnan la caja; el bloqueo impide adivinar pero no el préstamo de clave"),
    ("R03", "A02", "[A.15] Modificación deliberada de la información", "T3", "I",
     "La PC envía a la API un precio o cantidad manipulados y se guardan en el comprobante (DEF-01)",
     ("M", "A"), ("B", "B"), ("MB", "B"),
     "S2: la API toma precio y descripción del catálogo y rechaza cantidades/líneas fuera de rango (5/5)", "S2 (implantado)",
     "DEF-01 lo demostró en 1.1.0; un comprobante alterado es contingencia tributaria (CRQ-01)"),
    ("R04", "A04", "[A.11] Acceso no autorizado / [E.19] fuga del certificado y la clave SOL", "T6", "C A",
     "El .pfx y la clave SOL están en la PC principal sin protección formal",
     ("B", "A"), ("B", "A"), ("MB", "M"),
     "Ninguno formal (madurez [K] L1 en PILAR)", "S4 protección del certificado",
     "Con el certificado se emiten comprobantes válidos a nombre de la ferretería"),
    ("R05", "A06", "[E.18] Destrucción de información / [I.5] avería lógica de la base", "T5", "I D",
     "Borrado accidental o base corrupta tras un fallo del contenedor",
     ("M", "A"), ("M", "M"), ("M", "B"),
     "S3: pg_dump RF-16, restauración verificada (conteos idénticos), aviso si el respaldo tiene más de 24 h", "S3 (implantado) · S5 respaldo automático y fuera del local",
     "Respaldo manual: se pierde lo emitido desde el último respaldo (hasta 1 día)"),
    ("R06", "A07", "[I.5] Avería de origen físico o lógico / [A.25] robo del equipo", "T7", "D",
     "Una sola PC aloja API y base; si falla, las 3 cajas dejan de vender",
     ("M", "A"), ("M", "M"), ("B", "B"),
     "S3: hay respaldo para reinstalar en otra PC, sin procedimiento escrito", "S11 contingencia de la PC principal",
     "PC de mostrador sin mantenimiento planificado (madurez [HW] L1)"),
    ("R07", "A08", "[I.8] Fallo de servicios de comunicaciones", "T8", "D",
     "Cortes de Internet en Majes impiden enviar a la SUNAT",
     ("A", "A"), ("A", "B"), ("A", "B"),
     "Venta sin Internet y reenvío automático (RNF-05, HU07/HU17)", "Implantado en el producto · aceptar residual",
     "ENT-01 y OBS-01 registran cortes varias veces al mes; la venta continúa y el envío se reintenta"),
    ("R08", "A07", "[I.6] Corte del suministro eléctrico", "T4", "D",
     "La PC principal y el switch no tienen UPS",
     ("M", "A"), ("M", "A"), ("M", "B"),
     "Ninguno ([AUX] L0)", "S6 UPS y apagado controlado",
     "Cortes de luz varias veces al año; se detiene todo el local hasta que vuelve la energía"),
    ("R09", "A05", "[A.8] Difusión de software dañino (ransomware)", "T1", "C I D",
     "Actualizaciones sin calendario; el disco de respaldo queda conectado",
     ("M", "A"), ("M", "A"), ("B", "B"),
     "Antivirus de Windows; respaldos en disco conectado a la misma PC", "S7 protección contra software dañino · S5 copia desconectada",
     "Un cifrado de la PC principal alcanza la base y el disco conectado"),
    ("R10", "A09", "[A.25] Robo de soportes / [E.19] fuga de información", "T9", "C",
     "El respaldo .backup no está cifrado y contiene costos y datos de clientes",
     ("B", "A"), ("B", "A"), ("B", "B"),
     "Ninguno ([M] L1)", "S8 cifrado de respaldos",
     "Disco externo guardado en el local, sin custodia"),
    ("R11", "A10", "[E.1] Errores de los usuarios", "T5", "I",
     "Anulación o precio de catálogo registrados por error",
     ("A", "M"), ("A", "B"), ("M", "B"),
     "Anulación solo del Encargado (RF-03), validaciones y confirmaciones de la aplicación", "S9 política y capacitación",
     "Errores frecuentes en hora punta (OBS-01); la aplicación limita su alcance"),
    ("R12", "A08", "[A.14] Interceptación de información (escucha)", "T6", "C A",
     "La API se publica por HTTP en la LAN: token y contraseña viajan sin cifrar",
     ("B", "A"), ("B", "M"), ("MB", "M"),
     "Token Bearer con caducidad (CC-01); LAN cableada del local", "S10 HTTPS en la API",
     "Requiere un equipo en la red local con un capturador de tráfico"),
]

# ---------------------------------------------------------------- salvaguardas
SALVAGUARDAS = [
    # id, nombre, riesgos, tipo, estado, responsable, fecha, horas, costo extra S/, indicador, evidencia
    ("S1", "Autenticación y autorización por roles (RF-03, RNF-03, CC-01)", "R01, R02", "Preventiva", "Implantado y verificado",
     "Payehuanca R., J. J. (implementó CC-01) · verifica Chaisa F., A. L.", "2026-10-31", 0, 0,
     "100 % de rutas del Encargado con 403 al Vendedor; bloqueo al 5.º intento",
     "04_Controles/verificacion_controles.md (10/10) y pruebas_controles_S1_S2_S3.trx"),
    ("S2", "Validación de entradas en el servidor (CRQ-07, CRQ-14, DEF-01)", "R03", "Preventiva", "Implantado y verificado",
     "Huamani C., J. S. (DEF-01) y Condo Z., R. A. (CRQ-14) · verifica Chaisa F., A. L.", "2026-10-31", 0, 0,
     "0 comprobantes con precio distinto al del catálogo; 100 % de entradas fuera de rango rechazadas",
     "04_Controles/verificacion_controles.md (5/5)"),
    ("S3", "Respaldo y restauración de la base (RF-16, RNF-07)", "R05, R06", "Recuperación", "Implantado y verificado",
     "Chaisa F., A. L. · opera el Encargado general", "2026-10-31", 0, 0,
     "Restauración con conteos idénticos en 8 tablas; antigüedad del último respaldo <= 24 h",
     "04_Controles/verificacion_controles.md (3/3)"),
    ("S4", "Protección del certificado digital y de la clave SOL", "R04", "Preventiva", "Propuesto",
     "Gerente general · apoya Chaisa F., A. L.", "2026-11-20", 3, 0,
     "Certificado importado como no exportable; 0 copias del .pfx fuera del sobre sellado; clave SOL cambiada cada 6 meses", "—"),
    ("S5", "Respaldo automático diario, copia desconectada y fuera del local, prueba trimestral", "R05, R09", "Recuperación", "Propuesto",
     "Chaisa F., A. L. · opera el Encargado general", "2026-11-25", 6, 250,
     "100 % de días con respaldo; 1 restauración de prueba por trimestre", "—"),
    ("S6", "UPS para la PC principal y el switch, con apagado controlado", "R08", "Preventiva", "Propuesto",
     "Gerente general (compra) · Condo Z., R. A. (configura)", "2026-12-15", 2, 350,
     "Autonomía >= 10 min; 0 apagados bruscos de PostgreSQL", "—"),
    ("S7", "Protección contra software dañino (actualizaciones mensuales, cuentas sin privilegios)", "R09", "Preventiva", "Propuesto",
     "Condo Z., R. A.", "2026-11-30", 4, 0,
     "Actualizaciones aplicadas cada mes; vendedores sin cuenta de administrador de Windows", "—"),
    ("S8", "Cifrado de los respaldos (AES-256)", "R10", "Preventiva", "Propuesto",
     "Chaisa F., A. L.", "2026-11-25", 3, 0, "100 % de archivos de respaldo cifrados", "—"),
    ("S9", "Política de cuentas y capacitación (no compartir claves, cerrar sesión, anulaciones)", "R02, R11", "Preventiva", "Propuesto",
     "Huamani C., J. S. con el gerente general", "2026-12-02", 6, 0,
     "100 % del personal capacitado (acta); 0 comprobantes emitidos con cuenta ajena en la revisión mensual", "—"),
    ("S10", "HTTPS en la API (certificado de la LAN instalado en las 3 PC)", "R12", "Preventiva", "Propuesto",
     "Payehuanca R., J. J.", "2026-12-10", 8, 0, "0 rutas de la API accesibles por HTTP sin cifrar", "—"),
    ("S11", "Procedimiento de contingencia de la PC principal (reinstalar en la caja 2 desde el respaldo)", "R06", "Recuperación", "Propuesto",
     "Condo Z., R. A.", "2026-12-02", 5, 0, "Ensayo documentado: servicio restablecido en <= 4 h", "—"),
]
TARIFA = 25.0  # S/ por hora (misma de G02 y G04)

P_DE = {"MB": 1, "B": 2, "M": 3, "A": 4, "MA": 5}  # frecuencia -> P de la plantilla
I_DE = P_DE  # nivel de impacto -> I de la plantilla


def valor_escenario(act, dims):
    return max(VALOR[act][d] for d in dims.split() if d in VALOR[act])


def calcular():
    filas = []
    for e in ESCENARIOS:
        rid, act, amen, _, dims, vuln, pot, actu, obj, ctrl, salv, just = e
        v = valor_escenario(act, dims)
        res = {}
        for nombre, (f, d) in (("pot", pot), ("act", actu), ("obj", obj)):
            imp = impacto(v, d)
            res[nombre] = (f, d, imp, riesgo(imp, f))
        filas.append((e, v, res))
    return filas


# ---------------------------------------------------------------- estilo
FINO = Side(style="thin", color="999999")
BORDE = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
CAB = PatternFill("solid", fgColor="1F3864")
ENTRADA = PatternFill("solid", fgColor="FFF2CC")
FORMULA = PatternFill("solid", fgColor="DDEBF7")
COLOR_NIVEL = {"MA": "C00000", "A": "FF6600", "M": "FFC000", "B": "FFFF66", "MB": "C6EFCE"}


def cabecera(ws, fila, textos):
    for i, t in enumerate(textos, 1):
        c = ws.cell(fila, i, t)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = CAB
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BORDE


def colores_nivel(ws, rango):
    for n, color in COLOR_NIVEL.items():
        ws.conditional_formatting.add(rango, CellIsRule(operator="equal", formula=[f'"{n}"'],
                                                       fill=PatternFill(start_color=color, end_color=color, fill_type="solid")))


def anchos(ws, valores):
    for i, w in enumerate(valores, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------- libro MAGERIT
def libro_magerit(filas):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Escalas"
    ws["A1"] = "Escalas de MAGERIT v3 usadas en la matriz (Libro II cap. 4-5; Libro III §2.1, análisis mediante tablas)"
    ws["A1"].font = Font(bold=True, size=12)
    ws["A3"] = "Valor del activo (0-10) → nivel"
    ws["A3"].font = Font(bold=True)
    cabecera(ws, 4, ["Nivel", "Valor 0-10", "Significado"])
    for i, (n, r, s) in enumerate([("MA", "9-10", "muy alto / extremo"), ("A", "6-8", "alto"), ("M", "3-5", "medio"),
                                   ("B", "1-2", "bajo"), ("MB", "0", "despreciable")], 5):
        ws.cell(i, 1, n), ws.cell(i, 2, r), ws.cell(i, 3, s)
    ws["E3"] = "Frecuencia (ocurrencias por año)"
    ws["E3"].font = Font(bold=True)
    cabecera_f = ["Nivel", "Tasa anual", "Significado"]
    for i, t in enumerate(cabecera_f):
        c = ws.cell(4, 5 + i, t)
        c.font, c.fill, c.border = Font(bold=True, color="FFFFFF"), CAB, BORDE
    for i, (n, r, s) in enumerate([("MA", 100, "a diario"), ("A", 10, "mensualmente"), ("M", 1, "una vez al año"),
                                   ("B", 0.1, "cada varios años"), ("MB", 0.01, "muy rara vez (siglos)")], 5):
        ws.cell(i, 5, n), ws.cell(i, 6, r), ws.cell(i, 7, s)
    ws["I3"] = "Degradación del activo cuando ocurre"
    ws["I3"].font = Font(bold=True)
    for i, t in enumerate(["Nivel", "Proporción", "Significado"]):
        c = ws.cell(4, 9 + i, t)
        c.font, c.fill, c.border = Font(bold=True, color="FFFFFF"), CAB, BORDE
    for i, (n, r, s) in enumerate([("B", "≈ 1 %", "afecta un registro o una operación"),
                                   ("M", "≈ 10 %", "afecta una parte (un día, un módulo)"),
                                   ("A", "≈ 100 %", "afecta todo el activo")], 5):
        ws.cell(i, 9, n), ws.cell(i, 10, r), ws.cell(i, 11, s)

    ws["A12"] = "Tabla de impacto (valor × degradación)"
    ws["A12"].font = Font(bold=True)
    cabecera(ws, 13, ["valor \\ degradación", "B", "M", "A"])
    for i, n in enumerate(["MA", "A", "M", "B", "MB"], 14):
        ws.cell(i, 1, n).font = Font(bold=True)
        for j, x in enumerate(IMPACTO[n], 2):
            ws.cell(i, j, x).border = BORDE
    colores_nivel(ws, "B14:D18")
    ws["F12"] = "Tabla de riesgo (impacto × frecuencia)"
    ws["F12"].font = Font(bold=True)
    for i, t in enumerate(["impacto \\ frecuencia", "MB", "B", "M", "A", "MA"]):
        c = ws.cell(13, 6 + i, t)
        c.font, c.fill, c.border = Font(bold=True, color="FFFFFF"), CAB, BORDE
    for i, n in enumerate(["MA", "A", "M", "B", "MB"], 14):
        ws.cell(i, 6, n).font = Font(bold=True)
        for j, x in enumerate(RIESGO[n], 7):
            ws.cell(i, j, x).border = BORDE
    colores_nivel(ws, "G14:K18")
    ws["A21"] = ("Lectura: el impacto es la consecuencia de que la amenaza se materialice sobre un activo de cierto valor; "
                 "el riesgo pondera ese impacto por la frecuencia. Los niveles son ordinales: no se suman ni se convierten a soles.")
    ws["A22"] = ("Potencial = sin salvaguardas · Actual = producto 1.1.1 con los controles que existen hoy · "
                 "Objetivo = con el plan de tratamiento (previsto mientras no se implante y verifique).")
    anchos(ws, [20, 10, 10, 10, 12, 14, 12, 12, 12, 12, 34])

    # Valor acumulado
    wv = wb.create_sheet("Valor acumulado")
    cabecera(wv, 1, ["Activo", "Nombre", "[D]", "[I]", "[C]", "[A]", "[T]", "Origen del valor"])
    for i, a in enumerate(ACTIVOS, 2):
        wv.cell(i, 1, a[0]), wv.cell(i, 2, a[1])
        for j, d in enumerate("DICAT", 3):
            wv.cell(i, j, VALOR[a[0]].get(d))
        wv.cell(i, 8, "Valoración directa (A.2 de PILAR)" if a[0] in ("A01", "A02", "A03", "A04")
                else "Acumulado: máximo de los activos esenciales que dependen de él")
    anchos(wv, [8, 50, 6, 6, 6, 6, 6, 60])

    # Escenarios con fórmulas
    we = wb.create_sheet("Escenarios")
    cols = ["ID", "Activo", "Amenaza (catálogo MAGERIT)", "Dim.", "Vulnerabilidad", "Valor 0-10", "Nivel valor",
            "Pot. frec.", "Pot. degr.", "Pot. impacto", "Pot. riesgo",
            "Act. frec.", "Act. degr.", "Act. impacto", "Act. riesgo",
            "Obj. frec.", "Obj. degr.", "Obj. impacto", "Obj. riesgo",
            "Controles actuales", "Salvaguardas", "Justificación (información usada)"]
    cabecera(we, 1, cols)
    nv = '=IF(F{r}>=9,"MA",IF(F{r}>=6,"A",IF(F{r}>=3,"M",IF(F{r}>=1,"B","MB"))))'
    imp = '=INDEX(Escalas!$B$14:$D$18,MATCH($G{r},Escalas!$A$14:$A$18,0),MATCH({d}{r},Escalas!$B$13:$D$13,0))'
    rie = '=INDEX(Escalas!$G$14:$K$18,MATCH({i}{r},Escalas!$F$14:$F$18,0),MATCH({f}{r},Escalas!$G$13:$K$13,0))'
    for k, (e, v, res) in enumerate(filas, 2):
        rid, act, amen, _, dims, vuln, pot, actu, obj, ctrl, salv, just = e
        datos = [rid, act, amen, dims, vuln, v, nv.format(r=k)]
        for c0, (f, d) in zip(("H", "L", "P"), (pot, actu, obj)):
            ci = get_column_letter(openpyxl.utils.column_index_from_string(c0) + 1)
            cimp = get_column_letter(openpyxl.utils.column_index_from_string(c0) + 2)
            datos += [f, d, imp.format(r=k, d=ci), rie.format(r=k, i=cimp, f=c0)]
        datos += [ctrl, salv, just]
        for j, x in enumerate(datos, 1):
            c = we.cell(k, j, x)
            c.border = BORDE
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j in (6, 8, 9, 12, 13, 16, 17):
                c.fill = ENTRADA
            if j in (7, 10, 11, 14, 15, 18, 19):
                c.fill = FORMULA
    n = len(filas) + 1
    colores_nivel(we, f"J2:K{n}")
    colores_nivel(we, f"N2:O{n}")
    colores_nivel(we, f"R2:S{n}")
    for rango in (f"H2:H{n}", f"L2:L{n}", f"P2:P{n}"):
        dv = DataValidation(type="list", formula1='"MB,B,M,A,MA"')
        we.add_data_validation(dv)
        dv.add(rango)
    for rango in (f"I2:I{n}", f"M2:M{n}", f"Q2:Q{n}"):
        dv = DataValidation(type="list", formula1='"B,M,A"')
        we.add_data_validation(dv)
        dv.add(rango)
    anchos(we, [5, 6, 30, 6, 36, 7, 6] + [6] * 12 + [40, 34, 44])
    we.freeze_panes = "C2"
    we.cell(n + 2, 1, "Amarillo: entrada justificada · Azul: fórmula sobre la hoja Escalas · Las situaciones siguen las fases de PILAR (potencial, current, target).")

    # Priorización
    wp = wb.create_sheet("Priorización")
    cabecera(wp, 1, ["Orden", "ID", "Activo", "Amenaza", "Riesgo potencial", "Riesgo actual", "Riesgo objetivo", "Prioridad", "Respuesta", "Responsable"])
    orden = sorted(filas, key=lambda x: (-NIVELES.index(x[2]["act"][3]), -NIVELES.index(x[2]["pot"][3]), x[0][0]))
    resp = {s[0]: s[5] for s in SALVAGUARDAS}
    for k, (e, v, res) in enumerate(orden, 2):
        r = res["act"][3]
        pri = "1 - inmediata" if r == "MA" else "2 - alta" if r == "A" else "3 - programada" if r == "M" else "4 - vigilar"
        primera = e[10].split("·")[-1].strip().split()[0]
        quien = resp.get(primera, "Encargado general")
        for j, x in enumerate([k - 1, e[0], e[1], e[2], res["pot"][3], r, res["obj"][3], pri, e[10], quien], 1):
            c = wp.cell(k, j, x)
            c.border = BORDE
            c.alignment = Alignment(wrap_text=True, vertical="top")
    colores_nivel(wp, f"E2:G{n}")
    anchos(wp, [6, 5, 6, 40, 10, 10, 10, 14, 44, 44])

    # Plan de tratamiento
    wt = wb.create_sheet("Plan de tratamiento")
    cabecera(wt, 1, ["ID", "Salvaguarda", "Riesgos", "Tipo", "Estado", "Responsable", "Fecha", "Esfuerzo (h)",
                     "Costo esfuerzo S/", "Otros costos S/", "Costo total S/", "Indicador", "Evidencia"])
    wt.cell(1, 15, "Tarifa S/ por hora")
    wt.cell(2, 15, TARIFA).fill = ENTRADA
    for k, s in enumerate(SALVAGUARDAS, 2):
        sid, nom, rie_s, tipo, est, quien, fecha, h, extra, ind, evid = s
        datos = [sid, nom, rie_s, tipo, est, quien, fecha, h, f"=H{k}*$O$2", extra, f"=I{k}+J{k}", ind, evid]
        for j, x in enumerate(datos, 1):
            c = wt.cell(k, j, x)
            c.border = BORDE
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j in (9, 11):
                c.fill = FORMULA
    t = len(SALVAGUARDAS) + 2
    wt.cell(t, 7, "Total").font = Font(bold=True)
    for col in "HIJK":
        wt[f"{col}{t}"] = f"=SUM({col}2:{col}{t - 1})"
        wt[f"{col}{t}"].font = Font(bold=True)
    wt.cell(t + 2, 1, "S1-S3 ya fueron implantados durante el desarrollo (CC-01 en 1.1.0, DEF-01 y CRQ-14 en 1.1.1, RF-16): su costo está en las horas reales de G04 y aquí solo se registra su verificación. "
                      "S4-S11 son controles propuestos: su reducción de riesgo es prevista, no comprobada.")
    anchos(wt, [5, 46, 9, 12, 20, 40, 11, 8, 10, 10, 10, 46, 42, 4, 12])

    # PILAR
    wpi = wb.create_sheet("PILAR (contraste)")
    wpi["A1"] = "Riesgo acumulado calculado por PILAR Basic 2026.1.1 (A.6 Riesgo, escala 0-10). Transcrito de 03_PILAR/capturas/07 a 10."
    wpi["A1"].font = Font(bold=True)
    datos_pilar = {
        "potencial": [("A01", 6.0, None, None, None, None), ("A02", 5.4, 6.9, 5.1, 6.5, 5.1), ("A03", 3.7, 5.1, 6.3, 4.8, 3.4)],
        "current (actual)": [("A01", 5.7, None, None, None, None), ("A02", 5.2, 6.7, 3.7, 5.9, 4.1), ("A03", 3.4, 4.9, 4.9, 4.2, 2.3)],
        "target (objetivo)": [("A01", 3.9, None, None, None, None), ("A02", 3.3, 4.3, 2.1, 3.9, 2.4), ("A03", 1.5, 2.5, 3.2, 2.2, 0.93)],
        "PILAR (recomendación)": [("A01", 3.0, None, None, None, None), ("A02", 2.4, 3.9, 2.1, 3.5, 2.1), ("A03", 0.92, 2.2, 3.3, 1.7, 0.86)],
    }
    fila = 3
    for fase, filas_p in datos_pilar.items():
        wpi.cell(fila, 1, fase).font = Font(bold=True)
        fila += 1
        cabecera_p = ["Activo", "[D]", "[I]", "[C]", "[A]", "[T]"]
        for j, x in enumerate(cabecera_p, 1):
            c = wpi.cell(fila, j, x)
            c.font, c.fill = Font(bold=True, color="FFFFFF"), CAB
        for fp in filas_p:
            fila += 1
            for j, x in enumerate(fp, 1):
                wpi.cell(fila, j, x).border = BORDE
        fila += 2
    wpi.cell(fila, 1, "Leyenda de PILAR: 0 despreciable · 1 bajo · 2 medio · 3 alto · 4 muy alto · 5 crítico · 6 muy crítico · 7 extremadamente crítico · 8 desastre · 9 catástrofe")
    anchos(wpi, [24, 8, 8, 8, 8, 8])

    wb.save(AQUI / "matriz_riesgos_magerit.xlsx")


# ---------------------------------------------------------------- plantilla docente
CATALOGO = [  # códigos locales de la plantilla adaptados al caso (instrucción 5)
    ("T1", "Ransomware / software dañino", "Ataque", "Actualizaciones sin calendario; respaldo conectado a la PC", "Actualizaciones, cuentas sin privilegios, copia desconectada"),
    ("T2", "Suplantación de usuario", "Ataque", "Contraseñas adivinables o compartidas", "Hash fuerte, bloqueo por intentos, política de cuentas"),
    ("T3", "Alteración de comprobantes o precios", "Abuso o error", "Validación solo en el cliente", "Validación y precios tomados en el servidor"),
    ("T4", "Falla eléctrica", "Falla técnica", "Ausencia de respaldo eléctrico", "UPS y apagado controlado"),
    ("T5", "Borrado o error en los datos", "Error humano", "Restauración no ensayada; errores de operación", "Respaldo, ensayo de recuperación y capacitación"),
    ("T6", "Divulgación o interceptación de datos", "Abuso o error", "Acceso sin restricción por rol; HTTP sin cifrar; claves sin custodia", "Acceso mínimo por rol, cifrado y custodia de claves"),
    ("T7", "Falla del servidor (PC principal)", "Falla técnica", "Sin redundancia ni mantenimiento", "Mantenimiento y plan de recuperación"),
    ("T8", "Pérdida de conectividad", "Falla técnica", "Un solo enlace a Internet", "Operación sin conexión y reenvío automático"),
    ("T9", "Robo de equipo o soporte", "Ataque físico", "Disco de respaldo sin cifrado ni custodia", "Cifrado y control físico"),
    ("T10", "Error de actualización", "Error técnico", "Cambios sin prueba ni reversión", "Pruebas previas, SVN y plan de reversión"),
]

# Evaluación actual de la plantilla = línea base 1.0.0 (antes de CC-01 y DEF-01) para R01-R03 y R05,
# porque S1-S3 son precisamente los tratamientos implantados y verificados en esta guía.
BASE_100 = {"R01": "Ninguno: la versión 1.0.0 no tenía ingreso con roles ni API protegida (CC-01 llegó en 1.1.0)",
            "R02": "Ninguno: en 1.0.0 no había cuentas con contraseña cifrada ni bloqueo (CC-01)",
            "R03": "Validación solo en la aplicación de escritorio (DEF-01 abierto hasta 1.1.1)",
            "R05": "Respaldo RF-16 sin restauración ensayada ni aviso de antigüedad"}


def plantilla(filas):
    destino = AQUI / "Plan_Riesgo_Condor.xlsx"
    shutil.copy(PLANTILLA, destino)
    wb = openpyxl.load_workbook(destino)
    wa = wb["Activos"]
    wa["B4"] = "Sistema de Ventas y Facturación Cóndor 1.1.1 — Ferretería Cóndor Majes S.A.C."
    wa["B5"] = "Huamani C., J. S. · Payehuanca R., J. J. · Condo Z., R. A. · Chaisa F., A. L. (líder G06)"
    wa["B6"] = "PN-01 venta y facturación, PN-02 cotización, PN-03 abastecimiento; 3 PC, red local y enlace a la SUNAT"
    wa["B7"] = "Próximos 12 meses (nov 2026 - oct 2027)"
    for r in range(10, 30):
        for c in range(1, 11):
            wa.cell(r, c).value = None
    for i, a in enumerate(ACTIVOS, 10):
        for j, x in enumerate(a, 1):
            wa.cell(i, j, x)
    for dv in wb["Cruces Activo-Amenaza"].data_validations.dataValidation:
        if "A1,A2" in (dv.formula1 or ""):
            dv.formula1 = '"' + ",".join(f"A{n:02d}" for n in range(1, 21)) + '"'

    wc = wb["Catálogo amenazas"]
    for i, t in enumerate(CATALOGO, 5):
        for j, x in enumerate(t, 1):
            wc.cell(i, j, x)
    wc["A16"] = ("Adaptación (instrucción 5): se conservaron los códigos T1-T10 y se ajustó el texto al caso Cóndor. "
                 "La amenaza equivalente del catálogo MAGERIT figura en cada escenario de matriz_riesgos_magerit.xlsx.")

    wx = wb["Cruces Activo-Amenaza"]
    for k, (e, v, res) in enumerate(filas, 6):
        rid, act, amen, cod, dims, vuln, pot, actu, obj, ctrl, salv, just = e
        base = res["pot"] if rid in BASE_100 else res["act"]
        p, i = P_DE[base[0]], I_DE[base[2]]
        wx.cell(k, 1, rid), wx.cell(k, 2, act), wx.cell(k, 4, cod)
        wx.cell(k, 6, vuln)
        wx.cell(k, 7, dims)
        wx.cell(k, 8, BASE_100.get(rid, ctrl))
        wx.cell(k, 9, p), wx.cell(k, 10, i)
        wx.cell(k, 11, f"P={p}: frecuencia MAGERIT {base[0]} ({NOMBRE_NIVEL[base[0]]}). I={i}: impacto MAGERIT {base[2]} "
                       f"(valor {v}, degradación {base[1]}). {just}.")

    wr = wb["Análisis de Riesgos"]
    trat = {s[0]: s for s in SALVAGUARDAS}
    for k, (e, v, res) in enumerate(filas):
        rid = e[0]
        fila = 31 + k
        if rid in BASE_100:
            sid = {"R01": "S1", "R02": "S1", "R03": "S2", "R05": "S3"}[rid]
            s = trat[sid]
            resid = res["act"]
            estado = "Verificado"
            evid = f"{s[10]} · producto 1.1.1"
            accion = s[1] + (" + S9 (propuesta)" if rid == "R02" else " + S5 (propuesta)" if rid == "R05" else "")
        else:
            sids = [x.strip().split()[0] for x in e[10].split("·")]
            sid = next((x for x in sids if x in trat), None)
            s = trat.get(sid)
            resid = res["obj"]
            estado = "Propuesto" if s else "Implementado"
            evid = "Supuesto didáctico: control propuesto, residual previsto" if s else \
                   "Suite del producto: HU07_EnviarSunatTests, HU17_ReenvioAutomaticoTests (G07)"
            accion = s[1] if s else "Mantener venta sin Internet y reenvío automático (RNF-05)"
        tratamiento = "Aceptar" if rid == "R07" else "Mitigar"
        quien = s[5] if s else "Encargado general"
        plazo = 0 if estado == "Verificado" else 30
        if s and estado == "Propuesto":
            from datetime import date
            y, m, d = map(int, s[6].split("-"))
            plazo = (date(y, m, d) - date(2026, 11, 1)).days
        if rid == "R07":
            plazo = 30
        p_r, i_r = P_DE[resid[0]], I_DE[resid[2]]
        r_r = p_r * i_r
        if rid == "R07":
            decision = ("Gerente: acepta el residual como excepción documentada; no hay segundo proveedor de Internet en la zona "
                        "y RNF-05 mantiene la venta; revisar en 6 meses")
        elif r_r <= 4:
            decision = "Aceptado por el gerente general (residual dentro del umbral)"
        elif estado == "Verificado":
            decision = "Gerente: acepta temporalmente; se reduce con la medida propuesta indicada"
        else:
            decision = "Gerente: excepción documentada hasta implantar y verificar la medida; revisar en 3 meses"
        for col, x in zip("BCDEFGHIN", [tratamiento, accion, quien, max(plazo, 1), estado, evid, p_r, i_r, decision]):
            wr[f"{col}{fila}"] = x
    wb.save(destino)


if __name__ == "__main__":
    filas = calcular()
    libro_magerit(filas)
    plantilla(filas)
    for e, v, res in filas:
        print(e[0], e[1], e[4], "valor", v, "| pot", res["pot"], "| act", res["act"], "| obj", res["obj"])
