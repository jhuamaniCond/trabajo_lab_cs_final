using Condor.ClienteApi;

namespace Condor.Pruebas.Api;

/// <summary>CC-01: sección Api de condor.json, la dirección del backend en la PC principal.</summary>
public sealed class ConfiguracionApiTests : IDisposable
{
    private readonly string _carpeta = Directory.CreateTempSubdirectory("condor-api-").FullName;

    public void Dispose() => Directory.Delete(_carpeta, recursive: true);

    private void Escribir(string json) => File.WriteAllText(Path.Combine(_carpeta, ConfiguracionApi.NombreArchivo), json);

    [Fact]
    public void La_plantilla_condor_ejemplo_json_apunta_a_la_API()
    {
        var raiz = new DirectoryInfo(AppContext.BaseDirectory);
        while (raiz is not null && !File.Exists(Path.Combine(raiz.FullName, "CondorVentas.sln")))
            raiz = raiz.Parent;
        File.Copy(Path.Combine(raiz!.FullName, "src", "Condor.Escritorio", "condor.ejemplo.json"),
            Path.Combine(_carpeta, ConfiguracionApi.NombreArchivo));

        var config = ConfiguracionApi.Cargar(_carpeta);

        Assert.Equal("http://192.168.1.10:5080", config.Url);
        Assert.Equal(15, config.TiempoEsperaSegundos);
    }

    [Fact]
    public void Sin_archivo_avisa_que_hay_que_copiar_la_plantilla()
    {
        var ex = Assert.Throws<FileNotFoundException>(() => ConfiguracionApi.Cargar(_carpeta));
        Assert.Contains("condor.ejemplo.json", ex.Message);
    }

    [Fact]
    public void Sin_la_seccion_Api_explica_que_agregar()
    {
        Escribir("""{ "Servidor": "localhost", "Puerto": 5432 }""");

        var ex = Assert.Throws<InvalidDataException>(() => ConfiguracionApi.Cargar(_carpeta));
        Assert.Contains("\"Api\"", ex.Message);
    }

    [Theory]
    [InlineData("""{ "Api": { "Url": "192.168.1.10:5080" } }""")]
    [InlineData("""{ "Api": { "Url": "ftp://192.168.1.10" } }""")]
    [InlineData("""{ "Api": { "Url": "http://localhost:5080", "TiempoEsperaSegundos": 0 } }""")]
    [InlineData("""{ "Api": """)]
    public void Una_direccion_o_espera_invalida_no_se_acepta(string json)
    {
        Escribir(json);
        Assert.Throws<InvalidDataException>(() => ConfiguracionApi.Cargar(_carpeta));
    }
}
