using Condor.Dominio.Entidades;
using Condor.Dominio.Sunat;
using Condor.Dominio.Ventas;

namespace Condor.Dominio.Reportes;

/// <summary>Una venta del período, sin detalle, tal como la lee el reporte.</summary>
public sealed record VentaResumida(DateTimeOffset Fecha, string TipoComprobante, decimal Total, decimal Igv, string EstadoSunat,
    string Terminal, string Usuario);

/// <summary>Una fila agrupada del reporte: por día, tipo, terminal o usuario.</summary>
public sealed record LineaReporte(string Clave, int Cantidad, decimal Total);

/// <summary>
/// Reporte consolidado de ventas del Encargado general (CC-01): cuántas
/// ventas hubo en el período, cuánto suman y cómo se reparten por día, tipo
/// de comprobante, terminal y usuario. Sigue la regla del Historial (HU-18):
/// las proformas no son ventas y los comprobantes rechazados por la SUNAT no
/// suman (se vuelven a emitir); los rechazados se cuentan aparte.
/// </summary>
public sealed class ReporteVentas
{
    /// <summary>Período más largo que se puede pedir (un año).</summary>
    public const int DiasMaximos = 366;

    private ReporteVentas(DateOnly desde, DateOnly hasta) => (Desde, Hasta) = (desde, hasta);

    public DateOnly Desde { get; }

    public DateOnly Hasta { get; }

    public int CantidadVentas { get; private init; }

    public decimal Total { get; private init; }

    public decimal Igv { get; private init; }

    public decimal OpGravada => Total - Igv;

    /// <summary>Total entre la cantidad de ventas, redondeado a céntimos; 0 sin ventas.</summary>
    public decimal TicketPromedio => CantidadVentas == 0 ? 0m : Math.Round(Total / CantidadVentas, 2, MidpointRounding.AwayFromZero);

    /// <summary>Boletas y facturas que aún esperan respuesta de la SUNAT.</summary>
    public int PendientesSunat { get; private init; }

    /// <summary>Comprobantes rechazados por la SUNAT en el período (no suman en el total).</summary>
    public int Rechazados { get; private init; }

    public IReadOnlyList<LineaReporte> PorDia { get; private init; } = Array.Empty<LineaReporte>();

    public IReadOnlyList<LineaReporte> PorTipo { get; private init; } = Array.Empty<LineaReporte>();

    public IReadOnlyList<LineaReporte> PorTerminal { get; private init; } = Array.Empty<LineaReporte>();

    public IReadOnlyList<LineaReporte> PorUsuario { get; private init; } = Array.Empty<LineaReporte>();

    /// <summary>Lanza ArgumentException si el período está al revés o pasa de <see cref="DiasMaximos"/> días.</summary>
    public static void ValidarPeriodo(DateOnly desde, DateOnly hasta)
    {
        if (hasta < desde)
            throw new ArgumentException("La fecha final no puede ser anterior a la inicial.");
        if (hasta.DayNumber - desde.DayNumber + 1 > DiasMaximos)
            throw new ArgumentException($"El período no puede pasar de {DiasMaximos} días.");
    }

    /// <summary>
    /// Arma el reporte con las ventas leídas. Las que caen fuera del período
    /// (en días de Perú) se ignoran.
    /// </summary>
    public static ReporteVentas Consolidar(DateOnly desde, DateOnly hasta, IEnumerable<VentaResumida> ventas)
    {
        ValidarPeriodo(desde, hasta);

        var delPeriodo = ventas
            .Where(v => v.TipoComprobante != TipoComprobante.Proforma)
            .Where(v => EmisionComprobante.FechaPeru(v.Fecha) is var dia && dia >= desde && dia <= hasta)
            .ToList();
        var validas = delPeriodo.Where(v => v.EstadoSunat != EstadoSunat.Rechazado).ToList();

        return new ReporteVentas(desde, hasta)
        {
            CantidadVentas = validas.Count,
            Total = validas.Sum(v => v.Total),
            Igv = validas.Sum(v => v.Igv),
            PendientesSunat = validas.Count(v => TipoComprobante.EsElectronico(v.TipoComprobante) && v.EstadoSunat == EstadoSunat.Pendiente),
            Rechazados = delPeriodo.Count - validas.Count,
            PorDia = Agrupar(validas, v => EmisionComprobante.FechaPeru(v.Fecha).ToString("yyyy-MM-dd"), ordenarPorClave: true),
            PorTipo = Agrupar(validas, v => NombreTipo(v.TipoComprobante)),
            PorTerminal = Agrupar(validas, v => v.Terminal),
            PorUsuario = Agrupar(validas, v => v.Usuario),
        };
    }

    public static string NombreTipo(string tipo) => tipo switch
    {
        TipoComprobante.Boleta => "Boleta",
        TipoComprobante.Factura => "Factura",
        TipoComprobante.NotaVenta => "Nota de venta",
        _ => tipo,
    };

    /// <summary>Por día, en orden de fecha; las demás agrupaciones, de mayor a menor total.</summary>
    private static IReadOnlyList<LineaReporte> Agrupar(IEnumerable<VentaResumida> ventas, Func<VentaResumida, string> clave,
        bool ordenarPorClave = false)
    {
        var grupos = ventas.GroupBy(clave).Select(g => new LineaReporte(g.Key, g.Count(), g.Sum(v => v.Total)));
        return (ordenarPorClave
            ? grupos.OrderBy(l => l.Clave, StringComparer.Ordinal)
            : grupos.OrderByDescending(l => l.Total).ThenBy(l => l.Clave, StringComparer.Ordinal)).ToList();
    }
}
