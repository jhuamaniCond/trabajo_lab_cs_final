using Condor.Dominio.Contratos;
using Condor.Dominio.Seguridad;
using Condor.Pruebas.Infraestructura;

namespace Condor.Pruebas.Dominio;

/// <summary>
/// CC-01: ingreso con usuario y contraseña. Usa un repositorio en memoria y un
/// reloj fijo, así el bloqueo de 15 minutos se prueba sin esperar.
/// </summary>
public class ServicioAutenticacionTests
{
    private readonly UsuarioRepositorioEnMemoria _usuarios = UsuarioRepositorioEnMemoria.ConUsuariosDemo();
    private DateTimeOffset _ahora = new(2026, 11, 20, 15, 0, 0, TimeSpan.Zero);

    private ServicioAutenticacion Servicio() => new(_usuarios, () => _ahora);

    [Fact]
    public async Task Con_la_clave_correcta_ingresa_con_su_rol()
    {
        var resultado = await Servicio().AutenticarAsync("vendedor1", "Vendedor2026!", "PC-1");

        Assert.True(resultado.Exitoso);
        Assert.Equal(Roles.Vendedor, resultado.Cuenta!.Rol);
        Assert.Contains(_usuarios.Bitacora, a => a is { Usuario: "vendedor1", Exitoso: true, Terminal: "PC-1" });
    }

    [Fact]
    public async Task El_usuario_no_distingue_mayusculas_ni_espacios()
    {
        var resultado = await Servicio().AutenticarAsync("  ENCARGADO ", "Encargado2026!", "PC-1");

        Assert.True(resultado.Exitoso);
        Assert.True(resultado.Cuenta!.EsEncargado);
    }

    [Fact]
    public async Task La_clave_si_distingue_mayusculas()
    {
        var resultado = await Servicio().AutenticarAsync("vendedor1", "vendedor2026!", "PC-1");

        Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, resultado.Estado);
        Assert.Null(resultado.Cuenta);
    }

    [Theory]
    [InlineData(null, "x")]
    [InlineData("", "x")]
    [InlineData("   ", "x")]
    [InlineData("vendedor1", null)]
    [InlineData("vendedor1", "")]
    public async Task Sin_usuario_o_sin_clave_no_consulta_la_base(string? usuario, string? clave)
    {
        _usuarios.Error = new InvalidOperationException("no debía consultarse");

        var resultado = await Servicio().AutenticarAsync(usuario, clave, "PC-1");

        Assert.Equal(EstadoAutenticacion.DatosIncompletos, resultado.Estado);
        Assert.Empty(_usuarios.Bitacora);
    }

    [Fact]
    public async Task Usuario_inexistente_e_inactivo_dan_el_mismo_mensaje_que_la_clave_equivocada()
    {
        _usuarios.Agregar("retirado", "Clave2026!", Roles.Vendedor, activo: false);

        var inexistente = await Servicio().AutenticarAsync("nadie", "Clave2026!", "PC-1");
        var inactivo = await Servicio().AutenticarAsync("retirado", "Clave2026!", "PC-1");
        var equivocada = await Servicio().AutenticarAsync("vendedor1", "otra", "PC-1");

        Assert.All(new[] { inexistente, inactivo, equivocada }, r =>
        {
            Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, r.Estado);
            Assert.Equal(ServicioAutenticacion.MensajeInvalidas, r.Mensaje);
        });
        Assert.Equal(new[] { "usuario inexistente", "cuenta inactiva", "contraseña incorrecta" },
            _usuarios.Bitacora.Select(a => a.Detalle));
    }

    [Fact]
    public async Task Cuatro_fallos_no_bloquean_y_el_quinto_si()
    {
        var servicio = Servicio();
        for (var i = 1; i < ServicioAutenticacion.IntentosMaximos; i++)
            Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, (await servicio.AutenticarAsync("vendedor1", "mal", "PC-1")).Estado);
        Assert.Equal(4, _usuarios.Cuenta("vendedor1").IntentosFallidos);

        var quinto = await servicio.AutenticarAsync("vendedor1", "mal", "PC-1");

        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, quinto.Estado);
        Assert.Equal(_ahora + ServicioAutenticacion.DuracionBloqueo, _usuarios.Cuenta("vendedor1").BloqueadoHasta);
        Assert.Contains("10:15", quinto.Mensaje); // 15:15 UTC = 10:15 en Perú.
    }

    [Fact]
    public async Task Bloqueada_no_ingresa_ni_con_la_clave_correcta()
    {
        await Bloquear("vendedor1");
        _ahora += TimeSpan.FromMinutes(14);

        var resultado = await Servicio().AutenticarAsync("vendedor1", "Vendedor2026!", "PC-1");

        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, resultado.Estado);
        Assert.Equal("cuenta bloqueada", _usuarios.Bitacora[^1].Detalle);
    }

    [Fact]
    public async Task Pasados_los_15_minutos_vuelve_a_ingresar_y_se_limpia_el_bloqueo()
    {
        await Bloquear("vendedor1");
        _ahora += ServicioAutenticacion.DuracionBloqueo + TimeSpan.FromSeconds(1);

        var resultado = await Servicio().AutenticarAsync("vendedor1", "Vendedor2026!", "PC-1");

        Assert.True(resultado.Exitoso);
        Assert.Null(_usuarios.Cuenta("vendedor1").BloqueadoHasta);
        Assert.Equal(0, _usuarios.Cuenta("vendedor1").IntentosFallidos);
    }

    [Fact]
    public async Task Un_acceso_correcto_reinicia_los_intentos_fallidos()
    {
        var servicio = Servicio();
        await servicio.AutenticarAsync("encargado", "mal", "PC-1");
        await servicio.AutenticarAsync("encargado", "mal", "PC-1");

        await servicio.AutenticarAsync("encargado", "Encargado2026!", "PC-1");

        Assert.Equal(0, _usuarios.Cuenta("encargado").IntentosFallidos);
    }

    [Fact]
    public async Task El_bloqueo_de_una_cuenta_no_afecta_a_las_otras()
    {
        await Bloquear("vendedor1");

        Assert.True((await Servicio().AutenticarAsync("encargado", "Encargado2026!", "PC-1")).Exitoso);
    }

    [Fact]
    public async Task Sin_conexion_la_excepcion_llega_a_quien_llama()
    {
        _usuarios.Error = new SinConexionException(new TimeoutException());

        await Assert.ThrowsAsync<SinConexionException>(() => Servicio().AutenticarAsync("vendedor1", "x", "PC-1"));
    }

    private async Task Bloquear(string usuario)
    {
        var servicio = Servicio();
        for (var i = 0; i < ServicioAutenticacion.IntentosMaximos; i++)
            await servicio.AutenticarAsync(usuario, "mal", "PC-1");
    }
}
