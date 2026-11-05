using Condor.Dominio.Entidades;
using Condor.Dominio.Validacion;
using Condor.PruebasUnitarias.Dobles;

namespace Condor.PruebasUnitarias;

/// <summary>
/// Componente 2: <see cref="ValidadorDocumento"/> (RF-06, CRQ-04).
/// DNI de 8 dígitos y RUC de 11 con prefijo y dígito verificador módulo 11.
/// </summary>
public class ValidadorDocumentoTests
{
    [Theory]
    [Trait("Caso", "PU-07"), Trait("Requisito", "CRQ-04"), Trait("Riesgo", "R11")]
    [InlineData(Datos.RucValido)]          // persona jurídica (20)
    [InlineData(Datos.RucPersonaNatural)]  // persona natural (10)
    public void PU_07_RUC_valido_se_acepta(string ruc)
    {
        Assert.True(ValidadorDocumento.EsRucValido(ruc));
        Assert.Null(ValidadorDocumento.Error(TipoDocumento.Ruc, ruc));
        Assert.Equal(TipoDocumento.Ruc, ValidadorDocumento.TipoSegunLargo(ruc));
    }

    [Fact]
    [Trait("Caso", "PU-08"), Trait("Requisito", "CRQ-04"), Trait("Riesgo", "R11")]
    public void PU_08_RUC_con_digito_verificador_equivocado_se_rechaza()
    {
        const string rucMalDigitado = "20131312954"; // último dígito cambiado: 5 -> 4

        Assert.False(ValidadorDocumento.EsRucValido(rucMalDigitado));
        Assert.Equal("El RUC no es válido: revise los números (el dígito verificador no coincide).",
            ValidadorDocumento.Error(TipoDocumento.Ruc, rucMalDigitado));
    }

    [Fact]
    [Trait("Caso", "PU-09"), Trait("Requisito", "CRQ-04"), Trait("Riesgo", "R11")]
    public void PU_09_RUC_con_prefijo_no_permitido_se_rechaza()
    {
        Assert.Equal("El RUC debe empezar con 10, 15, 16, 17 o 20.",
            ValidadorDocumento.Error(TipoDocumento.Ruc, "30131312955"));
    }

    [Theory]
    [Trait("Caso", "PU-10"), Trait("Requisito", "CRQ-04"), Trait("Riesgo", "R11")]
    [InlineData("4578123", false)]    // 7 dígitos: límite inferior - 1
    [InlineData("45781236", true)]    // 8 dígitos: el largo exacto
    [InlineData("457812361", false)]  // 9 dígitos: límite superior + 1
    [InlineData("4578123A", false)]   // 8 caracteres pero con letra
    [InlineData("", false)]
    [InlineData(null, false)]
    public void PU_10_DNI_solo_es_valido_con_exactamente_8_digitos(string? dni, bool esperado)
    {
        Assert.Equal(esperado, ValidadorDocumento.EsDniValido(dni));
    }

    [Fact]
    [Trait("Caso", "PU-11"), Trait("Requisito", "RF-06"), Trait("Riesgo", "R11")]
    public void PU_11_Puntos_guiones_y_espacios_digitados_se_ignoran()
    {
        Assert.Equal(Datos.RucValido, ValidadorDocumento.Limpiar(" 20.131.312-955 "));
        Assert.True(ValidadorDocumento.EsRucValido(" 20.131.312-955 "));
        Assert.Equal(TipoDocumento.Dni, ValidadorDocumento.TipoSegunLargo("45 781 236"));
    }

    [Theory]
    [Trait("Caso", "PU-12"), Trait("Requisito", "CRQ-04"), Trait("Riesgo", "R11")]
    [InlineData("201313129")]   // 9 dígitos
    [InlineData("20131312955")] // 11 dígitos
    [InlineData("201313129X")]  // 10 caracteres con letra
    public void PU_12_Verificador_sin_10_digitos_lanza_excepcion(string primerosDiez)
    {
        var ex = Assert.Throws<ArgumentException>(() => ValidadorDocumento.DigitoVerificadorRuc(primerosDiez));

        Assert.Equal("primerosDiez", ex.ParamName);
        Assert.Equal(5, ValidadorDocumento.DigitoVerificadorRuc("2013131295")); // con 10 dígitos sí calcula
    }
}
