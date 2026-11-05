using Condor.Datos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;
using Condor.Dominio.Ventas;
using Condor.Pruebas.Infraestructura;
using Npgsql;

namespace Condor.Pruebas.Datos;

/// <summary>CC-01: cuentas, bitácora de accesos y reporte consolidado en PostgreSQL.</summary>
[Collection(BaseDatos.Nombre)]
public class UsuarioRepositorioTests
{
    private readonly BaseDatosFixture _bd;

    public UsuarioRepositorioTests(BaseDatosFixture bd) => _bd = bd;

    [FactConBD]
    public async Task Los_usuarios_de_demostracion_ingresan_con_su_clave()
    {
        var servicio = new ServicioAutenticacion(new UsuarioRepositorio(_bd.Conexiones));

        var encargado = await servicio.AutenticarAsync("encargado", "Encargado2026!", "PC-PRUEBA");

        Assert.True(encargado.Exitoso);
        Assert.Equal(Roles.Encargado, encargado.Cuenta!.Rol);
    }

    [FactConBD]
    public async Task El_bloqueo_queda_guardado_en_la_base_central()
    {
        var nombre = await CrearCuentaAsync();
        var repo = new UsuarioRepositorio(_bd.Conexiones);
        var servicio = new ServicioAutenticacion(repo);

        for (var i = 0; i < ServicioAutenticacion.IntentosMaximos; i++)
            await servicio.AutenticarAsync(nombre, "mal", "PC-PRUEBA");

        // Otra PC (otro servicio, mismo repositorio) también la ve bloqueada.
        var otraPc = await new ServicioAutenticacion(new UsuarioRepositorio(_bd.Conexiones)).AutenticarAsync(nombre, "Clave2026!", "PC-2");
        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, otraPc.Estado);
        Assert.NotNull((await repo.BuscarAsync(nombre))!.BloqueadoHasta);
        Assert.Equal(ServicioAutenticacion.IntentosMaximos + 1L, await ContarAsync(
            "SELECT count(*) FROM acceso_usuario WHERE nombre_usuario = @n AND NOT exitoso", nombre));
    }

    [FactConBD]
    public async Task Un_acceso_correcto_queda_en_la_bitacora_y_actualiza_el_ultimo_acceso()
    {
        var nombre = await CrearCuentaAsync();
        var repo = new UsuarioRepositorio(_bd.Conexiones);

        await new ServicioAutenticacion(repo).AutenticarAsync(nombre, "Clave2026!", "PC-PRUEBA");

        Assert.NotNull((await repo.BuscarAsync(nombre))!.UltimoAcceso);
        Assert.Equal(1L, await ContarAsync(
            "SELECT count(*) FROM acceso_usuario WHERE nombre_usuario = @n AND exitoso AND terminal = 'PC-PRUEBA'", nombre));
    }

    [FactConBD]
    public async Task La_base_rechaza_un_rol_desconocido()
    {
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand(
            "INSERT INTO usuario (nombre_usuario, nombre_completo, rol, hash_clave) VALUES (@n, 'X', 'ADMIN', 'x')", conexion);
        cmd.Parameters.AddWithValue("n", Nombre());

        var error = await Assert.ThrowsAsync<PostgresException>(() => cmd.ExecuteNonQueryAsync());
        Assert.Equal(PostgresErrorCodes.CheckViolation, error.SqlState);
    }

    [FactConBD]
    public async Task El_reporte_lee_las_ventas_del_dia_con_su_usuario_y_terminal()
    {
        var terminal = await new TerminalRepositorio(_bd.Conexiones).RegistrarAccesoAsync(DatosPrueba.NombreUnico("PC-REP"));
        var producto = await new ProductoRepositorio(_bd.Conexiones).RegistrarAsync(DatosPrueba.Nuevo(DatosPrueba.NombreUnico("Lija"), 2.50m));
        var boleta = EmisionComprobante.Preparar(new SolicitudEmision(TipoEmision.NotaVenta, new[]
        {
            new DetalleComprobante { ProductoId = producto.Id, Descripcion = producto.Nombre, Cantidad = 4, PrecioUnitario = 2.50m },
        }));
        boleta.TerminalId = terminal.Id;
        boleta.Usuario = "vendedor2";
        var emitida = await new ComprobanteRepositorio(_bd.Conexiones).EmitirAsync(boleta);
        var hoy = EmisionComprobante.FechaPeru(emitida.Fecha);

        var ventas = await new ReporteVentasRepositorio(_bd.Conexiones).VentasDelPeriodoAsync(hoy, hoy);

        Assert.Contains(ventas, v => v.Terminal == terminal.Nombre && v.Usuario == "vendedor2" && v.Total == 10m
                                     && v.TipoComprobante == TipoComprobante.NotaVenta);
    }

    private static string Nombre() => ("u" + Guid.NewGuid().ToString("N"))[..20];

    private async Task<string> CrearCuentaAsync()
    {
        var nombre = Nombre();
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand(
            "INSERT INTO usuario (nombre_usuario, nombre_completo, rol, hash_clave) VALUES (@n, 'Prueba', 'VENDEDOR', @h)", conexion);
        cmd.Parameters.AddWithValue("n", nombre);
        cmd.Parameters.AddWithValue("h", HashClave.Generar("Clave2026!", new byte[16], 1000));
        await cmd.ExecuteNonQueryAsync();
        return nombre;
    }

    private async Task<long> ContarAsync(string sql, string nombre)
    {
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand(sql, conexion);
        cmd.Parameters.AddWithValue("n", nombre);
        return (long)(await cmd.ExecuteScalarAsync())!;
    }
}
