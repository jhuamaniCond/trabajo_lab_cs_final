"""Genera catalogo_casos_prueba.xlsx (G07) a partir de los reportes reales.

Los estados, fechas y conteos NO se escriben a mano: se leen de los .trx de
xUnit y de los Cobertura.xml de ReportGenerator que dejó ejecutar_suite.ps1.

Uso:  python 02_Catalogo/generar_catalogo.py      (desde G07_Pruebas_Unitarias)
Requiere: Python 3.10+ y openpyxl (pip install openpyxl)
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

G07 = Path(__file__).resolve().parents[1]
NS = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
REVISION = "r21"  # revisión SVN en la que se registra G07 (trunk)

HU, PA, CO, CH = ("Huamani C., J. S.", "Payehuanca R., J. J.", "Condo Z., R. A.", "Chaisa F., A. L.")

# ---------------------------------------------------------------- casos ----
# (id, requisito, riesgo, unidad, objetivo, tipo, datos y preparación, dobles, resultado esperado, autor)
CASOS = [
    ("PU-01", "RF-07", "R03", "CalculadoraVenta.Importe", "El importe de la línea es cantidad × precio", "Válido",
     "cantidad 3, precio S/ 28.50", "—", "85.50", HU),
    ("PU-02", "CRQ-01", "R03", "CalculadoraVenta.Redondear / Importe", "Redondeo comercial a céntimos en el medio céntimo", "Valor límite",
     "2.345, 2.344 y -2.345; 0.333 kg × S/ 10.15 (3.37995)", "—", "2.35, 2.34, -2.35 y 3.38", HU),
    ("PU-03", "CRQ-01", "R03", "CalculadoraVenta.Totales", "Separar op. gravada e IGV de precios que ya incluyen IGV", "Válido",
     "importes 520.00 + 180.00 + 45.00 (ejemplo del wireframe)", "—", "Total 745.00 = op. gravada 631.36 + IGV 113.64", HU),
    ("PU-04", "RF-07", "R03", "CalculadoraVenta.Totales", "Venta sin líneas", "Valor límite",
     "lista vacía de importes", "—", "TotalesVenta.Cero (0, 0, 0)", HU),
    ("PU-05", "CRQ-14", "R03", "CalculadoraVenta.Importe", "Rechazar cantidades no positivas", "Excepción / límite",
     "cantidad 0, -1 y -0.001; precio 10", "—", "ArgumentOutOfRangeException con ParamName = cantidad", HU),
    ("PU-06", "CRQ-07", "R03", "CalculadoraVenta.Importe", "Rechazar precio cero; aceptar el menor positivo", "Excepción / límite",
     "precio 0 y precio 0.01, cantidad 1", "—", "ArgumentOutOfRangeException (precioUnitario); 0.01", HU),
    ("PU-07", "CRQ-04", "R11", "ValidadorDocumento.EsRucValido / Error / TipoSegunLargo", "Aceptar RUC válidos de persona jurídica y natural", "Válido",
     "20131312955 y 10461234564 (verificador módulo 11 correcto)", "—", "true; sin mensaje de error; tipo RUC", PA),
    ("PU-08", "CRQ-04", "R11", "ValidadorDocumento.Error", "Detectar un dígito verificador equivocado", "Inválido",
     "20131312954 (último dígito cambiado)", "—", "false y mensaje «El RUC no es válido: revise los números…»", PA),
    ("PU-09", "CRQ-04", "R11", "ValidadorDocumento.Error", "Rechazar prefijos de RUC no permitidos", "Inválido",
     "30131312955", "—", "«El RUC debe empezar con 10, 15, 16, 17 o 20.»", PA),
    ("PU-10", "CRQ-04", "R11", "ValidadorDocumento.EsDniValido", "DNI solo con 8 dígitos exactos", "Valor límite / inválido",
     "7, 8 y 9 dígitos; 8 caracteres con letra; vacío; null", "—", "solo «45781236» es válido", PA),
    ("PU-11", "RF-06", "R11", "ValidadorDocumento.Limpiar", "Ignorar puntos, guiones y espacios digitados o pegados", "Válido",
     "« 20.131.312-955 » y «45 781 236»", "—", "20131312955 válido; tipo DNI", PA),
    ("PU-12", "CRQ-04", "R11", "ValidadorDocumento.DigitoVerificadorRuc", "Exigir exactamente 10 dígitos para el verificador", "Excepción",
     "9 dígitos, 11 dígitos, 10 caracteres con letra; control con 2013131295", "—", "ArgumentException (primerosDiez); el control da 5", PA),
    ("PU-13", "CRQ-02", "R11", "EmisionComprobante.Errores / Preparar", "Boleta de exactamente S/ 700.00 sin DNI", "Valor límite",
     "boleta sin cliente, 25 × S/ 28.00 = 700.00", "—", "sin errores; total 700.00", HU),
    ("PU-14", "CRQ-02", "R11", "EmisionComprobante.Errores", "Boleta de S/ 700.01 sin DNI", "Valor límite + 1 / inválido",
     "boleta sin cliente, 700.00 + 0.01", "—", "un error en Documento: «…deben llevar el DNI del cliente…»", HU),
    ("PU-15", "CRQ-03", "R11", "EmisionComprobante.Preparar", "Factura a un cliente con DNI", "Excepción",
     "factura con cliente DNI 45781236", "—", "ComprobanteInvalidoException con 1 error en Documento", HU),
    ("PU-16", "CRQ-07", "R03", "EmisionComprobante.Preparar", "Factura válida: serie, numeración de líneas e importes recalculados", "Válido",
     "cliente RUC 20131312955; 10 × 28.50 (importe manipulado = 1.00) y 4 × 42.90", "—",
     "F001, tipo 01, ítems 1-2, importes 285.00 y 171.60, total 456.60 = 386.95 + 69.65", HU),
    ("PU-17", "CRQ-06", "R03", "EmisionComprobante.Errores", "Proforma ya convertida no se convierte otra vez", "Inválido",
     "proforma PR01-00000012 convertida en B001-00000045", "—", "error en Proforma: «…ya se convirtió en B001-00000045.»", HU),
    ("PU-18", "RF-08", "R03", "EmisionComprobante.VigenciaProforma / Comprobante.Vencida", "Proforma vale 7 días contando el de emisión", "Valor límite",
     "emisión 01-11-2026; consultas el 07-11 y el 08-11", "—", "válida hasta 07-11-2026; vencida el 08-11", HU),
    ("PU-19", "RF-01", "R02", "ServicioAutenticacion.AutenticarAsync", "Ingreso correcto con usuario normalizado y bitácora", "Válido",
     "cuenta vendedor1 / Condor2026!; se digita «  Vendedor1 »", "RepositorioUsuariosFalso, RelojFalso (01-11-2026 09:00)",
     "Exitoso; último acceso = reloj; 1 entrada «acceso correcto» en la bitácora", CH),
    ("PU-20", "RNF-03", "R02", "ServicioAutenticacion.AutenticarAsync", "Mismo mensaje para usuario inexistente y clave equivocada", "Inválido",
     "vendedor1 / clave-equivocada y noexiste / Condor2026!", "RepositorioUsuariosFalso, RelojFalso",
     "CredencialesInvalidas; «Usuario o contraseña incorrectos.»; acceso fallido en la bitácora", CH),
    ("PU-21", "RF-01", "R02", "ServicioAutenticacion.AutenticarAsync", "Datos vacíos no consultan la base", "Inválido / límite",
     "usuario vacío, solo espacios, clave vacía y ambos null", "RepositorioUsuariosFalso (espía de búsquedas)",
     "DatosIncompletos; 0 búsquedas; bitácora vacía", CH),
    ("PU-22", "RNF-03", "R02", "ServicioAutenticacion.AutenticarAsync", "El 5.º intento fallido bloquea 15 min, aun con la clave correcta", "Valor límite",
     "4 fallos, 5.º fallo, clave correcta a los 14 min 59 s", "RepositorioUsuariosFalso, RelojFalso",
     "1.º-4.º inválidas; 5.º bloqueada hasta 09:15; a las 09:14:59 sigue bloqueada", CH),
    ("PU-23", "RNF-03", "R02", "ServicioAutenticacion.AutenticarAsync", "A los 15 min exactos se desbloquea y reinicia intentos", "Valor límite",
     "5 fallos; reloj + 15:00; clave correcta", "RepositorioUsuariosFalso, RelojFalso",
     "Exitoso; intentos 0; BloqueadoHasta null; actualización (1, 0, null)", CH),
    ("PU-24", "RNF-03", "R02", "HashClave.Generar / Verificar", "Hash PBKDF2-SHA256, 100 000 iteraciones, sal de 16 bytes", "Válido / inválido",
     "clave Condor2026!; variante en minúsculas; hash con Base64 inválido", "—",
     "formato pbkdf2-sha256$100000$…; sal 16 bytes; verifica solo la clave exacta; sal distinta cada vez", CH),
    ("PU-25", "RF-15", "R03", "ReporteVentas.Consolidar", "Proformas no suman y rechazados se cuentan aparte", "Válido",
     "6 ventas de nov-2026: boleta, factura, nota, proforma, boleta rechazada, boleta pendiente", "Lista en memoria en lugar de PostgreSQL",
     "4 ventas, S/ 760.00, promedio 190.00, 1 rechazado, 1 pendiente; agrupaciones ordenadas", CH),
    ("PU-26", "CRQ-15", "R11", "ReporteVentas.ValidarPeriodo / Consolidar", "Período máximo de 366 días y fechas al revés", "Excepción / límite",
     "01-01-2026 + 365 días, + 366 días, un solo día, fin anterior al inicio", "—",
     "366 y 1 día aceptados; 367 y al revés: ArgumentException con su mensaje", CH),
    ("PU-27", "RF-15", "R03", "ReporteVentas.Consolidar", "Agrupar por día de Perú (UTC-5), no por día UTC", "Valor límite",
     "venta a las 03:00 UTC del 02-11 (22:00 del 01-11 en Majes)", "Lista en memoria",
     "cuenta el 01-11; el 02-11 queda con 0 ventas y promedio 0", CH),
]

COMPONENTES = {
    "Condor.Dominio.Ventas.CalculadoraVenta": "PU-01 a PU-06",
    "Condor.Dominio.Validacion.ValidadorDocumento": "PU-07 a PU-12",
    "Condor.Dominio.Ventas.EmisionComprobante": "PU-13 a PU-18",
    "Condor.Dominio.Seguridad.ServicioAutenticacion": "PU-19 a PU-23",
    "Condor.Dominio.Seguridad.HashClave": "PU-24",
    "Condor.Dominio.Reportes.ReporteVentas": "PU-25 a PU-27",
}

# Ejecuciones: (id, carpeta, trx, versión, propósito, comando)
EJECUCIONES = [
    ("E1", "03_Reportes/ejecucion_v1.1.1", "ejecucion_v1.1.1.trx", "1.1.1", "Ejecución de la suite G07 sobre la línea base vigente",
     r".\01_Suite\ejecutar_suite.ps1"),
    ("E2", "03_Reportes/cobertura_RNF-08", "cobertura_RNF-08.trx", "1.1.1", "Suite G07 dentro de la medición de cobertura del paquete (RNF-08)",
     r".\01_Suite\ejecutar_suite.ps1 -SuiteProducto -Nombre cobertura_RNF-08 -ConexionBD <cadena>"),
    ("E2b", "03_Reportes/cobertura_RNF-08", "cobertura_RNF-08_suite_producto.trx", "1.1.1", "Suite del producto (tests/Condor.Pruebas) en la misma medición",
     "(misma orden que E2)"),
    ("D1", "04_Defecto_Controlado/1_con_defecto", "DEF-02_con_defecto.trx", "1.1.1 + DEF-02", "Defecto controlado inyectado: se espera FALLO",
     r".\04_Defecto_Controlado\reproducir_defecto.ps1"),
    ("D2", "04_Defecto_Controlado/2_restaurado", "DEF-02_restaurado.trx", "1.1.1", "Código restaurado: se espera ÉXITO", "(misma orden que D1)"),
    ("R1", "05_Regresion/R1_producto_1.0.0_antes_CC-01", "R1_producto_1.0.0_antes_CC-01.trx", "1.0.0", "Regresión: producto antes de CC-01 (G02)",
     r".\01_Suite\ejecutar_suite.ps1 -Version 1.0.0 -Nombre R1_producto_1.0.0_antes_CC-01 -Salida G07_Pruebas_Unitarias/05_Regresion/R1_producto_1.0.0_antes_CC-01"),
    ("R2", "05_Regresion/R2_producto_1.1.1_despues_CC-01", "R2_producto_1.1.1_despues_CC-01.trx", "1.1.1", "Regresión: producto después de CC-01",
     r".\01_Suite\ejecutar_suite.ps1 -Nombre R2_producto_1.1.1_despues_CC-01 -Salida G07_Pruebas_Unitarias/05_Regresion/R2_producto_1.1.1_despues_CC-01"),
]


def leer_trx(ruta: Path) -> dict:
    raiz = ET.parse(ruta).getroot()
    c = raiz.find("t:ResultSummary/t:Counters", NS).attrib
    tiempos = raiz.find("t:Times", NS).attrib
    por_caso: dict[str, list[str]] = defaultdict(list)
    mensajes: dict[str, str] = {}
    for r in raiz.iterfind("t:Results/t:UnitTestResult", NS):
        m = re.search(r"PU_(\d\d)_", r.get("testName"))
        if not m:
            continue
        pu = f"PU-{m.group(1)}"
        por_caso[pu].append(r.get("outcome"))
        msg = r.find("t:Output/t:ErrorInfo/t:Message", NS)
        if msg is not None:
            mensajes[pu] = msg.text.strip().splitlines()[0]
    inicio = datetime.fromisoformat(re.sub(r"(\.\d{6})\d*", r"\1", tiempos["start"]))
    return {"total": int(c["total"]), "passed": int(c["passed"]), "failed": int(c["failed"]),
            "skipped": int(c.get("notExecuted", 0)) + (int(c["total"]) - int(c["executed"])),
            "inicio": inicio, "casos": por_caso, "mensajes": mensajes, "resultado": raiz.find("t:ResultSummary", NS).get("outcome")}


def leer_cobertura(ruta: Path) -> tuple[dict, tuple[int, int]]:
    """Líneas cubiertas/totales por clase (sumando clases anidadas) y del ensamblado."""
    raiz = ET.parse(ruta).getroot()
    lineas: dict[str, dict[tuple, int]] = defaultdict(dict)
    for cls in raiz.iter("class"):
        nombre = cls.get("name").split("/")[0].split("<")[0]
        for l in cls.find("lines").iter("line"):  # solo las líneas de la clase (no se repiten las de sus métodos)
            clave = (cls.get("filename"), l.get("number"))
            lineas[nombre][clave] = max(lineas[nombre].get(clave, 0), int(l.get("hits")))
    por_clase = {n: [sum(1 for h in d.values() if h > 0), len(d)] for n, d in lineas.items()}
    # Totales tal como los informa ReportGenerator (index.html y Summary.txt)
    return por_clase, (int(raiz.get("lines-covered")), int(raiz.get("lines-valid")))


def estado(lista: list[str]) -> str:
    if not lista:
        return "No ejecutado"
    return "Aprobado" if all(o == "Passed" for o in lista) else "Fallido"


# --------------------------------------------------------------- estilos ---
AZUL = PatternFill("solid", fgColor="1F3864")
GRIS = PatternFill("solid", fgColor="F2F2F2")
VERDE = PatternFill("solid", fgColor="E2EFDA")
ROJO = PatternFill("solid", fgColor="FCE4D6")
BORDE = Border(*(Side(style="thin", color="BFBFBF"),) * 4)


def hoja(wb, titulo, cabecera, filas, anchos):
    ws = wb.create_sheet(titulo)
    ws.append(cabecera)
    for f in filas:
        ws.append(list(f))
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), AZUL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BORDE
            if c.value in ("Aprobado", "Pasó", "Sin regresión", "Cerrado"):
                c.fill = VERDE
            elif c.value in ("Fallido", "Falló"):
                c.fill = ROJO
    for i, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = a
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def main():
    trx = {e[0]: leer_trx(G07 / e[1] / e[2]) for e in EJECUCIONES}
    cob_g07, tot_g07 = leer_cobertura(G07 / "03_Reportes/ejecucion_v1.1.1/cobertura/Cobertura.xml")
    cob_pkg, tot_pkg = leer_cobertura(G07 / "03_Reportes/cobertura_RNF-08/cobertura/Cobertura.xml")
    e1, d1, d2, r1, r2 = trx["E1"], trx["D1"], trx["D2"], trx["R1"], trx["R2"]
    pct = lambda c, t: f"{(1000 * c // t) / 10:.1f} %" if t else "—"  # trunca a 1 decimal, como ReportGenerator

    wb = Workbook()
    wb.remove(wb.active)

    # 1. Instrucciones -----------------------------------------------------
    ws = wb.create_sheet("Instrucciones")
    texto = [
        ("G07 · Pruebas unitarias del Sistema Cóndor", True),
        ("Producto probado: Sistema_Logistico_Condor_final 1.1.1 (trunk de svn://127.0.0.1/condor, revisión " + REVISION + "). Paquete de lógica de negocio: Condor.Dominio.", False),
        ("Herramientas: .NET SDK 8.0 · xUnit 2.9.2 + xunit.runner.visualstudio 2.8.2 · Microsoft.NET.Test.Sdk 17.11.1 · coverlet.collector 6.0.2 · ReportGenerator 5.3.11 (manifiesto 01_Suite/.config/dotnet-tools.json). No se mezclan APIs: solo [Fact]/[Theory]/Assert de xUnit 2.", False),
        ("", False),
        ("1. Ejecutar la suite (desde la carpeta G07_Pruebas_Unitarias, en PowerShell)", True),
        (r"   .\01_Suite\ejecutar_suite.ps1", False),
        ("   Usa el SDK de .NET 8 local o, si no está instalado, el contenedor mcr.microsoft.com/dotnet/sdk:8.0 (Docker Desktop). No necesita base de datos.", False),
        ("   Resultado esperado: 27 casos (43 ejecuciones contando las filas de [Theory]) aprobados; código de salida 0. Reportes en 03_Reportes/<nombre>/ (.trx, .html y cobertura/index.html).", False),
        ("   Solo con dotnet:  dotnet test 01_Suite/Condor.PruebasUnitarias --logger trx --collect \"XPlat Code Coverage\" --settings 01_Suite/cobertura.runsettings", False),
        ("", False),
        ("2. Reproducir el defecto controlado DEF-02", True),
        (r"   .\04_Defecto_Controlado\reproducir_defecto.ps1", False),
        ("   Cambia «>» por «>=» en EmisionComprobante (regla CRQ-02, ver DEF-02_boleta_700.patch), corre la suite (debe FALLAR PU-13), restaura el archivo, comprueba su SHA-256 y vuelve a correr la suite (debe PASAR). Deja bitacora_DEF-02.txt y los reportes 1_con_defecto/ y 2_restaurado/.", False),
        ("   A mano: aplicar el parche (svn patch 04_Defecto_Controlado/DEF-02_boleta_700.patch desde la carpeta Trabajo Grupal), ejecutar el paso 1, y restaurar con svn revert Sistema_Logistico_Condor_final/src/Condor.Dominio/Ventas/EmisionComprobante.cs.", False),
        ("", False),
        ("3. Regresión después del cambio CC-01 de G02", True),
        (r"   .\01_Suite\ejecutar_suite.ps1 -Version 1.0.0 -Nombre R1_producto_1.0.0_antes_CC-01 -Salida G07_Pruebas_Unitarias/05_Regresion/R1_producto_1.0.0_antes_CC-01", False),
        (r"   .\01_Suite\ejecutar_suite.ps1 -Nombre R2_producto_1.1.1_despues_CC-01 -Salida G07_Pruebas_Unitarias/05_Regresion/R2_producto_1.1.1_despues_CC-01", False),
        ("   -Version 1.0.0 compila la suite contra 05_Regresion/producto_1.0.0 (Condor.Dominio del Sprint 5, anterior a CC-01) y excluye la carpeta CC01/, porque ServicioAutenticacion, HashClave y ReporteVentas no existían.", False),
        ("", False),
        ("4. Cobertura del paquete (RNF-08)", True),
        (r"   .\01_Suite\ejecutar_suite.ps1 -SuiteProducto -Nombre cobertura_RNF-08 -ConexionBD \"Host=localhost;Port=5433;Database=condor_pruebas;Username=condor_app;Password=<clave>\"", False),
        ("   Suma la suite G07 y la del producto (tests/Condor.Pruebas). Sin -ConexionBD las pruebas [FactConBD] quedan omitidas y la cobertura baja un poco. Con Docker use Host=host.docker.internal.", False),
        ("", False),
        ("5. Regenerar este libro", True),
        ("   python 02_Catalogo/generar_catalogo.py   (lee los .trx y Cobertura.xml; no hay estados escritos a mano)", False),
    ]
    for i, (t, negrita) in enumerate(texto, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(bold=negrita, size=13 if i == 1 else 11)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 150

    # 2. Catálogo ----------------------------------------------------------
    filas = []
    for (pu, req, rie, uni, obj, tipo, datos, dobles, esperado, autor) in CASOS:
        filas.append((pu, req, rie, uni, obj, tipo, datos, dobles, esperado, autor,
                      e1["inicio"].strftime("%Y-%m-%d %H:%M UTC"), "1.1.1 (" + REVISION + ")",
                      estado(e1["casos"][pu]), len(e1["casos"][pu]), "03_Reportes/ejecucion_v1.1.1/ejecucion_v1.1.1.trx",
                      "DEF-02 (controlado): falló en D1, pasó en D2 tras restaurar" if pu == "PU-13" else "—"))
    hoja(wb, "Catálogo", ["ID", "Requisito", "Riesgo (G06)", "Unidad (clase.método)", "Objetivo", "Tipo de escenario",
                          "Datos y preparación", "Dobles de prueba", "Resultado esperado", "Autor",
                          "Fecha de ejecución", "Versión probada", "Estado", "Filas ejecutadas", "Reporte", "Defecto y cierre"],
         filas, [8, 9, 9, 30, 34, 15, 38, 26, 40, 18, 18, 14, 11, 9, 34, 30])

    # 3. Ejecuciones -------------------------------------------------------
    filas = []
    for (eid, carpeta, archivo, ver, prop, cmd) in EJECUCIONES:
        t = trx[eid]
        filas.append((eid, t["inicio"].strftime("%Y-%m-%d %H:%M:%S UTC"), ver, prop, t["total"], t["passed"], t["failed"], t["skipped"],
                      "Pasó" if t["failed"] == 0 else "Falló", f"{carpeta}/{archivo}", cmd))
    hoja(wb, "Ejecuciones", ["ID", "Inicio", "Versión", "Propósito", "Total", "Aprobadas", "Fallidas", "Omitidas", "Resultado", "Reporte TRX", "Comando"],
         filas, [6, 22, 14, 44, 8, 10, 9, 9, 10, 52, 70])

    # 4. Cobertura ---------------------------------------------------------
    filas = []
    for clase, casos in COMPONENTES.items():
        c, t = cob_g07[clase]
        cp, tp = cob_pkg[clase]
        filas.append((clase, casos, c, t, pct(c, t), pct(cp, tp), "Sí" if c / t >= 0.8 else "No"))
    filas.append(("Condor.Dominio (paquete completo) · solo suite G07", "PU-01 a PU-27", tot_g07[0], tot_g07[1], pct(*tot_g07), "—",
                  "No (la suite G07 cubre 5 componentes, no el paquete)"))
    filas.append(("Condor.Dominio (paquete completo) · suite G07 + suite del producto", "E2 + E2b", tot_pkg[0], tot_pkg[1], "—", pct(*tot_pkg),
                  "Sí" if tot_pkg[0] / tot_pkg[1] >= 0.8 else "No"))
    ws = hoja(wb, "Cobertura", ["Clase / alcance", "Casos", "Líneas cubiertas (G07)", "Líneas ejecutables", "Cobertura G07",
                                "Cobertura suite completa", "Meta ≥ 80 %"], filas, [62, 16, 14, 14, 14, 16, 40])
    base = ws.max_row + 2
    notas = [
        "Inclusiones: ensamblado Condor.Dominio completo (entidades, validaciones, ventas, seguridad, reportes, SUNAT, impresión), filtro [Condor.Dominio]* en 01_Suite/cobertura.runsettings y -assemblyfilters:+Condor.Dominio en ReportGenerator.",
        "Exclusiones: proyectos de pruebas, API, datos (Npgsql), presentación WPF, ClienteApi, Sunat (cliente HTTP) e Impresión (ESC/POS); código con [GeneratedCode], [CompilerGenerated] o [ExcludeFromCodeCoverage]. Las interfaces de Contratos/ no tienen líneas ejecutables.",
        "Las líneas se cuentan como en Cobertura.xml (coverlet): una línea es cubierta si se ejecutó al menos una vez; las clases anidadas y los métodos generados por async se suman a su clase.",
        "Cobertura no sustituye la verificación del comportamiento: cada caso tiene aserciones sobre valores, mensajes, excepciones o estado; DEF-02 demuestra que la suite detecta un cambio de un solo carácter en una regla.",
    ]
    for i, n in enumerate(notas):
        ws.cell(row=base + i, column=1, value=n).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=base + i, start_column=1, end_row=base + i, end_column=7)
        ws.row_dimensions[base + i].height = 32

    # 5. Regresión ---------------------------------------------------------
    filas = []
    for (pu, req, *_rest) in CASOS:
        a, d = r1["casos"].get(pu, []), r2["casos"].get(pu, [])
        if not a:
            concl = "Caso nuevo de CC-01 (la regla no existía en 1.0.0)"
        elif estado(a) == estado(d) == "Aprobado":
            concl = "Sin regresión"
        else:
            concl = "Regresión: revisar"
        filas.append((pu, req, estado(a) if a else "No aplica (no compila en 1.0.0)", estado(d), concl))
    hoja(wb, "Regresión CC-01", ["ID", "Requisito", "R1 · 1.0.0 antes de CC-01", "R2 · 1.1.1 después de CC-01", "Conclusión"],
         filas, [8, 10, 32, 30, 50])

    # 6. Registro de defectos ---------------------------------------------
    msg = d1["mensajes"].get("PU-13", "")
    hoja(wb, "Registro de defectos",
         ["ID", "Fecha", "Versión", "Requisito", "Pasos de reproducción", "Datos", "Resultado esperado", "Resultado obtenido",
          "Severidad", "Prioridad", "Responsable", "Estado", "Corrección", "Prueba de cierre"],
         [("DEF-02 (controlado, G07)", d1["inicio"].strftime("%Y-%m-%d"), "1.1.1 + parche DEF-02_boleta_700.patch", "CRQ-02 / RF-07",
           "1) Ejecutar 04_Defecto_Controlado/reproducir_defecto.ps1 (o aplicar el parche). 2) Correr la suite G07. 3) Ver PU-13 en el TRX de 1_con_defecto.",
           "Boleta sin cliente, 25 × S/ 28.00 = S/ 700.00",
           "Boleta de S/ 700.00 se emite sin DNI (solo > 700 lo exige)",
           f"PU-13 falló ({d1['failed']} de {d1['total']}): {msg}",
           "Mayor (impediría vender boletas de S/ 700 sin DNI, función importante)", "Alta (regla tributaria)",
           HU, "Cerrado",
           "Se restauró el archivo original (SHA-256 igual al de antes, ver bitacora_DEF-02.txt); no se registró en SVN porque es un defecto inyectado a propósito",
           f"D2: {d2['passed']} de {d2['total']} aprobadas (04_Defecto_Controlado/2_restaurado/DEF-02_restaurado.trx)"),
          ("DEF-01 (real, G03/G05)", "2026-10-30", "1.1.0", "CRQ-07",
           "POST /api/escritorio/comprobantes con un precio distinto al del catálogo", "Línea con precio modificado por la PC",
           "El servidor toma el precio del catálogo", "Se guardaba el precio enviado por la PC",
           "Crítico (expone la integridad de las ventas)", "Alta", HU, "Cerrado",
           "Rama SVN DEF-01-precio-catalogo integrada en r11 (producto 1.1.1)",
           "Api/ClienteApiTests (3 pruebas DEF-01); suite 930 aprobadas; en G07 PU-16 verifica que el dominio recalcula importes")],
         [22, 11, 22, 12, 46, 30, 30, 50, 26, 16, 18, 10, 46, 46])

    # 7. Trazabilidad ------------------------------------------------------
    por_req, por_rie = defaultdict(list), defaultdict(list)
    for (pu, req, rie, *_r) in CASOS:
        por_req[req].append(pu)
        por_rie[rie].append(pu)
    filas = [("Requisito", k, ", ".join(v), len(v)) for k, v in sorted(por_req.items())]
    filas += [("Riesgo G06", k, ", ".join(v), len(v)) for k, v in sorted(por_rie.items())]
    hoja(wb, "Trazabilidad", ["Tipo", "ID", "Casos que lo verifican", "N.º de casos"], filas, [12, 10, 70, 12])

    salida = G07 / "02_Catalogo/catalogo_casos_prueba.xlsx"
    wb.save(salida)
    print(f"{salida.name}: {len(CASOS)} casos · E1 {e1['passed']}/{e1['total']} · D1 {d1['failed']} fallida(s) · D2 {d2['passed']}/{d2['total']} · "
          f"R1 {r1['passed']}/{r1['total']} · R2 {r2['passed']}/{r2['total']} · cobertura G07 {pct(*tot_g07)} · paquete {pct(*tot_pkg)}")


if __name__ == "__main__":
    main()
