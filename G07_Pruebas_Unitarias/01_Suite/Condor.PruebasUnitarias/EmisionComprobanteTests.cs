using Condor.Dominio.Entidades;
using Condor.Dominio.Ventas;
using Condor.PruebasUnitarias.Dobles;

namespace Condor.PruebasUnitarias;

/// <summary>
/// Componente 3: <see cref="EmisionComprobante"/> (RF-07, RF-08, CRQ-02,
/// CRQ-03, CRQ-06, CRQ-07). Reglas para emitir boletas, facturas y proformas.
/// </summary>
public class EmisionComprobanteTests
{
    [Fact]
    [Trait("Caso", "PU-13"), Trait("Requisito", "CRQ-02"), Trait("Riesgo", "R11")]
    public void PU_13_Boleta_de_exactamente_700_soles_se_emite_sin_DNI()
    {
        // Límite: 700.00 no es "mayor que S/ 700" y la boleta puede ir sin cliente.
        var solicitud = new SolicitudEmision(TipoEmision.Boleta, new[] { Datos.Linea(25m, 28.00m) });

        Assert.Empty(EmisionComprobante.Errores(solicitud));
        Assert.Equal(700.00m, EmisionComprobante.Preparar(solicitud).Total);
    }

    [Fact]
    [Trait("Caso", "PU-14"), Trait("Requisito", "CRQ-02"), Trait("Riesgo", "R11")]
    public void PU_14_Boleta_de_700_01_sin_DNI_se_rechaza()
    {
        // Límite + 1 céntimo.
        var solicitud = new SolicitudEmision(TipoEmision.Boleta, new[] { Datos.Linea(25m, 28.00m), Datos.Linea(1m, 0.01m, productoId: 2) });

        var error = Assert.Single(EmisionComprobante.Errores(solicitud));
        Assert.Equal(CampoEmision.Documento, error.Campo);
        Assert.Contains("deben llevar el DNI del cliente", error.Mensaje);
    }

    [Fact]
    [Trait("Caso", "PU-15"), Trait("Requisito", "CRQ-03"), Trait("Riesgo", "R11")]
    public void PU_15_Factura_a_un_cliente_con_DNI_lanza_ComprobanteInvalidoException()
    {
        var solicitud = new SolicitudEmision(TipoEmision.Factura, new[] { Datos.Linea(2m, 28.50m) }, Datos.ClienteDni());

        var ex = Assert.Throws<ComprobanteInvalidoException>(() => EmisionComprobante.Preparar(solicitud));

        var error = Assert.Single(ex.Errores);
        Assert.Equal(CampoEmision.Documento, error.Campo);
        Assert.Equal("La factura requiere un cliente con RUC: digítelo y presione Buscar.", error.Mensaje);
    }

    [Fact]
    [Trait("Caso", "PU-16"), Trait("Requisito", "CRQ-07"), Trait("Riesgo", "R03")]
    public void PU_16_Factura_valida_usa_F001_numera_lineas_y_recalcula_importes()
    {
        var cemento = Datos.Linea(10m, 28.50m);
        cemento.Importe = 1.00m; // importe manipulado por la terminal: debe ignorarse
        var fierro = Datos.Linea(4m, 42.90m, productoId: 2, descripcion: "FIERRO 1/2\" ACEROS AREQUIPA");

        var comprobante = EmisionComprobante.Preparar(
            new SolicitudEmision(TipoEmision.Factura, new[] { cemento, fierro }, Datos.ClienteRuc()));

        Assert.Equal("F001", comprobante.SerieCodigo);
        Assert.Equal(TipoComprobante.Factura, comprobante.TipoComprobante);
        Assert.Equal(9, comprobante.ClienteId);
        Assert.Equal(new[] { 1, 2 }, comprobante.Detalle.Select(l => l.Item));
        Assert.Equal(new[] { 285.00m, 171.60m }, comprobante.Detalle.Select(l => l.Importe));
        Assert.Equal(456.60m, comprobante.Total);
        Assert.Equal(386.95m, comprobante.OpGravada);
        Assert.Equal(69.65m, comprobante.Igv);
    }

    [Fact]
    [Trait("Caso", "PU-17"), Trait("Requisito", "CRQ-06"), Trait("Riesgo", "R03")]
    public void PU_17_Proforma_ya_convertida_no_se_convierte_otra_vez()
    {
        var solicitud = new SolicitudEmision(TipoEmision.Boleta, new[] { Datos.Linea(1m, 28.50m) },
            Proforma: Datos.Proforma(convertidaEn: "B001-00000045"));

        var error = Assert.Single(EmisionComprobante.Errores(solicitud));
        Assert.Equal(CampoEmision.Proforma, error.Campo);
        Assert.Equal("La proforma PR01-00000012 ya se convirtió en B001-00000045.", error.Mensaje);
    }

    [Fact]
    [Trait("Caso", "PU-18"), Trait("Requisito", "RF-08"), Trait("Riesgo", "R03")]
    public void PU_18_Proforma_vale_7_dias_contando_el_de_emision()
    {
        var emision = new DateOnly(2026, 11, 1);
        var proforma = Datos.Proforma();
        proforma.ValidaHasta = EmisionComprobante.VigenciaProforma(emision);

        Assert.Equal(new DateOnly(2026, 11, 7), proforma.ValidaHasta);
        Assert.False(proforma.Vencida(new DateOnly(2026, 11, 7))); // último día de vigencia
        Assert.True(proforma.Vencida(new DateOnly(2026, 11, 8)));  // día siguiente
        Assert.Equal("PR01", EmisionComprobante.SerieDe(TipoEmision.Proforma));
    }
}
