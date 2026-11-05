using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Sunat;
using static Condor.ClienteApi.ClienteServidor;

namespace Condor.ClienteApi;

// Repositorios de Condor.Dominio.Contratos que, en lugar de PostgreSQL, llaman
// a las rutas /api/escritorio de Condor.Api (CC-01). Cada método es una
// petición; las reglas y la base de datos quedan en la PC principal.

public sealed class ProductoRepositorioApi : IProductoRepositorio
{
    private const string Base = "/api/escritorio/productos";
    private readonly ClienteServidor _s;

    public ProductoRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Producto> RegistrarAsync(Producto producto, CancellationToken ct = default) =>
        (await _s.PostAsync<Producto>(Base, producto, ct))!;

    public async Task<IReadOnlyList<Producto>> BuscarPorNombreAsync(string texto, int limite = 20, CancellationToken ct = default) =>
        await _s.GetAsync<List<Producto>>(Ruta(Base, ("texto", texto ?? string.Empty), ("limite", limite)), ct) ?? new();

    public async Task<IReadOnlyList<Producto>> ListarAsync(CancellationToken ct = default) =>
        await _s.GetAsync<List<Producto>>(Base, ct) ?? new();

    public Task<Producto?> BuscarPorCodigoBarrasAsync(string codigo, CancellationToken ct = default) =>
        string.IsNullOrWhiteSpace(codigo) ? Task.FromResult<Producto?>(null) : _s.GetAsync<Producto>($"{Base}/codigo/{Uri.EscapeDataString(codigo.Trim())}", ct);

    public async Task<Producto> AsignarCodigoBarrasAsync(long productoId, string? codigo, CancellationToken ct = default) =>
        (await _s.PutAsync<Producto>($"{Base}/{productoId}/codigo", new { codigo }, ct))!;
}

public sealed class ClienteRepositorioApi : IClienteRepositorio
{
    private const string Base = "/api/escritorio/clientes";
    private readonly ClienteServidor _s;

    public ClienteRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public Task<Cliente?> BuscarPorDocumentoAsync(TipoDocumento tipo, string numero, CancellationToken ct = default) =>
        _s.GetAsync<Cliente>(Ruta($"{Base}/documento", ("tipo", tipo.ToString()), ("numero", numero)), ct);

    public async Task<Cliente> RegistrarAsync(Cliente cliente, CancellationToken ct = default) =>
        (await _s.PostAsync<Cliente>(Base, cliente, ct))!;

    public async Task<IReadOnlyList<Cliente>> BuscarAsync(string? texto, int limite = 200, CancellationToken ct = default) =>
        await _s.GetAsync<List<Cliente>>(Ruta(Base, ("texto", texto), ("limite", limite)), ct) ?? new();
}

public sealed class ProveedorRepositorioApi : IProveedorRepositorio
{
    private const string Base = "/api/escritorio/proveedores";
    private readonly ClienteServidor _s;

    public ProveedorRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Proveedor> RegistrarAsync(Proveedor proveedor, CancellationToken ct = default) =>
        (await _s.PostAsync<Proveedor>(Base, proveedor, ct))!;

    public Task<Proveedor?> BuscarPorRucAsync(string ruc, CancellationToken ct = default) =>
        _s.GetAsync<Proveedor>($"{Base}/ruc/{Uri.EscapeDataString(ruc ?? string.Empty)}", ct);

    public async Task<IReadOnlyList<Proveedor>> BuscarAsync(string? texto, int limite = 200, CancellationToken ct = default) =>
        await _s.GetAsync<List<Proveedor>>(Ruta(Base, ("texto", texto), ("limite", limite)), ct) ?? new();
}

public sealed class CompraRepositorioApi : ICompraRepositorio
{
    private const string Base = "/api/escritorio/compras";
    private readonly ClienteServidor _s;

    public CompraRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Compra> RegistrarAsync(Compra compra, CancellationToken ct = default) =>
        (await _s.PostAsync<Compra>(Base, compra, ct))!;

    public Task<Compra?> ObtenerAsync(long id, CancellationToken ct = default) => _s.GetAsync<Compra>($"{Base}/{id}", ct);

    public async Task<ResultadoCompras> BuscarAsync(FiltroCompras filtro, CancellationToken ct = default) =>
        await _s.PostAsync<ResultadoCompras>($"{Base}/buscar", filtro, ct) ?? ResultadoCompras.Ninguna;
}

public sealed class GuiaRemisionRepositorioApi : IGuiaRemisionRepositorio
{
    private const string Base = "/api/escritorio/guias";
    private readonly ClienteServidor _s;

