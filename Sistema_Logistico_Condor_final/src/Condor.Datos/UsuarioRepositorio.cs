using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Npgsql;

namespace Condor.Datos;

/// <summary>
/// Cuentas de usuario y bitácora de accesos en la base de datos central
/// (CC-01, migración V014). Las reglas del ingreso están en
/// Condor.Dominio.Seguridad.ServicioAutenticacion; aquí solo se lee y se anota.
/// </summary>
public sealed class UsuarioRepositorio : IUsuarioRepositorio
{
    private readonly FabricaConexiones _conexiones;

    public UsuarioRepositorio(FabricaConexiones conexiones) => _conexiones = conexiones;

    public async Task<CuentaUsuario?> BuscarAsync(string nombreUsuario, CancellationToken ct = default)
    {
        await using var conexion = await _conexiones.AbrirAsync(ct);
        await using var cmd = new NpgsqlCommand(
            """
            SELECT id, nombre_usuario, nombre_completo, rol, hash_clave, activo, intentos_fallidos,
                   bloqueado_hasta, ultimo_acceso
            FROM usuario
            WHERE nombre_usuario = @nombre
            """, conexion);
        cmd.Parameters.AddWithValue("nombre", nombreUsuario);

        await using var lector = await cmd.ExecuteReaderAsync(ct);
        if (!await lector.ReadAsync(ct))
            return null;

        return new CuentaUsuario
        {
            Id = lector.GetInt64(0),
            NombreUsuario = lector.GetString(1),
            NombreCompleto = lector.GetString(2),
            Rol = lector.GetString(3),
            HashClave = lector.GetString(4),
            Activo = lector.GetBoolean(5),
            IntentosFallidos = lector.GetInt32(6),
            BloqueadoHasta = lector.IsDBNull(7) ? null : lector.GetFieldValue<DateTimeOffset>(7),
            UltimoAcceso = lector.IsDBNull(8) ? null : lector.GetFieldValue<DateTimeOffset>(8),
        };
    }

    public async Task ActualizarIntentosAsync(long id, int intentosFallidos, DateTimeOffset? bloqueadoHasta, CancellationToken ct = default)
    {
        await using var conexion = await _conexiones.AbrirAsync(ct);
        await using var cmd = new NpgsqlCommand(
            "UPDATE usuario SET intentos_fallidos = @intentos, bloqueado_hasta = @hasta WHERE id = @id", conexion);
        cmd.Parameters.AddWithValue("id", id);
        cmd.Parameters.AddWithValue("intentos", intentosFallidos);
        cmd.Parameters.AddWithValue("hasta", (object?)bloqueadoHasta ?? DBNull.Value);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    public async Task RegistrarAccesoAsync(string nombreUsuario, string? terminal, bool exitoso, string detalle,
        CancellationToken ct = default)
    {
        await using var conexion = await _conexiones.AbrirAsync(ct);
        await using var lote = new NpgsqlBatch(conexion);

        var bitacora = new NpgsqlBatchCommand(
            """
            INSERT INTO acceso_usuario (nombre_usuario, terminal, exitoso, detalle)
            VALUES (left(@nombre, 20), left(@terminal, 60), @exitoso, left(@detalle, 200))
            """);
        bitacora.Parameters.AddWithValue("nombre", nombreUsuario);
        bitacora.Parameters.AddWithValue("terminal", (object?)terminal ?? DBNull.Value);
        bitacora.Parameters.AddWithValue("exitoso", exitoso);
        bitacora.Parameters.AddWithValue("detalle", detalle);
        lote.BatchCommands.Add(bitacora);

        if (exitoso)
        {
            var ultimo = new NpgsqlBatchCommand("UPDATE usuario SET ultimo_acceso = now() WHERE nombre_usuario = @nombre");
            ultimo.Parameters.AddWithValue("nombre", nombreUsuario);
            lote.BatchCommands.Add(ultimo);
        }

        await lote.ExecuteNonQueryAsync(ct);
    }
}
