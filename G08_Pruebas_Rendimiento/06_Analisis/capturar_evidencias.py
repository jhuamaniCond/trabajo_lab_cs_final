"""Captura los reportes HTML (dashboard) de JMeter en Chrome sin ventana, para el informe de G08.

Uso: python capturar_evidencias.py   (escribe capturas/*.png)
Requiere selenium 4 y Google Chrome (Selenium Manager descarga el controlador).
Cada captura es un elemento del dashboard: la tabla Statistics (percentiles por transacción),
la tabla de APDEX o un gráfico de la sección Charts.
"""
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

AQUI = Path(__file__).resolve().parent
RES = AQUI.parent / "04_Resultados"
SALIDA = AQUI / "capturas"

# (archivo, carpeta del resultado, página, id del elemento)
CAPTURAS = [
    ("01_dashboard_carga_antes.png", "1_antes/carga", "index.html", "statisticsTable"),
    ("02_dashboard_carga_despues.png", "2_despues/carga", "index.html", "statisticsTable"),
    ("03_apdex_carga_despues.png", "2_despues/carga", "index.html", "apdexTable"),
    ("04_estres_despues_tiempos.png", "2_despues/estres", "content/pages/OverTime.html", "bodyResponseTimeOverTime"),
    ("05_estres_despues_usuarios_activos.png", "2_despues/estres", "content/pages/OverTime.html", "bodyActiveThreadsOverTime"),
    ("06_pico_despues_tiempos.png", "2_despues/pico", "content/pages/OverTime.html", "bodyResponseTimeOverTime"),
    ("07_pico_despues_usuarios_activos.png", "2_despues/pico", "content/pages/OverTime.html", "bodyActiveThreadsOverTime"),
    ("08_estabilidad_despues_tiempos.png", "2_despues/estabilidad", "content/pages/OverTime.html", "bodyResponseTimeOverTime"),
    ("09_estabilidad_despues_estadisticas.png", "2_despues/estabilidad", "index.html", "statisticsTable"),
    ("10_capacidad_50u_antes_estadisticas.png", "1_antes/capacidad_50u", "index.html", "statisticsTable"),
    ("11_capacidad_50u_despues_estadisticas.png", "2_despues/capacidad_50u", "index.html", "statisticsTable"),
]


def main():
    SALIDA.mkdir(exist_ok=True)
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1500,1100")
    opciones.add_argument("--allow-file-access-from-files")
    driver = webdriver.Chrome(options=opciones)
    try:
        for archivo, carpeta, pagina, elemento in CAPTURAS:
            ruta = RES / carpeta / "dashboard" / pagina
            if not ruta.exists():
                print("falta", ruta)
                continue
            driver.get(ruta.as_uri())
            el = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, elemento)))
            if elemento.startswith("body") and not el.is_displayed():
                # Gráfico plegado: se abre con su encabezado para que flot lo dibuje.
                nombre = elemento[len("body"):]
                enlace = driver.find_element(By.CSS_SELECTOR, f"[data-toggle='collapse'][href='#body{nombre}']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", enlace)
                WebDriverWait(driver, 20).until(EC.visibility_of(el))
            # Las tablas se llenan por JavaScript y los gráficos (flot) se dibujan después.
            if elemento.endswith("Table"):
                WebDriverWait(driver, 20).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, f"#{elemento} tbody tr")) > 0)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(2)
            # Encabezado del panel incluido en la captura (título del gráfico o de la tabla).
            panel = driver.execute_script("return arguments[0].closest('.panel') || arguments[0];", el)
            panel.screenshot(str(SALIDA / archivo))
            print("captura", archivo)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