    public GuiaRemisionRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<GuiaRemision> EmitirAsync(GuiaRemision guia, CancellationToken ct = default) =>
        (await _s.PostAsync<GuiaRemision>(Base, guia, ct))!;

    public Task<GuiaRemision?> ObtenerAsync(long id, CancellationToken ct = default) => _s.GetAsync<GuiaRemision>($"{Base}/{id}", ct);

    public async Task<IReadOnlyList<GuiaRemision>> BuscarAsync(FiltroGuias filtro, CancellationToken ct = default) =>
        await _s.PostAsync<List<GuiaRemision>>($"{Base}/buscar", filtro, ct) ?? new();

    public Task RegistrarRespuestaAsync(long id, RespuestaSunat respuesta, CancellationToken ct = default) =>
        _s.PostAsync($"{Base}/{id}/respuesta", respuesta, ct);

    public Task RegistrarFallaAsync(long id, string motivo, CancellationToken ct = default) =>
        _s.PostAsync($"{Base}/{id}/falla", new { motivo }, ct);

    public async Task<IReadOnlyList<GuiaRemision>> ListarPendientesAsync(int limite = 50, CancellationToken ct = default) =>
        await _s.GetAsync<List<GuiaRemision>>(Ruta($"{Base}/pendientes", ("limite", limite)), ct) ?? new();

    public Task RegistrarImpresionAsync(long id, CancellationToken ct = default) => _s.PostAsync($"{Base}/{id}/impresion", null, ct);
}

public sealed class EmpresaRepositorioApi : IEmpresaRepositorio
{
    private readonly ClienteServidor _s;

    public EmpresaRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Empresa> ObtenerAsync(CancellationToken ct = default) =>
        (await _s.GetAsync<Empresa>("/api/escritorio/empresa", ct))!;
}

public sealed class ComprobanteRepositorioApi : IComprobanteRepositorio
{
    private const string Base = "/api/escritorio/comprobantes";
    private readonly ClienteServidor _s;

    public ComprobanteRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Comprobante> EmitirAsync(Comprobante comprobante, CancellationToken ct = default)
    {
        if (comprobante.Detalle.Count == 0)
            throw new InvalidOperationException("El comprobante no tiene productos.");
        var emitido = (await _s.PostAsync<Comprobante>(Base, comprobante, ct))!;
        // Se devuelve el mismo objeto actualizado, como hace el repositorio de PostgreSQL.
        comprobante.Id = emitido.Id;
        comprobante.SerieId = emitido.SerieId;
        comprobante.Numero = emitido.Numero;
        comprobante.Fecha = emitido.Fecha;
        comprobante.EstadoSunat = emitido.EstadoSunat;
        comprobante.ValidaHasta = emitido.ValidaHasta;
        comprobante.Usuario = emitido.Usuario;
        comprobante.OpGravada = emitido.OpGravada;
        comprobante.Igv = emitido.Igv;
        comprobante.Total = emitido.Total;
        return comprobante;
    }

    public Task<Comprobante?> ObtenerAsync(long id, CancellationToken ct = default) => _s.GetAsync<Comprobante>($"{Base}/{id}", ct);

    public async Task<IReadOnlyList<Comprobante>> ListarRecientesAsync(int limite = 30, CancellationToken ct = default) =>
        await _s.GetAsync<List<Comprobante>>(Ruta($"{Base}/recientes", ("limite", limite)), ct) ?? new();

    public Task RegistrarImpresionAsync(long id, CancellationToken ct = default) => _s.PostAsync($"{Base}/{id}/impresion", null, ct);

    public async Task<IReadOnlyList<Comprobante>> ListarProformasAsync(string? texto, int limite = 100, CancellationToken ct = default) =>
        await _s.GetAsync<List<Comprobante>>(Ruta($"{Base}/proformas", ("texto", texto), ("limite", limite)), ct) ?? new();

    public async Task<ResultadoComprobantes> BuscarAsync(FiltroComprobantes filtro, CancellationToken ct = default) =>
        await _s.PostAsync<ResultadoComprobantes>($"{Base}/buscar", filtro, ct) ?? ResultadoComprobantes.Ninguno;
}

public sealed class EnvioSunatRepositorioApi : IEnvioSunatRepositorio
{
    private const string Base = "/api/escritorio/sunat";
    private readonly ClienteServidor _s;

