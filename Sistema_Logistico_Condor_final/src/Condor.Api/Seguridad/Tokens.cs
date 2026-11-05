using System.Security.Claims;
using System.Text;
using Condor.Dominio.Entidades;
using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;

namespace Condor.Api.Seguridad;

/// <summary>Sección Jwt de appsettings.json.</summary>
public sealed class ConfiguracionJwt
{
    public const int LargoMinimoClave = 32;

    public string Emisor { get; set; } = "CondorVentas";

    public string Audiencia { get; set; } = "CondorVentas";

    /// <summary>Clave HMAC-SHA256 con la que se firman los tokens; al menos 32 caracteres.</summary>
    public string Clave { get; set; } = string.Empty;

    public int MinutosValidez { get; set; } = 480;

    public SymmetricSecurityKey LlaveFirma => new(Encoding.UTF8.GetBytes(Clave));

    public void Validar()
    {
        if (string.IsNullOrWhiteSpace(Clave) || Clave.Length < LargoMinimoClave)
            throw new InvalidOperationException($"Jwt:Clave debe tener al menos {LargoMinimoClave} caracteres (appsettings.json o Jwt__Clave).");
        if (MinutosValidez is < 1 or > 1440)
            throw new InvalidOperationException("Jwt:MinutosValidez debe estar entre 1 y 1440.");
    }
}

/// <summary>Nombres de los datos (claims) que lleva el token.</summary>
public static class Reclamos
{
    public const string Usuario = "sub";
    public const string Nombre = "nombre";
    public const string Rol = "rol";
}

/// <summary>Emite el token de acceso de quien ingresó por POST /api/auth/login.</summary>
public sealed class EmisorTokens
{
    private readonly ConfiguracionJwt _config;
    private readonly TimeProvider _reloj;

    public EmisorTokens(ConfiguracionJwt config, TimeProvider reloj)
    {
        _config = config;
        _reloj = reloj;
    }

    public (string Token, DateTimeOffset Expira) Emitir(CuentaUsuario cuenta)
    {
        var ahora = _reloj.GetUtcNow();
        var expira = ahora.AddMinutes(_config.MinutosValidez);
        var token = new JsonWebTokenHandler().CreateToken(new SecurityTokenDescriptor
        {
            Issuer = _config.Emisor,
            Audience = _config.Audiencia,
            IssuedAt = ahora.UtcDateTime,
            NotBefore = ahora.UtcDateTime,
            Expires = expira.UtcDateTime,
            Subject = new ClaimsIdentity(new[]
            {
                new Claim(Reclamos.Usuario, cuenta.NombreUsuario),
                new Claim(Reclamos.Nombre, cuenta.NombreCompleto),
                new Claim(Reclamos.Rol, cuenta.Rol),
            }),
            SigningCredentials = new SigningCredentials(_config.LlaveFirma, SecurityAlgorithms.HmacSha256),
        });
        return (token, expira);
    }
}
