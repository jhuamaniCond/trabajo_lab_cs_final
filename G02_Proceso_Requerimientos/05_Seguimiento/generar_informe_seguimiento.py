"""Genera informe_seguimiento.md con los datos que devuelve Redmine
(estados, historial de transiciones, responsables y evidencia).

    python generar_informe_seguimiento.py http://localhost:3010 <clave API>
"""
import json
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]
AQUI = Path(__file__).resolve().parent
LIMA = timezone(timedelta(hours=-5))
TRAZADOS = ["RF-01", "RF-03", "RF-07", "RF-08", "RF-15"]
ROL = {("Registrado", "Analizado"): "Analista", ("Analizado", "Aprobado"): "CCB",
       ("Analizado", "Rechazado"): "CCB", ("Aprobado", "Implementado"): "Desarrollador",
       ("Implementado", "Verificado"): "Evaluador de calidad", ("Verificado", "Cerrado"): "CCB",
       ("Verificado", "Implementado"): "Evaluador de calidad"}
VERIFICACION = {  # guía donde se verificarán los requisitos que quedan en Implementado
    "RF-02": "G09 (cierre de sesión)", "RF-04": "G07, G09", "RF-05": "G07, G08, G09", "RF-06": "G07, G09",
    "RF-09": "G07", "RF-10": "G07", "RF-11": "G07", "RF-12": "G07", "RF-13": "G07", "RF-14": "G07, G09",
    "RF-16": "G06, G07", "RNF-01": "G07", "RNF-02": "G08", "RNF-03": "G06, G07", "RNF-04": "G07",
    "RNF-05": "G07", "RNF-06": "G09 (cronometrado)", "RNF-07": "G06, G07", "RNF-08": "G07 (cobertura)",
}


