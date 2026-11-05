"""Captura las pantallas de Redmine usadas como evidencia de G02 (página completa).

    python capturar_redmine.py http://localhost:3010

Usa Chrome sin ventana a través de Selenium; deja los PNG en capturas/.
"""
import base64
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

URL = sys.argv[1].rstrip("/")
SALIDA = Path(__file__).resolve().parent / "capturas"
SALIDA.mkdir(exist_ok=True)

COLUMNAS = "&".join(f"c[]={c}" for c in
                    ["tracker", "cf_1", "cf_6", "subject", "status", "priority", "author", "assigned_to",
                     "fixed_version", "updated_on"])
PANTALLAS = [
    ("01_estados", "/issue_statuses"),
    ("02_tipos_peticion", "/trackers"),
    ("03_campos_personalizados", "/custom_fields"),
    ("04_roles", "/roles"),
    ("05_flujo_resumen", "/workflows"),
    ("06_flujo_analista", "/workflows/edit?role_id[]=6&tracker_id[]=4&used_statuses_only=0"),
    ("07_flujo_ccb", "/workflows/edit?role_id[]=7&tracker_id[]=4&used_statuses_only=0"),
    ("08_flujo_desarrollador", "/workflows/edit?role_id[]=8&tracker_id[]=4&used_statuses_only=0"),
    ("09_flujo_evaluador", "/workflows/edit?role_id[]=9&tracker_id[]=4&used_statuses_only=0"),
    ("10_miembros_proyecto", "/projects/condor/settings/members"),
    ("11_lista_peticiones", f"/projects/condor/issues?set_filter=1&f[]=status_id&op[status_id]=*&sort=id"
                            f"&per_page=50&{COLUMNAS}"),
    ("12_historial_RF-01", "/issues/1"),
    ("13_historial_RF-03", "/issues/22"),
    ("14_historial_RF-07", "/issues/5"),
    ("15_historial_RF-08", "/issues/6"),
    ("16_historial_RF-15", "/issues/23"),
    ("17_solicitud_CC-01", "/issues/20"),
    ("18_solicitud_CC-02", "/issues/26"),
    ("19_informe_resumen", "/projects/condor/issues/report"),
    ("20_informe_estado_por_tipo", "/projects/condor/issues/report/tracker"),
    ("21_informe_por_asignado", "/projects/condor/issues/report/assigned_to"),
    ("22_hoja_de_ruta_1.1.0", "/versions/2"),
]

op = webdriver.ChromeOptions()
op.add_argument("--headless=new")
op.add_argument("--window-size=1440,900")
op.add_argument("--lang=es")
nav = webdriver.Chrome(options=op)
try:
    nav.get(URL + "/login")
    nav.find_element(By.ID, "username").send_keys("admin")
    nav.find_element(By.ID, "password").send_keys("Condor2026!")
    nav.find_element(By.ID, "login-submit").click()
    for nombre, ruta in PANTALLAS:
        nav.get(URL + ruta)
        # Redmine escribe «hace 2 minutos»; la fecha y hora exactas están en el title del enlace.
        nav.execute_script(r"""
            document.querySelectorAll('a[title]').forEach(a => {
              if (!/^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/.test(a.title)) return;
              a.textContent = a.title;
              const antes = a.previousSibling;
              if (antes && antes.nodeType === 3) antes.textContent = antes.textContent.replace(/hace\s*$/, 'el ');
            });""")
        alto = nav.execute_script("return document.documentElement.scrollHeight")
        png = nav.execute_cdp_cmd("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": 1440, "height": alto, "scale": 1}})
        (SALIDA / f"{nombre}.png").write_bytes(base64.b64decode(png["data"]))
        print(nombre, alto)
finally:
    nav.quit()
