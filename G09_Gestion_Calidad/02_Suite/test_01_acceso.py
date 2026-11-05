"""Acceso: ingreso correcto, credenciales inválidas, restricción por rol y cierre de sesión."""
import unittest

from selenium.webdriver.common.keys import Keys

import datos
from comun import URL, PruebaWeb
from paginas import PaginaIngresar, PaginaPrincipal


class CP01_AccesoCorrecto(PruebaWeb):
    caso, requisitos = "CP-01", "RF-01"

    def test_encargado_ingresa_y_ve_su_usuario_y_rol(self):
        PaginaIngresar(self.driver).ingresar(*datos.ENCARGADO)
        principal = PaginaPrincipal(self.driver).esperar()

        self.assertEqual("encargado", principal.usuario())
        self.assertEqual("Encargado general", principal.rol())
        self.assertEqual("MenuVenta", principal.menu_activo())
        self.assertTrue(principal.esta_visible("ModuloVenta"))
        self.assertFalse(principal.esta_visible("PantallaIngresar"))
        self.evidencia("nueva_venta_encargado")


class CP02_CredencialesInvalidas(PruebaWeb):
    caso, requisitos = "CP-02", "RF-01, RNF-03"

    def test_clave_equivocada_muestra_el_mensaje_generico_y_no_entra(self):
        ingresar = PaginaIngresar(self.driver)
        ingresar.ingresar(*datos.VENDEDOR_CLAVE_ERRADA)

        self.assertEqual("Usuario o contraseña incorrectos.", ingresar.error())
        self.assertTrue(ingresar.mostrada())
        self.assertFalse(ingresar.esta_visible("PantallaPrincipal"))
        self.assertEqual("", ingresar.el("CampoClave").get_attribute("value"), "la contraseña debe borrarse")
        self.evidencia("credenciales_invalidas")

        # Un usuario que no existe recibe el mismo mensaje (no revela si existe).
        ingresar.ingresar("usuario_que_no_existe", "Cualquiera1!")
        self.assertEqual("Usuario o contraseña incorrectos.", ingresar.error())

        # Sin datos no se consulta la base.
        ingresar.escribir("CampoUsuario", "")
        ingresar.escribir("CampoClave", "")
        ingresar.clic("BotonIngresar")
        ingresar.esperar_texto("TextoError", "Ingrese su usuario y su contraseña.")

        # Datos aislados: un ingreso correcto pone en cero los intentos de vendedor2.
        ingresar.ingresar(*datos.VENDEDOR2)
        self.assertEqual("vendedor2", PaginaPrincipal(self.driver).esperar().usuario())


class CP03_RestriccionPorRol(PruebaWeb):
    caso, requisitos = "CP-03", "RF-03, RNF-03"

    def test_vendedor_no_ve_ni_abre_los_modulos_del_encargado(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        self.assertEqual("Vendedor", principal.rol())

        for modulo in ("Compras", "Proveedores", "Guias", "Respaldo", "Reporte"):
            self.assertFalse(principal.menu_visible(modulo), f"el Vendedor no debe ver {modulo}")
        for modulo in ("Venta", "Catalogo", "Clientes", "Historial", "Proformas"):
            self.assertTrue(principal.menu_visible(modulo), f"el Vendedor debe ver {modulo}")
        self.evidencia("menu_vendedor")

        # Con la dirección del módulo: se queda en Nueva venta con Acceso denegado.
        self.driver.get(URL + "#/proveedores")
        principal.esperar_texto("TextoMensaje", "Acceso denegado")
        self.assertIn("Proveedores es solo para el Encargado general", principal.mensaje())
        self.assertTrue(principal.esta_visible("ModuloVenta"))
        self.assertFalse(principal.esta_visible("ModuloProveedores"))
        self.evidencia("acceso_denegado_por_direccion")

        # Con la tecla del módulo (F4 Compras) pasa lo mismo.
        principal.el("CampoProducto").send_keys(Keys.F4)
        principal.esperar_texto("TextoMensaje", "Compras es solo para el Encargado general")
        self.assertEqual("MenuVenta", principal.menu_activo())


class CP14_CierreDeSesion(PruebaWeb):
    caso, requisitos = "CP-14", "RF-02"

    def test_cerrar_sesion_vuelve_a_ingresar_y_no_deja_la_sesion_abierta(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        principal.ir_a("Historial")

        principal.cerrar_sesion()
        ingresar = PaginaIngresar(self.driver)
        ingresar.visible("VentanaIngresar")
        self.assertFalse(ingresar.esta_visible("PantallaPrincipal"))
        self.assertEqual("", ingresar.el("CampoUsuario").get_attribute("value"))
        self.assertIsNone(self.driver.execute_script("return sessionStorage.getItem('condor.sesion');"),
                          "el token no debe quedar guardado")
        self.evidencia("sesion_cerrada")

        # Recargar o volver a la dirección de un módulo no reabre la sesión.
        self.driver.get(URL + "#/historial")
        self.driver.refresh()
        ingresar.visible("VentanaIngresar")
        self.assertFalse(ingresar.esta_visible("PantallaPrincipal"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
