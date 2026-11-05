"""Ejecuta la suite Selenium de G09 y guarda el reporte de la ejecución.

    python ejecutar_suite.py --etiqueta 1.2.0_regresion [--patron "test_0*.py"] [--ventana]

Deja en 04_Reportes/<fecha>_<etiqueta>/:
  reporte.html     reporte legible: caso, requisitos, estado, duración, mediciones, capturas y error
  resultados.xml   formato JUnit (lo leen Jenkins, GitLab, Azure DevOps...)
  resultados.json  los mismos datos para el dictamen y la matriz de trazabilidad
  ejecucion.log    salida de unittest (verbosity=2) con las trazas de los fallos
  capturas/        evidencias de cada caso y captura automática de cada fallo
  entorno.json     versión del producto (GET /api/salud), navegador, Selenium, Python y SO

Un caso fallido hace que el comando termine con código 1: la falla se propaga
al ejecutor, no se captura ni se oculta.
"""
import argparse
import html
import io
import json
import os
import platform
import sys
import time
import unittest
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
REPORTES = RAIZ.parent / "04_Reportes"


class Resultado(unittest.TextTestResult):
    """Guarda por caso: estado, duración, mediciones, capturas y error."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.casos = []
        self._inicio = {}

    def startTest(self, test):
        self._inicio[test.id()] = time.perf_counter()
        super().startTest(test)

    def _registrar(self, test, estado, error=None):
        self.casos.append({
            "id": test.id(),
            "caso": getattr(test, "caso", ""),
            "requisitos": getattr(test, "requisitos", ""),
            "descripcion": (test._testMethodName.replace("test_", "").replace("_", " ")),
            "estado": estado,
            "segundos": round(time.perf_counter() - self._inicio.get(test.id(), time.perf_counter()), 2),
            "mediciones": getattr(test, "mediciones", {}),
            "capturas": getattr(test, "capturas", []),
            "error": self._exc_info_to_string(error, test) if error else "",
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self._registrar(test, "APROBADO")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._registrar(test, "FALLIDO", err)

    def addError(self, test, err):
        super().addError(test, err)
        self._registrar(test, "ERROR", err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._registrar(test, "OMITIDO")


def entorno(url):
    datos = {"fecha": datetime.now().isoformat(timespec="seconds"), "url": url,
             "python": platform.python_version(), "so": platform.platform()}
    try:
        import selenium
        datos["selenium"] = selenium.__version__
    except ImportError:
        pass
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/api/salud", timeout=5) as r:
            datos["producto"] = json.load(r)
    except Exception as e:  # la suite igual corre y fallará con un mensaje claro
        datos["producto"] = {"error": str(e)}
    return datos


def version_navegador():
    from comun import crear_driver
    d = crear_driver()
    try:
        caps = d.capabilities
        return {"navegador": caps.get("browserName"), "version": caps.get("browserVersion"),
                "controlador": (caps.get("chrome") or caps.get("msedge") or {}).get("chromedriverVersion", caps.get("msedge", {}).get("msedgedriverVersion", ""))}
    finally:
        d.quit()


def escribir_junit(casos, ruta, total_s):
    suite = ET.Element("testsuite", name="Condor G09 Selenium", tests=str(len(casos)),
                       failures=str(sum(c["estado"] == "FALLIDO" for c in casos)),
                       errors=str(sum(c["estado"] == "ERROR" for c in casos)),
                       skipped=str(sum(c["estado"] == "OMITIDO" for c in casos)), time=f"{total_s:.2f}")
    for c in casos:
        clase, metodo = c["id"].rsplit(".", 1)
        tc = ET.SubElement(suite, "testcase", classname=clase, name=f'{c["caso"]} {metodo}', time=str(c["segundos"]))
        if c["estado"] in ("FALLIDO", "ERROR"):
            ET.SubElement(tc, "failure" if c["estado"] == "FALLIDO" else "error",
                          message=c["error"].strip().splitlines()[-1][:300]).text = c["error"]
        elif c["estado"] == "OMITIDO":
            ET.SubElement(tc, "skipped")
        ET.SubElement(tc, "system-out").text = json.dumps({"requisitos": c["requisitos"], "mediciones": c["mediciones"],
                                                           "capturas": c["capturas"]}, ensure_ascii=False)
    ET.ElementTree(suite).write(ruta, encoding="utf-8", xml_declaration=True)


def escribir_html(casos, ent, ruta, etiqueta, total_s):
    aprobados = sum(c["estado"] == "APROBADO" for c in casos)
    color = {"APROBADO": "#2E9E4F", "FALLIDO": "#B3261E", "ERROR": "#B3261E", "OMITIDO": "#9A8F84"}
    filas = []
    for c in casos:
        med = "<br>".join(f"{html.escape(k)}: <b>{v}</b>" for k, v in c["mediciones"].items())
        caps = " ".join(f'<a href="capturas/{html.escape(n)}" target="_blank"><img src="capturas/{html.escape(n)}" alt="{html.escape(n)}" title="{html.escape(n)}"></a>' for n in c["capturas"])
        err = f'<pre>{html.escape(c["error"])}</pre>' if c["error"] else ""
        filas.append(f'<tr><td><b>{html.escape(c["caso"])}</b></td><td>{html.escape(c["descripcion"])}<div class="id">{html.escape(c["id"])}</div>{err}</td>'
                     f'<td>{html.escape(c["requisitos"])}</td><td style="color:{color[c["estado"]]};font-weight:700">{c["estado"]}</td>'
                     f'<td class="d">{c["segundos"]:.1f} s</td><td>{med}</td><td class="caps">{caps}</td></tr>')
    prod = ent.get("producto", {})
    nav = ent.get("navegador", {})
    ruta.write_text(f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>G09 Selenium · {html.escape(etiqueta)}</title>
<style>body{{font:14px Segoe UI,sans-serif;background:#EDE8DF;color:#2A221D;margin:24px}}h1{{font-family:Cambria,Georgia,serif;margin:0}}
.resumen{{display:flex;gap:12px;margin:14px 0}}.resumen div{{background:#F3EEE6;border:1px solid #DFD8CD;border-radius:6px;padding:10px 16px}}
.resumen b{{display:block;font-size:22px}}table{{border-collapse:collapse;width:100%;background:#F3EEE6}}th{{background:#E8E1D5;text-align:left}}
th,td{{padding:8px 10px;border-bottom:1px solid #DFD8CD;vertical-align:top}}.d{{text-align:right}}.id{{color:#9A8F84;font-size:11px}}
pre{{white-space:pre-wrap;background:#F8E3DE;color:#B3261E;padding:8px;font-size:11px;max-height:260px;overflow:auto}}
.caps img{{height:70px;border:1px solid #D3CBBE;margin:2px}}</style></head><body>
<h1>Suite Selenium · Sistema Cóndor</h1><div>Ejecución <b>{html.escape(etiqueta)}</b> · {html.escape(ent["fecha"])}</div>
<div class="resumen"><div>Casos<b>{len(casos)}</b></div><div>Aprobados<b style="color:#2E9E4F">{aprobados}</b></div>
<div>Fallidos / error<b style="color:#B3261E">{len(casos) - aprobados}</b></div><div>Duración<b>{total_s:.0f} s</b></div>
<div>Producto<b>{html.escape(str(prod.get("version", prod.get("error", "?"))))}</b></div>
<div>Navegador<b>{html.escape(str(nav.get("navegador", "")))} {html.escape(str(nav.get("version", "")))}</b></div>
<div>Selenium<b>{html.escape(ent.get("selenium", ""))}</b></div></div>
<p>URL: {html.escape(ent["url"])} · Python {html.escape(ent["python"])} · {html.escape(ent["so"])}</p>
<table><thead><tr><th>Caso</th><th>Descripción</th><th>Requisitos</th><th>Estado</th><th>Duración</th><th>Mediciones</th><th>Capturas</th></tr></thead>
<tbody>{"".join(filas)}</tbody></table></body></html>""", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--etiqueta", default="ejecucion")
    ap.add_argument("--patron", default="test_*.py")
    ap.add_argument("--ventana", action="store_true", help="con ventana del navegador (por defecto, headless)")
    args = ap.parse_args()

    carpeta = REPORTES / f"{datetime.now():%Y%m%d_%H%M}_{args.etiqueta}"
    carpeta.mkdir(parents=True, exist_ok=True)
    os.environ["CONDOR_CARPETA_EJECUCION"] = str(carpeta)
    if args.ventana:
        os.environ["CONDOR_HEADLESS"] = "0"
    sys.path.insert(0, str(RAIZ))
    from comun import URL

    ent = entorno(URL)
    try:
        ent["navegador"] = version_navegador()
    except Exception as e:
        ent["navegador"] = {"error": str(e)}
    (carpeta / "entorno.json").write_text(json.dumps(ent, indent=2, ensure_ascii=False), encoding="utf-8")

    suite = unittest.defaultTestLoader.discover(str(RAIZ), pattern=args.patron, top_level_dir=str(RAIZ))
    salida = io.StringIO()

    class Doble(io.TextIOBase):
        def write(self, s):
            sys.stdout.write(s)
            salida.write(s)
            return len(s)

    ejecutor = unittest.TextTestRunner(stream=Doble(), verbosity=2, resultclass=Resultado)
    inicio = time.perf_counter()
    resultado = ejecutor.run(suite)
    total = time.perf_counter() - inicio
    (carpeta / "ejecucion.log").write_text(salida.getvalue(), encoding="utf-8")

    casos = sorted(resultado.casos, key=lambda c: c["caso"])
    (carpeta / "resultados.json").write_text(json.dumps({"etiqueta": args.etiqueta, "entorno": ent, "segundos": round(total, 1),
                                                         "casos": casos}, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_junit(casos, carpeta / "resultados.xml", total)
    escribir_html(casos, ent, carpeta / "reporte.html", args.etiqueta, total)
    print(f"\nReporte: {carpeta / 'reporte.html'}")
    sys.exit(0 if resultado.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
