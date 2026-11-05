using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Condor.Api;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Reportes;
using Condor.Dominio.Sunat;

namespace Condor.Pruebas.Api;

/// <summary>
/// CC-01: backend REST. Ingreso con JWT, permisos por rol, validaciones y
/// emisión de comprobantes con las mismas reglas de la app de escritorio.
/// </summary>
public class ApiTests
{
    // ---- Salud e ingreso ----------------------------------------------------

    [Fact]
    public async Task Salud_responde_sin_token()
    {
        await using var api = new ApiDePrueba();

        var salud = await api.CreateClient().GetFromJsonAsync<SaludDto>("/api/salud");

        Assert.Equal("OK", salud!.Estado);
        Assert.Equal("API-PRUEBA", salud.Terminal);
    }

    [Fact]
    public async Task Salud_sin_base_de_datos_responde_503()
    {
        await using var api = new ApiDePrueba { BaseDatosResponde = false };

        var respuesta = await api.CreateClient().GetAsync("/api/salud");

        Assert.Equal(HttpStatusCode.ServiceUnavailable, respuesta.StatusCode);
    }

    [Fact]
    public async Task Login_correcto_devuelve_el_token_y_el_rol()
    {
        await using var api = new ApiDePrueba();

        var respuesta = await api.CreateClient().PostAsJsonAsync("/api/auth/login", new LoginPedido("encargado", "Encargado2026!"));
        var login = await respuesta.Content.ReadFromJsonAsync<LoginRespuesta>();

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
        Assert.Equal("ENCARGADO", login!.Rol);
        Assert.Equal(3, login.Token.Split('.').Length);
        Assert.True(login.Expira > DateTimeOffset.UtcNow);
    }

    [Theory]
    [InlineData("vendedor1", "mal", HttpStatusCode.Unauthorized)]
    [InlineData("nadie", "Vendedor2026!", HttpStatusCode.Unauthorized)]
    [InlineData("", "", HttpStatusCode.BadRequest)]
    public async Task Login_invalido_responde_con_el_codigo_que_corresponde(string usuario, string clave, HttpStatusCode esperado)
    {
        await using var api = new ApiDePrueba();

        var respuesta = await api.CreateClient().PostAsJsonAsync("/api/auth/login", new LoginPedido(usuario, clave));

        Assert.Equal(esperado, respuesta.StatusCode);
    }

    [Fact]
    public async Task Cinco_claves_equivocadas_bloquean_la_cuenta_con_423()
    {
        await using var api = new ApiDePrueba();
        var http = api.CreateClient();
        HttpResponseMessage? ultima = null;

        for (var i = 0; i < 5; i++)
            ultima = await http.PostAsJsonAsync("/api/auth/login", new LoginPedido("vendedor1", "mal"));
        var conLaCorrecta = await http.PostAsJsonAsync("/api/auth/login", new LoginPedido("vendedor1", "Vendedor2026!"));

        Assert.Equal(HttpStatusCode.Locked, ultima!.StatusCode);
        Assert.Equal(HttpStatusCode.Locked, conLaCorrecta.StatusCode);
    }

    [Fact]
    public async Task Yo_devuelve_quien_ingreso()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var yo = await http.GetFromJsonAsync<UsuarioActual>("/api/auth/yo");

