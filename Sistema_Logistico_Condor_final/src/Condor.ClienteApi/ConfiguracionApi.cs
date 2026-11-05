using System.Text.Json;

namespace Condor.ClienteApi;

/// <summary>
/// Sección "Api" de condor.json (CC-01): dirección del backend en la PC
/// principal. Desde la versión 1.1.0 las PC ya no necesitan la clave de
/// PostgreSQL, solo esta dirección.
/// </summary>
public sealed class ConfiguracionApi
{
    public const string NombreArchivo = "condor.json";
    public const string Seccion = "Api";

    /// <summary>Dirección de Condor.Api, por ejemplo http://192.168.1.10:5080.</summary>
    public string Url { get; set; } = "http://localhost:5080";

    /// <summary>Segundos de espera de cada petición; bajo para avisar pronto si la red se cae.</summary>
    public int TiempoEsperaSegundos { get; set; } = 15;

    /// <summary>
    /// Solo en la PC principal: ruta de CondorApi.exe (absoluta o relativa a la
    /// carpeta del programa). Si la API no responde al abrir la app, la app la
    /// arranca en segundo plano. Vacío en las demás PC.
    /// </summary>
    public string? Backend { get; set; }

    /// <summary>Ruta completa de <see cref="Backend"/>; null si esta PC no arranca el backend.</summary>
    public string? RutaBackend(string? carpetaPrograma = null) => string.IsNullOrWhiteSpace(Backend)
        ? null
        : Path.GetFullPath(Path.Combine(carpetaPrograma ?? AppContext.BaseDirectory, Backend));

    private static readonly JsonSerializerOptions OpcionesJson = new()
    {
        PropertyNameCaseInsensitive = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    /// <summary>Lee la sección Api de condor.json (por defecto, junto al ejecutable).</summary>
    /// <exception cref="FileNotFoundException">Si condor.json no existe.</exception>
    /// <exception cref="InvalidDataException">Si falta la sección o está mal escrita.</exception>
    public static ConfiguracionApi Cargar(string? carpeta = null)
    {
        var ruta = Path.Combine(carpeta ?? AppContext.BaseDirectory, NombreArchivo);
        if (!File.Exists(ruta))
            throw new FileNotFoundException(
                $"No se encontró {NombreArchivo}. Copie condor.ejemplo.json como {NombreArchivo} y ponga en Api > Url la dirección de la PC principal.",
                ruta);

        ConfiguracionApi? config = null;
        try
        {
            using var documento = JsonDocument.Parse(File.ReadAllText(ruta), new JsonDocumentOptions
            {
                CommentHandling = JsonCommentHandling.Skip,
                AllowTrailingCommas = true,
            });
            foreach (var propiedad in documento.RootElement.EnumerateObject())
            {
                if (string.Equals(propiedad.Name, Seccion, StringComparison.OrdinalIgnoreCase))
                    config = propiedad.Value.Deserialize<ConfiguracionApi>(OpcionesJson);
            }
        }
        catch (JsonException ex)
        {
            throw new InvalidDataException($"{NombreArchivo} no tiene un formato JSON válido: {ex.Message}", ex);
        }

        if (config is null)
            throw new InvalidDataException(
                $"Falta la sección \"{Seccion}\" en {NombreArchivo}: agregue \"Api\": {{ \"Url\": \"http://<IP de la PC principal>:5080\" }}.");
        config.Validar();
        return config;
    }

    public void Validar()
    {
        if (!Uri.TryCreate(Url, UriKind.Absolute, out var uri) || uri.Scheme is not ("http" or "https"))
            throw new InvalidDataException($"Api > Url debe ser una dirección http, por ejemplo http://192.168.1.10:5080 (está \"{Url}\").");
        if (TiempoEsperaSegundos is < 1 or > 300)
            throw new InvalidDataException("Api > TiempoEsperaSegundos debe estar entre 1 y 300.");
        if (Backend is not null && Backend.IndexOfAny(Path.GetInvalidPathChars()) >= 0)
            throw new InvalidDataException("Api > Backend tiene caracteres no válidos.");
    }

    public override string ToString() => Url;
}
