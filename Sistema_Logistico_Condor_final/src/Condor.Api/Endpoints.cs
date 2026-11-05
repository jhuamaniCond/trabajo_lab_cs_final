using System.Security.Claims;
using Condor.Api.Infraestructura;
using Condor.Api.Seguridad;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Reportes;
using Condor.Dominio.Seguridad;
using Condor.Dominio.Validacion;
using Condor.Dominio.Ventas;

namespace Condor.Api;

/// <summary>
/// Rutas HTTP de la API (CC-01). Todas, salvo /api/salud y el ingreso,
/// exigen el token; proveedores, reporte y respaldos, además, el rol
/// ENCARGADO. Las reglas son las mismas clases de Condor.Dominio que usa la
/// app de escritorio.
/// </summary>
public static class Endpoints
{
    public const string PoliticaEncargado = "Encargado";

    /// <summary>Más líneas que esto en un comprobante es un error del cliente HTTP, no una venta real.</summary>
    public const int LineasMaximas = 100;

    public static void Mapear(WebApplication app)
    {
        app.MapGet("/api/salud", SaludAsync).AllowAnonymous();
        app.MapPost("/api/auth/login", IngresarAsync).AllowAnonymous();

        var api = app.MapGroup("/api").RequireAuthorization();
        api.MapGet("/auth/yo", (ClaimsPrincipal usuario) => Results.Ok(new UsuarioActual(
            usuario.FindFirstValue(Reclamos.Usuario)!, usuario.FindFirstValue(Reclamos.Nombre)!, usuario.FindFirstValue(Reclamos.Rol)!)));

        api.MapGet("/productos", BuscarProductosAsync);
        api.MapGet("/productos/codigo/{codigo}", ProductoPorCodigoAsync);
        api.MapPost("/productos", RegistrarProductoAsync);

        api.MapGet("/clientes", BuscarClientesAsync);
        api.MapGet("/clientes/{documento}", ClientePorDocumentoAsync);
        api.MapPost("/clientes", RegistrarClienteAsync);

        api.MapPost("/comprobantes", EmitirAsync);
        api.MapGet("/comprobantes", HistorialAsync);
        api.MapGet("/comprobantes/{id:long}", ComprobanteAsync);

        // CC-03: proformas y su conversión en venta (HU-09) para el portal web.
        api.MapGet("/proformas", ProformasAsync);
        api.MapPost("/proformas/{id:long}/convertir", ConvertirProformaAsync);

        var encargado = api.MapGroup("").RequireAuthorization(PoliticaEncargado);
        encargado.MapGet("/proveedores", BuscarProveedoresAsync);
        encargado.MapPost("/proveedores", RegistrarProveedorAsync);
        encargado.MapGet("/reportes/ventas", ReporteVentasAsync);
        encargado.MapGet("/respaldos", RespaldosAsync);
        // CC-03: compras a proveedores (HU-11) para el portal web.
        encargado.MapGet("/compras", ComprasAsync);
        encargado.MapPost("/compras", RegistrarCompraAsync);
    }

    // ---- Salud e ingreso ----------------------------------------------------

    private static async Task<IResult> SaludAsync(ContextoApi contexto, SondaBaseDatos sonda, CancellationToken ct)
    {
        var baseDatos = await sonda.Probar(ct);
        var estado = baseDatos && contexto.Lista ? "OK" : baseDatos ? "PREPARANDO" : "SIN_BASE_DATOS";
        var cuerpo = new SaludDto(estado, baseDatos, typeof(Endpoints).Assembly.GetName().Version?.ToString(3) ?? "-", contexto.NombreTerminal);
        return estado == "OK" ? Results.Ok(cuerpo) : Results.Json(cuerpo, statusCode: StatusCodes.Status503ServiceUnavailable);
    }

    private static async Task<IResult> IngresarAsync(LoginPedido pedido, ServicioAutenticacion autenticacion, EmisorTokens tokens,
        HttpContext http, CancellationToken ct)
    {
        var origen = $"API {http.Connection.RemoteIpAddress}";
        var resultado = await autenticacion.AutenticarAsync(pedido.Usuario, pedido.Clave, origen, ct);
        if (resultado is { Exitoso: true, Cuenta: { } cuenta })
        {
            var (token, expira) = tokens.Emitir(cuenta);
            return Results.Ok(new LoginRespuesta(token, expira, cuenta.NombreUsuario, cuenta.NombreCompleto, cuenta.Rol));
        }

        var estado = resultado.Estado switch
        {
            EstadoAutenticacion.DatosIncompletos => StatusCodes.Status400BadRequest,
            EstadoAutenticacion.CuentaBloqueada => StatusCodes.Status423Locked,
            _ => StatusCodes.Status401Unauthorized,
        };
        return Results.Problem(title: resultado.Mensaje, statusCode: estado);
    }

