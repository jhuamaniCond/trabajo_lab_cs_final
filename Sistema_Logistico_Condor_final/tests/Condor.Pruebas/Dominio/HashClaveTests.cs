using Condor.Datos;
using Condor.Dominio.Seguridad;
using System.Text.RegularExpressions;

namespace Condor.Pruebas.Dominio;

/// <summary>CC-01: las contraseñas se guardan solo como hash PBKDF2-SHA256.</summary>
public class HashClaveTests
{
    [Fact]
    public void La_clave_correcta_verifica_y_la_equivocada_no()
    {
        var hash = HashClave.Generar("Ferreteria2026!");

        Assert.True(HashClave.Verificar("Ferreteria2026!", hash));
        Assert.False(HashClave.Verificar("ferreteria2026!", hash));
        Assert.False(HashClave.Verificar("", hash));
    }

    [Fact]
    public void El_hash_no_contiene_la_clave_y_tiene_el_formato_documentado()
    {
        var hash = HashClave.Generar("Secreta123");

        Assert.DoesNotContain("Secreta123", hash);
        Assert.Matches(@"^pbkdf2-sha256\$100000\$[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$", hash);
    }

    [Fact]
    public void Dos_hashes_de_la_misma_clave_son_distintos_por_la_sal()
    {
        Assert.NotEqual(HashClave.Generar("Igual2026"), HashClave.Generar("Igual2026"));
    }

    [Fact]
    public void Con_la_misma_sal_e_iteraciones_el_hash_es_reproducible()
    {
        var sal = Enumerable.Range(1, 16).Select(i => (byte)i).ToArray();

        Assert.Equal(HashClave.Generar("abc", sal, 1000), HashClave.Generar("abc", sal, 1000));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("texto-plano")]
    [InlineData("md5$1000$c2Fs$aGFzaA==")]
    [InlineData("pbkdf2-sha256$cero$c2Fs$aGFzaA==")]
    [InlineData("pbkdf2-sha256$0$c2Fs$aGFzaA==")]
    [InlineData("pbkdf2-sha256$1000$no-es-base64!$aGFzaA==")]
    [InlineData("pbkdf2-sha256$1000$$")]
    public void Un_hash_vacio_o_mal_formado_nunca_verifica(string? hash)
    {
        Assert.False(HashClave.Verificar("cualquiera", hash));
    }

    [Fact]
    public void Una_sal_demasiado_corta_se_rechaza()
    {
        Assert.Throws<ArgumentException>(() => HashClave.Generar("abc", new byte[4], 1000));
        Assert.Throws<ArgumentOutOfRangeException>(() => HashClave.Generar("abc", new byte[16], 0));
    }

    /// <summary>Los usuarios de demostración de V014 entran con las claves de docs/seguridad.md.</summary>
    [Theory]
    [InlineData("encargado", "Encargado2026!")]
    [InlineData("vendedor1", "Vendedor2026!")]
    [InlineData("vendedor2", "Vendedor2026!")]
    public void Los_usuarios_de_la_migracion_V014_verifican_con_su_clave_documentada(string usuario, string clave)
    {
        var sql = Migrador.Disponibles().Single(m => m.Version == 14).Sql;
        var hash = Regex.Match(sql, $@"\('{usuario}',[^']*'[^']*',\s*'[A-Z]+',\s*'(?<hash>[^']+)'\)").Groups["hash"].Value;

        Assert.NotEmpty(hash);
        Assert.True(HashClave.Verificar(clave, hash));
        Assert.False(HashClave.Verificar(clave + "x", hash));
    }
}
