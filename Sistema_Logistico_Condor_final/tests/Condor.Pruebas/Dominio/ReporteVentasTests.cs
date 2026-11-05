using Condor.Dominio.Entidades;
using Condor.Dominio.Reportes;
using Condor.Dominio.Sunat;

namespace Condor.Pruebas.Dominio;

/// <summary>CC-01: reporte consolidado de ventas del Encargado general.</summary>
public class ReporteVentasTests
{
    private static readonly DateOnly Dia20 = new(2026, 11, 20);
    private static readonly DateOnly Dia21 = new(2026, 11, 21);

    /// <summary>Instante en hora de Perú (UTC-5).</summary>
    private static DateTimeOffset Peru(int dia, int hora) => new(2026, 11, dia, hora, 0, 0, TimeSpan.FromHours(-5));

    private static VentaResumida Venta(DateTimeOffset fecha, string tipo, decimal total, string estado = EstadoSunat.Aceptado,
        string terminal = "PC-1", string usuario = "vendedor1") =>
        new(fecha, tipo, total, Math.Round(total * 18 / 118, 2), estado, terminal, usuario);

    [Fact]
    public void Suma_las_ventas_y_las_agrupa_por_dia_tipo_terminal_y_usuario()
    {
        var reporte = ReporteVentas.Consolidar(Dia20, Dia21, new[]
        {
            Venta(Peru(20, 9), TipoComprobante.Boleta, 118m),
            Venta(Peru(20, 10), TipoComprobante.Factura, 236m, terminal: "PC-2", usuario: "encargado"),
            Venta(Peru(21, 11), TipoComprobante.NotaVenta, 50m, estado: EstadoSunat.Pendiente),
        });

        Assert.Equal(3, reporte.CantidadVentas);
        Assert.Equal(404m, reporte.Total);
        Assert.Equal(reporte.Total - reporte.Igv, reporte.OpGravada);
        Assert.Equal(134.67m, reporte.TicketPromedio);
        Assert.Equal(new[] { "2026-11-20", "2026-11-21" }, reporte.PorDia.Select(l => l.Clave));
        Assert.Equal(354m, reporte.PorDia[0].Total);
        Assert.Equal(new[] { "Factura", "Boleta", "Nota de venta" }, reporte.PorTipo.Select(l => l.Clave));
        Assert.Equal(new LineaReporte("PC-2", 1, 236m), reporte.PorTerminal[0]);
        Assert.Equal(2, reporte.PorUsuario.Single(l => l.Clave == "vendedor1").Cantidad);
    }

    [Fact]
    public void Las_proformas_no_son_ventas_y_los_rechazados_se_cuentan_aparte()
    {
        var reporte = ReporteVentas.Consolidar(Dia20, Dia20, new[]
        {
            Venta(Peru(20, 9), TipoComprobante.Boleta, 100m),
            Venta(Peru(20, 9), TipoComprobante.Proforma, 900m),
            Venta(Peru(20, 9), TipoComprobante.Factura, 500m, estado: EstadoSunat.Rechazado),
        });

        Assert.Equal(1, reporte.CantidadVentas);
        Assert.Equal(100m, reporte.Total);
        Assert.Equal(1, reporte.Rechazados);
    }

    [Fact]
    public void Cuenta_las_boletas_y_facturas_pendientes_pero_no_las_notas_de_venta()
    {
        var reporte = ReporteVentas.Consolidar(Dia20, Dia20, new[]
        {
            Venta(Peru(20, 9), TipoComprobante.Boleta, 10m, EstadoSunat.Pendiente),
            Venta(Peru(20, 9), TipoComprobante.NotaVenta, 10m, EstadoSunat.Pendiente),
            Venta(Peru(20, 9), TipoComprobante.Factura, 10m, EstadoSunat.Observado),
        });

        Assert.Equal(1, reporte.PendientesSunat);
        Assert.Equal(3, reporte.CantidadVentas);
    }

    [Fact]
    public void Los_limites_del_periodo_se_cuentan_en_dias_de_Peru()
    {
        // 23:30 del 20 en Perú es 04:30 UTC del 21: es venta del 20.
        var nocheDel20 = Peru(20, 23).AddMinutes(30);
        var reporte = ReporteVentas.Consolidar(Dia20, Dia20, new[]
        {
            Venta(nocheDel20, TipoComprobante.Boleta, 30m),
            Venta(Peru(21, 0), TipoComprobante.Boleta, 99m),
            Venta(Peru(19, 23), TipoComprobante.Boleta, 99m),
        });

        Assert.Equal(1, reporte.CantidadVentas);
        Assert.Equal(30m, reporte.Total);
    }

    [Fact]
    public void Sin_ventas_todo_queda_en_cero()
    {
        var reporte = ReporteVentas.Consolidar(Dia20, Dia21, Array.Empty<VentaResumida>());

        Assert.Equal(0, reporte.CantidadVentas);
        Assert.Equal(0m, reporte.Total);
        Assert.Equal(0m, reporte.TicketPromedio);
        Assert.Empty(reporte.PorDia);
    }

    [Fact]
    public void Un_periodo_al_reves_se_rechaza()
    {
        Assert.Throws<ArgumentException>(() => ReporteVentas.Consolidar(Dia21, Dia20, Array.Empty<VentaResumida>()));
    }

    [Fact]
    public void El_periodo_puede_ser_de_un_anio_pero_no_mas()
    {
        var inicio = new DateOnly(2026, 1, 1);

        ReporteVentas.ValidarPeriodo(inicio, inicio.AddDays(ReporteVentas.DiasMaximos - 1));
        Assert.Throws<ArgumentException>(() => ReporteVentas.ValidarPeriodo(inicio, inicio.AddDays(ReporteVentas.DiasMaximos)));
    }
}
