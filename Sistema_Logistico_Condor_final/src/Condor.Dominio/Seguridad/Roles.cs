namespace Condor.Dominio.Seguridad;

/// <summary>
/// Roles del sistema (CC-01). Reemplazan al perfil único MAESTRO de HU-14:
/// el Vendedor atiende el mostrador y el Encargado general, además, maneja
/// proveedores, compras, guías, respaldos y el reporte consolidado.
/// </summary>
public static class Roles
{
    public const string Vendedor = "VENDEDOR";
    public const string Encargado = "ENCARGADO";

    public static IReadOnlyList<string> Todos { get; } = new[] { Vendedor, Encargado };

    public static bool EsValido(string? rol) => rol is Vendedor or Encargado;

    /// <summary>Nombre del rol tal como sale en la pantalla.</summary>
    public static string Nombre(string? rol) => rol switch
    {
        Vendedor => "Vendedor",
        Encargado => "Encargado general",
        _ => rol ?? "-",
    };
}
