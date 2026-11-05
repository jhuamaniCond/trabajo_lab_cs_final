"""G09 en Redmine: registra la solicitud de cambio CC-03 con su recorrido completo
por el flujo de G02, anota en cada requisito el caso Selenium que lo verificó y
deja capturas de las peticiones.

    python 08_Redmine/actualizar_redmine.py http://localhost:3010 <clave de los usuarios de demostración>

Cada paso se hace con la cuenta de quien lo realiza (autenticación básica), así el
historial muestra el responsable real. Regla del flujo de G02: quien implementa no
verifica ni cierra.
  CC-03  registra Payehuanca (suite G09), analiza Condo, aprueba el gerente,
         implementa Condo (r28-r31, trunk r32), verifica Chaisa, cierra Payehuanca
Las cifras se leen de los resultados.json de 04_Reportes, no se escriben a mano.
El script es idempotente: si un paso ya está hecho, lo salta.
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

G09 = Path(__file__).resolve().parents[1]
URL, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]
ESTADO = {"Registrado": 7, "Analizado": 8, "Aprobado": 9, "Implementado": 11, "Verificado": 12, "Cerrado": 13}
PROYECTO, TRACKER_CAMBIO = 1, 5
UB = "`G09_Gestion_Calidad`"

# Requisito -> casos Selenium que lo verificaron (01_Plan/plan_pruebas_aceptacion.md).
CASOS = {
    "RF-01": "CP-01, CP-02", "RF-02": "CP-14", "RF-03": "CP-03, CP-12, CP-13", "RF-04": "CP-05, CP-06",
    "RF-05": "CP-05, CP-06, CP-07", "RF-06": "CP-04, CP-05, CP-08", "RF-07": "CP-07, CP-08, CP-09, CP-10",
    "RF-08": "CP-10", "RF-11": "CP-13", "RF-12": "CP-13", "RF-14": "CP-07, CP-11", "RF-15": "CP-12",
    "RNF-01": "CP-07", "RNF-03": "CP-02, CP-03", "RNF-06": "CP-07",
}


def api(metodo, ruta, cuerpo=None, como="admin", binario=None):
    cab = {"Authorization": "Basic " + base64.b64encode(f"{como}:{CLAVE}".encode()).decode()}
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
    tipo = {".html": "text/html", ".png": "image/png", ".md": "text/markdown", ".xml": "application/xml"}.get(ruta.suffix, "text/plain")
    return {"token": token, "filename": ruta.name, "content_type": tipo}


def issue(n):
    return api("GET", f"/issues/{n}.json?include=journals")["issue"]


def buscar(prefijo, tracker=None):
    filtro = f"&tracker_id={tracker}" if tracker else ""
    for i in api("GET", f"/issues.json?project_id={PROYECTO}&status_id=*&limit=100{filtro}")["issues"]:
        if i["subject"].startswith(prefijo + " ") or i["subject"] == prefijo:
            return i["id"]
    return None


def usuario_id(login):
    return next(u["id"] for u in api("GET", "/users.json?limit=100")["users"] if u["login"] == login)


def mover(n, como, estado, nota, adjuntos=(), campos=None, asignar=None):
    actual = issue(n)["status"]["name"]
    if actual == estado:
        print(f"#{n}: ya estaba en {estado}")
        return
    cuerpo = {"status_id": ESTADO[estado], "notes": nota}
    if adjuntos:
        cuerpo["uploads"] = [subir(a, como) for a in adjuntos]
    if campos:
        cuerpo["custom_fields"] = campos
    if asignar:
        cuerpo["assigned_to_id"] = usuario_id(asignar)
    api("PUT", f"/issues/{n}.json", {"issue": cuerpo}, como)
    quedo = issue(n)["status"]["name"]
    if quedo != estado:
        raise SystemExit(f"#{n}: se esperaba {estado} y quedó {quedo} (¿transición no permitida para {como}?)")
    print(f"#{n}: {actual} -> {estado} ({como})")


def anotar(n, como, marca, nota, campos=None):
    if any(marca in (j.get("notes") or "") for j in issue(n)["journals"]):
        print(f"#{n}: la nota ya existía")
        return
    cuerpo = {"notes": nota}
    if campos:
        cuerpo["custom_fields"] = campos
    api("PUT", f"/issues/{n}.json", {"issue": cuerpo}, como)
    print(f"#{n}: nota ({como})")


def campo(n, nombre, extra):
    cf = next((c for c in issue(n)["custom_fields"] if c["name"] == nombre), None)
    if cf is None:
        return None
    valor = cf.get("value") or ""
    return [{"id": cf["id"], "value": valor if extra in valor else (valor.rstrip() + "\n" + extra).strip()}]


def version(nombre, descripcion):
    for v in api("GET", f"/projects/{PROYECTO}/versions.json")["versions"]:
        if v["name"] == nombre:
            return v["id"]
    return api("POST", f"/projects/{PROYECTO}/versions.json",
               {"version": {"name": nombre, "status": "open", "description": descripcion}})["version"]["id"]


# ---------------------------------------------------------------- resultados medidos
def ejecucion(sufijo):
    carpeta = next(c for c in sorted((G09 / "04_Reportes").iterdir()) if c.name.endswith(sufijo))
    return carpeta, json.loads((carpeta / "resultados.json").read_text(encoding="utf-8"))


def resumen(sufijo):
    carpeta, d = ejecucion(sufijo)
    ok = sum(c["estado"] == "APROBADO" for c in d["casos"])
    nav = d["entorno"]["navegador"]
    return carpeta, d, ok, len(d["casos"]), f'{nav["navegador"]} {nav["version"]}'


finales = [resumen(s) for s in ("r32_final-3", "r32_final-4", "r32_edge-2")]
assert all(ok == total for _, _, ok, total, _ in finales), "La regresión final no está en verde: no se verifica CC-03"
_, defectos, ok_def, total_def, _ = resumen("r30_defectos")
TABLA = ("| Ejecución | Navegador | Aprobados |\n|---|---|---|\n"
         + "".join(f"| `{c.name}` | {nav} | {ok}/{total} |\n" for c, _, ok, total, nav in finales))
cp07 = next(c["mediciones"] for c in finales[0][1]["casos"] if c["caso"] == "CP-07")

# --- CC-03 (solicitud de cambio) ------------------------------------------------
cc = buscar("CC-03", TRACKER_CAMBIO)
if cc:
    print(f"CC-03 ya existe: #{cc}")
else:
    cc01 = buscar("CC-01", TRACKER_CAMBIO) or 20
    campos = {c["name"]: c["id"] for c in issue(cc01)["custom_fields"]}
    cc = api("POST", "/issues.json", {"issue": {
        "project_id": PROYECTO, "tracker_id": TRACKER_CAMBIO, "status_id": ESTADO["Registrado"], "priority_id": 3,
        "subject": "CC-03 Portal web del mostrador (interfaz automatizable con Selenium, G09)",
        "description": "El enunciado y la Guía 9 exigen una interfaz web automatizable con Selenium WebDriver y un navegador. "
                       "El producto solo tiene la app WPF y la API REST. Propuesta: un portal web servido por Condor.Api, con el "
                       "aspecto de la app y sin reglas propias, más las rutas de proformas y compras para cubrir los tres procesos.\n\n"
                       f"Documento completo: {UB}/00_Solicitud_Cambio/CC-03_portal_web.md",
        "custom_fields": [{"id": campos["ID cambio"], "value": "CC-03"},
                          {"id": campos["Motivo"], "value": "G09 exige Selenium WebDriver con navegador; el producto no tenía interfaz web. Se descartó Appium + WinAppDriver (sin mantenimiento desde 2020)."},
                          {"id": campos["Decisión"], "value": "Pendiente"}],
    }}, como="jpayehuanca")["issue"]["id"]
    print(f"CC-03 registrada: #{cc}")

campos = {c["name"]: c["id"] for c in issue(cc)["custom_fields"]}
mover(cc, "rcondo", "Analizado",
      "Análisis de impacto. Ver el documento de la solicitud (sección 3).",
      campos=[{"id": campos["Impacto en diseño"], "value": "DD-09 (SDD 1.1): portal estático en Condor.Api/wwwroot; componentes y despliegue actualizados; 4 rutas nuevas (proformas y compras) con las reglas de Condor.Dominio. Sin cambios en Condor.Dominio, Condor.Datos ni en la base. ERS 1.2: interfaz INT-07."},
              {"id": campos["Impacto en costo"], "value": "17 h × S/ 25.00 = S/ 425.00 (portal 6 h, rutas y xUnit 2 h, suite Selenium 6 h, análisis 1 h, dictamen 2 h)"},
              {"id": campos["Impacto en plazo"], "value": "1 día con 3 integrantes; no mueve el segundo entregable (25-11-2026)"},
              {"id": campos["Riesgos"], "value": "R12 (interceptación en la LAN) sube: el portal se abre por HTTP desde cualquier navegador; S10 (HTTPS) sube de prioridad. XSS mitigado escapando todo texto de la API. La autorización no se debilita: la API repite el rol (S1)."},
              {"id": campos["Pruebas afectadas"], "value": "Nuevas: Api/PortalWebTests (11) y suite Selenium CP-01 a CP-14. Repetir: suite completa del producto."}],
      asignar="gerente")
mover(cc, "gerente", "Aprobado",
      "**Decisión del CCB: aprobada.** Condiciones: el portal no tiene reglas propias; el aspecto sigue el de la app; se "
      "desarrolla en una rama SVN y se integra con la suite en verde. Versión afectada: 1.2.0.",
      campos=[{"id": campos["Decisión"], "value": "Aprobada"}], asignar="rcondo")
api("PUT", f"/issues/{cc}.json", {"issue": {"fixed_version_id": version("1.2.0", "CC-03 (G09): portal web del mostrador")}}, como="admin")
mover(cc, "rcondo", "Implementado",
      "Implementado en la rama `branches/CC-03-portal-web` (r28 a r31) e integrado en trunk en **r32**. Versión **1.2.0** (CHANGELOG). "
      "Suite del producto: 944 aprobadas, 0 fallidas, 5 omitidas (`04_Reportes/xunit_1.2.0-r32`).\n\n"
      f"La suite Selenium detectó dos defectos del portal en r30 ({ok_def}/{total_def}): **DEF-03** (lista de Compras con 0 líneas) y "
      "**DEF-04** (aviso de la emisión anterior visible al convertir una proforma), corregidos en r31. "
      f"Registro: {UB}/05_Defectos/registro_defectos.md",
      adjuntos=[G09 / "04_Reportes/xunit_1.2.0-r32/suite_producto_1.2.0_r32.html"], asignar="achaisa")
mover(cc, "achaisa", "Verificado",
      "Verificado con la suite Selenium de G09 (Selenium 4.52.0, Python 3.12) sobre trunk r32, por un integrante distinto de quien "
      "lo implementó:\n\n" + TABLA +
      f"\nLos tres procesos se recorren completos: PN-01 (CP-07), PN-02 (CP-10, cambio de estado VIGENTE → CONVERTIDA) y "
      f"PN-03 (CP-13). RNF-01: {cp07.get('RNF-01 sugerencias (ms)')} ms (< 1 000 ms). Capturas y reporte en {UB}/04_Reportes.",
      adjuntos=[finales[0][0] / "reporte.html", finales[0][0] / "capturas" / "CP-10_03_proforma_convertida.png"],
      asignar="jpayehuanca")
mover(cc, "jpayehuanca", "Cerrado",
      "Cierre: cambio integrado en trunk r32 por configuración, ERS 1.2 y SDD 1.1 actualizados, regresión xUnit y Selenium en verde. "
      "Pendiente fuera de CC-03: etiqueta del avance 2 (`tags/v0.2.0`) desde trunk.")

# --- Requisitos: caso Selenium que los verificó --------------------------------
for codigo, casos in CASOS.items():
    n = buscar(codigo)
    if not n:
        print(f"{codigo}: no está en Redmine (solo se gestionan los requisitos de G02); se omite")
        continue
    estados = {c["caso"]: c["estado"] for c in finales[0][1]["casos"]}
    detalle = ", ".join(f"{c.strip()} {estados.get(c.strip(), '?').lower()}" for c in casos.split(","))
    anotar(n, "jpayehuanca", "G09 Selenium",
           f"**G09 Selenium** (portal web 1.2.0, trunk r32): {detalle} en Chrome (dos ejecuciones) y Edge. "
           f"Plan: {UB}/01_Plan/plan_pruebas_aceptacion.md; reportes: {UB}/04_Reportes.",
           campos=campo(n, "Pruebas vinculadas", f"- G09: {casos} (Selenium)"))

print(f"\nListo. CC-03 = #{cc}. Capturas: python 08_Redmine/capturar_redmine.py {URL} <clave> {cc}")
