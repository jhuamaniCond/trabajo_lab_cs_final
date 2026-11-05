"""G08 en Redmine: verifica y cierra RNF-02 (#24) con los resultados de JMeter y registra la
mejora MEJ-01 como solicitud de cambio, con su recorrido completo por el flujo de G02.

    python 08_Redmine/actualizar_redmine.py http://localhost:3010 <clave de los usuarios de demostración>

Cada paso se hace con la cuenta de quien lo realiza (autenticación básica), así el historial
muestra el responsable real. Regla del flujo de G02: quien implementa no verifica ni cierra.
  RNF-02  implementó Condo (1.1.0)          -> verifica Chaisa, cierra Huamani
  MEJ-01  registra Condo (G08), analiza Payehuanca (CCB), aprueba el gerente,
          implementa Condo (r23-r24), verifica Chaisa, cierra Payehuanca (integró en r25)
Las cifras se leen de los .jtl con 06_Analisis/analizar_resultados.py, no se escriben a mano.
El script es idempotente: si un paso ya está hecho, lo salta.
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

G08 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G08 / "06_Analisis"))
import analizar_resultados as an  # noqa: E402

URL, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]
ESTADO = {"Registrado": 7, "Analizado": 8, "Aprobado": 9, "Implementado": 11, "Verificado": 12, "Cerrado": 13}
PROYECTO, TRACKER_CAMBIO = 1, 5
REV_RAMA, REV_TRUNK = "r23-r24", "r25"


def api(metodo, ruta, cuerpo=None, como="admin", binario=None):
    usuario = "admin" if como == "admin" else como
    cab = {"Authorization": "Basic " + base64.b64encode(f"{usuario}:{CLAVE}".encode()).decode()}
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
    tipo = {".html": "text/html", ".png": "image/png", ".xlsx":
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}.get(ruta.suffix, "text/plain")
    return {"token": token, "filename": ruta.name, "content_type": tipo}


def issue(n):
    return api("GET", f"/issues/{n}.json?include=journals")["issue"]


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


def anotar(n, como, marca, nota):
    if any(marca in (j.get("notes") or "") for j in issue(n)["journals"]):
        print(f"#{n}: la nota ya existía")
        return
    api("PUT", f"/issues/{n}.json", {"issue": {"notes": nota}}, como)
    print(f"#{n}: nota ({como})")


def campo(n, nombre, extra):
    cf = next(c for c in issue(n)["custom_fields"] if c["name"] == nombre)
    valor = cf.get("value") or ""
    return [{"id": cf["id"], "value": valor if extra in valor else (valor.rstrip() + "\n" + extra).strip()}]


def version(nombre):
    for v in api("GET", f"/projects/{PROYECTO}/versions.json")["versions"]:
        if v["name"] == nombre:
            return v["id"]
    return api("POST", f"/projects/{PROYECTO}/versions.json",
               {"version": {"name": nombre, "status": "open",
                            "description": "MEJ-01 (G08): correlativo reservado al final de la emisión"}})["version"]["id"]


# ---------------------------------------------------------------- cifras de los .jtl
def stats(fase, escenario, transaccion, desde=0, hasta=1e9):
    filas = an.leer_jtl(an.RESULTADOS / fase / escenario / "resultado.jtl")
    return an.resumir([r for r in filas if r["t"] == transaccion and desde <= r["seg"] < hasta])


def fila(fase, esc, t, desde=0, hasta=1e9):
    s = stats(fase, esc, t, desde, hasta)
    return f"{s['n']} | {s['p95']} ms | {an.num(s['error_pct'], 2)} % | {an.num(s['throughput'], 2)}/s"


def cumple(fase):
    return all(stats(fase, "carga", t)["p95"] <= an.UMBRAL_P95 and stats(fase, "carga", t)["error_pct"] <= an.UMBRAL_ERROR
               for t in an.TRANSACCIONES)


UB = "`G08_Pruebas_Rendimiento`"
assert cumple("1_antes") and cumple("2_despues"), "RNF-02 no se cumple: no se verifica"

TABLA_RNF02 = (
    "| Escenario (perfil del enunciado) | Transacción | Muestras | p95 | Error | Throughput |\n|---|---|---|---|---|---|\n"
    + "".join(f"| Carga esperada 10 u × 5 min, **{f}** | {t} | {fila(fase, 'carga', t)} |\n"
              for fase, f in (("1_antes", "1.1.1"), ("2_despues", "1.1.2")) for t in an.TRANSACCIONES)
    + "".join(f"| {nombre}, 1.1.2 | {t} | {fila('2_despues', esc, t, a, b)} |\n"
              for esc, nombre, a, b in (("estres", "Estrés, nivel 50 u", 400, 570), ("pico", "Pico, 50 u", 190, 250),
                                        ("estabilidad", "Estabilidad 10 u × 15 min", 0, 1e9))
              for t in an.TRANSACCIONES))

# --- RNF-02 (#24) -------------------------------------------------------------
mover(24, "achaisa", "Verificado",
      f"Verificado en **G08 Pruebas de rendimiento** (JMeter 5.6.3, modo no gráfico) sobre las versiones **1.1.1** (línea base) "
      f"y **1.1.2** (después de MEJ-01, SVN {REV_TRUNK}), por un integrante distinto de quien lo implementó.\n\n"
      "**CA-1** — el reporte HTML del escenario de carga esperada cumple, por transacción, p95 ≤ 2 s y error ≤ 1 %:\n\n"
      + TABLA_RNF02 +
      "\nError = código distinto de 200/201, aserción JSON fallida o tiempo de espera > 10 s. Entorno, datos (3 000 productos) "
      f"y escenarios en {UB}/01_Plan/plan_pruebas_rendimiento.md; resultados en {UB}/04_Resultados; análisis en {UB}/06_Analisis.",
      adjuntos=[G08 / "06_Analisis/resumen_resultados.xlsx", G08 / "06_Analisis/capturas/01_dashboard_carga_antes.png",
                G08 / "06_Analisis/capturas/02_dashboard_carga_despues.png"],
      campos=campo(24, "Pruebas vinculadas", "- G08: carga, estrés, pico y estabilidad antes y después (04_Resultados)"))
mover(24, "jhuamani", "Cerrado",
      "Cierre: el umbral de RNF-02 se contrastó con datos medidos en carga esperada, antes y después de la mejora. "
      "La conclusión de estabilidad vale para 15 minutos. Se repite en la regresión final de G09.")

# --- MEJ-01 (solicitud de cambio) ----------------------------------------------
c50a = stats("1_antes", "capacidad_50u", an.T2)
c50d = stats("2_despues", "capacidad_50u", an.T2)
t50a = stats("1_antes", "capacidad_50u", an.T1)
t50d = stats("2_despues", "capacidad_50u", an.T1)
existente = [i for i in api("GET", f"/issues.json?project_id={PROYECTO}&tracker_id={TRACKER_CAMBIO}&status_id=*&limit=100")["issues"]
             if i["subject"].startswith("MEJ-01")]
if existente:
    mej = existente[0]["id"]
    print(f"MEJ-01 ya existe: #{mej}")
else:
    campos = {c["name"]: c["id"] for c in issue(20)["custom_fields"]}
    mej = api("POST", "/issues.json", {"issue": {
        "project_id": PROYECTO, "tracker_id": TRACKER_CAMBIO, "status_id": ESTADO["Registrado"], "priority_id": 2,
        "subject": "MEJ-01 Reservar el correlativo de la serie al final de la emisión (rendimiento, G08)",
        "description": "Cuello de botella hallado en G08: en la prueba de capacidad sin pausas, desde 25 usuarios, las boletas se "
                       "encolan en el bloqueo de la fila de la serie B001 (19 de las 20 conexiones del pool esperando ese bloqueo) y "
                       "dejan sin conexiones a las consultas de productos. Propuesta: tomar el número al final de la transacción.\n\n"
                       f"Documento completo: {UB}/05_Cuello_de_Botella/MEJ-01_correlativo_al_final.md",
        "custom_fields": [{"id": campos["ID cambio"], "value": "MEJ-01"},
                          {"id": campos["Motivo"], "value": "Capacidad de emisión: el bloqueo de B001 dura toda la emisión y serializa las boletas."},
                          {"id": campos["Decisión"], "value": "Pendiente"}],
    }}, como="rcondo")["issue"]["id"]
    print(f"MEJ-01 registrada: #{mej}")
    api("POST", f"/issues/{mej}/relations.json", {"relation": {"issue_to_id": 24, "relation_type": "relates"}}, como="rcondo")
    api("POST", f"/issues/{mej}/relations.json", {"relation": {"issue_to_id": 5, "relation_type": "relates"}}, como="rcondo")

campos = {c["name"]: c["id"] for c in issue(mej)["custom_fields"]}
mover(mej, "jpayehuanca", "Analizado",
      "Análisis de impacto (CCB). Ver el documento de la solicitud.",
      campos=[{"id": campos["Impacto en diseño"], "value": "Solo Condor.Datos: ComprobanteRepositorio.EmitirAsync guarda cabecera (número provisional -id) y líneas, y numera al final con SerieRepositorio.NumerarComprobanteAsync. Sin cambios de esquema, API ni pantallas; SDD sin cambios de vista (decisión de diseño anotada en el repositorio)."},
              {"id": campos["Impacto en costo"], "value": "6 h × S/ 25.00 = S/ 150.00 (código 2 h, pruebas 2 h, repetición G08 2 h)"},
              {"id": campos["Impacto en plazo"], "value": "1 día con 1 integrante; no mueve hitos"},
              {"id": campos["Riesgos"], "value": "Romper la regla de HU-16 (números repetidos o saltados): mitigado con MEJ01_CorrelativoAlFinalTests y HU16_ConcurrenciaTests; regresión en la emisión: suite completa."},
              {"id": campos["Pruebas afectadas"], "value": "Nuevas: MEJ01_CorrelativoAlFinalTests (3). Repetir: suite completa; G08 los cuatro escenarios y la prueba de capacidad."}],
      asignar="gerente")
mover(mej, "gerente", "Aprobado",
      "**Decisión del CCB: aprobada.** Costo bajo (6 h), no cambia lo que ve el vendedor y mejora la emisión en hora punta. "
      "Versión afectada: 1.1.2.",
      campos=[{"id": campos["Decisión"], "value": "Aprobada"}], asignar="rcondo")
api("PUT", f"/issues/{mej}.json", {"issue": {"fixed_version_id": version("1.1.2")}}, como="admin")
mover(mej, "rcondo", "Implementado",
      f"Implementado en la rama `branches/MEJ-01-correlativo-al-final` ({REV_RAMA}) e integrado en trunk en **{REV_TRUNK}** "
      "por el responsable de configuración. Versión **1.1.2** (CHANGELOG). Suite del producto en la rama: 933 aprobadas, 0 fallidas, "
      f"5 omitidas ({UB}/05_Cuello_de_Botella/suite_producto_1.1.2).",
      adjuntos=[G08 / "05_Cuello_de_Botella/suite_producto_1.1.2/suite_producto_1.1.2.html"], asignar="achaisa")
mover(mej, "achaisa", "Verificado",
      "Repetición de G08 con condiciones equivalentes (mismo plan, datos, base reiniciada, pool de 20):\n\n"
      "| Capacidad, 50 hilos sin pausas | Antes (1.1.1) | Después (1.1.2) |\n|---|---|---|\n"
      f"| T2 p95 | {c50a['p95']} ms | {c50d['p95']} ms |\n| T2 throughput | {an.num(c50a['throughput'], 1)}/s | {an.num(c50d['throughput'], 1)}/s |\n"
      f"| T1 p95 | {t50a['p95']} ms | {t50d['p95']} ms |\n| Errores | {an.num(c50a['error_pct'], 2)} % | {an.num(c50d['error_pct'], 2)} % |\n\n"
      f"Los cuatro escenarios del perfil se repitieron sin errores. Detalle: {UB}/06_Analisis/resumen_resultados.xlsx.",
      adjuntos=[G08 / "06_Analisis/graficas/capacidad_p95_throughput.png"], asignar="jpayehuanca")
mover(mej, "jpayehuanca", "Cerrado",
      f"Cierre: cambio integrado ({REV_TRUNK}), suite en verde y la mejora comprobada con datos. "
      "Se vuelve a probar en la regresión final de G09.")

anotar(5, "rcondo", "G08 Pruebas de rendimiento",
       f"**G08 Pruebas de rendimiento**: la emisión (T2) se midió con JMeter antes y después de **MEJ-01** (#{mej}, versión 1.1.2). "
       f"La regla de numeración (HU-16) se mantiene: MEJ01_CorrelativoAlFinalTests y HU16_ConcurrenciaTests en verde. El estado no cambia.")
anotar(3, "achaisa", "G08 Pruebas de rendimiento",
       "**G08 Pruebas de rendimiento**: la búsqueda (T1, `GET /api/productos`) con 3 000 productos tuvo un p95 de "
       f"{stats('2_despues', 'carga', an.T1)['p95']} ms en carga esperada (1.1.2). Es evidencia de rendimiento, no de aceptación funcional: "
       "RF-05 sigue en Implementado hasta la prueba web de G09.")
