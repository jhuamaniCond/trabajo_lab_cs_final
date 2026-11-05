"""Page Objects del portal web Cóndor (CC-03).

Los selectores son los id estables del portal, que repiten los AutomationId de
la app de escritorio (CampoUsuario, BotonIngresar, MenuVenta...). No se usan
XPath por posición ni textos traducibles como selector.
"""
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from comun import ESPERA, URL


class Pagina:
    def __init__(self, driver):
        self.driver = driver
        # La tabla se vuelve a pintar al buscar: un elemento viejo no es un fallo (DEF-06).
        self.espera = WebDriverWait(driver, ESPERA, ignored_exceptions=(StaleElementReferenceException,))

    def el(self, id_):
        return self.driver.find_element(By.ID, id_)

    def visible(self, id_):
        return self.espera.until(EC.visibility_of_element_located((By.ID, id_)))

    def clic(self, id_):
        self.espera.until(EC.element_to_be_clickable((By.ID, id_))).click()

    def escribir(self, id_, texto, limpiar=True):
        campo = self.visible(id_)
        if limpiar:
            campo.send_keys(Keys.CONTROL, "a")
            campo.send_keys(Keys.DELETE)
        campo.send_keys(texto)
        return campo

    def texto(self, id_):
        return self.visible(id_).text.strip()

    def esta_visible(self, id_):
        elementos = self.driver.find_elements(By.ID, id_)
        return bool(elementos) and elementos[0].is_displayed()

    def esperar_texto(self, id_, fragmento):
        self.espera.until(EC.text_to_be_present_in_element((By.ID, id_), fragmento))
        return self.texto(id_)

    def tecla(self, *teclas):
        self.driver.switch_to.active_element.send_keys(*teclas)


class PaginaIngresar(Pagina):
    def abrir(self):
        self.driver.get(URL)
        self.visible("CampoUsuario")
        return self

    def ingresar(self, usuario, clave):
        self.escribir("CampoUsuario", usuario)
        self.escribir("CampoClave", clave)
        self.clic("BotonIngresar")

    def error(self):
        return self.texto("TextoError")

    def mostrada(self):
        return self.esta_visible("VentanaIngresar")


class PaginaPrincipal(Pagina):
    """Menú lateral y pie de la ventana principal."""

    def esperar(self):
        self.visible("PantallaPrincipal")
        self.espera.until(lambda d: self.el("TextoUsuario").text.strip() != "")
        return self

    def ir_a(self, modulo):
        self.clic("Menu" + modulo)
        seccion = {"Guias": "ModuloSoloEscritorio"}.get(modulo, "Modulo" + modulo)
        self.visible(seccion)

    def usuario(self):
        return self.texto("TextoUsuario")

    def rol(self):
        return self.texto("TextoRol")

    def mensaje(self):
        return self.el("TextoMensaje").text.strip()

    def menu_visible(self, modulo):
        return self.esta_visible("Menu" + modulo)

    def menu_activo(self):
        return self.driver.find_element(By.CSS_SELECTOR, ".menu.activo").get_attribute("id")

    def cerrar_sesion(self):
        self.clic("MenuCerrarSesion")


class PaginaVenta(Pagina):
    def buscar_producto(self, texto):
        self.escribir("CampoProducto", texto)
        return self.visible("ListaSugerencias")

    def sugerencias(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "#ListaSugerencias li")

    def agregar_primera_sugerencia(self, texto, cantidad):
        """Solo teclado, como en el mostrador: Enter elige y Enter en Cantidad agrega."""
        self.buscar_producto(texto)
        self.el("CampoProducto").send_keys(Keys.ENTER)
        self.espera.until(lambda d: d.switch_to.active_element.get_attribute("id") == "CampoCantidad")
        cantidad_campo = self.el("CampoCantidad")
        cantidad_campo.send_keys(Keys.CONTROL, "a")
        cantidad_campo.send_keys(str(cantidad), Keys.ENTER)

    def lineas(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "#TablaDetalle tbody tr")

    def esperar_lineas(self, n):
        self.espera.until(lambda d: len(self.lineas()) == n)
        return self.lineas()

    def total(self):
        return self.texto("TextoTotal")

    def buscar_cliente(self, documento):
        self.escribir("CampoDocumento", documento)
        self.el("CampoDocumento").send_keys(Keys.ENTER)

    def elegir_tipo(self, id_tipo):
        # El radio está oculto con CSS; se pulsa su etiqueta, como el usuario.
        self.driver.find_element(By.CSS_SELECTOR, f"label.opcion:has(#{id_tipo}) span").click()

    def tipo_elegido(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'input[name="tipo"]:checked').get_attribute("id")

    def emitir(self):
        self.clic("BotonEmitir")

    def resultado(self):
        return self.texto("TextoResultadoEmision")

    def error_emision(self):
        return self.texto("TextoErrorEmision")


class PaginaClientes(Pagina):
    def nuevo_cliente(self, documento, nombre, direccion="", desde_venta=False):
        self.clic("BotonNuevoCliente" if desde_venta else "BotonNuevoClienteModulo")
        self.visible("VentanaNuevoCliente")
        self.escribir("CampoNuevoDocumento", documento)
        self.escribir("CampoNuevoNombre", nombre)
        if direccion:
            self.escribir("CampoNuevaDireccion", direccion)
        self.clic("BotonGuardarCliente")

    def filas(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "#TablaClientes tbody tr")


class PaginaCatalogo(Pagina):
    def nuevo_producto(self, nombre, precio, unidad="UND", desde_venta=False):
        self.clic("BotonNuevoProducto" if desde_venta else "BotonNuevoProductoCatalogo")
        self.visible("VentanaNuevoProducto")
        self.escribir("CampoNombreProducto", nombre)
        self.escribir("CampoPrecioProducto", precio)
        self.el("CampoUnidadProducto").send_keys(unidad)
        self.clic("BotonGuardarProducto")

    def buscar(self, texto):
        self.escribir("CampoBuscarCatalogo", texto)
        self.clic("BotonBuscarCatalogo")

    def filas(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "#TablaCatalogo tbody tr")


class PaginaHistorial(Pagina):
    def filas(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "#TablaHistorial tbody tr")

    def fechas(self, desde, hasta):
        for id_, valor in (("FiltroDesde", desde), ("FiltroHasta", hasta)):
            self.driver.execute_script("arguments[0].value = arguments[1];", self.el(id_), valor)

    def buscar(self):
        self.clic("BotonBuscarHistorial")


class PaginaProformas(Pagina):
    def buscar(self, texto):
        self.escribir("CampoBuscarProformas", texto)
        self.clic("BotonBuscarProformas")

    def fila(self, numero):
        return self.espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#TablaProformas tr[data-numero="{numero}"]')))

    def estado(self, numero):
        return self.fila(numero).find_element(By.CSS_SELECTOR, "td.estado").text.strip()
