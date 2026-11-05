using Condor.Datos;
using Condor.Dominio.Contratos;

namespace Condor.Api.Infraestructura;

/// <summary>
/// Datos de la API que se conocen al arrancar: la terminal con la que se
/// registran los comprobantes emitidos por HTTP.
/// </summary>
public sealed class ContextoApi
{
    /// <summary>Nombre con el que la API aparece en la tabla terminal y en los tickets.</summary>
    public string NombreTerminal { get; init; } = $"API-{Environment.MachineName}";

    /// <summary>Id de la terminal en la base central; 0 hasta que arranque.</summary>
    public int TerminalId { get; set; }

    public bool Lista => TerminalId > 0;

    private long _versionCatalogo;

    /// <summary>
    /// Sube cada vez que cambia el catálogo (T-13): las PC la consultan cada
    /// pocos segundos y, si cambió, refrescan el buscador.
    /// </summary>
    public long VersionCatalogo => Interlocked.Read(ref _versionCatalogo);

    public void CatalogoCambiado() => Interlocked.Increment(ref _versionCatalogo);
}

/// <summary>
/// Al arrancar, aplica las migraciones pendientes y registra la terminal de
/// la API, igual que hace cada PC del mostrador al abrir el programa. Si la
/// base no responde, lo reintenta cada 10 s sin detener la API (GET
/// /api/salud dice si ya está lista). Luego escucha el aviso LISTEN/NOTIFY
/// del catálogo, que también llega cuando otra herramienta lo cambia.
/// </summary>
public sealed class PreparacionBaseDatos : BackgroundService
{
    private readonly FabricaConexiones _conexiones;
    private readonly ContextoApi _contexto;
    private readonly ILogger<PreparacionBaseDatos> _log;

    public PreparacionBaseDatos(FabricaConexiones conexiones, ContextoApi contexto, ILogger<PreparacionBaseDatos> log)
    {
        _conexiones = conexiones;
        _contexto = contexto;
        _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested && !_contexto.Lista)
        {
            try
            {
                var aplicadas = await new Migrador(_conexiones).AplicarAsync(ct);
                var terminal = await new TerminalRepositorio(_conexiones).RegistrarAccesoAsync(_contexto.NombreTerminal, ct);
                _contexto.TerminalId = terminal.Id;
                _log.LogInformation("Base de datos lista ({Aplicadas} migraciones aplicadas). Terminal {Terminal} = {Id}.",
                    aplicadas, terminal.Nombre, terminal.Id);

                var aviso = new AvisoCatalogo(_conexiones.CadenaConexion);
                aviso.CatalogoCambiado += _contexto.CatalogoCambiado;
                aviso.Iniciar();
                ct.Register(() => _ = aviso.DisposeAsync());
            }
            catch (SinConexionException ex)
            {
                _log.LogWarning("Sin conexión con la base de datos central: {Mensaje}. Se reintenta en 10 s.", ex.Message);
                await Task.Delay(TimeSpan.FromSeconds(10), ct);
            }
        }
    }
}
