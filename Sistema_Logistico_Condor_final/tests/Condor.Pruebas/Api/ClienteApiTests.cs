using Condor.ClienteApi;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;
using Condor.Dominio.Validacion;
using Condor.Dominio.Ventas;
using Condor.Pruebas.Infraestructura;

namespace Condor.Pruebas.Api;

/// <summary>
/// CC-01: la app de escritorio usa el backend. Estas pruebas llaman a la API
/// en memoria con el mismo cliente HTTP y los mismos repositorios
/// (Condor.ClienteApi) que usa la app, y comprueban que los datos, las reglas
/// y los errores llegan igual que cuando la app hablaba con PostgreSQL.
/// </summary>
public class ClienteApiTests
{
    private static async Task<(ApiDePrueba Api, ClienteServidor Servidor)> IngresarAsync(string usuario = "vendedor1",
        string clave = "Vendedor2026!")
    {
        var api = new ApiDePrueba();
        var servidor = new ClienteServidor(api.CreateClient());
        var resultado = await new AutenticadorApi(servidor).AutenticarAsync(usuario, clave, "PC-1");
        Assert.True(resultado.Exitoso, resultado.Mensaje);
        return (api, servidor);
    }

    // ---- Ingreso ------------------------------------------------------------

    [Fact]
    public async Task El_ingreso_por_la_API_devuelve_la_cuenta_y_guarda_el_token()
    {
        await using var api = new ApiDePrueba();
        var servidor = new ClienteServidor(api.CreateClient());

        var resultado = await new AutenticadorApi(servidor).AutenticarAsync("encargado", "Encargado2026!", "PC-1");

        Assert.True(resultado.Exitoso);
        Assert.Equal(Roles.Encargado, resultado.Cuenta!.Rol);
        Assert.NotNull(servidor.Token);
    }

    [Fact]
    public async Task La_clave_equivocada_y_el_bloqueo_llegan_como_resultado_no_como_excepcion()
    {
        await using var api = new ApiDePrueba();
        var autenticador = new AutenticadorApi(new ClienteServidor(api.CreateClient()));

        var equivocada = await autenticador.AutenticarAsync("vendedor1", "mal", "PC-1");
        for (var i = 0; i < 4; i++)
            await autenticador.AutenticarAsync("vendedor1", "mal", "PC-1");
        var bloqueada = await autenticador.AutenticarAsync("vendedor1", "Vendedor2026!", "PC-1");
        var incompleto = await autenticador.AutenticarAsync("", "", "PC-1");

        Assert.Equal(EstadoAutenticacion.CredencialesInvalidas, equivocada.Estado);
        Assert.Equal(ServicioAutenticacion.MensajeInvalidas, equivocada.Mensaje);
        Assert.Equal(EstadoAutenticacion.CuentaBloqueada, bloqueada.Estado);
        Assert.Contains("bloqueada", bloqueada.Mensaje);
        Assert.Equal(EstadoAutenticacion.DatosIncompletos, incompleto.Estado);
    }

    [Fact]
    public async Task El_login_de_la_app_funciona_con_el_backend()
    {
        await using var api = new ApiDePrueba();
        var vm = new Condor.Presentacion.ViewModels.LoginViewModel(new AutenticadorApi(new ClienteServidor(api.CreateClient())), "PC-1")
        {
            Usuario = "vendedor1",
            Clave = "Vendedor2026!",
        };

        await vm.IngresarCommand.EjecutarAsync();

        Assert.Equal("vendedor1", vm.Cuenta!.NombreUsuario);
    }

    // ---- Errores de conexión y permisos -------------------------------------

    [Fact]
    public async Task Sin_la_API_las_operaciones_lanzan_SinConexion_y_Probar_da_false()
    {
        // Puerto cerrado: nadie escucha.
        var servidor = new ClienteServidor(new ConfiguracionApi { Url = "http://127.0.0.1:1", TiempoEsperaSegundos = 2 });

        Assert.False(await servidor.ProbarAsync());
        await Assert.ThrowsAsync<SinConexionException>(() => new ProductoRepositorioApi(servidor).ListarAsync());
    }

    [Fact]
    public async Task Con_la_base_caida_el_cliente_recibe_SinConexion()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        api.Comprobantes.ErrorAlEmitir = new SinConexionException(new TimeoutException());

