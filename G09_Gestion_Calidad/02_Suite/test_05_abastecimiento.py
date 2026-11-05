"""PN-03 Abastecimiento: registrar proveedor y su compra (solo el Encargado general)."""
import unittest
from datetime import date, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import datos
from comun import PruebaWeb
from paginas import PaginaIngresar, PaginaPrincipal


class CP13_ProveedorYCompra(PruebaWeb):
    caso, requisitos = "CP-13", "RF-11, RF-12, RF-03"

    def test_registra_proveedor_y_compra_y_rechaza_la_compra_repetida(self):
        ruc, razon = datos.ruc_valido(), f"Distribuidora G09 {datos.SUFIJO} S.A.C."
        serie, numero = "F" + datos.SUFIJO[-3:], datos.numero_compra()
        PaginaIngresar(self.driver).ingresar(*datos.ENCARGADO)
        principal = PaginaPrincipal(self.driver).esperar()

        # 1. Proveedor nuevo (RF-11).
        principal.ir_a("Proveedores")
        principal.clic("BotonNuevoProveedor")
        principal.visible("VentanaNuevoProveedor")
        principal.escribir("CampoProveedorRuc", ruc)
        principal.escribir("CampoProveedorRazon", razon)
        principal.escribir("CampoProveedorTelefono", "054 123456")
        principal.escribir("CampoProveedorContacto", "Contacto G09")
        principal.clic("BotonGuardarProveedor")
        principal.esperar_texto("TextoMensaje", f"Proveedor {razon} registrado.")
        self.hasta(lambda d: [f for f in d.find_elements(By.CSS_SELECTOR, "#TablaProveedores tbody tr") if ruc in f.text])
        self.evidencia("proveedor_registrado")

        # El mismo RUC no se registra dos veces.
        principal.clic("BotonNuevoProveedor")
        principal.escribir("CampoProveedorRuc", ruc)
        principal.escribir("CampoProveedorRazon", razon)
        principal.clic("BotonGuardarProveedor")
        self.hasta(lambda d: principal.esta_visible("ErrorNuevoProveedor"))
        principal.clic("BotonCancelarProveedor")

        # 2. Compra a ese proveedor (RF-12).
        principal.ir_a("Compras")
        self.registrar_compra(principal, ruc, serie, numero)
        principal.esperar_texto("TextoMensaje", f"de {razon} registrada")
        documento = f"Factura {serie}-{numero:08d}"
        self.hasta(lambda d: [f for f in d.find_elements(By.CSS_SELECTOR, "#TablaCompras tbody tr") if documento in f.text])
        fila = [f for f in self.driver.find_elements(By.CSS_SELECTOR, "#TablaCompras tbody tr") if documento in f.text][0].text
        # 10 × 15.50 + 2 × 25.00 = S/ 205.00 con IGV; op. gravada 205 / 1.18 = S/ 173.73.
        self.assertIn("S/ 205.00", fila)
        self.assertIn("S/ 173.73", fila, "DEF-03: la lista debe mostrar importes correctos de la compra")
        self.evidencia("compra_registrada")

        # 3. El mismo comprobante del proveedor no se registra dos veces.
        self.registrar_compra(principal, ruc, serie, numero)
        principal.esperar_texto("ErrorNuevaCompra", "ya está registrada")
        self.evidencia("compra_repetida")
        principal.clic("BotonCancelarCompra")

        # 4. Fecha futura: la rechaza ValidadorCompra.
        self.registrar_compra(principal, ruc, serie, numero + 1, fecha=date.today() + timedelta(days=3))
        principal.esperar_texto("ErrorNuevaCompra", "no puede ser posterior a hoy")

    def registrar_compra(self, p, ruc, serie, numero, fecha=None):
        p.clic("BotonNuevaCompra")
        p.visible("VentanaNuevaCompra")
        p.escribir("CampoCompraRuc", ruc)
        p.escribir("CampoCompraSerie", serie)
        p.escribir("CampoCompraNumero", str(numero))
        fecha = (fecha or date.today() - timedelta(days=1)).isoformat()
        self.driver.execute_script("arguments[0].value = arguments[1];", p.el("CampoCompraFecha"), fecha)
        for producto, cantidad, costo in (("cemento", 10, "15.50"), ("clavo", 2, "25.00")):
            p.escribir("CampoCompraProducto", producto)
            # DEF-07: esperar a que la lista corresponda a ESTA búsqueda; la anterior
            # sigue en el datalist mientras llega la respuesta.
            self.hasta(lambda d, t=producto: self.opciones_de(t))
            p.escribir("CampoCompraProducto", self.opciones_de(producto)[0])
            p.escribir("CampoCompraCantidad", str(cantidad))
            p.escribir("CampoCompraCosto", costo)
            p.clic("BotonAgregarLineaCompra")
        self.hasta(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#TablaLineasCompra tbody tr")) == 2)
        lineas = [f.text.lower() for f in self.driver.find_elements(By.CSS_SELECTOR, "#TablaLineasCompra tbody tr")]
        self.assertIn("cemento", lineas[0])
        self.assertIn("clavo", lineas[1], "DEF-07: la segunda línea debe ser el producto buscado")
        p.clic("BotonGuardarCompra")

    def opciones_de(self, texto):
        """Opciones del datalist que contienen el texto buscado."""
        valores = [o.get_attribute("value") for o in self.driver.find_elements(By.CSS_SELECTOR, "#ListaCompraProductos option")]
        return [v for v in valores if texto.lower() in v.lower()]


if __name__ == "__main__":
    unittest.main(verbosity=2)
