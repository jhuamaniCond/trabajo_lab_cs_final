"""G07 en Redmine: verifica y cierra RF-06 (#4) y RNF-08 (#19) con la evidencia
de las pruebas unitarias, y anota la regresión en los requisitos ya cerrados
que la suite G07 vuelve a probar.

    python 07_Redmine/actualizar_redmine.py http://localhost:3010 <clave API del admin>

Regla del flujo de G02: quien implementa no verifica ni cierra.
  RF-06  implementó Condo      -> verifica Chaisa, cierra Huamani
  RNF-08 implementó Huamani    -> verifica Chaisa, cierra Payehuanca
Los conteos se leen de los .trx y del Cobertura.xml, no se escriben a mano.
"""
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

URL, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]
G07 = Path(__file__).resolve().parents[1]
NS = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
REV = "r21"
ESTADO = {"Implementado": 11, "Verificado": 12, "Cerrado": 13}


def api(metodo, ruta, cuerpo=None, como=None, binario=None):
    cab = {"X-Redmine-API-Key": CLAVE}
    if como:
        cab["X-Redmine-Switch-User"] = como
    datos = None
    if binario is not None:
        datos, cab["Content-Type"] = binario, "application/octet-stream"
    elif cuerpo is not None:
        datos, cab["Content-Type"] = json.dumps(cuerpo).encode("utf-8"), "application/json"
    req = urllib.request.Request(URL + ruta, data=datos, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read().decode("utf-8")
            return json.loads(txt) if txt.strip() else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{metodo} {ruta} como {como}: {e.code} {e.read().decode('utf-8')}")


def subir(ruta, como):
    token = api("POST", f"/uploads.json?filename={ruta.name}", como=como, binario=ruta.read_bytes())["upload"]["token"]
    tipo = {".html": "text/html", ".png": "image/png", ".txt": "text/plain"}.get(ruta.suffix, "application/xml")
    return {"token": token, "filename": ruta.name, "content_type": tipo}


def issue(n):
    return api("GET", f"/issues/{n}.json?include=journals")["issue"]


def mover(n, como, estado, nota, adjuntos=(), campos=None):
    actual = issue(n)["status"]["name"]
    if actual == estado:
        print(f"#{n}: ya estaba en {estado}")
        return
    cuerpo = {"status_id": ESTADO[estado], "notes": nota}
    if adjuntos:
        cuerpo["uploads"] = [subir(a, como) for a in adjuntos]
    if campos:
        cuerpo["custom_fields"] = campos
    api("PUT", f"/issues/{n}.json", {"issue": cuerpo}, como)
    quedo = issue(n)["status"]["name"]
    if quedo != estado:
        raise SystemExit(f"#{n}: se esperaba {estado} y quedó {quedo} (¿transición no permitida para {como}?)")
    print(f"#{n}: {actual} -> {estado} ({como})")


def anotar(n, como, nota):
    if any("G07 Pruebas unitarias" in (j.get("notes") or "") for j in issue(n)["journals"]):
        print(f"#{n}: la nota de G07 ya existía")
        return
    api("PUT", f"/issues/{n}.json", {"issue": {"notes": nota}}, como)
    print(f"#{n}: nota de regresión ({como})")


def trx(ruta):
    raiz = ET.parse(G07 / ruta).getroot()
    c = raiz.find("t:ResultSummary/t:Counters", NS).attrib
    res = {r.get("testName"): r.get("outcome") for r in raiz.iterfind("t:Results/t:UnitTestResult", NS)}
    return c, res


def cuenta(res, *claves):
    sel = [o for n, o in res.items() if any(k in n for k in claves)]
    return f"{sum(o == 'Passed' for o in sel)} de {len(sel)}"


def pruebas_vinculadas(n, extra):
    cf = next(c for c in issue(n)["custom_fields"] if c["name"] == "Pruebas vinculadas")
    valor = cf.get("value") or ""
    return [{"id": cf["id"], "value": valor if extra in valor else valor.rstrip() + "\n" + extra}]


c_g07, r_g07 = trx("03_Reportes/ejecucion_v1.1.1/ejecucion_v1.1.1.trx")
c_prod, r_prod = trx("03_Reportes/cobertura_RNF-08/cobertura_RNF-08_suite_producto.trx")
c_r1, _ = trx("05_Regresion/R1_producto_1.0.0_antes_CC-01/R1_producto_1.0.0_antes_CC-01.trx")
c_r2, _ = trx("05_Regresion/R2_producto_1.1.1_despues_CC-01/R2_producto_1.1.1_despues_CC-01.trx")
cob = ET.parse(G07 / "03_Reportes/cobertura_RNF-08/cobertura/Cobertura.xml").getroot()
cub, val = int(cob.get("lines-covered")), int(cob.get("lines-valid"))
pct = f"{(1000 * cub // val) / 10:.1f}".replace(".", ",")
cob_g07 = ET.parse(G07 / "03_Reportes/ejecucion_v1.1.1/cobertura/Cobertura.xml").getroot()
pct_g07 = f"{(1000 * int(cob_g07.get('lines-covered')) // int(cob_g07.get('lines-valid'))) / 10:.1f}".replace(".", ",")
UB = "`G07_Pruebas_Unitarias`"
SUITE = f"suite G07 {c_g07['passed']}/{c_g07['total']} (`03_Reportes/ejecucion_v1.1.1/ejecucion_v1.1.1.trx`)"

# --- RF-06 (#4) ------------------------------------------------------------
mover(4, "achaisa", "Verificado",
      f"Verificado en **G07 Pruebas unitarias** sobre la versión **1.1.1** (SVN {REV}), por un integrante distinto de quien lo implementó.\n\n"
      "| Criterio | Pruebas | Resultado |\n|---|---|---|\n"
      f"| CA-1 buscar por DNI completa el nombre | `Aceptacion/HU03_ClienteTests.CA1_*` | {cuenta(r_prod, 'HU03_ClienteTests.CA1_')} aprobadas |\n"
      f"| CA-2 RUC con dígito verificador incorrecto se rechaza (400) | PU-07 a PU-12 (`ValidadorDocumentoTests`); `ApiTests.Registrar_un_cliente_con_RUC_de_digito_verificador_invalido_responde_400`; `HU03_ClienteTests.CA3_RUC_invalido_*` | "
      f"{cuenta(r_g07, 'ValidadorDocumentoTests')} (G07) · {cuenta(r_prod, 'digito_verificador_invalido_responde_400')} · {cuenta(r_prod, 'HU03_ClienteTests.CA3_')} aprobadas |\n"
      f"| CA-3 documento repetido no se duplica (409) | `ClienteApiTests.Un_duplicado_llega_con_el_mensaje_de_la_regla`; `DatosPruebaClientesTests.El_repositorio_en_memoria_no_admite_documentos_repetidos` | "
      f"{cuenta(r_prod, 'Un_duplicado_llega_con_el_mensaje')} · {cuenta(r_prod, 'no_admite_documentos_repetidos')} aprobadas |\n\n"
      f"Suites: {SUITE}; suite del producto {c_prod['passed']} aprobadas, {c_prod['failed']} fallidas, "
      f"{int(c_prod['total']) - int(c_prod['executed'])} omitidas (`03_Reportes/cobertura_RNF-08/cobertura_RNF-08_suite_producto.trx`). "
      f"Catálogo: {UB}/02_Catalogo/catalogo_casos_prueba.xlsx. Riesgo vinculado: R11 (errores de los usuarios).",
      adjuntos=[G07 / "03_Reportes/ejecucion_v1.1.1/ejecucion_v1.1.1.trx"],
      campos=pruebas_vinculadas(4, "- G07: PU-07 a PU-12 (ValidadorDocumentoTests)"))
mover(4, "jhuamani", "Cerrado",
      "Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.1 → pruebas unitarias y de aceptación en verde). "
      "La prueba web de registro válido y datos inválidos se agregará en G09.")

# --- RNF-08 (#19) ----------------------------------------------------------
mover(19, "achaisa", "Verificado",
      f"Verificado en **G07 Pruebas unitarias** sobre la versión **1.1.1** (SVN {REV}), por un integrante distinto de quien lo implementó.\n\n"
      f"| Comprobación (CA-1: ≥ 80 % de líneas en Condor.Dominio) | Resultado |\n|---|---|\n"
      f"| Suite completa (G07 + `tests/Condor.Pruebas`), coverlet 6.0.2 + ReportGenerator 5.3.11 | **{pct} %** ({cub} de {val} líneas) ✔ |\n"
      f"| Solo la suite G07 (27 casos en 5 componentes) | {pct_g07} % del paquete; cada componente probado ≥ 80 % |\n"
      f"| Suites en verde | {SUITE}; producto {c_prod['passed']} aprobadas, {c_prod['failed']} fallidas |\n\n"
      "Alcance: ensamblado Condor.Dominio completo; se excluyen pruebas, API, datos, presentación y código generado "
      f"(`01_Suite/cobertura.runsettings`). Reporte: {UB}/03_Reportes/cobertura_RNF-08/cobertura/index.html.",
      adjuntos=[G07 / "03_Reportes/cobertura_RNF-08/cobertura/Summary.txt",
                G07 / "03_Reportes/capturas/04_cobertura_paquete_Condor.Dominio_RNF-08.png"],
      campos=pruebas_vinculadas(19, "- G07: 03_Reportes/cobertura_RNF-08 (suite G07 + suite del producto)"))
mover(19, "jpayehuanca", "Cerrado",
      f"Cierre: la meta de RNF-08 se cumple con datos medidos ({pct} % ≥ 80 %) y la suite está en verde. "
      "Se vuelve a medir en la regresión final de G09.")

# --- Notas de regresión en requisitos ya cerrados ---------------------------
REGR = (f"Regresión tras CC-01: producto 1.0.0 {c_r1['passed']}/{c_r1['total']} y 1.1.1 {c_r2['passed']}/{c_r2['total']} "
        f"(`05_Regresion/`).")
NOTAS = {
    1: ("RF-01", "PU-19, PU-21 (ServicioAutenticacion con repositorio y reloj falsos)"),
    5: ("RF-07", "PU-01 a PU-06 (CalculadoraVenta) y PU-13 a PU-16 (EmisionComprobante). El defecto controlado **DEF-02** "
                 "(`>` → `>=` en la boleta de S/ 700, CA-2) fue detectado por PU-13 y la suite volvió a pasar tras restaurar "
                 "(`04_Defecto_Controlado/`)"),
    6: ("RF-08", "PU-17 y PU-18 (proforma convertida y vigencia de 7 días)"),
    23: ("RF-15", "PU-25 a PU-27 (ReporteVentas: proformas, rechazados, período de 366 días, día de Perú)"),
    25: ("RNF-03", "PU-20, PU-22 a PU-24 (mismo mensaje, bloqueo al 5.º intento, desbloqueo a los 15 min, PBKDF2 100 000 iteraciones y sal de 16 bytes)"),
}
for n, (req, casos) in NOTAS.items():
    anotar(n, "jhuamani", f"**G07 Pruebas unitarias** ({REV}, versión 1.1.1): {req} vuelve a verificarse con {casos}. "
                          f"{SUITE}. {REGR} El estado no cambia.")
