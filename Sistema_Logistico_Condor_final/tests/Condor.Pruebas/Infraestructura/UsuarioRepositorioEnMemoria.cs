using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;

namespace Condor.Pruebas.Infraestructura;

/// <summary>Doble de prueba de las cuentas y la bitácora de accesos (CC-01).</summary>
public sealed class UsuarioRepositorioEnMemoria : IUsuarioRepositorio
{
    /// <summary>Iteraciones bajas para que las pruebas no tarden; el formato es el mismo.</summary>
    private const int IteracionesPrueba = 1_000;

    private readonly List<CuentaUsuario> _cuentas = new();

    public sealed record Acceso(string Usuario, string? Terminal, bool Exitoso, string Detalle);

    public List<Acceso> Bitacora { get; } = new();

    /// <summary>Si se asigna, BuscarAsync lanza esta excepción (para simular la red caída).</summary>
    public Exception? Error { get; set; }

    public CuentaUsuario Agregar(string usuario, string clave, string rol, bool activo = true)
    {
        var cuenta = new CuentaUsuario
        {
            Id = _cuentas.Count + 1,
            NombreUsuario = usuario,
            NombreCompleto = $"Usuario {usuario}",
            Rol = rol,
            HashClave = HashClave.Generar(clave, new byte[16], IteracionesPrueba),
            Activo = activo,
        };
        _cuentas.Add(cuenta);
        return cuenta;
    }

    /// <summary>Vendedor vendedor1 / Vendedor2026! y encargado / Encargado2026!, como los de V014.</summary>
    public static UsuarioRepositorioEnMemoria ConUsuariosDemo()
    {
        var repo = new UsuarioRepositorioEnMemoria();
        repo.Agregar("vendedor1", "Vendedor2026!", Roles.Vendedor);
        repo.Agregar("encargado", "Encargado2026!", Roles.Encargado);
        return repo;
    }

    public CuentaUsuario Cuenta(string usuario) => _cuentas.Single(c => c.NombreUsuario == usuario);

    public Task<CuentaUsuario?> BuscarAsync(string nombreUsuario, CancellationToken ct = default)
    {
        if (Error is not null)
            throw Error;
        // Copia, como haría la base de datos: el servicio no debe depender de modificar el objeto guardado.
        var cuenta = _cuentas.FirstOrDefault(c => c.NombreUsuario == nombreUsuario);
        return Task.FromResult(cuenta is null ? null : new CuentaUsuario
        {
            Id = cuenta.Id,
            NombreUsuario = cuenta.NombreUsuario,
            NombreCompleto = cuenta.NombreCompleto,
            Rol = cuenta.Rol,
            HashClave = cuenta.HashClave,
            Activo = cuenta.Activo,
            IntentosFallidos = cuenta.IntentosFallidos,
            BloqueadoHasta = cuenta.BloqueadoHasta,
            UltimoAcceso = cuenta.UltimoAcceso,
        });
    }

    public Task ActualizarIntentosAsync(long id, int intentosFallidos, DateTimeOffset? bloqueadoHasta, CancellationToken ct = default)
    {
        var cuenta = _cuentas.Single(c => c.Id == id);
        cuenta.IntentosFallidos = intentosFallidos;
        cuenta.BloqueadoHasta = bloqueadoHasta;
        return Task.CompletedTask;
    }

    public Task RegistrarAccesoAsync(string nombreUsuario, string? terminal, bool exitoso, string detalle, CancellationToken ct = default)
    {
        Bitacora.Add(new Acceso(nombreUsuario, terminal, exitoso, detalle));
        return Task.CompletedTask;
    }
}

/// <summary>Doble del lector del reporte consolidado: devuelve las ventas que se le den.</summary>
public sealed class ReporteVentasRepositorioEnMemoria : IReporteVentasRepositorio
{
    public List<Condor.Dominio.Reportes.VentaResumida> Ventas { get; } = new();

    public Task<IReadOnlyList<Condor.Dominio.Reportes.VentaResumida>> VentasDelPeriodoAsync(DateOnly desde, DateOnly hasta,
        CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<Condor.Dominio.Reportes.VentaResumida>>(Ventas.ToList());
}