    // ---- Productos (HU-01, HU-02, HU-13) ------------------------------------

    private static async Task<IResult> BuscarProductosAsync(IProductoRepositorio productos, string? texto, int? limite, CancellationToken ct)
    {
        var tope = Math.Clamp(limite ?? 20, 1, 100);
        var encontrados = string.IsNullOrWhiteSpace(texto)
            ? (await productos.ListarAsync(ct)).Take(tope).ToList()
            : await productos.BuscarPorNombreAsync(texto, tope, ct);
        return Results.Ok(encontrados.Select(ProductoDto.De));
    }

    private static async Task<IResult> ProductoPorCodigoAsync(IProductoRepositorio productos, string codigo, CancellationToken ct) =>
        await productos.BuscarPorCodigoBarrasAsync(codigo, ct) is { } producto
            ? Results.Ok(ProductoDto.De(producto))
            : Results.Problem(title: $"No hay un producto con el código {codigo}.", statusCode: StatusCodes.Status404NotFound);

    private static async Task<IResult> RegistrarProductoAsync(NuevoProductoPedido pedido, IProductoRepositorio productos, CancellationToken ct)
    {
        // Se valida aquí, antes de llegar al repositorio (validación de entradas, G6).
        var producto = ValidadorProducto.Validar(new Producto
        {
            Nombre = pedido.Nombre ?? string.Empty,
            Precio = pedido.Precio,
            Unidad = string.IsNullOrWhiteSpace(pedido.Unidad) ? "UND" : pedido.Unidad,
            CodigoBarras = pedido.CodigoBarras,
        });
        producto = await productos.RegistrarAsync(producto, ct);
        return Results.Created($"/api/productos/codigo/{producto.CodigoBarras ?? producto.Id.ToString()}", ProductoDto.De(producto));
    }

    // ---- Clientes (HU-03) ---------------------------------------------------

    private static async Task<IResult> BuscarClientesAsync(IClienteRepositorio clientes, string? texto, int? limite, CancellationToken ct) =>
        Results.Ok((await clientes.BuscarAsync(texto, Math.Clamp(limite ?? 50, 1, 200), ct)).Select(ClienteDto.De));

    private static async Task<IResult> ClientePorDocumentoAsync(IClienteRepositorio clientes, string documento, CancellationToken ct)
    {
        var tipo = ValidadorDocumento.TipoSegunLargo(documento)
                   ?? throw new ArgumentException("El documento debe ser un DNI de 8 dígitos o un RUC de 11.");
        return await clientes.BuscarPorDocumentoAsync(tipo, documento, ct) is { } cliente
            ? Results.Ok(ClienteDto.De(cliente))
            : Results.Problem(title: $"No hay un cliente con {Cliente.Etiqueta(tipo)} {ValidadorDocumento.Limpiar(documento)}.",
                statusCode: StatusCodes.Status404NotFound);
    }

    private static async Task<IResult> RegistrarClienteAsync(NuevoClientePedido pedido, IClienteRepositorio clientes, CancellationToken ct)
    {
        var cliente = ValidadorCliente.Validar(new Cliente
        {
            TipoDocumento = ValidadorDocumento.TipoSegunLargo(pedido.Documento) ?? TipoDocumento.SinDocumento,
            NumeroDocumento = pedido.Documento ?? string.Empty,
            Nombre = pedido.Nombre ?? string.Empty,
            Direccion = pedido.Direccion,
        });
        cliente = await clientes.RegistrarAsync(cliente, ct);
        return Results.Created($"/api/clientes/{cliente.NumeroDocumento}", ClienteDto.De(cliente));
    }

    // ---- Comprobantes (HU-05, HU-06, HU-08, HU-09, HU-18) -------------------

