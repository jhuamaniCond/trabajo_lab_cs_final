using Condor.Dominio.Entidades;

namespace Condor.Api;

// Cuerpos de las peticiones y respuestas en JSON (camelCase). Ver docs/api.md.

public sealed record LoginPedido(string? Usuario, string? Clave);

public sealed record LoginRespuesta(string Token, DateTimeOffset Expira, string Usuario, string Nombre, string Rol);

public sealed record UsuarioActual(string Usuario, string Nombre, string Rol);

public sealed record ProductoDto(long Id, string Nombre, decimal Precio, string Unidad, string? CodigoBarras)
{
    public static ProductoDto De(Producto p) => new(p.Id, p.Nombre, p.Precio, p.Unidad, p.CodigoBarras);
}

public sealed record NuevoProductoPedido(string? Nombre, decimal Precio, string? Unidad, string? CodigoBarras);

public sealed record ClienteDto(long Id, string TipoDocumento, string NumeroDocumento, string Nombre, string? Direccion)
{
    public static ClienteDto De(Cliente c) => new(c.Id, Cliente.Etiqueta(c.TipoDocumento), c.NumeroDocumento, c.Nombre, c.Direccion);
}

/// <param name="Documento">DNI (8 dígitos) o RUC (11 dígitos); el tipo se deduce del largo.</param>
public sealed record NuevoClientePedido(string? Documento, string? Nombre, string? Direccion);

public sealed record ProveedorDto(long Id, string Ruc, string RazonSocial, string? NombreComercial, string? Direccion, string? Telefono,
    string? Correo, string? Contacto)
{
    public static ProveedorDto De(Proveedor p) =>
        new(p.Id, p.Ruc, p.RazonSocial, p.NombreComercial, p.Direccion, p.Telefono, p.Correo, p.Contacto);
}

public sealed record NuevoProveedorPedido(string? Ruc, string? RazonSocial, string? NombreComercial, string? Direccion, string? Telefono,
    string? Correo, string? Contacto);

public sealed record LineaPedido(long ProductoId, decimal Cantidad);

/// <param name="Tipo">BOLETA, BOLETA_DNI, FACTURA, NOTA_VENTA o PROFORMA.</param>
/// <param name="DocumentoCliente">DNI o RUC de un cliente ya registrado; vacío para la boleta sin DNI.</param>
/// <param name="Detalle">Productos y cantidades; el precio y la descripción salen del catálogo.</param>
public sealed record EmitirPedido(string? Tipo, string? DocumentoCliente, IReadOnlyList<LineaPedido>? Detalle);

public sealed record LineaComprobanteDto(int Item, long ProductoId, string Descripcion, string Unidad, decimal Cantidad,
    decimal PrecioUnitario, decimal Importe);

public sealed record ComprobanteDto(long Id, string Tipo, string Numero, DateTimeOffset Fecha, ClienteDto? Cliente, decimal OpGravada,
    decimal Igv, decimal Total, string EstadoSunat, string Usuario, string? Terminal, DateOnly? ValidaHasta,
    IReadOnlyList<LineaComprobanteDto> Detalle)
{
    public static ComprobanteDto De(Comprobante c) => new(c.Id, c.TipoCorto, c.NumeroCompleto, c.Fecha,
        c.Cliente is null ? null : ClienteDto.De(c.Cliente), c.OpGravada, c.Igv, c.Total,
        TipoComprobante.EsElectronico(c.TipoComprobante) ? c.EstadoSunat : "NO APLICA", c.Usuario, c.TerminalNombre, c.ValidaHasta,
        c.Detalle.Select(l => new LineaComprobanteDto(l.Item, l.ProductoId, l.Descripcion, l.Unidad, l.Cantidad, l.PrecioUnitario, l.Importe))
            .ToList());
}

/// <param name="Tipo">BOLETA, BOLETA_DNI, FACTURA o NOTA_VENTA.</param>
/// <param name="DocumentoCliente">Opcional: otro cliente ya registrado; si falta, el de la proforma.</param>
public sealed record ConvertirPedido(string? Tipo, string? DocumentoCliente);

/// <param name="Estado">VIGENTE, VENCIDA o CONVERTIDA (CC-03).</param>
public sealed record ProformaDto(long Id, string Numero, DateTimeOffset Fecha, ClienteDto? Cliente, decimal Total, DateOnly? ValidaHasta,
    string Estado, string? ConvertidaEn)
{
    public static ProformaDto De(Comprobante p, DateOnly hoy) => new(p.Id, p.NumeroCompleto, p.Fecha,
        p.Cliente is null ? null : ClienteDto.De(p.Cliente), p.Total, p.ValidaHasta,
        p.Convertida ? "CONVERTIDA" : p.Vencida(hoy) ? "VENCIDA" : "VIGENTE", p.ConvertidaEn);
}

public sealed record LineaCompraPedido(long ProductoId, decimal Cantidad, decimal CostoUnitario);

/// <param name="TipoDocumento">01 factura o 03 boleta del proveedor.</param>
public sealed record NuevaCompraPedido(string? RucProveedor, string? TipoDocumento, string? Serie, long Numero, DateOnly? FechaEmision,
    string? Observacion, IReadOnlyList<LineaCompraPedido>? Detalle);

/// <param name="Lineas">Productos de la compra; null en la búsqueda, que trae solo las cabeceras (DEF-03).</param>
public sealed record CompraDto(long Id, string Documento, DateOnly FechaEmision, string? RucProveedor, string? Proveedor, decimal OpGravada,
    decimal Igv, decimal Total, int? Lineas)
{
    // Toda compra guardada tiene al menos una línea: sin detalle cargado, el número no se conoce.
    public static CompraDto De(Compra c) => new(c.Id, c.DocumentoCompleto, c.FechaEmision, c.Proveedor?.Ruc, c.Proveedor?.RazonSocial,
        c.OpGravada, c.Igv, c.Total, c.Detalle.Count == 0 ? null : c.Detalle.Count);
}

public sealed record ComprasDto(int Cantidad, decimal Total, IReadOnlyList<CompraDto> Compras);

public sealed record HistorialDto(int Cantidad, decimal Total, IReadOnlyList<ComprobanteDto> Comprobantes);

public sealed record RespaldoDto(long Id, string Archivo, string Carpeta, string Tamano, DateTimeOffset TerminadoEn, string? Terminal)
{
    public static RespaldoDto De(Respaldo r) => new(r.Id, r.Archivo, r.Carpeta, r.Tamano, r.TerminadoEn, r.TerminalNombre);
}

public sealed record SaludDto(string Estado, bool BaseDatos, string Version, string Terminal);
