using Condor.Dominio.Seguridad;

namespace Condor.Presentacion.ViewModels;

/// <summary>
/// Qué módulos del menú abre cada rol (CC-01). El Vendedor atiende el
/// mostrador; Compras (F4), Proveedores (F6), Guías (F8) y Respaldo (F9) son
/// del Encargado general, como dicen sus historias (HU-04, HU-10, HU-11, HU-15).
/// </summary>
public static class PermisosModulo
{
    private static readonly HashSet<Modulo> DelVendedor = new()
    {
        Modulo.Venta, Modulo.Catalogo, Modulo.Clientes, Modulo.Historial, Modulo.Proformas,
    };

    /// <summary>True si el rol puede abrir el módulo. Un rol desconocido solo abre Nueva venta.</summary>
    public static bool Permitido(this Modulo modulo, string? rol) => rol switch
    {
        Roles.Encargado => true,
        Roles.Vendedor => DelVendedor.Contains(modulo),
        _ => modulo == Modulo.Venta,
    };

    /// <summary>Módulos que el rol puede abrir, en el orden del menú.</summary>
    public static IReadOnlyList<Modulo> De(string? rol) => Enum.GetValues<Modulo>().Where(m => m.Permitido(rol)).ToList();
}