    private static async Task<IResult> EmitirAsync(EmitirPedido pedido, ClaimsPrincipal usuario, ContextoApi contexto,
        IConsultaProductos catalogo, IClienteRepositorio clientes, IComprobanteRepositorio comprobantes, CancellationToken ct)
    {
        if (!contexto.Lista)
            return Results.Problem(title: "La API aún no se registró en la base de datos central; reintente en unos segundos.",
                statusCode: StatusCodes.Status503ServiceUnavailable);

        var tipo = LeerTipo(pedido.Tipo);
        var lineas = pedido.Detalle ?? Array.Empty<LineaPedido>();
        if (lineas.Count > LineasMaximas)
            throw new ArgumentException($"Un comprobante no puede tener más de {LineasMaximas} líneas.");
        if (lineas.FirstOrDefault(l => l.Cantidad <= 0 || l.Cantidad > 99_999 || decimal.Round(l.Cantidad, 3) != l.Cantidad) is { } mala)
            throw new ArgumentException($"La cantidad del producto {mala.ProductoId} debe ser mayor que cero, hasta 99 999 y con 3 decimales como máximo.");

        // El precio y la descripción salen del catálogo, no de la petición.
        var productos = (await catalogo.ObtenerAsync(lineas.Select(l => l.ProductoId).ToList(), ct)).ToDictionary(p => p.Id);
        if (lineas.FirstOrDefault(l => !productos.ContainsKey(l.ProductoId)) is { } faltante)
            throw new ArgumentException($"El producto {faltante.ProductoId} no existe o ya no está en el catálogo.");

        Cliente? cliente = null;
        if (!string.IsNullOrWhiteSpace(pedido.DocumentoCliente))
        {
            var tipoDocumento = ValidadorDocumento.TipoSegunLargo(pedido.DocumentoCliente)
                                ?? throw new ArgumentException("El documento del cliente debe ser un DNI de 8 dígitos o un RUC de 11.");
            cliente = await clientes.BuscarPorDocumentoAsync(tipoDocumento, pedido.DocumentoCliente, ct)
                      ?? throw new ArgumentException(
                          $"El cliente con {Cliente.Etiqueta(tipoDocumento)} {ValidadorDocumento.Limpiar(pedido.DocumentoCliente)} no está registrado: regístrelo con POST /api/clientes.");
        }

        var detalle = lineas.Select(l =>
        {
            var producto = productos[l.ProductoId];
            return new DetalleComprobante
            {
                ProductoId = producto.Id,
                Descripcion = producto.Nombre,
                Unidad = producto.Unidad,
                Cantidad = l.Cantidad,
                PrecioUnitario = producto.Precio,
            };
        }).ToList();

        var comprobante = EmisionComprobante.Preparar(new SolicitudEmision(tipo, detalle, cliente));
        comprobante.TerminalId = contexto.TerminalId;
        comprobante.TerminalNombre = contexto.NombreTerminal;
        comprobante.Usuario = usuario.FindFirstValue(Reclamos.Usuario)!;

        var emitido = await comprobantes.EmitirAsync(comprobante, ct);
        return Results.Created($"/api/comprobantes/{emitido.Id}", ComprobanteDto.De(emitido));
    }

    /// <summary>Tipo de la petición: BOLETA, BOLETA_DNI, FACTURA, NOTA_VENTA o PROFORMA (sin distinguir mayúsculas).</summary>
    public static TipoEmision LeerTipo(string? tipo) => tipo?.Trim().ToUpperInvariant() switch
    {
        "BOLETA" => TipoEmision.Boleta,
        "BOLETA_DNI" => TipoEmision.BoletaConDni,
        "FACTURA" => TipoEmision.Factura,
        "NOTA_VENTA" => TipoEmision.NotaVenta,
        "PROFORMA" => TipoEmision.Proforma,
        _ => throw new ArgumentException("Tipo de comprobante inválido: use BOLETA, BOLETA_DNI, FACTURA, NOTA_VENTA o PROFORMA."),
    };

    private static async Task<IResult> HistorialAsync(IComprobanteRepositorio comprobantes, DateOnly? desde, DateOnly? hasta, string? tipo,
        string? texto, int? limite, CancellationToken ct)
    {
        if (desde > hasta)
            throw new ArgumentException("La fecha final no puede ser anterior a la inicial.");
        if (tipo is not null and not (TipoComprobante.Boleta or TipoComprobante.Factura or TipoComprobante.NotaVenta or TipoComprobante.Proforma))
            throw new ArgumentException("El tipo debe ser 01 (factura), 03 (boleta), NV (nota de venta) o PR (proforma).");

        var resultado = await comprobantes.BuscarAsync(new FiltroComprobantes(desde, hasta, tipo, texto, Math.Clamp(limite ?? 50, 1, 200)), ct);
        return Results.Ok(new HistorialDto(resultado.Cantidad, resultado.Total, resultado.Comprobantes.Select(ComprobanteDto.De).ToList()));
    }

