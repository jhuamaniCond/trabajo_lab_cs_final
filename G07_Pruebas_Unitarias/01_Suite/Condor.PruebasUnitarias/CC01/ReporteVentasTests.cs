using Condor.Dominio.Entidades;
using Condor.Dominio.Reportes;
using Condor.Dominio.Sunat;

namespace Condor.PruebasUnitarias.CC01;

/// <summary>
/// Componente 5: <see cref="ReporteVentas"/> (RF-15, CRQ-15; agregado por CC-01).
/// Las ventas se pasan como lista en memoria en lugar de leerlas de PostgreSQL.
/// </summary>
public class ReporteVentasTests
{
    private static readonly TimeSpan Peru = TimeSpan.FromHours(-5);

    private static VentaResumida Venta(int dia, string tipo, decimal total, string estado = EstadoSunat.Aceptado,
        string terminal = "CAJA-1", string usuario = "vendedor1", int hora = 10) =>
        new(new DateTimeOffset(2026, 11, dia, hora, 0, 0, Peru), tipo, total, Math.Round(total - total / 1.18m, 2), estado, terminal, usuario);

    [Fact]
    [Trait("Caso", "PU-25"), Trait("Requisito", "RF-15"), Trait("Riesgo", "R03")]
    public void PU_25_Proformas_no_suman_y_rechazados_se_cuentan_aparte()
    {
        var ventas = new[]
        {
            Venta(2, TipoComprobante.Boleta, 100.00m),
            Venta(2, TipoComprobante.Factura, 590.00m, terminal: "CAJA-2", usuario: "encargado"),
            Venta(3, TipoComprobante.NotaVenta, 50.00m),
            Venta(3, TipoComprobante.Proforma, 999.00m),                         // no es venta
            Venta(3, TipoComprobante.Boleta, 80.00m, estado: EstadoSunat.Rechazado), // no suma
            Venta(4, TipoComprobante.Boleta, 20.00m, estado: EstadoSunat.Pendiente),
        };

        var r = ReporteVentas.Consolidar(new DateOnly(2026, 11, 1), new DateOnly(2026, 11, 30), ventas);

        Assert.Equal(4, r.CantidadVentas);
        Assert.Equal(760.00m, r.Total);
        Assert.Equal(190.00m, r.TicketPromedio);
        Assert.Equal(1, r.Rechazados);
        Assert.Equal(1, r.PendientesSunat);
        Assert.Equal(new[] { "2026-11-02", "2026-11-03", "2026-11-04" }, r.PorDia.Select(l => l.Clave));
        Assert.Equal(new LineaReporte("Factura", 1, 590.00m), r.PorTipo[0]); // mayor total primero
        Assert.Equal(new LineaReporte("encargado", 1, 590.00m), r.PorUsuario[0]);
    }

    [Fact]
    [Trait("Caso", "PU-26"), Trait("Requisito", "CRQ-15"), Trait("Riesgo", "R11")]
    public void PU_26_Periodo_de_366_dias_se_acepta_y_de_367_o_al_reves_lanza_excepcion()
    {
        var desde = new DateOnly(2026, 1, 1);

        ReporteVentas.ValidarPeriodo(desde, desde.AddDays(365)); // 366 días: límite permitido
        ReporteVentas.ValidarPeriodo(desde, desde);              // un solo día

        var largo = Assert.Throws<ArgumentException>(() => ReporteVentas.ValidarPeriodo(desde, desde.AddDays(366)));
        Assert.Equal("El período no puede pasar de 366 días.", largo.Message);
        var reves = Assert.Throws<ArgumentException>(() => ReporteVentas.Consolidar(desde, desde.AddDays(-1), Array.Empty<VentaResumida>()));
        Assert.Equal("La fecha final no puede ser anterior a la inicial.", reves.Message);
    }

    [Fact]
    [Trait("Caso", "PU-27"), Trait("Requisito", "RF-15"), Trait("Riesgo", "R03")]
    public void PU_27_Las_ventas_se_agrupan_por_dia_de_Peru_y_no_por_dia_UTC()
    {
        // 22:00 del 1-nov en Majes = 03:00 del 2-nov en UTC.
        var nocturna = Venta(1, TipoComprobante.Boleta, 35.00m, hora: 22) with { Fecha = new DateTimeOffset(2026, 11, 2, 3, 0, 0, TimeSpan.Zero) };

        var soloDia1 = ReporteVentas.Consolidar(new DateOnly(2026, 11, 1), new DateOnly(2026, 11, 1), new[] { nocturna });
        var soloDia2 = ReporteVentas.Consolidar(new DateOnly(2026, 11, 2), new DateOnly(2026, 11, 2), new[] { nocturna });

        Assert.Equal(1, soloDia1.CantidadVentas);
        Assert.Equal("2026-11-01", Assert.Single(soloDia1.PorDia).Clave);
        Assert.Equal(0, soloDia2.CantidadVentas);
        Assert.Equal(0m, soloDia2.TicketPromedio);
    }
}
