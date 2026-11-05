"""Utilidades compartidas por la suite Selenium de G09.

Mismo enfoque que el Lab 9 (comun.py: crear_driver y captura), adaptado al
producto:
- crear_driver(): Chrome o Edge con Selenium Manager (sin ruta fija al driver).
- PruebaWeb: unittest.TestCase base. Abre un navegador nuevo por caso (los
  casos no comparten sesión ni datos y el orden no influye), guarda una captura
  automática cuando un caso falla y deja capturas de evidencia con evidencia().
- Solo esperas explícitas (WebDriverWait); no se mezcla con implicit wait.
"""
import configparser
import os
import re
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

RAIZ = Path(__file__).resolve().parent

_ini = configparser.ConfigParser()
_ini.read(RAIZ / "config.ini", encoding="utf-8")


def config(clave, defecto=None):
    """Valor de config.ini; la variable de entorno CONDOR_<CLAVE> lo reemplaza."""
    return os.environ.get("CONDOR_" + clave.upper(), _ini.get("suite", clave, fallback=defecto))


URL = config("url").rstrip("/") + "/"
ESPERA = float(config("espera", "10"))

# Carpeta de la ejecución en curso (la fija ejecutar_suite.py); capturas aquí.
CARPETA_EJECUCION = Path(os.environ.get("CONDOR_CARPETA_EJECUCION", RAIZ / "_ultima_ejecucion"))
CARPETA_CAPTURAS = CARPETA_EJECUCION / "capturas"


def crear_driver():
    navegador = config("navegador", "chrome").lower()
    headless = config("headless", "1") == "1"
    ancho, alto = config("ancho", "1440"), config("alto", "900")
    if navegador == "edge":
        opciones = webdriver.EdgeOptions()
    else:
        opciones = webdriver.ChromeOptions()
    if headless:
        opciones.add_argument("--headless=new")
    opciones.add_argument(f"--window-size={ancho},{alto}")
    opciones.add_argument("--lang=es-PE")
    opciones.add_experimental_option("prefs", {"intl.accept_languages": "es-PE,es"})
    opciones.add_argument("--disable-search-engine-choice-screen")
    opciones.set_capability("goog:loggingPrefs" if navegador != "edge" else "ms:loggingPrefs", {"browser": "ALL"})
    # Selenium Manager descarga/ubica chromedriver o msedgedriver automáticamente.
    driver = webdriver.Edge(options=opciones) if navegador == "edge" else webdriver.Chrome(options=opciones)
    driver.set_page_load_timeout(30)
    return driver


def nombre_archivo(texto):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", texto).strip("_")[:90]


class PruebaWeb(unittest.TestCase):
    """Caso web: navegador nuevo, captura en fallo y evidencias."""

    # Identificador del caso (CP-01...) y requisitos que verifica; lo usa el reporte.
    caso = ""
    requisitos = ""

    def setUp(self):
        self.driver = crear_driver()
        self.espera = WebDriverWait(self.driver, ESPERA, ignored_exceptions=(StaleElementReferenceException,))
        self.capturas = []
        self.mediciones = {}
        self.driver.get(URL)

    def _callTestMethod(self, method):
        # Captura automática del fallo en el momento en que ocurre, con la
        # pantalla tal como quedó; luego la excepción sigue hacia el ejecutor
        # (no se oculta: el caso queda FALLIDO o ERROR).
        try:
            super()._callTestMethod(method)
        except Exception:
            try:
                self.evidencia("FALLO")
            except Exception:  # el navegador pudo haberse cerrado
                pass
            raise

    def tearDown(self):
        self.driver.quit()

    def evidencia(self, descripcion):
        """Captura del navegador como evidencia del paso (04_Reportes/<ejecución>/capturas)."""
        CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)
        id_caso = self.caso or self.id().split(".")[-1]
        ruta = CARPETA_CAPTURAS / f"{nombre_archivo(id_caso)}_{len(self.capturas) + 1:02d}_{nombre_archivo(descripcion)}.png"
        self.driver.save_screenshot(str(ruta))
        self.capturas.append(ruta.name)
        return ruta

    def medir(self, nombre, valor):
        """Registra una medición (ms, s...) que el reporte muestra junto al caso."""
        self.mediciones[nombre] = valor

    # Atajos de espera explícita ------------------------------------------------

    def visible(self, by, valor):
        return self.espera.until(EC.visibility_of_element_located((by, valor)))

    def hasta(self, condicion, mensaje=""):
        return self.espera.until(condicion, mensaje)


def cronometro():
    return time.perf_counter()
