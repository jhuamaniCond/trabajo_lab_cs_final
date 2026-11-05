"""Registro válido y datos inválidos: clientes y productos."""
import unittest

from selenium.webdriver.support import expected_conditions as EC

import datos
from comun import PruebaWeb
from paginas import PaginaCatalogo, PaginaClientes, PaginaIngresar, PaginaPrincipal, PaginaVenta


class CP04_RegistroValidoCliente(PruebaWeb):
    caso, requisitos = "CP-04", "RF-06"

    def test_registra_un_cliente_con_dni_y_se_encuentra_en_la_venta(self):
        dni, nombre = datos.dni_nuevo(), datos.nombre_cliente()
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        principal.ir_a("Clientes")
        clientes = PaginaClientes(self.driver)

        clientes.nuevo_cliente(dni, nombre, "Av. Prueba 123, Majes")

        self.hasta(EC.invisibility_of_element_located(("id", "VentanaNuevoCliente")))
        principal.esperar_texto("TextoMensaje", f"Cliente {nombre} registrado.")
        self.hasta(lambda d: len(clientes.filas()) == 1 and dni in clientes.filas()[0].text)
        self.assertIn(nombre, clientes.filas()[0].text)
        self.evidencia("cliente_registrado")

        # Persistencia: en Nueva venta, el DNI encuentra al cliente recién registrado.
        principal.ir_a("Venta")
        venta = PaginaVenta(self.driver)
        venta.buscar_cliente(dni)
        venta.esperar_texto("ClienteNombre", nombre)
        self.assertEqual(f"DNI {dni}", venta.texto("ClienteDocumento"))
        self.assertEqual("TipoConDni", venta.tipo_elegido())
        self.evidencia("cliente_en_la_venta")


class CP05_DatosInvalidos(PruebaWeb):
    caso, requisitos = "CP-05", "RF-06, RF-04, RF-05"

    def test_rechaza_documentos_precio_y_cantidad_invalidos(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        venta = PaginaVenta(self.driver)

        # DNI con menos de 8 dígitos: el campo se marca en rojo y no se consulta.
        venta.buscar_cliente(datos.DNI_CORTO)
        self.assertEqual("El documento debe ser un DNI de 8 dígitos o un RUC de 11.", venta.texto("ErrorCliente"))
        self.assertIn("invalido", venta.el("CampoDocumento").get_attribute("class"))
        self.evidencia("dni_invalido")

        # Documento válido pero no registrado.
        venta.buscar_cliente(datos.dni_nuevo())
        venta.esperar_texto("TextoSinCliente", "Ese documento no está registrado")

        # Cantidad cero.
        venta.buscar_producto(datos.PRODUCTO_BUSQUEDA)
        venta.el("CampoProducto").send_keys("")
        venta.escribir("CampoCantidad", datos.CANTIDAD_INVALIDA)
        venta.clic("BotonAgregar")
        venta.esperar_texto("ErrorVenta", "La cantidad debe ser mayor que cero")
        self.assertEqual(0, len(venta.lineas()))

        # Nuevo cliente con RUC de dígito verificador errado: lo rechaza el servidor.
        clientes = PaginaClientes(self.driver)
        clientes.nuevo_cliente(datos.ruc_digito_errado(), "Empresa Inválida S.A.C.", desde_venta=True)
        clientes.esperar_texto("ErrorNuevoCliente", "el dígito verificador no coincide")
        self.assertTrue(clientes.esta_visible("VentanaNuevoCliente"))
        self.evidencia("ruc_invalido")
        clientes.clic("BotonCancelarCliente")

        # Nuevo producto con precio cero.
        principal.ir_a("Catalogo")
        catalogo = PaginaCatalogo(self.driver)
        catalogo.nuevo_producto(datos.nombre_producto(), datos.PRECIO_CERO)
        catalogo.esperar_texto("ErrorNuevoProducto", "El precio debe ser mayor que cero.")
        self.evidencia("precio_invalido")

        # Nuevo producto sin nombre.
        catalogo.escribir("CampoNombreProducto", "")
        catalogo.escribir("CampoPrecioProducto", "10.50")
        catalogo.clic("BotonGuardarProducto")
        catalogo.esperar_texto("ErrorNuevoProducto", "El nombre es obligatorio.")


class CP06_RegistroValidoProducto(PruebaWeb):
    caso, requisitos = "CP-06", "RF-04, RF-05"

    def test_registra_un_producto_y_se_vende_con_su_precio(self):
        nombre = datos.nombre_producto()
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        principal.ir_a("Catalogo")
        catalogo = PaginaCatalogo(self.driver)

        catalogo.nuevo_producto(nombre, "12.35", "KG")

        principal.esperar_texto("TextoMensaje", f"Producto «{nombre}» registrado")
        self.hasta(lambda d: len(catalogo.filas()) == 1 and nombre in catalogo.filas()[0].text)
        fila = catalogo.filas()[0].text
        self.assertIn("KG", fila)
        self.assertIn("S/ 12.35", fila)
        self.evidencia("producto_registrado")

        # La venta lo encuentra en la búsqueda y toma el precio del catálogo.
        principal.ir_a("Venta")
        venta = PaginaVenta(self.driver)
        venta.agregar_primera_sugerencia(nombre, 2)
        linea = venta.esperar_lineas(1)[0]
        self.assertIn(nombre, linea.text)
        self.assertEqual("S/ 24.70", venta.total())


if __name__ == "__main__":
    unittest.main(verbosity=2)
