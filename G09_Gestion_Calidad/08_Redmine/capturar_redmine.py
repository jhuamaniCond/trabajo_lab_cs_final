"""Captura en Chrome (sin ventana) las peticiones de Redmine que G09 actualizó.

    python 08_Redmine/capturar_redmine.py http://localhost:3010 <clave del admin> <número de CC-03>

La clave se pasa por argumento: no se guarda en el repositorio.
"""
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL, CLAVE, CC03 = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
SALIDA = Path(__file__).resolve().parent / "capturas"
SALIDA.mkdir(exist_ok=True)
COLUMNAS = "&".join(f"c[]={c}" for c in ["tracker", "cf_1", "subject", "status", "assigned_to", "updated_on"])
PANTALLAS = [
    ("01_CC-03_solicitud_de_cambio_cerrada", f"/issues/{CC03}"),
    ("02_solicitudes_de_cambio", f"/projects/condor/issues?set_filter=1&f[]=tracker_id&op[tracker_id]=%3D&v[tracker_id][]=5"
                                 f"&f[]=status_id&op[status_id]=*&sort=id&per_page=50&{COLUMNAS}"),
    ("03_requisitos_tras_G09", f"/projects/condor/issues?set_filter=1&f[]=tracker_id&op[tracker_id]=%3D&v[tracker_id][]=4"
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
    nav.find_element(By.ID, "password").send_keys(CLAVE)
    nav.find_element(By.ID, "login-submit").click()
    WebDriverWait(nav, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.logout")))
    for nombre, ruta in PANTALLAS:
        nav.get(URL + ruta)
        WebDriverWait(nav, 10).until(EC.presence_of_element_located((By.ID, "content")))
        alto = nav.execute_script("return document.body.scrollHeight")
        nav.set_window_size(1440, min(max(alto, 900), 4000))
        nav.save_screenshot(str(SALIDA / f"{nombre}.png"))
        nav.set_window_size(1440, 900)
        print("captura:", nombre)
finally:
    nav.quit()
