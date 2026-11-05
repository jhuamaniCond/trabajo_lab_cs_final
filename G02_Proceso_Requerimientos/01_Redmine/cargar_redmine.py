"""Carga en Redmine los requisitos de la ERS y las solicitudes CC-01 y CC-02,
y los hace recorrer el flujo con el usuario que tiene el rol de cada transición.

    python cargar_redmine.py http://localhost:3010 <clave API del admin>

Requisitos: haber ejecutado configurar_redmine.rb. Fuente de los requisitos:
G01_Requerimientos/03_REMUS/condor_datos.json. Evidencia de las pruebas:
04_Pruebas/*.trx (suite ejecutada sobre el producto 1.1.0).

Cada operación se hace con la clave del administrador y la cabecera
X-Redmine-Switch-User, de modo que el historial muestra al integrante que
realizó cada transición y Redmine aplica el flujo de su rol.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
G02 = AQUI.parent
DATOS = G02.parent / "G01_Requerimientos" / "03_REMUS" / "condor_datos.json"
PRUEBAS = G02 / "04_Pruebas"
URL, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]

ANALISTAS = ["jhuamani", "jpayehuanca", "rcondo", "achaisa"]
NUEVOS_CC01 = {"RF-02", "RF-03", "RF-15", "RNF-02", "RNF-03"}
TRAZADOS = ["RF-01", "RF-03", "RF-07", "RF-08", "RF-15"]  # los cinco que llegan a Cerrado
RF01_V10 = ("Acceder con el perfil único MAESTRO",
            "El sistema deberá abrir directamente la pantalla Nueva venta con el perfil único MAESTRO, "
            "sin pedir usuario ni contraseña, y registrar en cada comprobante la terminal desde donde se emitió (HU-14).",
            ["Al abrir el programa se muestra Nueva venta sin ventana de ingreso.",
             "Cada comprobante guarda usuario = MAESTRO y el nombre de la terminal."])


# --- API ------------------------------------------------------------------------
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


def ids(ruta, clave, campo="name"):
    return {x[campo]: x["id"] for x in api("GET", ruta)[clave]}


TIPO = ids("/trackers.json", "trackers")
ESTADO = ids("/issue_statuses.json", "issue_statuses")
PRIORIDAD = ids("/enumerations/issue_priorities.json", "issue_priorities")
CAMPO = ids("/custom_fields.json", "custom_fields")
VERSION = ids("/projects/condor/versions.json", "versions")
USUARIO = ids("/users.json?limit=100", "users", "login")


def cf(**valores):
    nombres = {"id_ers": "ID ERS", "tipo": "Tipo de requisito", "fuente": "Fuente",
               "criterio": "Criterio de aceptación", "pruebas": "Pruebas vinculadas",
               "id_cambio": "ID cambio", "motivo": "Motivo", "diseno": "Impacto en diseño",
               "costo": "Impacto en costo", "plazo": "Impacto en plazo", "riesgos": "Riesgos",
               "pruebas_af": "Pruebas afectadas", "decision": "Decisión"}
    return [{"id": CAMPO[nombres[k]], "value": v} for k, v in valores.items()]


def crear(como, tipo, asunto, descripcion, prioridad, asignado, campos):
    issue = {"project_id": "condor", "tracker_id": TIPO[tipo], "subject": asunto,
             "description": descripcion, "priority_id": PRIORIDAD[prioridad],
             "fixed_version_id": VERSION["1.1.0"], "assigned_to_id": USUARIO[asignado],
             "custom_fields": campos}
    return api("POST", "/issues.json", {"issue": issue}, como)["issue"]["id"]


def subir(ruta, como):
    token = api("POST", f"/uploads.json?filename={ruta.name}", como=como,
                binario=ruta.read_bytes())["upload"]["token"]
    tipo = "text/html" if ruta.suffix == ".html" else "application/xml"
    return {"token": token, "filename": ruta.name, "content_type": tipo}


def mover(n, como, estado, nota, asignado=None, campos=None, adjuntos=()):
    issue = {"status_id": ESTADO[estado], "notes": nota}
    if asignado:
        issue["assigned_to_id"] = USUARIO[asignado]
    if campos:
        issue["custom_fields"] = campos
    if adjuntos:
        issue["uploads"] = [subir(a, como) for a in adjuntos]
    api("PUT", f"/issues/{n}.json", {"issue": issue}, como)
    actual = api("GET", f"/issues/{n}.json")["issue"]["status"]["name"]
    if actual != estado:
        raise SystemExit(f"#{n}: se esperaba {estado} y quedó {actual} (¿transición no permitida para {como}?)")


def relacionar(a, b, como, tipo="relates"):
    api("POST", f"/issues/{a}/relations.json", {"relation": {"issue_to_id": b, "relation_type": tipo}}, como)


# --- Evidencia de pruebas (TRX) ---------------------------------------------------
def resultados(trx):
    ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
    raiz = ET.parse(PRUEBAS / trx).getroot()
    clases = Counter()
    for r in raiz.iterfind(".//t:UnitTestResult", ns):
        clase = r.get("testName").split("(")[0].rsplit(".", 1)[0].replace("Condor.Pruebas.", "")
        clases[(clase, r.get("outcome"))] += 1
    return clases


SUITE = resultados("suite_completa_v1.1.0.trx")


def evidencia(pruebas):
    """Resume, por clase de prueba vinculada, cuántos casos pasaron en la suite 1.1.0."""
    filas = []
    for p in pruebas:
        if ":" in p:                  # prueba prevista en otra guía (G06, G08, G09)
            continue
        base = p.split(" ")[0].replace("/", ".").rstrip("*").rstrip(".")
        if not base.endswith("Tests"):
            base += "Tests"
        ok = sum(n for (c, o), n in SUITE.items() if c.startswith(base) and o == "Passed")
        mal = sum(n for (c, o), n in SUITE.items() if c.startswith(base) and o == "Failed")
        if ok or mal:
            filas.append(f"| `{base}` | {ok} | {mal} |")
    return filas


# --- Datos de la ERS -------------------------------------------------------------
d = json.loads(DATOS.read_text(encoding="utf-8"))
PART = {p["id"]: p["nombre"] for p in d["participantes"]}
PRIO = {"vital": "Alta", "importante": "Media"}
REQ = {}
for u in d["casosUso"]:
    REQ[u["codigo"]] = dict(tipo="Funcional", nombre=u["nombre"], desc=f"El sistema deberá {u['descripcion']}.",
                            crit=u["criterios"], pruebas=u["pruebas"], fuentes=u["fuentes"],
                            tecnicas=u.get("tecnicas", []), prio=PRIO[u["importancia"]], origen=u.get("hu", ""))
for n in d["noFuncionales"]:
    REQ[n["codigo"]] = dict(tipo="No funcional", nombre=n["nombre"], desc=f"El sistema deberá {n['descripcion']}.",
                            crit=n["criterios"], pruebas=n["pruebas"], fuentes=n["fuentes"],
                            tecnicas=n.get("tecnicas", []), prio=PRIO[n["importancia"]],
                            origen=f"{n['atributo']} · meta: {n['meta']}")


def lista(xs, pref="CA"):
    return "\n".join(f"- **{pref}-{i}** {x}" for i, x in enumerate(xs, 1))


def fuente(r):
    return ", ".join(PART[f] for f in r["fuentes"]) + (f" ({', '.join(r['tecnicas'])})" if r["tecnicas"] else "")


def descripcion(codigo, r, desc=None):
    return (f"{desc or r['desc']}\n\n**Origen:** {r['origen']}\n\n"
            f"Fuente en la ERS: `G01_Requerimientos/01_ERS/ERS_Condor_v1.1.md` · REMUS: `condor.rem`")


def campos_req(codigo, r, crit=None):
    return cf(id_ers=codigo, tipo=r["tipo"], fuente=fuente(r), criterio=lista(crit or r["crit"]),
              pruebas="\n".join(f"- {p}" for p in r["pruebas"]))


orden = sorted(REQ, key=lambda c: (c.startswith("RNF"), int(c.split("-")[1])))
issue = {}


def registrar_y_aprobar(codigo, i, nota_aprobacion, asunto=None, desc=None, crit=None):
    r = REQ[codigo]
    analista = ANALISTAS[i % 4]
    n = crear(analista, "Requisito", f"{codigo} {asunto or r['nombre']}", descripcion(codigo, r, desc),
              r["prio"], analista, campos_req(codigo, r, crit))
    mover(n, analista, "Analizado",
          f"Análisis: requisito claro, consistente con el glosario y verificable "
          f"({len(crit or r['crit'])} criterio(s) de aceptación). Revisión con la lista de "
          f"`G01_Requerimientos/07_Revision/lista_revision.md`.", asignado="gerente")
    mover(n, "gerente", "Aprobado", nota_aprobacion, asignado=ANALISTAS[(i + 1) % 4])
    issue[codigo] = n
    return n


# 1) Línea base 1.0 (ERS del 2026-10-29): 19 requisitos, RF-01 con el perfil MAESTRO.
print("Línea base 1.0")
for i, codigo in enumerate(c for c in orden if c not in NUEVOS_CC01):
    if codigo == "RF-01":
        registrar_y_aprobar(codigo, i, "Aprobado por el CCB en la línea base **ERS 1.0** (2026-10-29).",
                            asunto=RF01_V10[0], desc=RF01_V10[1], crit=RF01_V10[2])
    else:
        registrar_y_aprobar(codigo, i, "Aprobado por el CCB en la línea base **ERS 1.0** (2026-10-29).")

# 2) CC-01: registro, análisis de impacto y aprobación.
print("CC-01")
CC = "G02_Proceso_Requerimientos/03_Solicitudes_Cambio/"
cc01 = crear("gerente", "Solicitud de cambio", "CC-01 Ingreso con usuario, contraseña y roles; backend REST",
             "Reemplazar el perfil único MAESTRO sin credenciales (RF-01 de la ERS 1.0, HU-14) por ingreso con "
             "usuario y contraseña, dos roles (Vendedor y Encargado general) y un backend REST con reporte "
             f"consolidado de ventas.\n\nDocumento completo: `{CC}CC-01_ingreso_con_roles.md`",
             "Alta", "jpayehuanca",
             cf(id_cambio="CC-01",
                motivo="El gerente necesita saber quién emitió cada comprobante y que los vendedores no vean "
                       "costos ni respaldos (ENT-01 A5, CFL-06). El curso exige autenticación, roles, reporte "
                       "consolidado y rutas HTTP para JMeter."))
mover(cc01, "jpayehuanca", "Analizado",
      "Análisis de impacto completo en los campos de la solicitud y en "
      f"`{CC}CC-01_ingreso_con_roles.md` (requisitos, diseño, costo, plazo, riesgos y pruebas).",
      asignado="gerente",
      campos=cf(diseno="Migración V014 (usuario, acceso_usuario); Condor.Dominio.Seguridad; nuevo backend "
                       "Condor.Api (JWT, política Encargado); nuevo Condor.ClienteApi; ventana Ingresar y permisos "
                       "por rol. Arquitectura cliente – API – base. Requisitos: RF-01 reescrito, RF-07 ampliado, "
                       "RF-02, RF-03, RF-15, RNF-02 y RNF-03 nuevos.",
                costo="56 h × S/ 25.00 = S/ 1 400.00",
                plazo="≈ 4 días hábiles con 4 integrantes; se absorbe en el incremento 1, no mueve el hito del 11-11-2026",
                riesgos="Venta más lenta en hora punta (mitigado: sesión de 480 min por turno); caída de la API "
                        "detiene la venta (pasa a G06); exposición de contraseñas (PBKDF2, bloqueo); regresión en "
                        "la emisión (suite completa).",
                pruebas_af="Nuevas: HashClaveTests, ServicioAutenticacionTests, ReporteVentasTests, "
                           "LoginViewModelTests, CC01_IngresoConRolesTests, ApiTests, ClienteApiTests, "
                           "UsuarioRepositorioTests. Repetir: suite completa. Previstas: G08 y G09."))
mover(cc01, "gerente", "Aprobado",
      "**Decisión del CCB: aprobada.** Necesidad del cliente y exigencia del curso; costo moderado (56 h) y sin "
      "mover el hito. Versión objetivo: **1.1.0**; línea base resultante: **ERS 1.1**.",
      asignado="jhuamani", campos=cf(decision="Aprobada"))
relacionar(cc01, issue["RF-01"], "jpayehuanca")
relacionar(cc01, issue["RF-07"], "jpayehuanca")

# 3) Aplicación de CC-01 a la línea base: RF-01 reescrito, RF-07 ampliado y 5 requisitos nuevos.
print("ERS 1.1")
r = REQ["RF-01"]
api("PUT", f"/issues/{issue['RF-01']}.json", {"issue": {
    "subject": f"RF-01 {r['nombre']}", "description": descripcion("RF-01", r), "custom_fields": campos_req("RF-01", r),
    "notes": f"Requisito reescrito por **CC-01** (#{cc01}): de «{RF01_V10[0]}» a «{r['nombre']}». "
             "Queda en la ERS 1.1 (apéndice B)."}}, "jhuamani")
api("PUT", f"/issues/{issue['RF-07']}.json", {"issue": {
    "custom_fields": campos_req("RF-07", REQ["RF-07"]),
    "notes": f"Se agrega el criterio CA-5 por **CC-01** (#{cc01}): el comprobante guarda el usuario de la sesión "
             "(CRQ-11). ERS 1.1."}}, "jhuamani")
for i, codigo in enumerate(c for c in orden if c in NUEVOS_CC01):
    n = registrar_y_aprobar(codigo, i, f"Aprobado por el CCB como parte de **CC-01** (#{cc01}); "
                                       "entra en la línea base **ERS 1.1** (2026-10-30).")
    relacionar(cc01, n, "jhuamani")

# 4) Implementación en la versión 1.1.0 del producto.
print("Implementación")
CODIGO = {
    "RF-01": "`Condor.Dominio/Seguridad/ServicioAutenticacion.cs`, `HashClave`, `Condor.Presentacion/ViewModels/LoginViewModel.cs`, "
             "`Condor.Escritorio/Vistas/LoginWindow.xaml`, ruta `POST /api/ingreso`, migración V014.",
    "RF-03": "`Condor.Dominio/Seguridad/Roles.cs`, `Condor.Presentacion/ViewModels/PermisosModulo.cs`, "
             "política `Encargado` en `Condor.Api/Endpoints.cs`.",
    "RF-07": "`Condor.Dominio/Ventas/EmisionComprobante.cs`, `CalculadoraVenta.cs`, "
             "`POST /api/escritorio/comprobantes` (usuario tomado del token).",
    "RF-08": "`EmisionComprobante` (conversión), `Condor.Presentacion/ViewModels/ProformasViewModel.cs`, "
             "migración V011 (`proforma_id`, trigger `ck_proforma`).",
    "RF-15": "`Condor.Dominio/Reportes/ReporteVentas.cs`, `Condor.Datos/ReporteVentasRepositorio.cs`, "
             "ruta `GET /api/reportes/ventas` (solo Encargado).",
}
for i, codigo in enumerate(orden):
    dev = ANALISTAS[(i + 1) % 4]
    detalle = CODIGO.get(codigo, f"origen {REQ[codigo]['origen']}")
    mover(issue[codigo], dev, "Implementado",
          f"Implementado en la versión **1.1.0** del producto (`Sistema_Logistico_Condor_final`, CHANGELOG). "
          f"Código: {detalle}", asignado=ANALISTAS[(i + 2) % 4])
mover(cc01, "jhuamani", "Implementado",
      "Implementado en la versión **1.1.0**: ERS 1.1 y REMUS regenerado; diseño en `docs/seguridad.md`, "
      "`docs/api.md` y `docs/modelo_datos.md` (este último corregido al cerrar el cambio: seguía diciendo «usuario "
      "siempre MAESTRO»); código V014, Condor.Api, Condor.ClienteApi, LoginWindow y PermisosModulo; pruebas nuevas "
      "listadas en *Pruebas afectadas*.", asignado="rcondo")

# 5) Verificación y cierre de CC-01 con la regresión.
reg = resultados("regresion_CC-01.trx")
ok = sum(n for (_, o), n in reg.items() if o == "Passed")
mal = sum(n for (_, o), n in reg.items() if o == "Failed")
mover(cc01, "rcondo", "Verificado",
      f"Regresión de las pruebas afectadas por CC-01 sobre la versión 1.1.0, con PostgreSQL: **{ok} aprobadas, "
      f"{mal} fallidas**. Se adjunta el reporte. Comando en `{CC}CC-01_ingreso_con_roles.md`.",
      asignado="gerente", adjuntos=[PRUEBAS / "regresion_CC-01.html"])
mover(cc01, "gerente", "Cerrado",
      "Cierre: ERS 1.1, diseño, código y pruebas actualizados y la regresión en verde. Pendiente para G05: "
      "registrar la versión 1.1.0 en SVN y etiquetarla.")

# 6) Verificación y cierre de los cinco requisitos trazados.
print("Verificación de los cinco requisitos")
total_ok = sum(n for (_, o), n in SUITE.items() if o == "Passed")
total_mal = sum(n for (_, o), n in SUITE.items() if o == "Failed")
total_omit = sum(n for (_, o), n in SUITE.items() if o == "NotExecuted")
# Quien implementa un requisito no lo verifica ni lo cierra.
evaluadores = {"RF-01": "rcondo", "RF-03": "rcondo", "RF-07": "rcondo", "RF-08": "achaisa", "RF-15": "jpayehuanca"}
cierres = {"RF-01": "jhuamani", "RF-03": "jhuamani", "RF-07": "jhuamani", "RF-08": "jpayehuanca", "RF-15": "jpayehuanca"}
for codigo in TRAZADOS:
    filas = evidencia(REQ[codigo]["pruebas"])
    mover(issue[codigo], evaluadores[codigo], "Verificado",
          f"Verificado contra sus criterios de aceptación con la suite automatizada sobre la versión 1.1.0 "
          f"(`04_Pruebas/suite_completa_v1.1.0.trx`; suite completa: {total_ok} aprobadas, {total_mal} fallidas, "
          f"{total_omit} omitidas).\n\n| Clase de prueba vinculada | Aprobadas | Fallidas |\n|---|---|---|\n"
          + "\n".join(filas), asignado=cierres[codigo],
          adjuntos=[PRUEBAS / "suite_completa_v1.1.0.html"] if codigo == "RF-01" else ())
    mover(issue[codigo], cierres[codigo], "Cerrado",
          "Cierre: trazabilidad completa (fuente → ERS 1.1 → código 1.1.0 → pruebas en verde). Las pruebas "
          "previstas en G08/G09 se agregarán a la matriz de trazabilidad final.")

# 7) CC-02: registro, análisis y rechazo.
print("CC-02")
cc02 = crear("achaisa", "Solicitud de cambio", "CC-02 Descuento manual del vendedor en la línea de venta",
             "Permitir que el vendedor aplique hasta un 10 % de descuento a cada línea de la venta, con motivo; "
             "el sistema recalcularía operación gravada e IGV.\n\n"
             f"Documento completo: `{CC}CC-02_descuento_en_venta.md`",
             "Media", "rcondo",
             cf(id_cambio="CC-02",
                motivo="El 75 % de los vendedores pide poder cambiar el precio para hacer descuentos (CUE-01, P12); "
                       "hoy rebajan «a ojo» (ENT-01 B9). CFL-03 lo dejó como posible cambio futuro."))
mover(cc02, "rcondo", "Analizado",
      f"Análisis de impacto completo en los campos y en `{CC}CC-02_descuento_en_venta.md`.", asignado="gerente",
      campos=cf(diseno="Contradice CRQ-07 y reabre CFL-03. Migración V015 (descuento por línea); CalculadoraVenta, "
                       "EmisionComprobante y ReporteVentas; XML UBL con cac:AllowanceCharge (catálogo 53); ticket; "
                       "API acepta descuento de la terminal; columna editable en la venta.",
                costo="38 h × S/ 25.00 = S/ 950.00",
                plazo="≈ 3 días hábiles; cae en el incremento 2 y obliga a repetir las líneas base de G07 y G08; "
                      "riesgo para el hito del 25-11-2026",
                riesgos="Alto: pérdida de margen o fraude. Alto: rechazo SUNAT por XML de descuentos. Medio: "
                        "regresión en el cálculo del IGV (CRQ-01). Medio: contradice CRQ-07 y CFL-03.",
                pruebas_af="CalculadoraVentaTests, EmisionComprobanteTests, HU05, HU06, HU08, HU09, Sunat/*, "
                           "FormatoTicketTests, ReporteVentasTests, ApiTests; G08 emitir boleta; G09 registro válido."))
mover(cc02, "gerente", "Rechazado",
      "**Decisión del CCB: rechazada.** 1) Contradice CRQ-07 y la resolución de CFL-03: los precios los fija solo "
      "el catálogo. 2) Dos riesgos altos sin mitigación en esta versión. 3) Costo y plazo comprometen el hito del "
      "25-11-2026. **Alternativa:** el Encargado general actualiza el precio en el catálogo (RF-04) para promociones. "
      "Se reevaluará después de la 1.0.0 como descuento autorizado por el Encargado. La línea base sigue siendo la "
      "ERS 1.1.", campos=cf(decision="Rechazada"))
relacionar(cc02, issue["RF-07"], "rcondo")

print(f"Listo: {len(issue)} requisitos, CC-01 #{cc01}, CC-02 #{cc02}")
