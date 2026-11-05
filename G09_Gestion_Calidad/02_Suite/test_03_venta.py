"""PN-01 Venta y facturación: boleta solo con teclado, factura con RUC y sus reglas."""
import re
import time
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import datos
from comun import PruebaWeb, config
from paginas import PaginaClientes, PaginaHistorial, PaginaIngresar, PaginaPrincipal, PaginaVenta


def soles(texto):
    return float(texto.replace("S/", "").strip())


class CP07_VentaBoletaConTeclado(PruebaWeb):
    caso, requisitos = "CP-07", "RF-05, RF-07, RF-14, RNF-01, RNF-06"

    def test_boleta_con_teclado_queda_emitida_y_en_el_historial(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        venta = PaginaVenta(self.driver)
        inicio_venta = time.perf_counter()

        # RNF-01: tiempo entre la tercera letra y la lista de sugerencias.
        campo = venta.visible("CampoProducto")
        campo.send_keys(datos.PRODUCTO_BUSQUEDA[:2])
        t0 = time.perf_counter()
        campo.send_keys(datos.PRODUCTO_BUSQUEDA[2])
        venta.visible("ListaSugerencias")
        ms = (time.perf_counter() - t0) * 1000
        self.medir("RNF-01 sugerencias (ms)", round(ms))
        self.assertLess(ms, float(config("rnf01_ms", "1000")), "RNF-01: la lista debe aparecer en menos de 1 s")
        for li in venta.sugerencias():
            self.assertIn("cemento", li.text.lower())
        self.evidencia("sugerencias")

        # Solo teclado: Enter elige, cantidad 2 y Enter agrega; F10 emite.
        campo.send_keys(datos.PRODUCTO_BUSQUEDA[3:])
        self.hasta(lambda d: venta.sugerencias() and all("cemento" in li.text.lower() for li in venta.sugerencias()))
        precio = float(re.search(r"S/ ([\d.]+)", venta.sugerencias()[0].text).group(1))
        campo.send_keys(Keys.ENTER)
        self.hasta(lambda d: d.switch_to.active_element.get_attribute("id") == "CampoCantidad")
        cantidad = self.driver.switch_to.active_element
        cantidad.send_keys(Keys.CONTROL, "a")
        cantidad.send_keys("2", Keys.ENTER)
        venta.esperar_lineas(1)
        total = round(precio * 2, 2)
        self.assertEqual(f"S/ {total:.2f}", venta.total())
        op, igv = soles(venta.texto("TextoOpGravada")), soles(venta.texto("TextoIgv"))
        self.assertAlmostEqual(round(total / 1.18, 2), op, places=2)
        self.assertAlmostEqual(total, round(op + igv, 2), places=2)
        self.assertEqual("TipoBoleta", venta.tipo_elegido())
        self.driver.switch_to.active_element.send_keys(Keys.F10)

        resultado = venta.esperar_texto("TextoResultadoEmision", "emitida")
        segundos = time.perf_counter() - inicio_venta
        self.medir("RNF-06 venta con teclado (s)", round(segundos, 1))
        self.assertLessEqual(segundos, float(config("rnf06_segundos", "60")))
        numero = re.search(r"Boleta (B001-\d{8}) emitida · Total S/ ([\d.]+) · SUNAT: PENDIENTE", resultado)
        self.assertIsNotNone(numero, resultado)
        self.assertEqual(f"{total:.2f}", numero.group(2))
        # La pantalla queda lista para la siguiente venta.
        self.assertEqual(0, len(venta.lineas()))
        self.assertEqual("S/ 0.00", venta.total())
        self.assertFalse(venta.el("BotonEmitir").is_enabled())
        self.evidencia("boleta_emitida")

        # Consulta: el comprobante está en el historial con su total.
        principal.el("CampoProducto").send_keys(Keys.F5)
        historial = PaginaHistorial(self.driver)
        historial.visible("ModuloHistorial")
        historial.escribir("FiltroTexto", numero.group(1), limpiar=True)
        historial.buscar()
        self.hasta(lambda d: len(historial.filas()) == 1 and numero.group(1) in historial.filas()[0].text)
        fila = historial.filas()[0].text
        self.assertIn(f"S/ {total:.2f}", fila)
        self.assertIn("vendedor1", fila)
        self.assertIn("PENDIENTE", fila)
        self.evidencia("boleta_en_historial")


class CP08_FacturaConRuc(PruebaWeb):
    caso, requisitos = "CP-08", "RF-06, RF-07"

    def test_factura_a_un_cliente_con_ruc_recien_registrado(self):
        ruc = datos.ruc_valido()
        razon = "Constructora G09 " + datos.SUFIJO + " S.A.C."
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        PaginaPrincipal(self.driver).esperar()
        venta = PaginaVenta(self.driver)

        venta.agregar_primera_sugerencia(datos.PRODUCTO_BUSQUEDA, 10)
        venta.esperar_lineas(1)
        venta.buscar_cliente(ruc)
        venta.esperar_texto("TextoSinCliente", "no está registrado")
        clientes = PaginaClientes(self.driver)
        clientes.nuevo_cliente(ruc, razon, "Av. Industrial 450, Majes", desde_venta=True)
        venta.esperar_texto("ClienteNombre", razon)
        self.assertEqual("TipoFactura", venta.tipo_elegido(), "con RUC se elige Factura")

        venta.emitir()
        resultado = venta.esperar_texto("TextoResultadoEmision", "emitida")
        self.assertRegex(resultado, r"^Factura F001-\d{8} emitida")
        self.evidencia("factura_emitida")


class CP09_ReglasDeEmision(PruebaWeb):
    caso, requisitos = "CP-09", "RF-07"

    def test_factura_sin_ruc_y_boleta_mayor_a_700_sin_dni_no_se_emiten(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        PaginaPrincipal(self.driver).esperar()
        venta = PaginaVenta(self.driver)
        venta.agregar_primera_sugerencia(datos.PRODUCTO_BUSQUEDA, 1)
        venta.esperar_lineas(1)

        venta.elegir_tipo("TipoFactura")
        venta.emitir()
        self.assertIn("La factura requiere un cliente con RUC", venta.error_emision())
        self.assertEqual(1, len(venta.lineas()), "la venta no se pierde")
        self.evidencia("factura_sin_ruc")

        # Boleta de más de S/ 700 sin DNI (R. 007-99/SUNAT).
        cantidad = venta.driver.find_element(By.CSS_SELECTOR, "#TablaDetalle input.cantidad")
        cantidad.send_keys(Keys.CONTROL, "a")
        cantidad.send_keys("40", Keys.TAB)
        self.hasta(lambda d: soles(venta.total()) > 700)
        venta.elegir_tipo("TipoBoleta")
        venta.emitir()
        self.hasta(EC.text_to_be_present_in_element(("id", "TextoErrorEmision"), "deben llevar el DNI del cliente"))
        self.evidencia("boleta_mayor_700_sin_dni")

        # Esc cancela la venta en curso.
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self.hasta(lambda d: len(venta.lineas()) == 0)
        self.assertFalse(venta.esta_visible("ErrorEmision"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
