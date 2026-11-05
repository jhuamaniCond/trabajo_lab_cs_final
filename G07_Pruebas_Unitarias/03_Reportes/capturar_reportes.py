"""Captura en Chrome (sin ventana) los reportes HTML de G07 como evidencia.

    python 03_Reportes/capturar_reportes.py        (desde G07_Pruebas_Unitarias)

Abre los reportes de ejecución de xUnit (logger html de VSTest) con todas las
secciones desplegadas y los reportes de cobertura de ReportGenerator, y guarda
capturas de página completa en la carpeta capturas/ de cada sección.
Requiere: Python 3, selenium 4 y Google Chrome.
"""
import base64
from pathlib import Path

from selenium import webdriver

G07 = Path(__file__).resolve().parents[1]

CAPTURAS = [
    # (carpeta de salida, nombre, archivo html, ancho[, modo]); modo "linea:N" recorta alrededor de la línea N
    # del código fuente y "resumen" deja plegada la lista de resultados (la suite del producto tiene 935 filas)
    ("03_Reportes/capturas", "01_ejecucion_v1.1.1_43_aprobadas", "03_Reportes/ejecucion_v1.1.1/ejecucion_v1.1.1.html", 1500),
    ("03_Reportes/capturas", "02_cobertura_suite_G07_resumen", "03_Reportes/ejecucion_v1.1.1/cobertura/index.html", 1500),
    ("03_Reportes/capturas", "03_cobertura_G07_EmisionComprobante", "03_Reportes/ejecucion_v1.1.1/cobertura/Condor.Dominio_EmisionComprobante.html", 1500, "linea:132"),
    ("03_Reportes/capturas", "04_cobertura_paquete_Condor.Dominio_RNF-08", "03_Reportes/cobertura_RNF-08/cobertura/index.html", 1500),
    ("03_Reportes/capturas", "05_ejecucion_suite_producto_930_aprobadas", "03_Reportes/cobertura_RNF-08/cobertura_RNF-08_suite_producto.html", 1500, "resumen"),
    ("04_Defecto_Controlado/capturas", "01_DEF-02_con_defecto_PU-13_falla", "04_Defecto_Controlado/1_con_defecto/DEF-02_con_defecto.html", 1500),
    ("04_Defecto_Controlado/capturas", "02_DEF-02_linea_inyectada_en_cobertura", "04_Defecto_Controlado/1_con_defecto/cobertura/Condor.Dominio_EmisionComprobante.html", 1500, "linea:132"),
    ("04_Defecto_Controlado/capturas", "03_DEF-02_restaurado_43_aprobadas", "04_Defecto_Controlado/2_restaurado/DEF-02_restaurado.html", 1500),
    ("05_Regresion/capturas", "01_R1_producto_1.0.0_antes_CC-01", "05_Regresion/R1_producto_1.0.0_antes_CC-01/R1_producto_1.0.0_antes_CC-01.html", 1500),
    ("05_Regresion/capturas", "02_R2_producto_1.1.1_despues_CC-01", "05_Regresion/R2_producto_1.1.1_despues_CC-01/R2_producto_1.1.1_despues_CC-01.html", 1500),
]

# El logger html de VSTest no trae estilos: se le da un formato legible y se
# despliegan todas las secciones <details>. El contenido no se modifica.
ESTILO_VSTEST = r"""
document.querySelectorAll('details').forEach(d => d.open = true);
const s = document.createElement('style');
s.textContent = `
 body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#222;font-size:14px}
 h1{font-size:24px;margin:0 0 12px} h2{font-size:18px;margin:22px 0 8px;border-bottom:2px solid #1f3864}
 .summary{display:flex;gap:28px;background:#f2f4f8;padding:12px 18px;border-radius:6px}
 .block span{color:#555} .total-tests,.pass-percentage,.test-run-time{font-size:22px;font-weight:600}
 .passedTests{color:#2e7d32;font-weight:700} .failedTests{color:#c62828;font-weight:700}
 summary{font-weight:600;padding:6px 0;color:#1f3864}
 .leaf-division{border-bottom:1px solid #e5e5e5;padding:3px 6px}
 .leaf-division>div:first-child{display:flex;justify-content:space-between}
 .pass{color:#2e7d32;font-weight:700;margin-right:6px} .fail{color:#c62828;font-weight:700;margin-right:6px}
 .duration{color:#777} .error-info{color:#c62828} pre{white-space:pre-wrap;margin:4px 0;background:#fff4f4;padding:6px}
 .error-info:empty{display:none}`;
document.head ? document.head.appendChild(s) : document.documentElement.prepend(s);
"""


def capturar(nav, carpeta, nombre, html, ancho, modo=None):
    destino = G07 / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    nav.set_window_size(ancho, 900)
    nav.get((G07 / html).as_uri())
    if html.split("/")[-2] != "cobertura":  # reportes de VSTest (los de ReportGenerator están en .../cobertura/)
        nav.execute_script(ESTILO_VSTEST)
        if modo == "resumen":
            nav.execute_script("document.querySelectorAll('details').forEach(d => d.open = false)")
    if modo and modo.startswith("linea:"):
        n = int(modo.split(":")[1])
        nav.set_window_size(ancho, 1000)
        # Fila de la línea N en la tabla de código de ReportGenerator; se deja contexto arriba.
        y = nav.execute_script(
            "const f=[...document.querySelectorAll('tr')].find(r=>r.cells.length>2&&r.cells[2].innerText.trim()==='%d');"
            "return f? f.getBoundingClientRect().top+window.scrollY:0" % n)
        png = nav.execute_cdp_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True,
                                  "clip": {"x": 0, "y": max(y - 380, 0), "width": ancho, "height": 760, "scale": 1}})
        (destino / f"{nombre}.png").write_bytes(base64.b64decode(png["data"]))
        print(f"{carpeta}/{nombre}.png  (recorte línea {n})")
        return
    alto = nav.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
    if modo == "resumen":
        alto = 420  # cabecera con totales y secciones plegadas; los mensajes informativos de 935 pruebas quedan fuera
    nav.execute_cdp_cmd("Emulation.setDeviceMetricsOverride",
                        {"width": ancho, "height": min(alto, 12000), "deviceScaleFactor": 1, "mobile": False})
    opciones = {"format": "png", "captureBeyondViewport": True}
    if modo == "resumen":
        opciones["clip"] = {"x": 0, "y": 0, "width": ancho, "height": alto, "scale": 1}
    png = nav.execute_cdp_cmd("Page.captureScreenshot", opciones)
    (destino / f"{nombre}.png").write_bytes(base64.b64decode(png["data"]))
    nav.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
    print(f"{carpeta}/{nombre}.png  ({ancho}x{min(alto, 12000)})")


op = webdriver.ChromeOptions()
op.add_argument("--headless=new")
op.add_argument("--allow-file-access-from-files")
op.add_argument("--lang=es")
nav = webdriver.Chrome(options=op)
try:
    for c in CAPTURAS:
        capturar(nav, *c)
finally:
    nav.quit()