        Assert.Equal(new UsuarioActual("vendedor1", "Usuario vendedor1", "VENDEDOR"), yo);
    }

    // ---- Autorización -------------------------------------------------------

    [Theory]
    [InlineData("/api/productos?texto=cem")]
    [InlineData("/api/comprobantes")]
    [InlineData("/api/reportes/ventas")]
    public async Task Sin_token_responde_401(string ruta)
    {
        await using var api = new ApiDePrueba();

        var respuesta = await api.CreateClient().GetAsync(ruta);

        Assert.Equal(HttpStatusCode.Unauthorized, respuesta.StatusCode);
    }

    [Fact]
    public async Task Un_token_alterado_no_se_acepta()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var token = http.DefaultRequestHeaders.Authorization!.Parameter!;
        http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token[..^4] + "AAAA");

        var respuesta = await http.GetAsync("/api/productos");

        Assert.Equal(HttpStatusCode.Unauthorized, respuesta.StatusCode);
    }

    [Theory]
    [InlineData("/api/reportes/ventas")]
    [InlineData("/api/proveedores")]
    [InlineData("/api/respaldos")]
    public async Task El_vendedor_recibe_403_en_las_rutas_del_encargado(string ruta)
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.GetAsync(ruta);

        Assert.Equal(HttpStatusCode.Forbidden, respuesta.StatusCode);
    }

    [Fact]
    public async Task El_vendedor_no_puede_registrar_proveedores()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/proveedores", new NuevoProveedorPedido("20100047218", "X", null, null, null, null, null));

        Assert.Equal(HttpStatusCode.Forbidden, respuesta.StatusCode);
        Assert.Equal(3, api.Proveedores.Proveedores.Count);
    }

    // ---- Productos y clientes -----------------------------------------------

    [Fact]
    public async Task Busca_productos_por_nombre()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var productos = await http.GetFromJsonAsync<List<ProductoDto>>("/api/productos?texto=esmalte");

        Assert.Equal(2, productos!.Count);
        Assert.All(productos, p => Assert.Contains("Esmalte", p.Nombre));
    }

    [Fact]
    public async Task Registrar_un_producto_invalido_responde_400_con_los_errores()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/productos", new NuevoProductoPedido("", -5m, null, null));
        var problema = await respuesta.Content.ReadFromJsonAsync<JsonElement>();

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
        Assert.True(problema.GetProperty("errores").GetArrayLength() >= 2);
    }

    [Fact]
    public async Task Registrar_un_producto_valido_responde_201()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/productos", new NuevoProductoPedido("Lija al agua N° 100", 2.50m, "UND", null));

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.Contains(api.Productos.Productos, p => p.Nombre == "Lija al agua N° 100");
    }

    [Fact]
    public async Task Cliente_por_documento_200_404_y_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        Assert.Equal(HttpStatusCode.OK, (await http.GetAsync("/api/clientes/45879632")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await http.GetAsync("/api/clientes/12345678")).StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, (await http.GetAsync("/api/clientes/123")).StatusCode);
    }

    [Fact]
    public async Task Registrar_un_cliente_con_RUC_de_digito_verificador_invalido_responde_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/clientes", new NuevoClientePedido("20131312956", "Empresa X", null));

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
    }

    // ---- Comprobantes -------------------------------------------------------

    [Fact]
    public async Task Emitir_boleta_usa_el_precio_del_catalogo_y_el_usuario_del_token()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var cemento = api.Productos.Productos[0];

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("boleta", null, new[] { new LineaPedido(cemento.Id, 2) }));
        var boleta = await respuesta.Content.ReadFromJsonAsync<ComprobanteDto>();

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.Equal("B001-00000001", boleta!.Numero);
        Assert.Equal(cemento.Precio * 2, boleta.Total);
        var guardado = Assert.Single(api.Comprobantes.Comprobantes);
        Assert.Equal("vendedor1", guardado.Usuario);
        Assert.Equal(9, guardado.TerminalId);
        Assert.Equal(EstadoSunat.Pendiente, boleta.EstadoSunat);
    }

    [Fact]
    public async Task Emitir_factura_con_cliente_RUC_registrado()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("FACTURA", "20131312955", new[] { new LineaPedido(1, 10) }));
        var factura = await respuesta.Content.ReadFromJsonAsync<ComprobanteDto>();

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.StartsWith("F001-", factura!.Numero);
        Assert.Equal("RUC", factura.Cliente!.TipoDocumento);
    }

    [Theory]
    [InlineData("FACTURA", null, 1, 1, "La factura requiere un cliente con RUC")]
    [InlineData("TICKET", null, 1, 1, "Tipo de comprobante inválido")]
    [InlineData("BOLETA", null, 999, 1, "El producto 999 no existe")]
    [InlineData("BOLETA", null, 1, 0, "debe ser mayor que cero")]
    [InlineData("BOLETA", "12345678", 1, 1, "no está registrado")]
    [InlineData("BOLETA", null, 1, 100, "deben llevar el DNI del cliente")]
    public async Task Emitir_con_datos_invalidos_responde_400_y_no_guarda(string tipo, string? documento, long producto,
        decimal cantidad, string mensaje)
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido(tipo, documento, new[] { new LineaPedido(producto, cantidad) }));
        var texto = await respuesta.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
        Assert.Contains(mensaje, texto);
        Assert.Empty(api.Comprobantes.Comprobantes);
    }

    [Fact]
    public async Task Emitir_sin_detalle_responde_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes", new EmitirPedido("BOLETA", null, null));

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
    }

    [Fact]
    public async Task Con_la_base_caida_responde_503()
    {
        await using var api = new ApiDePrueba();
        api.Comprobantes.ErrorAlEmitir = new SinConexionException(new TimeoutException());
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("BOLETA", null, new[] { new LineaPedido(1, 1) }));

        Assert.Equal(HttpStatusCode.ServiceUnavailable, respuesta.StatusCode);
    }

    [Fact]
    public async Task Antes_de_registrar_la_terminal_emitir_responde_503()
    {
        await using var api = new ApiDePrueba();
        api.Contexto.TerminalId = 0;
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("BOLETA", null, new[] { new LineaPedido(1, 1) }));

        Assert.Equal(HttpStatusCode.ServiceUnavailable, respuesta.StatusCode);
    }

    [Fact]
    public async Task Historial_y_detalle_del_comprobante_emitido()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var creado = await (await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("NOTA_VENTA", null, new[] { new LineaPedido(2, 3) }))).Content.ReadFromJsonAsync<ComprobanteDto>();

        var historial = await http.GetFromJsonAsync<HistorialDto>("/api/comprobantes");
        var detalle = await http.GetFromJsonAsync<ComprobanteDto>($"/api/comprobantes/{creado!.Id}");

        Assert.Equal(1, historial!.Comprobantes.Count);
        Assert.Equal("NO APLICA", detalle!.EstadoSunat);
        Assert.Equal(3, detalle.Detalle.Single().Cantidad);
        Assert.Equal(HttpStatusCode.NotFound, (await http.GetAsync("/api/comprobantes/999")).StatusCode);
    }

    [Fact]
    public async Task Historial_con_fechas_al_reves_responde_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.GetAsync("/api/comprobantes?desde=2026-11-21&hasta=2026-11-20");

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
    }

    // ---- Encargado ----------------------------------------------------------

    [Fact]
    public async Task El_encargado_obtiene_el_reporte_consolidado()
    {
        await using var api = new ApiDePrueba();
        api.Reporte.Ventas.Add(new VentaResumida(new DateTimeOffset(2026, 11, 20, 10, 0, 0, TimeSpan.FromHours(-5)),
            TipoComprobante.Boleta, 118m, 18m, EstadoSunat.Aceptado, "PC-1", "vendedor1"));
        var http = await api.EncargadoAsync();

        var reporte = await http.GetFromJsonAsync<JsonElement>("/api/reportes/ventas?desde=2026-11-20&hasta=2026-11-20");

        Assert.Equal(1, reporte.GetProperty("cantidadVentas").GetInt32());
        Assert.Equal(118m, reporte.GetProperty("total").GetDecimal());
        Assert.Equal("Boleta", reporte.GetProperty("porTipo")[0].GetProperty("clave").GetString());
    }

    [Fact]
    public async Task El_reporte_de_mas_de_un_anio_responde_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.EncargadoAsync();

        var respuesta = await http.GetAsync("/api/reportes/ventas?desde=2025-01-01&hasta=2026-11-20");

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
    }

    [Fact]
    public async Task El_encargado_registra_un_proveedor_y_el_duplicado_responde_409()
    {
        await using var api = new ApiDePrueba();
        var http = await api.EncargadoAsync();
        var existente = api.Proveedores.Proveedores[0];

        var duplicado = await http.PostAsJsonAsync("/api/proveedores",
            new NuevoProveedorPedido(existente.Ruc, "Otra razón social", null, null, null, null, null));
        var lista = await http.GetFromJsonAsync<List<ProveedorDto>>("/api/proveedores");

        Assert.Equal(HttpStatusCode.Conflict, duplicado.StatusCode);
        Assert.Equal(3, lista!.Count);
    }
}
