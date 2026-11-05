using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;

namespace Condor.ClienteApi;

/// <summary>
/// Ingreso de la app de escritorio por POST /api/auth/login (CC-01). Las
/// reglas (bloqueo, bitácora) las aplica la API; aquí se traduce la respuesta
/// y, si el ingreso es correcto, se guarda el token para las demás peticiones.
/// </summary>
public sealed class AutenticadorApi : IAutenticador
{
    private sealed record Respuesta(string Token, DateTimeOffset Expira, string Usuario, string Nombre, string Rol);

    private readonly ClienteServidor _servidor;

    public AutenticadorApi(ClienteServidor servidor) => _servidor = servidor;

    public async Task<ResultadoAutenticacion> AutenticarAsync(string? usuario, string? clave, string? terminal, CancellationToken ct = default)
    {
        _servidor.Token = null;
        using var respuesta = await _servidor.PostSinValidarAsync("/api/auth/login", new { usuario, clave }, ct);

        if (respuesta.IsSuccessStatusCode)
        {
            var datos = (await respuesta.Content.ReadFromJsonAsync<Respuesta>(ClienteServidor.Json, ct))!;
            _servidor.Token = datos.Token;
            var cuenta = new CuentaUsuario { NombreUsuario = datos.Usuario, NombreCompleto = datos.Nombre, Rol = datos.Rol };
            return new ResultadoAutenticacion(EstadoAutenticacion.Exitoso, cuenta, $"Bienvenido, {datos.Nombre}.");
        }

        var estado = respuesta.StatusCode switch
        {
            HttpStatusCode.BadRequest => EstadoAutenticacion.DatosIncompletos,
            HttpStatusCode.Locked => EstadoAutenticacion.CuentaBloqueada,
            HttpStatusCode.Unauthorized => EstadoAutenticacion.CredencialesInvalidas,
            _ => (EstadoAutenticacion?)null,
        };
        if (estado is null)
            throw await ClienteServidor.ErrorAsync(respuesta, ct);

        return new ResultadoAutenticacion(estado.Value, null, await TituloAsync(respuesta, ct) ?? ServicioAutenticacion.MensajeInvalidas);
    }

    /// <summary>Olvida el token (Cerrar sesión).</summary>
    public void CerrarSesion() => _servidor.Token = null;

    private static async Task<string?> TituloAsync(HttpResponseMessage respuesta, CancellationToken ct)
    {
        try
        {
            using var documento = JsonDocument.Parse(await respuesta.Content.ReadAsStringAsync(ct));
            return documento.RootElement.TryGetProperty("title", out var titulo) ? titulo.GetString() : null;
        }
        catch (JsonException)
        {
            return null;
        }
    }
}
