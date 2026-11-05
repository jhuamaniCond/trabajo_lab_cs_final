using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Condor.Dominio.Contratos;
using Condor.Dominio.Validacion;

namespace Condor.ClienteApi;

/// <summary>
/// Conexión de una PC con Condor.Api (CC-01): lleva el token de quien
/// ingresó y convierte las respuestas de error en las mismas excepciones que
/// lanzaban los repositorios de PostgreSQL. Así los ViewModels no cambian:
/// <list type="bullet">
/// <item>API apagada, red caída, tiempo agotado o base caída (503): <see cref="SinConexionException"/>,
/// que muestra el aviso de conexión con Reintentar (T-06).</item>
/// <item>Regla de negocio (400, 409): la excepción de Condor.Dominio con el mismo mensaje.</item>
/// <item>Sin permiso (403): <see cref="UnauthorizedAccessException"/>; sesión vencida (401): <see cref="SesionVencidaException"/>.</item>
/// </list>
/// </summary>
public sealed class ClienteServidor : IDisposable
{
    /// <summary>JSON de la API: camelCase, sin distinguir mayúsculas al leer.</summary>
    public static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web);

    private readonly HttpClient _http;
    private readonly TimeSpan _espera;
    private readonly bool _propio;

    public ClienteServidor(ConfiguracionApi config)
        : this(new HttpClient { BaseAddress = new Uri(config.Url) }, TimeSpan.FromSeconds(config.TiempoEsperaSegundos), propio: true)
    {
    }

    /// <summary>Con un HttpClient ya creado (las pruebas usan el de la API en memoria).</summary>
    public ClienteServidor(HttpClient http, TimeSpan? espera = null, bool propio = false)
    {
        _http = http;
        _http.Timeout = Timeout.InfiniteTimeSpan; // Cada petición lleva su propio tiempo de espera.
        _espera = espera ?? TimeSpan.FromSeconds(15);
        _propio = propio;
    }

    public Uri? Direccion => _http.BaseAddress;

    /// <summary>Token de quien ingresó; null antes de ingresar o tras cerrar sesión.</summary>
    public string? Token
    {
        get => _http.DefaultRequestHeaders.Authorization?.Parameter;
        set => _http.DefaultRequestHeaders.Authorization = value is null ? null : new AuthenticationHeaderValue("Bearer", value);
    }

    /// <summary>True si la API responde y su base de datos está lista (GET /api/salud); no lanza excepciones.</summary>
    public async Task<bool> ProbarAsync(CancellationToken ct = default)
    {
        try
        {
            using var respuesta = await EnviarAsync(HttpMethod.Get, "/api/salud", null, null, ct, lanzarSiError: false);
            return respuesta.IsSuccessStatusCode;
        }
        catch (SinConexionException)
        {
            return false;
        }
    }

    public Task<T?> GetAsync<T>(string ruta, CancellationToken ct = default) => LeerAsync<T>(HttpMethod.Get, ruta, null, null, ct);

    public Task<T?> PostAsync<T>(string ruta, object? cuerpo, CancellationToken ct = default, TimeSpan? espera = null) =>
        LeerAsync<T>(HttpMethod.Post, ruta, cuerpo, espera, ct);

    public Task<T?> PutAsync<T>(string ruta, object? cuerpo, CancellationToken ct = default) => LeerAsync<T>(HttpMethod.Put, ruta, cuerpo, null, ct);

    /// <summary>POST sin respuesta (anotar una impresión, una falla...).</summary>
    public async Task PostAsync(string ruta, object? cuerpo, CancellationToken ct = default)
    {
        using var _ = await EnviarAsync(HttpMethod.Post, ruta, cuerpo, null, ct);
    }

    /// <summary>POST que devuelve la respuesta tal cual, sin convertir los errores (el ingreso los interpreta).</summary>
    public Task<HttpResponseMessage> PostSinValidarAsync(string ruta, object? cuerpo, CancellationToken ct = default) =>
        EnviarAsync(HttpMethod.Post, ruta, cuerpo, null, ct, lanzarSiError: false);

    /// <summary>Arma una ruta con parámetros de consulta; los null no se envían.</summary>
    public static string Ruta(string ruta, params (string Nombre, object? Valor)[] parametros)
    {
        var consulta = string.Join("&", parametros
            .Where(p => p.Valor is not null)
            .Select(p => $"{p.Nombre}={Uri.EscapeDataString(Convert.ToString(p.Valor, System.Globalization.CultureInfo.InvariantCulture)!)}"));
        return consulta.Length == 0 ? ruta : $"{ruta}?{consulta}";
    }

    private async Task<T?> LeerAsync<T>(HttpMethod metodo, string ruta, object? cuerpo, TimeSpan? espera, CancellationToken ct)
    {
        using var respuesta = await EnviarAsync(metodo, ruta, cuerpo, espera, ct);
        if (respuesta.StatusCode == HttpStatusCode.NoContent || respuesta.Content.Headers.ContentLength == 0)
            return default;
        var texto = await respuesta.Content.ReadAsStringAsync(ct);
        return string.IsNullOrWhiteSpace(texto) ? default : JsonSerializer.Deserialize<T>(texto, Json);
    }

    private async Task<HttpResponseMessage> EnviarAsync(HttpMethod metodo, string ruta, object? cuerpo, TimeSpan? espera,
        CancellationToken ct, bool lanzarSiError = true)
    {
        using var tiempo = CancellationTokenSource.CreateLinkedTokenSource(ct);
        tiempo.CancelAfter(espera ?? _espera);
        using var peticion = new HttpRequestMessage(metodo, ruta);
        if (cuerpo is not null)
            peticion.Content = JsonContent.Create(cuerpo, cuerpo.GetType(), options: Json);

        HttpResponseMessage respuesta;
        try
        {
            respuesta = await _http.SendAsync(peticion, tiempo.Token);
        }
        catch (HttpRequestException ex)
        {
            throw new SinConexionException(ex);
        }
        catch (OperationCanceledException ex) when (!ct.IsCancellationRequested)
        {
            throw new SinConexionException(new TimeoutException($"La PC principal no respondió en {(espera ?? _espera).TotalSeconds:0} s.", ex));
        }

        if (!lanzarSiError || respuesta.IsSuccessStatusCode)
            return respuesta;

        using (respuesta)
            throw await ErrorAsync(respuesta, ct);
    }

    /// <summary>Convierte un application/problem+json en la excepción que corresponde.</summary>
    internal static async Task<Exception> ErrorAsync(HttpResponseMessage respuesta, CancellationToken ct)
    {
        string? titulo = null, tipo = null;
        var errores = new List<string>();
        try
        {
            using var documento = JsonDocument.Parse(await respuesta.Content.ReadAsStringAsync(ct));
            var raiz = documento.RootElement;
            if (raiz.TryGetProperty("title", out var t))
                titulo = t.GetString();
            if (raiz.TryGetProperty("tipo", out var tp))
                tipo = tp.GetString();
            if (raiz.TryGetProperty("errores", out var e) && e.ValueKind == JsonValueKind.Array)
                errores.AddRange(e.EnumerateArray().Select(x => x.GetString() ?? string.Empty));
        }
        catch (JsonException)
        {
            // Sin cuerpo JSON (401 y 403 del middleware de autenticación): basta el código.
        }

        var mensaje = errores.Count > 0 ? string.Join(" ", errores) : titulo ?? $"La PC principal respondió {(int)respuesta.StatusCode}.";
        return respuesta.StatusCode switch
        {
            HttpStatusCode.ServiceUnavailable => new SinConexionException(new HttpRequestException(mensaje)),
            HttpStatusCode.Unauthorized => new SesionVencidaException(),
            HttpStatusCode.Forbidden => new UnauthorizedAccessException("Acceso denegado: esta acción es solo para el Encargado general."),
            _ => tipo switch
            {
                nameof(ProductoInvalidoException) => new ProductoInvalidoException(errores.Count > 0 ? errores : new[] { mensaje }),
                nameof(ClienteInvalidoException) => new ClienteInvalidoException(errores.Count > 0 ? errores : new[] { mensaje }),
                nameof(ProveedorInvalidoException) => new ProveedorInvalidoException(errores.Count > 0 ? errores : new[] { mensaje }),
                nameof(RespaldoException) => new RespaldoException(mensaje),
                _ => new ErrorServidorException(mensaje, (int)respuesta.StatusCode, tipo),
            },
        };
    }

    public void Dispose()
    {
        if (_propio)
            _http.Dispose();
    }
}

/// <summary>La PC principal rechazó la operación; el mensaje es el de la regla de negocio.</summary>
public sealed class ErrorServidorException : Exception
{
    public ErrorServidorException(string mensaje, int estado, string? tipo) : base(mensaje)
    {
        Estado = estado;
        Tipo = tipo;
    }

    /// <summary>Código HTTP (400 regla, 409 duplicado...).</summary>
    public int Estado { get; }

    /// <summary>Nombre de la excepción en el servidor (ProformaYaConvertidaException...).</summary>
    public string? Tipo { get; }
}

/// <summary>El token venció (8 horas) o no es válido: hay que cerrar sesión e ingresar de nuevo.</summary>
public sealed class SesionVencidaException : Exception
{
    public SesionVencidaException()
        : base("Su sesión venció: pulse Cerrar sesión e ingrese de nuevo con su usuario y contraseña.")
    {
    }
}
