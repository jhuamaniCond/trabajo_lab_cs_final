using System.Net;
using System.Net.Http.Json;
using Condor.Api;

namespace Condor.Pruebas.Api;

/// <summary>
/// CC-03: portal web del mostrador. La API sirve las páginas de wwwroot y
/// expone las proformas y su conversión en venta (HU-09) con las mismas
/// reglas de EmisionComprobante.
/// </summary>
public class PortalWebTests
{
    private static async Task<ComprobanteDto> EmitirProformaAsync(HttpClient http, string? documento = "45879632")
    {
        var respuesta = await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("PROFORMA", documento, new[] { new LineaPedido(1, 4), new LineaPedido(2, 2) }));
        respuesta.EnsureSuccessStatusCode();
        return (await respuesta.Content.ReadFromJsonAsync<ComprobanteDto>())!;
    }

    [Fact]
    public async Task La_raiz_sirve_el_portal_sin_token()
    {
        await using var api = new ApiDePrueba();

        var respuesta = await api.CreateClient().GetAsync("/");
        var html = await respuesta.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
        Assert.Contains("Ferretería Cóndor", html);
        Assert.Contains("id=\"CampoUsuario\"", html);
    }

    [Fact]
    public async Task Proformas_lista_la_emitida_como_vigente()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var proforma = await EmitirProformaAsync(http);

        var lista = await http.GetFromJsonAsync<List<ProformaDto>>("/api/proformas");

        var dto = Assert.Single(lista!);
        Assert.Equal(proforma.Numero, dto.Numero);
        Assert.Equal("VIGENTE", dto.Estado);
        Assert.Null(dto.ConvertidaEn);
    }

    [Fact]
    public async Task Convertir_la_proforma_emite_la_boleta_y_la_marca_convertida()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var proforma = await EmitirProformaAsync(http);

        var respuesta = await http.PostAsJsonAsync($"/api/proformas/{proforma.Id}/convertir", new ConvertirPedido("BOLETA_DNI", null));
        var boleta = await respuesta.Content.ReadFromJsonAsync<ComprobanteDto>();
        var lista = await http.GetFromJsonAsync<List<ProformaDto>>("/api/proformas");

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.StartsWith("B001-", boleta!.Numero);
        Assert.Equal(proforma.Total, boleta.Total);
        Assert.Equal("vendedor1", boleta.Usuario);
        Assert.Equal("CONVERTIDA", lista!.Single().Estado);
        Assert.Equal(boleta.Numero, lista!.Single().ConvertidaEn);
    }

    [Fact]
    public async Task Una_proforma_convertida_no_se_convierte_otra_vez()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var proforma = await EmitirProformaAsync(http);
        await http.PostAsJsonAsync($"/api/proformas/{proforma.Id}/convertir", new ConvertirPedido("NOTA_VENTA", null));

        var segunda = await http.PostAsJsonAsync($"/api/proformas/{proforma.Id}/convertir", new ConvertirPedido("NOTA_VENTA", null));

        Assert.Equal(HttpStatusCode.BadRequest, segunda.StatusCode);
    }

    [Fact]
    public async Task La_proforma_no_se_convierte_en_otra_proforma()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var proforma = await EmitirProformaAsync(http);

        var respuesta = await http.PostAsJsonAsync($"/api/proformas/{proforma.Id}/convertir", new ConvertirPedido("PROFORMA", null));

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
    }

    [Fact]
    public async Task Convertir_un_comprobante_que_no_es_proforma_responde_404()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();
        var nota = (await (await http.PostAsJsonAsync("/api/comprobantes",
            new EmitirPedido("NOTA_VENTA", null, new[] { new LineaPedido(1, 1) }))).Content.ReadFromJsonAsync<ComprobanteDto>())!;

        var respuesta = await http.PostAsJsonAsync($"/api/proformas/{nota.Id}/convertir", new ConvertirPedido("BOLETA", null));

        Assert.Equal(HttpStatusCode.NotFound, respuesta.StatusCode);
    }

    [Fact]
    public async Task Proformas_sin_token_responde_401()
    {
        await using var api = new ApiDePrueba();

        var respuesta = await api.CreateClient().GetAsync("/api/proformas");

        Assert.Equal(HttpStatusCode.Unauthorized, respuesta.StatusCode);
    }

    // ---- Compras (HU-11) ----------------------------------------------------

    private static NuevaCompraPedido Compra(long numero = 1234, string serie = "F001", DateOnly? fecha = null) =>
        new("20370146994", "01", serie, numero, fecha ?? DateOnly.FromDateTime(DateTime.Today.AddDays(-1)), null,
            new[] { new LineaCompraPedido(1, 10, 27.50m), new LineaCompraPedido(2, 4, 40m) });

    [Fact]
    public async Task El_encargado_registra_la_compra_con_los_totales_recalculados()
    {
        await using var api = new ApiDePrueba();
        var http = await api.EncargadoAsync();

        var respuesta = await http.PostAsJsonAsync("/api/compras", Compra());
        var compra = await respuesta.Content.ReadFromJsonAsync<CompraDto>();
        var lista = await http.GetFromJsonAsync<ComprasDto>("/api/compras?proveedor=20370146994");

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.Equal(435.00m, compra!.Total);
        Assert.Equal(compra.Total, compra.OpGravada + compra.Igv);
        Assert.Equal(2, compra.Lineas);
        Assert.Equal(compra.Documento, Assert.Single(lista!.Compras).Documento);
    }

    [Fact]
    public async Task La_compra_repetida_del_mismo_proveedor_responde_409()
    {
        await using var api = new ApiDePrueba();
        var http = await api.EncargadoAsync();
        await http.PostAsJsonAsync("/api/compras", Compra());

        var repetida = await http.PostAsJsonAsync("/api/compras", Compra());

        Assert.Equal(HttpStatusCode.Conflict, repetida.StatusCode);
    }

    [Fact]
    public async Task La_compra_con_fecha_futura_o_serie_invalida_responde_400()
    {
        await using var api = new ApiDePrueba();
        var http = await api.EncargadoAsync();

        var futura = await http.PostAsJsonAsync("/api/compras", Compra(fecha: DateOnly.FromDateTime(DateTime.Today.AddDays(5))));
        var serie = await http.PostAsJsonAsync("/api/compras", Compra(serie: "F1"));

        Assert.Equal(HttpStatusCode.BadRequest, futura.StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, serie.StatusCode);
    }

    [Fact]
    public async Task El_vendedor_no_registra_compras()
    {
        await using var api = new ApiDePrueba();
        var http = await api.VendedorAsync();

        var respuesta = await http.PostAsJsonAsync("/api/compras", Compra());

        Assert.Equal(HttpStatusCode.Forbidden, respuesta.StatusCode);
    }
}
