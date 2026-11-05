using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;

namespace Condor.PruebasUnitarias.CC01;

/// <summary>
/// Doble de prueba (falso + espía) de <see cref="IUsuarioRepositorio"/>:
/// guarda las cuentas en memoria en lugar de PostgreSQL y anota cada llamada
/// para que la prueba compruebe qué se habría escrito en la base.
/// </summary>
public sealed class RepositorioUsuariosFalso : IUsuarioRepositorio
{
    private readonly Dictionary<string, CuentaUsuario> _cuentas = new();

    public int Busquedas { get; private set; }

    public List<(long Id, int Intentos, DateTimeOffset? BloqueadoHasta)> Actualizaciones { get; } = new();

    public List<(string Usuario, string? Terminal, bool Exitoso, string Detalle)> Bitacora { get; } = new();

    public CuentaUsuario Agregar(string usuario, string clave, string rol = Roles.Vendedor, bool activo = true)
    {
        var cuenta = new CuentaUsuario
        {
            Id = _cuentas.Count + 1,
            NombreUsuario = usuario,
            NombreCompleto = usuario.ToUpperInvariant(),
            Rol = rol,
            Activo = activo,
            // Sal fija y 1 000 iteraciones: el hash es reproducible y la prueba
            // no tarda lo que tardan las 100 000 iteraciones de producción.
            HashClave = HashClave.Generar(clave, new byte[16], 1_000),
        };
        _cuentas[usuario] = cuenta;
        return cuenta;
    }

    public Task<CuentaUsuario?> BuscarAsync(string nombreUsuario, CancellationToken ct = default)
    {
        Busquedas++;
        return Task.FromResult(_cuentas.GetValueOrDefault(nombreUsuario));
    }

    public Task ActualizarIntentosAsync(long id, int intentosFallidos, DateTimeOffset? bloqueadoHasta, CancellationToken ct = default)
    {
        Actualizaciones.Add((id, intentosFallidos, bloqueadoHasta));
        return Task.CompletedTask;
    }

    public Task RegistrarAccesoAsync(string nombreUsuario, string? terminal, bool exitoso, string detalle, CancellationToken ct = default)
    {
        Bitacora.Add((nombreUsuario, terminal, exitoso, detalle));
        return Task.CompletedTask;
    }
}

/// <summary>Reloj controlado por la prueba (reemplaza a DateTimeOffset.UtcNow).</summary>
public sealed class RelojFalso
{
    public RelojFalso(DateTimeOffset inicio) => Ahora = inicio;

    public DateTimeOffset Ahora { get; private set; }

    public void Avanzar(TimeSpan tiempo) => Ahora += tiempo;

    public Func<DateTimeOffset> Funcion => () => Ahora;
}
