using Condor.Dominio.Ventas;

namespace Condor.PruebasUnitarias;

/// <summary>
/// Componente 1: <see cref="CalculadoraVenta"/> (RF-07, CRQ-01, CRQ-14).
/// Importes, operación gravada, IGV y total de un comprobante.
/// </summary>
public class CalculadoraVentaTests
{
    [Fact]
    [Trait("Caso", "PU-01"), Trait("Requisito", "RF-07"), Trait("Riesgo", "R03")]
    public void PU_01_Importe_valido_es_cantidad_por_precio()
    {
        var importe = CalculadoraVenta.Importe(3m, 28.50m);

        Assert.Equal(85.50m, importe);
    }

    [Theory]
    [Trait("Caso", "PU-02"), Trait("Requisito", "CRQ-01"), Trait("Riesgo", "R03")]
    [InlineData(2.345, 2.35)]   // el medio céntimo sube (redondeo comercial)
    [InlineData(2.344, 2.34)]   // por debajo del medio céntimo baja
    [InlineData(-2.345, -2.35)] // simétrico en negativos (alejándose de cero)
    public void PU_02_Redondeo_comercial_a_centimos_en_el_limite_de_medio_centimo(double monto, double esperado)
    {
        Assert.Equal((decimal)esperado, CalculadoraVenta.Redondear((decimal)monto));
        // 0.333 kg a S/ 10.15 = 3.37995 -> 3.38
        Assert.Equal(3.38m, CalculadoraVenta.Importe(0.333m, 10.15m));
    }

    [Fact]
    [Trait("Caso", "PU-03"), Trait("Requisito", "CRQ-01"), Trait("Riesgo", "R03")]
    public void PU_03_Totales_separan_IGV_del_precio_que_ya_lo_incluye()
    {
        // Ejemplo del wireframe de Nueva venta: 745.00 = 631.36 + 113.64
        var totales = CalculadoraVenta.Totales(new[] { 520.00m, 180.00m, 45.00m });

        Assert.Equal(745.00m, totales.Total);
        Assert.Equal(631.36m, totales.OpGravada);
        Assert.Equal(113.64m, totales.Igv);
        Assert.Equal(totales.Total, totales.OpGravada + totales.Igv);
    }

    [Fact]
    [Trait("Caso", "PU-04"), Trait("Requisito", "RF-07"), Trait("Riesgo", "R03")]
    public void PU_04_Venta_sin_lineas_tiene_totales_en_cero()
    {
        Assert.Equal(TotalesVenta.Cero, CalculadoraVenta.Totales(Array.Empty<decimal>()));
    }

    [Theory]
    [Trait("Caso", "PU-05"), Trait("Requisito", "CRQ-14"), Trait("Riesgo", "R03")]
    [InlineData(0)]       // límite: cero no es una cantidad válida
    [InlineData(-1)]
    [InlineData(-0.001)]  // límite: el menor negativo con tres decimales
    public void PU_05_Cantidad_cero_o_negativa_lanza_excepcion(double cantidad)
    {
        var ex = Assert.Throws<ArgumentOutOfRangeException>(() => CalculadoraVenta.Importe((decimal)cantidad, 10m));

        Assert.Equal("cantidad", ex.ParamName);
    }

    [Fact]
    [Trait("Caso", "PU-06"), Trait("Requisito", "CRQ-07"), Trait("Riesgo", "R03")]
    public void PU_06_Precio_cero_lanza_excepcion_y_el_menor_precio_positivo_se_acepta()
    {
        var ex = Assert.Throws<ArgumentOutOfRangeException>(() => CalculadoraVenta.Importe(1m, 0m));
        Assert.Equal("precioUnitario", ex.ParamName);

        Assert.Equal(0.01m, CalculadoraVenta.Importe(1m, 0.01m));
    }
}
