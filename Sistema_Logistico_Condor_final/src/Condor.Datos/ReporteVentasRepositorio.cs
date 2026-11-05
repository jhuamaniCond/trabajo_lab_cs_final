using Condor.Dominio.Contratos;
using Condor.Dominio.Reportes;
using Npgsql;

namespace Condor.Datos;

/// <summary>
/// Lee las ventas de un período para el reporte consolidado (CC-01). Las
/// sumas y agrupaciones las hace Condor.Dominio.Reportes.ReporteVentas, así
/// se prueban sin base de datos.
/// </summary>
public sealed class ReporteVentasRepositorio : IReporteVentasRepositorio
{
    private readonly FabricaConexiones _conexiones;

    public ReporteVentasRepositorio(FabricaConexiones conexiones) => _conexiones = conexiones;

    public async Task<IReadOnlyList<VentaResumida>> VentasDelPeriodoAsync(DateOnly desde, DateOnly hasta, CancellationToken ct = default)
    {
        ReporteVentas.ValidarPeriodo(desde, hasta);

        await using var conexion = await _conexiones.AbrirAsync(ct);
        // Días de Perú, igual que el Historial (HU-18): usa ix_comprobante_fecha.
        await using var cmd = new NpgsqlCommand(
            """
            SELECT c.fecha, s.tipo_comprobante, c.total, c.igv, c.estado_sunat, t.nombre, c.usuario
            FROM comprobante c
            JOIN serie s ON s.id = c.serie_id
            JOIN terminal t ON t.id = c.terminal_id
            WHERE c.fecha >= (@desde::date)::timestamp AT TIME ZONE 'America/Lima'
              AND c.fecha < (@hasta::date + 1)::timestamp AT TIME ZONE 'America/Lima'
              AND s.tipo_comprobante <> 'PR'
            ORDER BY c.fecha
            """, conexion);
        cmd.Parameters.Add(new NpgsqlParameter("desde", NpgsqlTypes.NpgsqlDbType.Date) { Value = desde });
        cmd.Parameters.Add(new NpgsqlParameter("hasta", NpgsqlTypes.NpgsqlDbType.Date) { Value = hasta });

        var ventas = new List<VentaResumida>();
        await using var lector = await cmd.ExecuteReaderAsync(ct);
        while (await lector.ReadAsync(ct))
        {
            ventas.Add(new VentaResumida(
                lector.GetFieldValue<DateTimeOffset>(0),
                lector.GetString(1),
                lector.GetDecimal(2),
                lector.GetDecimal(3),
                lector.GetString(4),
                lector.GetString(5),
                lector.GetString(6)));
        }
        return ventas;
    }
}
