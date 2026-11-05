using Condor.Dominio.Seguridad;

namespace Condor.PruebasUnitarias.CC01;

/// <summary>
/// Componente 4: <see cref="ServicioAutenticacion"/> y <see cref="HashClave"/>
/// (RF-01, RNF-03; agregados por el cambio CC-01 de G02). La base de datos y el
/// reloj se reemplazan por <see cref="RepositorioUsuariosFalso"/> y <see cref="RelojFalso"/>.
/// </summary>
public class ServicioAutenticacionTests
{
    private static readonly DateTimeOffset Inicio = new(2026, 11, 1, 9, 0, 0, TimeSpan.FromHours(-5));

    private readonly RepositorioUsuariosFalso _repo = new();
    private readonly RelojFalso _reloj = new(Inicio);
    private readonly ServicioAutenticacion _servicio;

    // xUnit crea una instancia nueva de la clase por cada prueba: repositorio y
    // reloj son propios de cada caso y el orden de ejecución no influye.
    public ServicioAutenticacionTests()
    {
        _repo.Agregar("vendedor1", "Condor2026!");
        _servicio = new ServicioAutenticacion(_repo, _reloj.Funcion);
    }

    [Fact]
    [Trait("Caso", "PU-19"), Trait("Requisito", "RF-01"), Trait("Riesgo", "R02")]
    public async Task PU_19_Ingreso_correcto_normaliza_el_usuario_y_queda_en_la_bitacora()
    {
        var r = await _servicio.AutenticarAsync("  Vendedor1 ", "Condor2026!", "CAJA-1");

        Assert.Equal(EstadoAutenticacion.Exitoso, r.Estado);
        Assert.Equal("vendedor1", r.Cuenta!.NombreUsuario);
        Assert.Equal(Inicio, r.Cuenta.UltimoAcceso);
        Assert.Equal(("vendedor1", "CAJA-1", true, "acceso correcto"), Assert.Single(_repo.Bitacora));
    }

    [Theory]
    [Trait("Caso", "PU-20"), Trait("Requisito", "RNF-03"), Trait("Riesgo", "R02")]
    [InlineData("vendedor1", "clave-equivocada")]
    [InlineData("noexiste", "Condor2026!")]
    public async Task PU_20_Usuario_inexistente_y_clave_equivocada_dan_el_mismo_mensaje(string usuario, string clave)
    {
        var r = await _servicio.AutenticarAsync(usuario, clave, "CAJA-1");

        Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, r.Estado);
        Assert.Equal("Usuario o contraseña incorrectos.", r.Mensaje);
        Assert.Null(r.Cuenta);
        Assert.False(Assert.Single(_repo.Bitacora).Exitoso);
    }

    [Theory]
    [Trait("Caso", "PU-21"), Trait("Requisito", "RF-01"), Trait("Riesgo", "R02")]
    [InlineData("", "Condor2026!")]
    [InlineData("   ", "Condor2026!")]
    [InlineData("vendedor1", "")]
    [InlineData(null, null)]
    public async Task PU_21_Datos_vacios_no_consultan_la_base(string? usuario, string? clave)
    {
        var r = await _servicio.AutenticarAsync(usuario, clave, "CAJA-1");

        Assert.Equal(EstadoAutenticacion.DatosIncompletos, r.Estado);
        Assert.Equal(0, _repo.Busquedas);  // el doble espía no recibió ninguna búsqueda
        Assert.Empty(_repo.Bitacora);
    }

    [Fact]
    [Trait("Caso", "PU-22"), Trait("Requisito", "RNF-03"), Trait("Riesgo", "R02")]
    public async Task PU_22_El_quinto_intento_fallido_bloquea_15_minutos_aunque_luego_se_use_la_clave_correcta()
    {
        for (var i = 1; i <= 4; i++)
        {
            var fallo = await _servicio.AutenticarAsync("vendedor1", "mala", "CAJA-1");
            Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, fallo.Estado); // 1.º a 4.º: aún no bloquea
        }

        var quinto = await _servicio.AutenticarAsync("vendedor1", "mala", "CAJA-1");
        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, quinto.Estado);
        Assert.Equal((1L, 0, Inicio.AddMinutes(15)), _repo.Actualizaciones[^1]);

        _reloj.Avanzar(TimeSpan.FromMinutes(14).Add(TimeSpan.FromSeconds(59)));
        var conClaveCorrecta = await _servicio.AutenticarAsync("vendedor1", "Condor2026!", "CAJA-1");
        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, conClaveCorrecta.Estado);
        Assert.Equal("cuenta bloqueada", _repo.Bitacora[^1].Detalle);
    }

    [Fact]
    [Trait("Caso", "PU-23"), Trait("Requisito", "RNF-03"), Trait("Riesgo", "R02")]
    public async Task PU_23_A_los_15_minutos_exactos_se_desbloquea_y_reinicia_los_intentos()
    {
        for (var i = 0; i < ServicioAutenticacion.IntentosMaximos; i++)
            await _servicio.AutenticarAsync("vendedor1", "mala", "CAJA-1");

        _reloj.Avanzar(ServicioAutenticacion.DuracionBloqueo); // límite: 15:00 exactos
        var r = await _servicio.AutenticarAsync("vendedor1", "Condor2026!", "CAJA-1");

        Assert.Equal(EstadoAutenticacion.Exitoso, r.Estado);
        Assert.Equal(0, r.Cuenta!.IntentosFallidos);
        Assert.Null(r.Cuenta.BloqueadoHasta);
        Assert.Equal((1L, 0, (DateTimeOffset?)null), _repo.Actualizaciones[^1]);
    }

    [Fact]
    [Trait("Caso", "PU-24"), Trait("Requisito", "RNF-03"), Trait("Riesgo", "R02")]
    public void PU_24_La_clave_se_guarda_como_PBKDF2_SHA256_de_100000_iteraciones_con_sal_de_16_bytes()
    {
        var hash = HashClave.Generar("Condor2026!");
        var partes = hash.Split('$');

        Assert.Equal("pbkdf2-sha256", partes[0]);
        Assert.Equal("100000", partes[1]);
        Assert.Equal(16, Convert.FromBase64String(partes[2]).Length);
        Assert.DoesNotContain("Condor2026!", hash);
        Assert.True(HashClave.Verificar("Condor2026!", hash));
        Assert.False(HashClave.Verificar("condor2026!", hash));
        Assert.False(HashClave.Verificar("Condor2026!", "pbkdf2-sha256$100000$no-es-base64$x"));
        Assert.NotEqual(hash, HashClave.Generar("Condor2026!")); // sal nueva cada vez
    }
}