def get(ruta):
    req = urllib.request.Request(URL + ruta, headers={"X-Redmine-API-Key": CLAVE})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def fecha(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(LIMA).strftime("%d/%m/%Y %H:%M")


def campo(issue, nombre):
    return next((c.get("value") or "" for c in issue.get("custom_fields", []) if c["name"] == nombre), "")


def resumen_nota(nota):
    nota = re.sub(r"\n\|.*", "", nota or "", flags=re.S).strip()   # sin la tabla de pruebas
    nota = re.sub(r"\s+", " ", nota.replace("**", "").replace("`", ""))
    return nota if len(nota) <= 230 else nota[:227].rsplit(" ", 1)[0] + "…"


estados = {s["id"]: s["name"] for s in get("/issue_statuses.json")["issue_statuses"]}
peticiones = get("/projects/condor/issues.json?status_id=*&limit=100&sort=id")["issues"]
detalle = {p["id"]: get(f"/issues/{p['id']}.json?include=journals,relations,attachments")["issue"]
           for p in peticiones}
por_ers = {campo(i, "ID ERS") or campo(i, "ID cambio"): i for i in detalle.values()}
reqs = [i for i in detalle.values() if i["tracker"]["name"] == "Requisito"]
ccs = [i for i in detalle.values() if i["tracker"]["name"] == "Solicitud de cambio"]

L = []
w = L.append
w("# Informe de seguimiento de requisitos y cambios")
w("")
w("| Campo | Valor |")
w("|---|---|")
w("| Herramienta | Redmine 7.0.1 (contenedor `redmine-condor`, http://localhost:3010), proyecto «Sistema Cóndor» |")
w(f"| Fecha del corte | {datetime.now(LIMA).strftime('%d/%m/%Y %H:%M')} (hora de Lima) |")
w("| Línea base | ERS 1.1 · producto 1.1.0 |")
w(f"| Peticiones | {len(reqs)} requisitos y {len(ccs)} solicitudes de cambio |")
w("| Fuente de los datos | API REST de Redmine; generado con `generar_informe_seguimiento.py` |")
w("")

# 1. Estado general
w("## 1. Estado de los requisitos y cambios")
w("")
orden_estados = ["Registrado", "Analizado", "Aprobado", "Rechazado", "Implementado", "Verificado", "Cerrado"]
cnt = Counter((i["tracker"]["name"], i["status"]["name"]) for i in detalle.values())
w("| Tipo | " + " | ".join(orden_estados) + " | Total |")
w("|---|" + "---|" * (len(orden_estados) + 1))
for t in ["Requisito", "Solicitud de cambio"]:
    fila = [cnt[(t, e)] for e in orden_estados]
    w(f"| {t} | " + " | ".join(str(n) if n else "·" for n in fila) + f" | {sum(fila)} |")
w("")
rf = sum(1 for i in reqs if campo(i, "Tipo de requisito") == "Funcional")
w(f"De los {len(reqs)} requisitos ({rf} RF y {len(reqs) - rf} RNF), **{cnt[('Requisito', 'Cerrado')]} están cerrados** "
  f"(recorrieron el flujo completo con evidencia de pruebas) y **{cnt[('Requisito', 'Implementado')]} están "
  "implementados** en la versión 1.1.0 a la espera de la verificación que harán G06, G07, G08 y G09 (sección 4). "
  "Ningún requisito quedó sin implementar.")
w("")
prio = Counter(i["priority"]["name"] for i in reqs)
w(f"Por prioridad: Alta {prio['Alta']}, Media {prio['Media']}. Reportes de la herramienta: "
  "`01_Redmine/capturas/19_informe_resumen.png` (por tipo, prioridad, asignado, autor y versión), "
  "`20_informe_estado_por_tipo.png`, `21_informe_por_asignado.png` y `22_hoja_de_ruta_1.1.0.png`.")
w("")

# 2. Recorrido de los cinco requisitos
w("## 2. Recorrido de los cinco requisitos gestionados en el flujo completo")
w("")
w("Cada fila es una transición registrada en el historial de Redmine: fecha, usuario que la hizo (con su rol en el "
  "flujo) y la evidencia anotada. Capturas: `01_Redmine/capturas/12_historial_RF-01.png` a `16_historial_RF-15.png`; "
  "exportación PDF de cada petición en `01_Redmine/exportaciones/`.")
for codigo in TRAZADOS:
    i = por_ers[codigo]
    w("")
    w(f"### {i['subject']} (petición #{i['id']}, prioridad {i['priority']['name']}, estado {i['status']['name']})")
    w("")
    w("| Fecha | Transición | Responsable (rol) | Evidencia |")
    w("|---|---|---|---|")
    w(f"| {fecha(i['created_on'])} | Alta → Registrado | {i['author']['name']} (Analista) | "
      f"Registrado desde la ERS (`ID ERS` = {codigo}, fuente: {campo(i, 'Fuente')}) |")
    for j in i["journals"]:
        cambios = {d["name"]: d for d in j["details"]}
        if "status_id" in cambios:
            de = estados[int(cambios["status_id"]["old_value"])]
            a = estados[int(cambios["status_id"]["new_value"])]
            ev = resumen_nota(j["notes"])
            adj = [d["new_value"] for d in j["details"] if d["property"] == "attachment"]
            if adj:
                ev += f" Adjunto: `{adj[0]}`."
            w(f"| {fecha(j['created_on'])} | {de} → {a} | {j['user']['name']} ({ROL[(de, a)]}) | {ev} |")
        elif "subject" in cambios or "description" in cambios or any(
                d["property"] == "cf" for d in j["details"]):
            if j["notes"]:
                w(f"| {fecha(j['created_on'])} | (modificación) | {j['user']['name']} (Analista) | "
                  f"{resumen_nota(j['notes'])} |")
w("")

# 3. Solicitudes de cambio
w("## 3. Solicitudes de cambio")
w("")
w("| ID | Petición | Solicitante | Estado | Decisión | Versión | Impacto en costo | Impacto en plazo | Requisitos relacionados |")
w("|---|---|---|---|---|---|---|---|---|")
for i in ccs:
    rel = sorted(campo(detalle[r["issue_id"] if r["issue_id"] != i["id"] else r["issue_to_id"]], "ID ERS")
                 for r in i.get("relations", []))
    version = i["fixed_version"]["name"] if i["status"]["name"] != "Rechazado" else "— (sigue la 1.1.0)"
    w(f"| {campo(i, 'ID cambio')} | #{i['id']} | {i['author']['name']} | {i['status']['name']} | "
      f"{campo(i, 'Decisión')} | {version} | {campo(i, 'Impacto en costo')} | {campo(i, 'Impacto en plazo')} | "
      f"{', '.join(rel)} |")
w("")
for i in ccs:
    w(f"**{campo(i, 'ID cambio')}** — historial:")
    w("")
    w("| Fecha | Transición | Responsable | Nota |")
    w("|---|---|---|---|")
    w(f"| {fecha(i['created_on'])} | Alta → Registrado | {i['author']['name']} | {resumen_nota(campo(i, 'Motivo'))} |")
    for j in i["journals"]:
        cambios = {d["name"]: d for d in j["details"]}
        if "status_id" in cambios:
            de = estados[int(cambios["status_id"]["old_value"])]
            a = estados[int(cambios["status_id"]["new_value"])]
            w(f"| {fecha(j['created_on'])} | {de} → {a} | {j['user']['name']} ({ROL[(de, a)]}) | "
              f"{resumen_nota(j['notes'])} |")
    w("")
w("El análisis de impacto completo (requisitos, diseño, costo, plazo, riesgos y pruebas) está en "
  "`03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md` y `03_Solicitudes_Cambio/CC-02_descuento_en_venta.md`.")
w("")

# 4. Pendientes
w("## 4. Requisitos pendientes de verificación")
w("")
w("| Requisito | Petición | Estado | Asignado a (evaluador) | Se verificará en |")
w("|---|---|---|---|---|")
for i in sorted(reqs, key=lambda x: (campo(x, "ID ERS").startswith("RNF"), int(campo(x, "ID ERS").split("-")[1]))):
    c = campo(i, "ID ERS")
    if i["status"]["name"] != "Cerrado":
        w(f"| {i['subject']} | #{i['id']} | {i['status']['name']} | {i.get('assigned_to', {}).get('name', '—')} | "
          f"{VERIFICACION.get(c, '—')} |")
w("")
w("Estos requisitos ya tienen pruebas automatizadas en el producto (ERS 1.1, sección 6.2) y la suite 1.1.0 pasa "
  "completa, pero se cerrarán en Redmine cuando cada guía aporte su evidencia propia (catálogo de casos de G07, "
  "resultados JMeter de G08, suite Selenium de G09 y controles de G06). El flujo los mueve a Verificado y Cerrado "
  "en ese momento.")
w("")

# 5. Indicadores
w("## 5. Indicadores de seguimiento")
w("")
cerrados = [i for i in reqs if i["status"]["name"] == "Cerrado"]
w("| Indicador | Valor |")
w("|---|---|")
w(f"| Requisitos cerrados / total | {len(cerrados)} / {len(reqs)} ({100 * len(cerrados) / len(reqs):.0f} %) |")
w(f"| Requisitos implementados o más avanzados | {sum(1 for i in reqs if i['status']['name'] in ('Implementado', 'Verificado', 'Cerrado'))} / {len(reqs)} |")
w(f"| Solicitudes de cambio | {len(ccs)}: {sum(1 for i in ccs if campo(i, 'Decisión') == 'Aprobada')} aprobada(s) e "
  f"implementada(s), {sum(1 for i in ccs if campo(i, 'Decisión') == 'Rechazada')} rechazada(s) |")
afectados = sum(1 for i in reqs if any(campo(c, "ID cambio") == "CC-01" for c in ccs
                                       for r in c.get("relations", []) if i["id"] in (r["issue_id"], r["issue_to_id"])))
w(f"| Requisitos afectados por CC-01 | {afectados} de {len(reqs)} ({100 * afectados / len(reqs):.0f} % de la línea base) |")
w("| Pruebas de la versión 1.1.0 | 923 aprobadas, 0 fallidas, 5 omitidas (`04_Pruebas/suite_completa_v1.1.0.trx`) |")
w("| Regresión de CC-01 | 130 aprobadas, 0 fallidas (`04_Pruebas/regresion_CC-01.trx`) |")
w("| Esfuerzo estimado de los cambios analizados | CC-01: 56 h (S/ 1 400.00); CC-02: 38 h (S/ 950.00, no ejecutado) |")
w("")
w("**Limitación:** todas las transiciones se registraron en Redmine el 30/10/2026, cuando se configuró la "
  "herramienta, a partir de la línea base 1.0 (29/10/2026) y de la versión 1.1.0 ya construida. Las fechas del "
  "historial son las reales del registro, no se ajustaron hacia atrás. Las transiciones que hagan G06 a G09 "
  "quedarán con su propia fecha.")

(AQUI / "informe_seguimiento.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("informe_seguimiento.md generado")
