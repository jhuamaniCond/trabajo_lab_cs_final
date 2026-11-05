using System.Net.Http.Headers;
using System.Net.Http.Json;
using Condor.Api;
using Condor.Api.Infraestructura;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Pruebas.Infraestructura;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace Condor.Pruebas.Api;

/// <summary>
/// La API (CC-01) levantada en memoria con repositorios de prueba: no
/// necesita PostgreSQL ni abrir puertos. Cada prueba crea la suya, así los
/// datos no dependen del orden de ejecución.
/// </summary>
public sealed class ApiDePrueba : WebApplicationFactory<Program>
{
    public UsuarioRepositorioEnMemoria Usuarios { get; } = UsuarioRepositorioEnMemoria.ConUsuariosDemo();
    public ProductoRepositorioEnMemoria Productos { get; } = new(DatosPrueba.Catalogo());
    public ClienteRepositorioEnMemoria Clientes { get; } = new(DatosPrueba.Clientes());
    public ComprobanteRepositorioEnMemoria Comprobantes { get; } = new();
    public ProveedorRepositorioEnMemoria Proveedores { get; } = new(DatosPrueba.Proveedores());
    public RespaldoRepositorioEnMemoria Respaldos { get; } = new();
    public ReporteVentasRepositorioEnMemoria Reporte { get; } = new();
    public CompraRepositorioEnMemoria Compras { get; } = new();
    public GuiaRemisionRepositorioEnMemoria Guias { get; } = new();
    public EnvioSunatRepositorioEnMemoria Envios { get; } = new();
    public TerminalRepositorioEnMemoria Terminales { get; } = new();
    public GeneradorRespaldoFalso Generador { get; } = new();
    public ContextoApi Contexto { get; } = new() { NombreTerminal = "API-PRUEBA", TerminalId = 9 };
    public bool BaseDatosResponde { get; set; } = true;

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Development");
        builder.ConfigureTestServices(servicios =>
        {
            // Sin migraciones ni registro de terminal: la terminal ya viene en Contexto.
            var preparacion = servicios.Single(d => d.ImplementationType == typeof(PreparacionBaseDatos));
            servicios.Remove(preparacion);

            servicios.AddSingleton(Contexto);
            servicios.AddSingleton(new SondaBaseDatos(_ => Task.FromResult(BaseDatosResponde)));
            servicios.AddSingleton<IUsuarioRepositorio>(Usuarios);
            servicios.AddSingleton<IProductoRepositorio>(Productos);
            servicios.AddSingleton<IConsultaProductos>(Productos);
            servicios.AddSingleton<IClienteRepositorio>(Clientes);
            servicios.AddSingleton<IComprobanteRepositorio>(Comprobantes);
            servicios.AddSingleton<IProveedorRepositorio>(Proveedores);
            servicios.AddSingleton<IRespaldoRepositorio>(Respaldos);
            servicios.AddSingleton<IReporteVentasRepositorio>(Reporte);
            servicios.AddSingleton<ICompraRepositorio>(Compras);
            servicios.AddSingleton<IGuiaRemisionRepositorio>(Guias);
            servicios.AddSingleton<IEnvioSunatRepositorio>(Envios);
            servicios.AddSingleton<IEmpresaRepositorio>(new EmpresaRepositorioEnMemoria());
            servicios.AddSingleton<ITerminalRepositorio>(Terminales);
            servicios.AddSingleton(new ServicioRespaldo(Generador, DatosPrueba.DiscoExterno, 24));
        });
    }

    /// <summary>Cliente HTTP ya autenticado con ese usuario de demostración.</summary>
    public async Task<HttpClient> ClienteComoAsync(string usuario, string clave)
    {
        var http = CreateClient();
        var respuesta = await http.PostAsJsonAsync("/api/auth/login", new LoginPedido(usuario, clave));
        respuesta.EnsureSuccessStatusCode();
        var login = (await respuesta.Content.ReadFromJsonAsync<LoginRespuesta>())!;
        http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", login.Token);
        return http;
    }

    public Task<HttpClient> VendedorAsync() => ClienteComoAsync("vendedor1", "Vendedor2026!");

    public Task<HttpClient> EncargadoAsync() => ClienteComoAsync("encargado", "Encargado2026!");
}

/// <summary>Terminales registradas sin base de datos: un Id por nombre.</summary>
public sealed class TerminalRepositorioEnMemoria : ITerminalRepositorio
{
    private readonly Dictionary<string, Terminal> _terminales = new();

    public Task<Terminal> RegistrarAccesoAsync(string nombre, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(nombre))
            throw new ArgumentException("El nombre de la terminal no puede estar vacío.", nameof(nombre));
        if (!_terminales.TryGetValue(nombre, out var terminal))
            _terminales[nombre] = terminal = new Terminal { Id = _terminales.Count + 1, Nombre = nombre, RegistradoEn = DateTimeOffset.Now };
        terminal.UltimoAcceso = DateTimeOffset.Now;
        return Task.FromResult(terminal);
    }
}
