using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Ventas;

namespace Condor.Dominio.Seguridad;

public enum EstadoAutenticacion
{
    Exitoso,

    /// <summary>Falta el usuario o la contraseña.</summary>
    DatosIncompletos,

    /// <summary>Usuario inexistente, inactivo o contraseña equivocada (mismo mensaje para no revelar cuál).</summary>
    CredencialesInvalidas,

    /// <summary>Demasiados intentos fallidos: la cuenta espera <see cref="ServicioAutenticacion.DuracionBloqueo"/>.</summary>
    CuentaBloqueada,
}

/// <summary>
/// Quien comprueba usuario y contraseña: <see cref="ServicioAutenticacion"/>
/// contra la base de datos (lo usa la API) o el cliente HTTP de la app de
/// escritorio, que llama a POST /api/auth/login.
/// </summary>
public interface IAutenticador
{
    Task<ResultadoAutenticacion> AutenticarAsync(string? usuario, string? clave, string? terminal, CancellationToken ct = default);
}

public sealed record ResultadoAutenticacion(EstadoAutenticacion Estado, CuentaUsuario? Cuenta, string Mensaje)
{
    public bool Exitoso => Estado == EstadoAutenticacion.Exitoso;
}

/// <summary>
/// Ingreso con usuario y contraseña (CC-01). Lo usan la app de escritorio y
/// la API. Reglas:
/// <list type="bullet">
/// <item>Usuario o contraseña vacíos: no se consulta la base de datos.</item>
/// <item>Usuario inexistente, inactivo o contraseña equivocada: el mismo mensaje.</item>
/// <item><see cref="IntentosMaximos"/> contraseñas equivocadas seguidas bloquean la cuenta
/// <see cref="DuracionBloqueo"/>, aunque luego se escriba la correcta.</item>
/// <item>Un acceso correcto reinicia la cuenta de intentos.</item>
/// <item>Cada intento, correcto o no, queda en la bitácora de accesos.</item>
/// </list>
/// </summary>
public sealed class ServicioAutenticacion : IAutenticador
{
    public const int IntentosMaximos = 5;
    public static readonly TimeSpan DuracionBloqueo = TimeSpan.FromMinutes(15);

    public const string MensajeInvalidas = "Usuario o contraseña incorrectos.";

    private readonly IUsuarioRepositorio _usuarios;
    private readonly Func<DateTimeOffset> _ahora;

    public ServicioAutenticacion(IUsuarioRepositorio usuarios, Func<DateTimeOffset>? ahora = null)
    {
        _usuarios = usuarios;
        _ahora = ahora ?? (() => DateTimeOffset.UtcNow);
    }

    /// <summary>Los nombres de usuario no distinguen mayúsculas ni espacios alrededor.</summary>
    public static string Normalizar(string? usuario) => usuario?.Trim().ToLowerInvariant() ?? string.Empty;

    public async Task<ResultadoAutenticacion> AutenticarAsync(string? usuario, string? clave, string? terminal,
        CancellationToken ct = default)
    {
        var nombre = Normalizar(usuario);
        if (nombre.Length == 0 || string.IsNullOrEmpty(clave))
            return new(EstadoAutenticacion.DatosIncompletos, null, "Ingrese su usuario y su contraseña.");

        var cuenta = await _usuarios.BuscarAsync(nombre, ct);
        var ahora = _ahora();

        if (cuenta is null || !cuenta.Activo)
        {
            await _usuarios.RegistrarAccesoAsync(nombre, terminal, false, cuenta is null ? "usuario inexistente" : "cuenta inactiva", ct);
            return Invalidas();
        }

        if (cuenta.EstaBloqueada(ahora))
        {
            await _usuarios.RegistrarAccesoAsync(nombre, terminal, false, "cuenta bloqueada", ct);
            return Bloqueada(cuenta.BloqueadoHasta!.Value);
        }

        if (!HashClave.Verificar(clave, cuenta.HashClave))
        {
            var intentos = cuenta.IntentosFallidos + 1;
            DateTimeOffset? bloqueadoHasta = null;
            if (intentos >= IntentosMaximos)
            {
                bloqueadoHasta = ahora + DuracionBloqueo;
                intentos = 0;
            }

            cuenta.IntentosFallidos = intentos;
            cuenta.BloqueadoHasta = bloqueadoHasta;
            await _usuarios.ActualizarIntentosAsync(cuenta.Id, intentos, bloqueadoHasta, ct);
            await _usuarios.RegistrarAccesoAsync(nombre, terminal, false,
                bloqueadoHasta is null ? "contraseña incorrecta" : "contraseña incorrecta; cuenta bloqueada", ct);
            return bloqueadoHasta is { } hasta ? Bloqueada(hasta) : Invalidas();
        }

        if (cuenta.IntentosFallidos > 0 || cuenta.BloqueadoHasta is not null)
        {
            cuenta.IntentosFallidos = 0;
            cuenta.BloqueadoHasta = null;
            await _usuarios.ActualizarIntentosAsync(cuenta.Id, 0, null, ct);
        }
        cuenta.UltimoAcceso = ahora;
        await _usuarios.RegistrarAccesoAsync(nombre, terminal, true, "acceso correcto", ct);
        return new(EstadoAutenticacion.Exitoso, cuenta, $"Bienvenido, {cuenta.NombreCompleto}.");
    }

    private static ResultadoAutenticacion Invalidas() => new(EstadoAutenticacion.CredencialesInvalidas, null, MensajeInvalidas);

    private static ResultadoAutenticacion Bloqueada(DateTimeOffset hasta) => new(EstadoAutenticacion.CuentaBloqueada, null,
        $"Cuenta bloqueada por {IntentosMaximos} intentos fallidos. Intente de nuevo a las {hasta.ToOffset(EmisionComprobante.HoraPeru):HH:mm}.");
}
