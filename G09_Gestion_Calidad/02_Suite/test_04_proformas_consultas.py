"""PN-02 Cotización y conversión (cambio de estado) y consultas: historial y reporte."""
import re
import unittest
from datetime import date, timedelta

from selenium.webdriver.common.by import By

import datos
from comun import PruebaWeb
from paginas import PaginaClientes, PaginaHistorial, PaginaIngresar, PaginaPrincipal, PaginaProformas, PaginaVenta


class CP10_CambioDeEstadoProforma(PruebaWeb):
    caso, requisitos = "CP-10", "RF-08, RF-07"

    def test_proforma_vigente_pasa_a_convertida_y_no_se_convierte_dos_veces(self):
        dni, nombre = datos.dni_nuevo(), datos.nombre_cliente()
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        venta = PaginaVenta(self.driver)

        # 1. Emitir la proforma (cotización) para un cliente nuevo.
        venta.agregar_primera_sugerencia(datos.PRODUCTO_BUSQUEDA, 5)
        venta.esperar_lineas(1)
        total_cotizado = venta.total()
        PaginaClientes(self.driver).nuevo_cliente(dni, nombre, desde_venta=True)
        venta.esperar_texto("ClienteNombre", nombre)
        venta.elegir_tipo("TipoProforma")
        venta.emitir()
        resultado = venta.esperar_texto("TextoResultadoEmision", "emitida")
        proforma = re.search(r"Proforma (PR01-\d{8})", resultado).group(1)

        # 2. Estado inicial: VIGENTE (7 días contando el de emisión).
        principal.ir_a("Proformas")
        proformas = PaginaProformas(self.driver)
        proformas.buscar(dni)
        vigencia = (date.today() + timedelta(days=6)).strftime("%d/%m/%Y")
        self.hasta(lambda d: proformas.estado(proforma) == f"Vigente hasta el {vigencia}")
        self.assertIn("estado-vigente", proformas.fila(proforma).find_element(By.CSS_SELECTOR, "td.estado").get_attribute("class"))
        self.evidencia("proforma_vigente")

        # 3. Convertir en venta: el detalle y el cliente pasan a Nueva venta.
        proformas.fila(proforma).click()
        proformas.clic("BotonConvertir")
        venta.visible("ModuloVenta")
        venta.esperar_texto("TextoAvisoProforma", f"Venta desde la proforma {proforma}")
        self.assertEqual(total_cotizado, venta.total())
        self.assertEqual(nombre, venta.texto("ClienteNombre"))
        self.assertEqual("TipoConDni", venta.tipo_elegido())
        self.assertFalse(venta.el("CampoProducto").is_enabled(), "el detalle de la proforma no se cambia")
        self.assertFalse(venta.esta_visible("ResultadoEmision"), "DEF-04: no debe quedar el aviso de la emisión anterior")
        self.evidencia("proforma_en_venta")
        venta.emitir()
        boleta = re.search(r"Boleta (B001-\d{8}) emitida", venta.esperar_texto("TextoResultadoEmision", "emitida")).group(1)

        # 4. Estado final: CONVERTIDA, con el número de la boleta.
        principal.ir_a("Proformas")
        proformas.buscar(dni)
        self.hasta(lambda d: proformas.estado(proforma) == f"Convertida en {boleta}")
        self.evidencia("proforma_convertida")

        # 5. Una proforma convertida no se vuelve a convertir.
        proformas.fila(proforma).click()
        self.assertFalse(proformas.el("BotonConvertir").is_enabled())
        principal.esperar_texto("TextoMensaje", f"ya se convirtió en {boleta}")


class CP11_ConsultaHistorial(PruebaWeb):
    caso, requisitos = "CP-11", "RF-14"

    def test_filtra_por_tipo_y_rechaza_un_periodo_invertido(self):
        PaginaIngresar(self.driver).ingresar(*datos.VENDEDOR)
        principal = PaginaPrincipal(self.driver).esperar()
        principal.ir_a("Historial")
        historial = PaginaHistorial(self.driver)

        historial.clic("BotonTodo")
        self.hasta(lambda d: "comprobantes" in historial.texto("TextoHistorial"))
        todos = int(re.match(r"(\d+)", historial.texto("TextoHistorial")).group(1))

        historial.el("FiltroTipo").send_keys("Facturas")
        historial.buscar()
        self.hasta(lambda d: historial.filas() and all(f.text.startswith("Factura") for f in historial.filas()))
        resumen = historial.texto("TextoHistorial")
        facturas = int(re.match(r"(\d+)", resumen).group(1))
        self.assertLess(facturas, todos)
        self.assertRegex(resumen, r"Total del período S/ [\d.]+$")
        self.evidencia("historial_facturas")

        # Desde posterior a Hasta: lo rechaza la API con su mensaje.
        historial.fechas("2026-11-30", "2026-11-01")
        historial.buscar()
        historial.esperar_texto("ErrorHistorial", "La fecha final no puede ser anterior a la inicial.")
        self.assertEqual(0, len(historial.filas()))
        self.evidencia("periodo_invertido")


class CP12_ReporteConsolidado(PruebaWeb):
    caso, requisitos = "CP-12", "RF-15, RF-03"

    def test_el_encargado_genera_el_reporte_del_periodo(self):
        PaginaIngresar(self.driver).ingresar(*datos.ENCARGADO)
        principal = PaginaPrincipal(self.driver).esperar()
        principal.ir_a("Reporte")

        self.hasta(lambda d: principal.esta_visible("ResultadoReporte"))
        for id_, valor in (("ReporteDesde", "2026-10-01"), ("ReporteHasta", date.today().isoformat())):
            self.driver.execute_script("arguments[0].value = arguments[1];", principal.el(id_), valor)
        principal.clic("BotonGenerarReporte")
        self.hasta(lambda d: int(principal.texto("ReporteCantidad") or 0) > 0)

        cantidad = int(principal.texto("ReporteCantidad"))
        total = float(principal.texto("ReporteTotal").replace("S/", ""))
        por_tipo = self.driver.find_elements(By.CSS_SELECTOR, "#TablaReporteTipo tbody tr")
        suma_tipos = sum(float(f.find_elements(By.TAG_NAME, "td")[2].text.replace("S/", "")) for f in por_tipo)
        suma_cantidades = sum(int(f.find_elements(By.TAG_NAME, "td")[1].text) for f in por_tipo)
        self.assertAlmostEqual(total, suma_tipos, places=2)
        self.assertEqual(cantidad, suma_cantidades)
        self.assertTrue(self.driver.find_elements(By.CSS_SELECTOR, "#TablaReporteUsuario tbody tr"))
        self.evidencia("reporte_consolidado")

        # Período de más de 366 días: lo rechaza la regla de ReporteVentas.
        self.driver.execute_script("arguments[0].value = '2024-01-01';", principal.el("ReporteDesde"))
        principal.clic("BotonGenerarReporte")
        self.hasta(lambda d: principal.esta_visible("ErrorReporte"))
        self.assertFalse(principal.esta_visible("ResultadoReporte"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
