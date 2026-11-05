"""Captura en Chrome (sin ventana) las peticiones de Redmine que G08 actualizó.

    python 08_Redmine/capturar_redmine.py http://localhost:3010
"""
import base64
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

URL = sys.argv[1].rstrip("/")
SALIDA = Path(__file__).resolve().parent / "capturas"
SALIDA.mkdir(exist_ok=True)
COLUMNAS = "&".join(f"c[]={c}" for c in ["tracker", "cf_1", "subject", "status", "assigned_to", "updated_on"])
PANTALLAS = [
    ("01_RNF-02_verificado_y_cerrado", "/issues/24"),
    ("02_MEJ-01_solicitud_de_cambio_cerrada", "/issues/27"),
    ("03_RF-07_nota_G08", "/issues/5"),
    ("04_solicitudes_de_cambio", f"/projects/condor/issues?set_filter=1&f[]=tracker_id&op[tracker_id]=%3D&v[tracker_id][]=5"
                                 f"&f[]=status_id&op[status_id]=*&sort=id&per_page=50&{COLUMNAS}"),
    ("05_requisitos_estado_tras_G08", f"/projects/condor/issues?set_filter=1&f[]=tracker_id&op[tracker_id]=%3D&v[tracker_id][]=4"
                                      f"&f[]=status_id&op[status_id]=*&sort=cf_1&per_page=50&{COLUMNAS}"),
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
        # Redmine escribe «hace 2 minutos»; se reemplaza por la fecha y hora exactas del title.
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