    private static async Task<IResult> ComprobanteAsync(IComprobanteRepositorio comprobantes, long id, CancellationToken ct) =>
        await comprobantes.ObtenerAsync(id, ct) is { } comprobante
            ? Results.Ok(ComprobanteDto.De(comprobante))
            : Results.Problem(title: $"No existe el comprobante {id}.", statusCode: StatusCodes.Status404NotFound);

    // ---- Proformas (HU-09, CC-03) ------------------------------------------

    private static async Task<IResult> ProformasAsync(IComprobanteRepositorio comprobantes, TimeProvider reloj, string? texto, int? limite,
        CancellationToken ct)
    {
        var hoy = EmisionComprobante.FechaPeru(reloj.GetUtcNow());
        var proformas = await comprobantes.ListarProformasAsync(texto, Math.Clamp(limite ?? 100, 1, 500), ct);
        return Results.Ok(proformas.Select(p => ProformaDto.De(p, hoy)));
    }

    /// <summary>
    /// Convierte la proforma en boleta, boleta con DNI, factura o nota de venta.
    /// Las líneas y los precios son los cotizados en la proforma (HU-09); el
    /// cliente es el de la proforma salvo que se indique otro ya registrado.
    /// Las reglas son las de EmisionComprobante: una proforma convertida no se
    /// vuelve a convertir (409) y una vencida la rechaza la base (409).
    /// </summary>
    private static async Task<IResult> ConvertirProformaAsync(long id, ConvertirPedido pedido, ClaimsPrincipal usuario, ContextoApi contexto,
        IClienteRepositorio clientes, IComprobanteRepositorio comprobantes, CancellationToken ct)
    {
        if (!contexto.Lista)
            return Results.Problem(title: "La API aún no se registró en la base de datos central; reintente en unos segundos.",
                statusCode: StatusCodes.Status503ServiceUnavailable);

        var proforma = await comprobantes.ObtenerAsync(id, ct);
        if (proforma is null || proforma.TipoComprobante != TipoComprobante.Proforma)
            return Results.Problem(title: $"No existe la proforma {id}.", statusCode: StatusCodes.Status404NotFound);

        var tipo = LeerTipo(pedido.Tipo);
        var cliente = proforma.Cliente;
        if (!string.IsNullOrWhiteSpace(pedido.DocumentoCliente))
        {
            var tipoDocumento = ValidadorDocumento.TipoSegunLargo(pedido.DocumentoCliente)
                                ?? throw new ArgumentException("El documento del cliente debe ser un DNI de 8 dígitos o un RUC de 11.");
            cliente = await clientes.BuscarPorDocumentoAsync(tipoDocumento, pedido.DocumentoCliente, ct)
                      ?? throw new ArgumentException(
                          $"El cliente con {Cliente.Etiqueta(tipoDocumento)} {ValidadorDocumento.Limpiar(pedido.DocumentoCliente)} no está registrado.");
        }

        var comprobante = EmisionComprobante.Preparar(new SolicitudEmision(tipo, proforma.Detalle, cliente, proforma));
        comprobante.TerminalId = contexto.TerminalId;
        comprobante.TerminalNombre = contexto.NombreTerminal;
        comprobante.Usuario = usuario.FindFirstValue(Reclamos.Usuario)!;

        var emitido = await comprobantes.EmitirAsync(comprobante, ct);
        return Results.Created($"/api/comprobantes/{emitido.Id}", ComprobanteDto.De(emitido));
    }

    // ---- Solo el Encargado general ------------------------------------------

    private static async Task<IResult> BuscarProveedoresAsync(IProveedorRepositorio proveedores, string? texto, int? limite, CancellationToken ct) =>
        Results.Ok((await proveedores.BuscarAsync(texto, Math.Clamp(limite ?? 50, 1, 200), ct)).Select(ProveedorDto.De));

    private static async Task<IResult> RegistrarProveedorAsync(NuevoProveedorPedido pedido, IProveedorRepositorio proveedores, CancellationToken ct)
    {
        var proveedor = ValidadorProveedor.Validar(new Proveedor
        {
            Ruc = pedido.Ruc ?? string.Empty,
            RazonSocial = pedido.RazonSocial ?? string.Empty,
            NombreComercial = pedido.NombreComercial,
            Direccion = pedido.Direccion,
            Telefono = pedido.Telefono,
            Correo = pedido.Correo,
            Contacto = pedido.Contacto,
        });
        proveedor = await proveedores.RegistrarAsync(proveedor, ct);
        return Results.Created($"/api/proveedores?texto={proveedor.Ruc}", ProveedorDto.De(proveedor));
    }

