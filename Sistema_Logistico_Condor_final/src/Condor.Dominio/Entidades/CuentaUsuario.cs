using Condor.Dominio.Seguridad;

namespace Condor.Dominio.Entidades;

/// <summary>
/// Persona que usa el sistema con su usuario, contraseña y rol (CC-01).
/// </summary>
public sealed class CuentaUsuario
{
    public long Id { get; set; }

    /// <summary>Nombre para ingresar, en minúsculas (vendedor1, encargado).</summary>
    public string NombreUsuario { get; set; } = string.Empty;

    public string NombreCompleto { get; set; } = string.Empty;

    /// <summary>VENDEDOR o ENCARGADO (ver <see cref="Roles"/>).</summary>
    public string Rol { get; set; } = Roles.Vendedor;

    /// <summary>Hash PBKDF2 de la contraseña (ver <see cref="HashClave"/>).</summary>
    public string HashClave { get; set; } = string.Empty;

    public bool Activo { get; set; } = true;

    /// <summary>Contraseñas equivocadas seguidas desde el último acceso correcto.</summary>
    public int IntentosFallidos { get; set; }

    /// <summary>Hasta cuándo no puede ingresar tras demasiados intentos fallidos; null si no está bloqueada.</summary>
    public DateTimeOffset? BloqueadoHasta { get; set; }

    public DateTimeOffset? UltimoAcceso { get; set; }

    public bool EsEncargado => Rol == Roles.Encargado;

    public bool EstaBloqueada(DateTimeOffset ahora) => BloqueadoHasta is { } hasta && hasta > ahora;
}