        await Assert.ThrowsAsync<SinConexionException>(() => new ComprobanteRepositorioApi(servidor).EmitirAsync(Boleta(api)));
    }

    [Fact]
    public async Task Sin_token_se_avisa_que_la_sesion_vencio()
    {
        await using var api = new ApiDePrueba();
        var servidor = new ClienteServidor(api.CreateClient());

        await Assert.ThrowsAsync<SesionVencidaException>(() => new ProductoRepositorioApi(servidor).ListarAsync());
    }

    [Fact]
    public async Task El_vendedor_no_puede_usar_proveedores_ni_compras()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;

        await Assert.ThrowsAsync<UnauthorizedAccessException>(() => new ProveedorRepositorioApi(servidor).BuscarAsync(null));
        await Assert.ThrowsAsync<UnauthorizedAccessException>(() => new CompraRepositorioApi(servidor).BuscarAsync(new FiltroCompras()));
    }

    // ---- Datos y reglas -----------------------------------------------------

    [Fact]
    public async Task Productos_buscar_registrar_y_aviso_de_catalogo()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var productos = new ProductoRepositorioApi(servidor);
        var antes = await AvisoCatalogoApi.VersionAsync(servidor);

        var nuevo = await productos.RegistrarAsync(DatosPrueba.Nuevo("Lija al agua N° 120", 2.80m));
        var encontrados = await productos.BuscarPorNombreAsync("lija");

        Assert.True(nuevo.Id > 0);
        Assert.Equal(nuevo.Id, Assert.Single(encontrados).Id);
        Assert.Null(await productos.BuscarPorCodigoBarrasAsync("7750000000000"));
        Assert.True(await AvisoCatalogoApi.VersionAsync(servidor) > antes);
    }

    [Fact]
    public async Task Un_producto_invalido_llega_como_ProductoInvalidoException_con_sus_errores()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;

        var ex = await Assert.ThrowsAsync<ProductoInvalidoException>(() =>
            new ProductoRepositorioApi(servidor).AsignarCodigoBarrasAsync(1, "código con espacios"));

        Assert.NotEmpty(ex.Errores);
    }

    [Fact]
    public async Task Un_duplicado_llega_con_el_mensaje_de_la_regla()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var clientes = new ClienteRepositorioApi(servidor);

        var ex = await Assert.ThrowsAsync<ErrorServidorException>(() => clientes.RegistrarAsync(DatosPrueba.ClienteDni()));

        Assert.Equal(409, ex.Estado);
        Assert.Contains("Ya existe un cliente con DNI 45879632", ex.Message);
    }

    [Fact]
    public async Task Clientes_por_documento_y_por_texto()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var clientes = new ClienteRepositorioApi(servidor);

        var porDni = await clientes.BuscarPorDocumentoAsync(TipoDocumento.Dni, "45879632");
        var noExiste = await clientes.BuscarPorDocumentoAsync(TipoDocumento.Dni, "11111111");
        var porTexto = await clientes.BuscarAsync("constructora");

        Assert.Equal("Juan Pérez Quispe", porDni!.Nombre);
        Assert.Null(noExiste);
        Assert.Equal(TipoDocumento.Ruc, Assert.Single(porTexto).TipoDocumento);
    }

    [Fact]
    public async Task El_comprobante_viaja_con_su_detalle_y_el_servidor_recalcula_totales_y_usuario()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var comprobantes = new ComprobanteRepositorioApi(servidor);
        var boleta = Boleta(api);
        boleta.Total = 1m;              // Manipulado: el servidor lo recalcula.
        boleta.Usuario = "encargado";   // Suplantado: el servidor usa el del token.

        var emitida = await comprobantes.EmitirAsync(boleta);
        var leida = await comprobantes.ObtenerAsync(emitida.Id);

        Assert.Same(boleta, emitida);
        Assert.Equal("B001-00000001", emitida.NumeroCompleto);
        Assert.Equal(65.00m, emitida.Total);
        Assert.Equal("vendedor1", emitida.Usuario);
        Assert.Equal(2, leida!.Detalle.Count);
        Assert.Equal(32.50m, leida.Detalle[0].PrecioUnitario);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(100_000)]
    [InlineData(1.0005)]
    public async Task CRQ14_el_servidor_rechaza_cantidades_fuera_de_rango(double cantidad)
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var boleta = Boleta(api);
        boleta.Detalle[0].Cantidad = (decimal)cantidad;

        var error = await Assert.ThrowsAsync<ErrorServidorException>(() => new ComprobanteRepositorioApi(servidor).EmitirAsync(boleta));

        Assert.Equal(400, error.Estado);
        Assert.Empty(api.Comprobantes.Comprobantes);
    }

    [Fact]
    public async Task CRQ14_el_servidor_rechaza_mas_de_100_lineas()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var boleta = Boleta(api);
        var linea = boleta.Detalle[0];
        for (var i = boleta.Detalle.Count; i <= 100; i++)
            boleta.Detalle.Add(new DetalleComprobante { Item = i + 1, ProductoId = linea.ProductoId, Descripcion = linea.Descripcion, Unidad = linea.Unidad, Cantidad = 1, PrecioUnitario = linea.PrecioUnitario });

        var error = await Assert.ThrowsAsync<ErrorServidorException>(() => new ComprobanteRepositorioApi(servidor).EmitirAsync(boleta));

        Assert.Equal(400, error.Estado);
        Assert.Contains("100 líneas", error.Message);
    }

    [Fact]
    public async Task El_historial_devuelve_el_resultado_con_cantidad_y_total()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var comprobantes = new ComprobanteRepositorioApi(servidor);
        await comprobantes.EmitirAsync(Boleta(api));
        await comprobantes.EmitirAsync(Boleta(api));

        var resultado = await comprobantes.BuscarAsync(new FiltroComprobantes(Limite: 10));
        var recientes = await comprobantes.ListarRecientesAsync(5);

        Assert.Equal(2, resultado.Cantidad);
        Assert.Equal(2, resultado.Comprobantes.Count);
        Assert.Equal(2, recientes.Count);
    }

    [Fact]
    public async Task El_encargado_registra_y_busca_compras_con_su_detalle()
    {
        var (api, servidor) = await IngresarAsync("encargado", "Encargado2026!");
        await using var _ = api;
        var proveedor = api.Proveedores.Proveedores[0];
        var compra = ValidadorCompra.Preparar(new Compra
        {
            ProveedorId = proveedor.Id,
            Proveedor = proveedor,
            Serie = "F001",
            Numero = 77,
            FechaEmision = DateOnly.FromDateTime(DateTime.Today),
            TerminalId = 1,
            Detalle = { new() { ProductoId = 1, Descripcion = "Cemento", Unidad = "BLS", Cantidad = 100, CostoUnitario = 27.50m } },
        }, DateOnly.FromDateTime(DateTime.Today));
        var compras = new CompraRepositorioApi(servidor);

        var registrada = await compras.RegistrarAsync(compra);
        var leida = await compras.ObtenerAsync(registrada.Id);
        var resultado = await compras.BuscarAsync(new FiltroCompras());

        Assert.Equal(2750m, leida!.Total);
        Assert.Single(leida.Detalle);
        Assert.Equal(1, resultado.Cantidad);
    }

    [Fact]
    public async Task El_respaldo_se_genera_en_la_PC_principal_y_se_registra()
    {
        var (api, servidor) = await IngresarAsync("encargado", "Encargado2026!");
        await using var _ = api;
        var config = await GeneradorRespaldoApi.ConfiguracionAsync(servidor);
        var avances = new List<int>();

        var respaldo = await new GeneradorRespaldoApi(servidor).GenerarAsync(config!.Carpeta,
            new SincronoProgress<ProgresoRespaldo>(p => avances.Add(p.Porcentaje)));
        respaldo.TerminalId = 1;
        await new RespaldoRepositorioApi(servidor).RegistrarAsync(respaldo);

        Assert.True(config.Configurado);
        Assert.Equal(DatosPrueba.DiscoExterno, respaldo.Carpeta);
        Assert.Equal(new[] { 5, 100 }, avances);
        Assert.NotNull(await new RespaldoRepositorioApi(servidor).UltimoAsync());
    }

    [Fact]
    public async Task Terminal_empresa_y_resumen_de_pendientes()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;

        var terminal = await new TerminalRepositorioApi(servidor).RegistrarAccesoAsync("PC-3");
        var otraVez = await new TerminalRepositorioApi(servidor).RegistrarAccesoAsync("PC-3");
        var empresa = await new EmpresaRepositorioApi(servidor).ObtenerAsync();
        var resumen = await new EnvioSunatRepositorioApi(servidor).ResumenPendientesAsync();

        Assert.Equal(terminal.Id, otraVez.Id);
        Assert.Equal(DatosPrueba.Empresa().Ruc, empresa.Ruc);
        Assert.NotNull(resumen);
    }

    // ---- DEF-01 (CRQ-07): el precio no se toma de la PC ---------------------

    [Fact]
    public async Task DEF01_el_precio_y_la_descripcion_salen_del_catalogo_no_de_la_PC()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var comprobantes = new ComprobanteRepositorioApi(servidor);
        var boleta = Boleta(api);
        foreach (var linea in boleta.Detalle)
        {
            linea.PrecioUnitario = 0.10m;   // Manipulado en la PC.
            linea.Descripcion = "Regalo";
        }

        var emitida = await comprobantes.EmitirAsync(boleta);
        var leida = await comprobantes.ObtenerAsync(emitida.Id);

        Assert.Equal(65.00m, emitida.Total);
        Assert.All(leida!.Detalle, l => Assert.Equal(32.50m, l.PrecioUnitario));
        Assert.All(leida.Detalle, l => Assert.Equal(api.Productos.Productos[0].Nombre, l.Descripcion));
    }

    [Fact]
    public async Task DEF01_la_venta_desde_una_proforma_respeta_el_precio_cotizado_aunque_cambie_el_catalogo()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var comprobantes = new ComprobanteRepositorioApi(servidor);
        var cemento = api.Productos.Productos[0];
        var proforma = await comprobantes.EmitirAsync(EmisionComprobante.Preparar(new SolicitudEmision(TipoEmision.Proforma,
            new[] { new DetalleComprobante { ProductoId = cemento.Id, Descripcion = cemento.Nombre, Unidad = cemento.Unidad, Cantidad = 2, PrecioUnitario = 32.50m } })));
        cemento.Precio = 40.00m;            // El catálogo sube después de cotizar.
        var venta = EmisionComprobante.Preparar(new SolicitudEmision(TipoEmision.Boleta,
            proforma.Detalle.Select(l => new DetalleComprobante { ProductoId = l.ProductoId, Descripcion = l.Descripcion, Unidad = l.Unidad, Cantidad = l.Cantidad, PrecioUnitario = 0.10m }).ToList(),
            Proforma: proforma));

        var emitida = await comprobantes.EmitirAsync(venta);
        var leida = await comprobantes.ObtenerAsync(emitida.Id);

        Assert.Equal(proforma.Id, leida!.ProformaId);
        Assert.Equal(32.50m, leida.Detalle.Single().PrecioUnitario);
        Assert.Equal(65.00m, emitida.Total);
    }

    [Fact]
    public async Task DEF01_un_producto_que_no_esta_en_el_catalogo_se_rechaza()
    {
        var (api, servidor) = await IngresarAsync();
        await using var _ = api;
        var boleta = Boleta(api);
        boleta.Detalle[0].ProductoId = 999_999;

        var error = await Assert.ThrowsAsync<ErrorServidorException>(() => new ComprobanteRepositorioApi(servidor).EmitirAsync(boleta));

        Assert.Equal(400, error.Estado);
        Assert.Empty(api.Comprobantes.Comprobantes);
    }

    private static Comprobante Boleta(ApiDePrueba api)
    {
        var cemento = api.Productos.Productos[0];
        var boleta = EmisionComprobante.Preparar(new SolicitudEmision(TipoEmision.Boleta, new[]
        {
            new DetalleComprobante { ProductoId = cemento.Id, Descripcion = cemento.Nombre, Unidad = cemento.Unidad, Cantidad = 1, PrecioUnitario = 32.50m },
            new DetalleComprobante { ProductoId = cemento.Id, Descripcion = cemento.Nombre, Unidad = cemento.Unidad, Cantidad = 1, PrecioUnitario = 32.50m },
        }));
        boleta.TerminalId = 1;
        return boleta;
    }

    /// <summary>IProgress que informa en el mismo hilo (Progress&lt;T&gt; usaría el contexto de sincronización).</summary>
    private sealed class SincronoProgress<T>(Action<T> accion) : IProgress<T>
    {
        public void Report(T valor) => accion(valor);
    }
}
