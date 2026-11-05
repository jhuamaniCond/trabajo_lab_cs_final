using Condor.Dominio.Seguridad;

namespace Condor.Dominio.Entidades;

/// <summary>
/// Perfil de los documentos emitidos antes de CC-01, cuando el sistema no
/// pedía usuario ni contraseña (HU-14). Es también el usuario de una sesión
/// sin cuenta, que solo usan las pruebas de los módulos sin ingreso.
/// </summary>
public static class Perfiles
{
    public const string Maestro = "MAESTRO";
}

/// <summary>
/// Sesión de trabajo en una PC: la cuenta que ingresó con su contraseña
/// (CC-01) y la terminal desde la que se abrió el sistema (HU-14).
/// </summary>
public sealed class Sesion
{
    public Sesion(Terminal terminal, CuentaUsuario? cuenta = null)
    {
        Terminal = terminal;
        Cuenta = cuenta;
    }

    public Terminal Terminal { get; }

    /// <summary>Quién ingresó; null en una sesión sin ingreso (solo pruebas).</summary>
    public CuentaUsuario? Cuenta { get; }

    /// <summary>Nombre de usuario que queda en cada documento emitido.</summary>
    public string Usuario => Cuenta?.NombreUsuario ?? Perfiles.Maestro;

    /// <summary>VENDEDOR o ENCARGADO; null en una sesión sin ingreso.</summary>
    public string? Rol => Cuenta?.Rol;

    /// <summary>True si alguien ingresó con usuario y contraseña: se aplican los permisos de su rol.</summary>
    public bool Autenticada => Cuenta is not null;

    public bool EsEncargado => Cuenta?.Rol == Roles.Encargado;

    /// <summary>Sesión que se abre al instante, antes de confirmar la terminal con la base de datos.</summary>
    public static Sesion Local(string nombreEquipo, CuentaUsuario? cuenta = null) => new(new Terminal { Nombre = nombreEquipo }, cuenta);

    /// <summary>True cuando la terminal ya quedó registrada en la base de datos central.</summary>
    public bool Registrada => Terminal.Id > 0;
}