    /// <summary>Reporte consolidado del período; sin fechas, el día de hoy en Perú.</summary>
    private static async Task<IResult> ReporteVentasAsync(IReporteVentasRepositorio reporte, TimeProvider reloj, DateOnly? desde,
        DateOnly? hasta, CancellationToken ct)
    {
        var hoy = EmisionComprobante.FechaPeru(reloj.GetUtcNow());
        var inicio = desde ?? hasta ?? hoy;
        var fin = hasta ?? desde ?? hoy;
        ReporteVentas.ValidarPeriodo(inicio, fin);
        return Results.Ok(ReporteVentas.Consolidar(inicio, fin, await reporte.VentasDelPeriodoAsync(inicio, fin, ct)));
    }

    // ---- Compras (HU-11, CC-03) ---------------------------------------------

    private static async Task<IResult> ComprasAsync(ICompraRepositorio compras, DateOnly? desde, DateOnly? hasta, string? proveedor, int? limite,
        CancellationToken ct)
    {
        if (desde > hasta)
            throw new ArgumentException("La fecha final no puede ser anterior a la inicial.");
        var resultado = await compras.BuscarAsync(new FiltroCompras(desde, hasta, proveedor, Math.Clamp(limite ?? 200, 1, 500)), ct);
        return Results.Ok(new ComprasDto(resultado.Cantidad, resultado.Total, resultado.Compras.Select(CompraDto.De).ToList()));
    }

    /// <summary>
    /// Registra la compra con las reglas de ValidadorCompra (HU-11): proveedor
    /// registrado, serie y número, fecha no futura y productos del catálogo con
    /// cantidad y costo. Los importes y el IGV se recalculan aquí. Un
    /// comprobante del proveedor repetido responde 409.
    /// </summary>
    private static async Task<IResult> RegistrarCompraAsync(NuevaCompraPedido pedido, ContextoApi contexto, TimeProvider reloj,
        IProveedorRepositorio proveedores, IConsultaProductos catalogo, ICompraRepositorio compras, CancellationToken ct)
    {
        var lineas = pedido.Detalle ?? Array.Empty<LineaCompraPedido>();
        if (lineas.Count > LineasMaximas)
            throw new ArgumentException($"Una compra no puede tener más de {LineasMaximas} líneas.");
        var proveedor = string.IsNullOrWhiteSpace(pedido.RucProveedor) ? null : await proveedores.BuscarPorRucAsync(pedido.RucProveedor.Trim(), ct);
        var productos = (await catalogo.ObtenerAsync(lineas.Select(l => l.ProductoId).Distinct().ToList(), ct)).ToDictionary(p => p.Id);
        if (lineas.FirstOrDefault(l => !productos.ContainsKey(l.ProductoId)) is { } faltante)
            throw new ArgumentException($"El producto {faltante.ProductoId} no existe o ya no está en el catálogo.");

        var compra = new Compra
        {
            ProveedorId = proveedor?.Id ?? 0,
            Proveedor = proveedor,
            TipoDocumento = pedido.TipoDocumento ?? string.Empty,
            Serie = pedido.Serie ?? string.Empty,
            Numero = pedido.Numero,
            FechaEmision = pedido.FechaEmision ?? default,
            Observacion = pedido.Observacion,
            TerminalId = contexto.TerminalId,
            TerminalNombre = contexto.NombreTerminal,
        };
        compra.Detalle.AddRange(lineas.Select(l => new DetalleCompra
        {
            ProductoId = l.ProductoId,
            Descripcion = productos[l.ProductoId].Nombre,
            Unidad = productos[l.ProductoId].Unidad,
            Cantidad = l.Cantidad,
            CostoUnitario = l.CostoUnitario,
        }));
        compra = ValidadorCompra.Preparar(compra, EmisionComprobante.FechaPeru(reloj.GetUtcNow()));
        compra = await compras.RegistrarAsync(compra, ct);
        return Results.Created($"/api/compras?proveedor={proveedor!.Ruc}", CompraDto.De(compra));
    }

    private static async Task<IResult> RespaldosAsync(IRespaldoRepositorio respaldos, CancellationToken ct) =>
        Results.Ok((await respaldos.ListarAsync(10, ct)).Select(RespaldoDto.De));
}
