using Condor.Dominio.Entidades;

namespace Condor.PruebasUnitarias.Dobles;

/// <summary>
/// Datos de prueba fijos y reproducibles. Cada prueba arma los suyos con estos
/// métodos: no hay estado compartido entre pruebas, así que el orden en que
/// xUnit las ejecute (o si las corre en paralelo) no cambia el resultado.
/// </summary>
public static class Datos
{
    /// <summary>RUC válido de SUNAT (prefijo 20, verificador 5).</summary>
    public const string RucValido = "20131312955";

    /// <summary>RUC válido de persona natural (prefijo 10, verificador 4).</summary>
    public const string RucPersonaNatural = "10461234564";

    public const string DniValido = "45781236";

    /// <summary>Línea de venta con el precio con IGV del catálogo.</summary>
    public static DetalleComprobante Linea(decimal cantidad, decimal precio, long productoId = 1, string descripcion = "CEMENTO YURA IP 42.5 KG") =>
        new() { ProductoId = productoId, Descripcion = descripcion, Unidad = "BOL", Cantidad = cantidad, PrecioUnitario = precio };

    public static Cliente ClienteDni(long id = 7) =>
        new() { Id = id, TipoDocumento = TipoDocumento.Dni, NumeroDocumento = DniValido, Nombre = "QUISPE MAMANI ROSA" };

    public static Cliente ClienteRuc(long id = 9, string ruc = RucValido) =>
        new() { Id = id, TipoDocumento = TipoDocumento.Ruc, NumeroDocumento = ruc, Nombre = "CONSTRUCTORA MAJES S.A.C.", Direccion = "AV. PRINCIPAL 120, MAJES" };

    /// <summary>Proforma guardada (PR01) con vigencia y, si se indica, ya convertida.</summary>
    public static Comprobante Proforma(string? convertidaEn = null) =>
        new()
        {
            Id = 30,
            TipoComprobante = TipoComprobante.Proforma,
            SerieCodigo = "PR01",
            Numero = 12,
            ConvertidaEn = convertidaEn,
            ValidaHasta = new DateOnly(2026, 11, 7),
        };
}
