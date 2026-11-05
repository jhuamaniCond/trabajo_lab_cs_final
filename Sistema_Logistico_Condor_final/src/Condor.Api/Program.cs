using Condor.Api;
using Condor.Api.Infraestructura;
using Condor.Api.Seguridad;
using Condor.Datos;
using Condor.Datos.Respaldos;
using Condor.Dominio.Contratos;
using Condor.Dominio.Seguridad;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

// Backend REST del Sistema de Ventas Cóndor (CC-01). Corre en la PC
// principal junto a PostgreSQL; ver docs/api.md.
var builder = WebApplication.CreateBuilder(args);

var jwt = builder.Configuration.GetSection("Jwt").Get<ConfiguracionJwt>() ?? new ConfiguracionJwt();
jwt.Validar();

builder.Services.AddSingleton(jwt);
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<ContextoApi>();
builder.Services.AddSingleton<EmisorTokens>();

// Base de datos central: la misma de las PC del mostrador.
builder.Services.AddSingleton(_ =>
{
    var config = builder.Configuration.GetSection("BaseDatos").Get<ConfiguracionConexion>() ?? new ConfiguracionConexion();
    config.Validar();
    return new FabricaConexiones(config, $"API-{Environment.MachineName}");
});
builder.Services.AddSingleton(sp => new SondaBaseDatos(sp.GetRequiredService<FabricaConexiones>().ProbarAsync));
builder.Services.AddHostedService<PreparacionBaseDatos>();

// Repositorios de Condor.Datos (sin estado: uno para toda la API).
builder.Services.AddSingleton(sp => new ProductoRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IProductoRepositorio>(sp => sp.GetRequiredService<ProductoRepositorio>());
builder.Services.AddSingleton<IConsultaProductos>(sp => sp.GetRequiredService<ProductoRepositorio>());
builder.Services.AddSingleton<IClienteRepositorio>(sp => new ClienteRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IComprobanteRepositorio>(sp => new ComprobanteRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IProveedorRepositorio>(sp => new ProveedorRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IRespaldoRepositorio>(sp => new RespaldoRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IReporteVentasRepositorio>(sp => new ReporteVentasRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IUsuarioRepositorio>(sp => new UsuarioRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<ICompraRepositorio>(sp => new CompraRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IGuiaRemisionRepositorio>(sp => new GuiaRemisionRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IEmpresaRepositorio>(sp => new EmpresaRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<IEnvioSunatRepositorio>(sp => new EnvioSunatRepositorio(sp.GetRequiredService<FabricaConexiones>()));
builder.Services.AddSingleton<ITerminalRepositorio>(sp => new TerminalRepositorio(sp.GetRequiredService<FabricaConexiones>()));

// Respaldo (HU-15): sección Respaldo de appsettings.json, con la carpeta del disco externo.
builder.Services.AddSingleton(sp =>
{
    var config = builder.Configuration.GetSection(ConfiguracionRespaldo.Seccion).Get<ConfiguracionRespaldo>() ?? new ConfiguracionRespaldo();
    config.Validar();
    var generador = config.Configurada ? new GeneradorRespaldo(sp.GetRequiredService<FabricaConexiones>(), config.PgDump) : null;
    return new ServicioRespaldo(generador, config.Carpeta, config.AvisoHoras);
});

// Mismo JSON que el cliente de la app de escritorio (camelCase, Condor.Dominio.Entidades).
builder.Services.ConfigureHttpJsonOptions(opciones => opciones.SerializerOptions.PropertyNameCaseInsensitive = true);
builder.Services.AddSingleton(sp => new ServicioAutenticacion(sp.GetRequiredService<IUsuarioRepositorio>(),
    () => sp.GetRequiredService<TimeProvider>().GetUtcNow()));

// Ingreso con token JWT y permisos por rol (CC-01, control de G6).
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer(opciones =>
{
    opciones.MapInboundClaims = false;
    opciones.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidIssuer = jwt.Emisor,
        ValidateAudience = true,
        ValidAudience = jwt.Audiencia,
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = jwt.LlaveFirma,
        ValidateLifetime = true,
        ClockSkew = TimeSpan.FromSeconds(30),
        NameClaimType = Reclamos.Usuario,
        RoleClaimType = Reclamos.Rol,
    };
});
builder.Services.AddAuthorizationBuilder()
    .AddPolicy(Endpoints.PoliticaEncargado, politica => politica.RequireRole(Roles.Encargado));

builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<ManejadorErrores>();

var app = builder.Build();

app.UseExceptionHandler();
app.UseStatusCodePages();

// CC-03: portal web del mostrador (wwwroot). Usa las mismas rutas /api con el
// token JWT; no tiene reglas propias. http://localhost:5080/
app.UseDefaultFiles();
app.UseStaticFiles();
app.UseAuthentication();
app.UseAuthorization();

Endpoints.Mapear(app);
EndpointsEscritorio.Mapear(app);

app.Run();

/// <summary>Visible para las pruebas de integración (WebApplicationFactory).</summary>
public partial class Program;