    public EnvioSunatRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public Task RegistrarRespuestaAsync(long comprobanteId, RespuestaSunat respuesta, CancellationToken ct = default) =>
        _s.PostAsync($"{Base}/{comprobanteId}/respuesta", respuesta, ct);

    public Task RegistrarFallaAsync(long comprobanteId, string motivo, CancellationToken ct = default) =>
        _s.PostAsync($"{Base}/{comprobanteId}/falla", new { motivo }, ct);

    public async Task<IReadOnlyList<long>> ListarPendientesAsync(int limite = 100, CancellationToken ct = default) =>
        await _s.GetAsync<List<long>>(Ruta($"{Base}/pendientes", ("limite", limite)), ct) ?? new();

    public async Task<IReadOnlyList<long>> ReservarPendientesAsync(string terminal, TimeSpan espera, int limite = 20, CancellationToken ct = default) =>
        await _s.PostAsync<List<long>>($"{Base}/reservar", new { terminal, esperaSegundos = (int)espera.TotalSeconds, limite }, ct) ?? new();

    public Task LiberarAsync(string terminal, IReadOnlyCollection<long> comprobanteIds, CancellationToken ct = default) =>
        _s.PostAsync($"{Base}/liberar", new { terminal, ids = comprobanteIds }, ct);

    public async Task<ResumenPendientes> ResumenPendientesAsync(CancellationToken ct = default) =>
        await _s.GetAsync<ResumenPendientes>($"{Base}/resumen", ct) ?? ResumenPendientes.Ninguno;
}

public sealed class RespaldoRepositorioApi : IRespaldoRepositorio
{
    private const string Base = "/api/escritorio/respaldos";
    private readonly ClienteServidor _s;

    public RespaldoRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Respaldo> RegistrarAsync(Respaldo respaldo, CancellationToken ct = default) =>
        (await _s.PostAsync<Respaldo>(Base, respaldo, ct))!;

    public Task<Respaldo?> UltimoAsync(CancellationToken ct = default) => _s.GetAsync<Respaldo>($"{Base}/ultimo", ct);

    public async Task<IReadOnlyList<Respaldo>> ListarAsync(int limite = 10, CancellationToken ct = default) =>
        await _s.GetAsync<List<Respaldo>>(Ruta(Base, ("limite", limite)), ct) ?? new();
}

/// <summary>Configuración del respaldo en la PC principal (GET /api/escritorio/respaldos/configuracion).</summary>
public sealed record ConfiguracionRespaldoApi(bool Configurado, string Carpeta, int AvisoHoras);

/// <summary>
/// Genera el respaldo en la PC principal (HU-15): pg_dump corre allá, junto a
/// la base y el disco externo. Puede tardar, así que espera hasta 10 minutos.
/// El avance se informa al empezar y al terminar.
/// </summary>
public sealed class GeneradorRespaldoApi : IGeneradorRespaldo
{
    private readonly ClienteServidor _s;

    public GeneradorRespaldoApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Respaldo> GenerarAsync(string carpeta, IProgress<ProgresoRespaldo>? progreso = null, CancellationToken ct = default)
    {
        progreso?.Report(new ProgresoRespaldo(5, "Generando el respaldo en la PC principal…"));
        var respaldo = (await _s.PostAsync<Respaldo>("/api/escritorio/respaldos/generar", new { }, ct, TimeSpan.FromMinutes(10)))!;
        progreso?.Report(new ProgresoRespaldo(100, "Respaldo terminado."));
        return respaldo;
    }

    public static Task<ConfiguracionRespaldoApi?> ConfiguracionAsync(ClienteServidor servidor, CancellationToken ct = default) =>
        servidor.GetAsync<ConfiguracionRespaldoApi>("/api/escritorio/respaldos/configuracion", ct);
}

public sealed class TerminalRepositorioApi : ITerminalRepositorio
{
    private readonly ClienteServidor _s;

    public TerminalRepositorioApi(ClienteServidor servidor) => _s = servidor;

    public async Task<Terminal> RegistrarAccesoAsync(string nombre, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(nombre))
            throw new ArgumentException("El nombre de la terminal no puede estar vacío.", nameof(nombre));
        return (await _s.PostAsync<Terminal>("/api/escritorio/terminales", new { nombre }, ct))!;
    }
}

/// <summary>Versión del catálogo en la API: si cambia, otra PC registró o cambió un producto (T-13).</summary>
public static class AvisoCatalogoApi
{
    public static async Task<long> VersionAsync(ClienteServidor servidor, CancellationToken ct = default) =>
        await servidor.GetAsync<long>("/api/escritorio/catalogo/version", ct);
}
