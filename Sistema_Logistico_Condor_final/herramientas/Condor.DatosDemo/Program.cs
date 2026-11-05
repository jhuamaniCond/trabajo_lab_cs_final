// Datos de demostración (CC-01): clientes, proveedores, ventas, proformas,
// compras y guías, 25 o más de cada uno, repartidos en los últimos 30 días.
//
//   dotnet run --project herramientas/Condor.DatosDemo -- --config "C:\carpeta\con\condor.json"
//
// --config   carpeta donde está condor.json con los datos de PostgreSQL (por defecto, la actual).
// --forzar   carga otro lote aunque la base ya tenga datos.
// Cada sección (clientes, proveedores, ventas...) se carga solo si tiene menos de 25 registros,
// así se puede volver a ejecutar si se cortó a medias.
// Siempre genera lo mismo (semilla fija), así las capturas y las pruebas de interfaz se repiten.
// Solo para bases de demostración o de pruebas: nunca en la base del local.

using Condor.Datos;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Sunat;
using Condor.Dominio.Validacion;
using Condor.Dominio.Ventas;
using Npgsql;

var indiceConfig = Array.IndexOf(args, "--config");
var carpetaConfig = indiceConfig >= 0 && indiceConfig + 1 < args.Length ? args[indiceConfig + 1] : Directory.GetCurrentDirectory();
var forzar = args.Contains("--forzar");

ConfiguracionConexion config;
try
{
    config = ConfiguracionConexion.Cargar(carpetaConfig);
}
catch (Exception ex) when (ex is FileNotFoundException or InvalidDataException)
{
    Console.Error.WriteLine(ex.Message);
    return 1;
}

await using var conexiones = new FabricaConexiones(config, "DatosDemo");
await new Migrador(conexiones).AplicarAsync();

// True si la sección ya tiene 25 o más registros (y no se pidió --forzar).
async Task<bool> CompletaAsync(string seccion, string sql)
{
    var cantidad = await ContarAsync(sql);
    if (forzar || cantidad < 25)
        return false;
    Console.WriteLine($"{seccion}: ya hay {cantidad}; se omite.");
    return true;
}

var azar = new Random(2026);
var hoy = EmisionComprobante.FechaPeru(DateTimeOffset.UtcNow);
var productosRepo = new ProductoRepositorio(conexiones);
var clientesRepo = new ClienteRepositorio(conexiones);
var proveedoresRepo = new ProveedorRepositorio(conexiones);
var comprobantesRepo = new ComprobanteRepositorio(conexiones);
var comprasRepo = new CompraRepositorio(conexiones);
var guiasRepo = new GuiaRemisionRepositorio(conexiones);
var sunatRepo = new EnvioSunatRepositorio(conexiones);

// ---- Terminales y catálogo ------------------------------------------------
var terminales = new List<Terminal>();
foreach (var nombre in new[] { "PC-1", "PC-2", "PC-PRINCIPAL" })
    terminales.Add(await new TerminalRepositorio(conexiones).RegistrarAccesoAsync(nombre));
var usuarios = new[] { "vendedor1", "vendedor2", "encargado" };

var catalogo = (await productosRepo.ListarAsync()).ToList();
foreach (var (nombre, precio, unidad) in ProductosBase())
{
    if (catalogo.Count >= 25)
        break;
    if (catalogo.Any(p => string.Equals(p.Nombre, nombre, StringComparison.OrdinalIgnoreCase)))
        continue;
    catalogo.Add(await productosRepo.RegistrarAsync(new Producto { Nombre = nombre, Precio = precio, Unidad = unidad }));
}
Console.WriteLine($"Catálogo: {catalogo.Count} productos.");

// ---- Clientes (F3) --------------------------------------------------------
var clientes = new List<Cliente>();
if (await CompletaAsync("Clientes", "SELECT count(*) FROM cliente"))
    clientes.AddRange(await clientesRepo.BuscarAsync(null, 500));
else
{
foreach (var (nombre, direccion) in Personas())
    clientes.Add(await RegistrarClienteAsync(new Cliente
    {
        TipoDocumento = TipoDocumento.Dni, NumeroDocumento = Dni(), Nombre = nombre, Direccion = direccion,
    }));
foreach (var (nombre, direccion) in Empresas())
    clientes.Add(await RegistrarClienteAsync(new Cliente
    {
        TipoDocumento = TipoDocumento.Ruc, NumeroDocumento = Ruc("20"), Nombre = nombre, Direccion = direccion,
    }));
}
var conDni = clientes.Where(c => c.TipoDocumento == TipoDocumento.Dni).ToList();
var conRuc = clientes.Where(c => c.TipoDocumento == TipoDocumento.Ruc).ToList();
Console.WriteLine($"Clientes: {clientes.Count} ({conDni.Count} con DNI, {conRuc.Count} con RUC).");

// ---- Proveedores (F6) -----------------------------------------------------
var proveedores = new List<Proveedor>();
if (await CompletaAsync("Proveedores", "SELECT count(*) FROM proveedor"))
    proveedores.AddRange(await proveedoresRepo.BuscarAsync(null, 500));
var i = 0;
foreach (var (razon, comercial, rubro) in proveedores.Count >= 25 ? [] : Proveedores())
{
    i++;
    var proveedor = new Proveedor
    {
        Ruc = Ruc("20"),
        RazonSocial = razon,
        NombreComercial = comercial,
        Direccion = $"{(i % 3 == 0 ? "Av. Parra" : i % 3 == 1 ? "Parque Industrial, Mz. " + (char)('A' + i % 8) : "Av. Ejército")} {100 + i * 13}, Arequipa",
        Telefono = $"9{azar.Next(10_000_000, 99_999_999)}",
        Correo = $"ventas@{comercial.ToLowerInvariant().Replace(" ", "").Replace(".", "")}.com.pe",
        Contacto = $"{Personas()[i % Personas().Length].Nombre.Split(' ')[0]} ({rubro})",
    };
    try
    {
        proveedores.Add(await proveedoresRepo.RegistrarAsync(proveedor));
    }
    catch (ProveedorDuplicadoException)
    {
        // RUC al azar repetido: muy raro; se omite.
    }
}
Console.WriteLine($"Proveedores: {proveedores.Count}.");

// ---- Ventas (F5 Historial) ------------------------------------------------
var fechasVentas = await CompletaAsync("Ventas", "SELECT count(*) FROM comprobante c JOIN serie s ON s.id = c.serie_id WHERE s.tipo_comprobante <> 'PR'")
    ? new List<DateTimeOffset>()
    : FechasAscendentes(45, diasAtras: 30);
var ventas = new List<Comprobante>();
for (var n = 0; n < fechasVentas.Count; n++)
{
    var tipo = (n % 9) switch
    {
        0 or 3 or 6 => TipoEmision.Factura,
        1 or 4 => TipoEmision.BoletaConDni,
        8 => TipoEmision.NotaVenta,
        _ => TipoEmision.Boleta,
    };
    var cliente = tipo switch
    {
        TipoEmision.Factura => conRuc[azar.Next(conRuc.Count)],
        TipoEmision.BoletaConDni => conDni[azar.Next(conDni.Count)],
        _ => null,
    };
    var detalle = Lineas(tipo == TipoEmision.Factura ? 4 : 3, tipo == TipoEmision.Factura ? 40 : 6);
    if (tipo == TipoEmision.Boleta && Total(detalle) > EmisionComprobante.MontoBoletaIdentificada)
        detalle = Lineas(1, 2);
    var venta = await EmitirAsync(tipo, detalle, cliente, n);
    await FechaAsync("comprobante", venta.Id, fechasVentas[n]);
    await comprobantesRepo.RegistrarImpresionAsync(venta.Id); // El ticket salió al vender.
    venta.Fecha = fechasVentas[n];
    ventas.Add(venta);

    // La mayoría ya fue aceptada por la SUNAT; las de las últimas horas siguen pendientes.
    if (venta.EsElectronico && fechasVentas[n] < DateTimeOffset.UtcNow.AddHours(-6))
        await sunatRepo.RegistrarRespuestaAsync(venta.Id, Aceptada(venta.NumeroCompleto, venta.NombreTipo));
}
Console.WriteLine($"Ventas: {ventas.Count} (boletas, facturas y notas de venta).");

// ---- Proformas (F7) -------------------------------------------------------
var fechasProformas = await CompletaAsync("Proformas", "SELECT count(*) FROM comprobante c JOIN serie s ON s.id = c.serie_id WHERE s.tipo_comprobante = 'PR'")
    ? new List<DateTimeOffset>()
    : FechasAscendentes(26, diasAtras: 6);
var convertidas = 0;
for (var n = 0; n < fechasProformas.Count; n++)
{
    var cliente = n % 3 == 0 ? conDni[azar.Next(conDni.Count)] : conRuc[azar.Next(conRuc.Count)];
    var proforma = await EmitirAsync(TipoEmision.Proforma, Lineas(5, 60), cliente, n);

    // Una de cada cinco ya se convirtió en venta.
    if (n % 5 == 0)
    {
        var tipo = cliente.TipoDocumento == TipoDocumento.Ruc ? TipoEmision.Factura : TipoEmision.BoletaConDni;
        var venta = EmisionComprobante.Preparar(new SolicitudEmision(tipo, proforma.Detalle.Select(Copia).ToList(), cliente, proforma));
        Firmar(venta, n);
        await comprobantesRepo.EmitirAsync(venta);
        var fechaVenta = Min(fechasProformas[n].AddHours(2), DateTimeOffset.UtcNow.AddMinutes(-5));
        await FechaAsync("comprobante", venta.Id, fechaVenta);
        await comprobantesRepo.RegistrarImpresionAsync(venta.Id);
        if (fechaVenta < DateTimeOffset.UtcNow.AddHours(-6))
            await sunatRepo.RegistrarRespuestaAsync(venta.Id, Aceptada(venta.NumeroCompleto, venta.NombreTipo));
        convertidas++;
    }

    await FechaAsync("comprobante", proforma.Id, fechasProformas[n]);
    await EjecutarAsync("UPDATE comprobante SET valida_hasta = (fecha AT TIME ZONE 'America/Lima')::date + @dias - 1 WHERE id = @id",
        ("id", proforma.Id), ("dias", EmisionComprobante.DiasVigenciaProforma));
}
Console.WriteLine($"Proformas: {fechasProformas.Count} ({convertidas} ya convertidas en venta).");

// ---- Compras (F4) ---------------------------------------------------------
var fechasCompras = await CompletaAsync("Compras", "SELECT count(*) FROM compra")
    ? new List<DateTimeOffset>()
    : FechasAscendentes(28, diasAtras: 30);
var compras = 0;
for (var n = 0; n < fechasCompras.Count; n++)
{
    var proveedor = proveedores[n % proveedores.Count];
    var compra = new Compra
    {
        ProveedorId = proveedor.Id,
        Proveedor = proveedor,
        TipoDocumento = n % 6 == 5 ? TipoDocumentoCompra.Boleta : TipoDocumentoCompra.Factura,
        Serie = n % 6 == 5 ? "B001" : $"F00{1 + n % 3}",
        Numero = 1000 + n * 37,
        FechaEmision = EmisionComprobante.FechaPeru(fechasCompras[n]),
        TerminalId = terminales[2].Id,
        Observacion = n % 4 == 0 ? "Reposición de stock para obras de la semana." : null,
    };
    var item = 0;
    foreach (var producto in Elegir(azar.Next(1, 5)))
        compra.Detalle.Add(new DetalleCompra
        {
            Item = ++item,
            ProductoId = producto.Id,
            Descripcion = producto.Nombre,
            Unidad = producto.Unidad,
            Cantidad = azar.Next(10, 120),
            CostoUnitario = Math.Round(producto.Precio * 0.78m, 2),
        });
    try
    {
        var registrada = await comprasRepo.RegistrarAsync(ValidadorCompra.Preparar(compra, hoy));
        await FechaAsync("compra", registrada.Id, fechasCompras[n], columna: "registrada_en");
        compras++;
    }
    catch (CompraDuplicadaException)
    {
    }
}
Console.WriteLine($"Compras: {compras}.");

// ---- Guías de remisión (F8) -----------------------------------------------
var fechasGuias = await CompletaAsync("Guías", "SELECT count(*) FROM guia_remision")
    ? new List<DateTimeOffset>()
    : FechasAscendentes(26, diasAtras: 20);
var guias = 0;
for (var n = 0; n < fechasGuias.Count; n++)
{
    var destinatario = conRuc[n % conRuc.Count];
    var dia = EmisionComprobante.FechaPeru(fechasGuias[n]);
    var guia = new GuiaRemision
    {
        FechaTraslado = hoy,
        Motivo = MotivoTraslado.Venta,
        Modalidad = n % 4 == 3 ? ModalidadTraslado.Publico : ModalidadTraslado.Privado,
        DestinatarioTipo = TipoDocumento.Ruc,
        DestinatarioDocumento = destinatario.NumeroDocumento,
        DestinatarioNombre = destinatario.Nombre,
        PartidaUbigeo = "040520",
        PartidaDireccion = "Av. Principal s/n, Pedregal, Majes - Caylloma - Arequipa",
        LlegadaUbigeo = n % 2 == 0 ? "040520" : "040101",
        LlegadaDireccion = destinatario.Direccion ?? "Obra en Majes",
        PesoBrutoKg = azar.Next(150, 2500),
        TerminalId = terminales[2].Id,
    };
    if (guia.EsPublico)
    {
        guia.TransportistaRuc = Ruc("20");
        guia.TransportistaRazonSocial = "Transportes Colca Express S.A.C.";
    }
    else
    {
        guia.VehiculoPlaca = n % 2 == 0 ? "V1A-952" : "V3C-418";
        guia.ConductorDni = n % 2 == 0 ? "45879632" : "40218876";
        guia.ConductorNombres = n % 2 == 0 ? "Juan" : "Rosa";
        guia.ConductorApellidos = n % 2 == 0 ? "Pérez Quispe" : "Huamaní Torres";
        guia.ConductorLicencia = n % 2 == 0 ? "Q45879632" : "Q40218876";
    }
    var item = 0;
    foreach (var producto in Elegir(azar.Next(1, 4)))
        guia.Detalle.Add(new DetalleGuia { Item = ++item, ProductoId = producto.Id, Descripcion = producto.Nombre, Unidad = producto.Unidad, Cantidad = azar.Next(5, 80) });

    var emitida = await guiasRepo.EmitirAsync(ValidadorGuia.Preparar(guia, hoy));
    await EjecutarAsync("UPDATE guia_remision SET fecha = @fecha, fecha_traslado = @dia WHERE id = @id",
        ("id", emitida.Id), ("fecha", fechasGuias[n]), ("dia", dia));
    if (fechasGuias[n] < DateTimeOffset.UtcNow.AddDays(-1))
        await guiasRepo.RegistrarRespuestaAsync(emitida.Id, Aceptada(emitida.NumeroCompleto, "Guía de remisión"));
    guias++;
}
Console.WriteLine($"Guías de remisión: {guias}.");
Console.WriteLine("Datos de demostración cargados.");
return 0;

// ---- Ayudas ---------------------------------------------------------------

async Task<Cliente> RegistrarClienteAsync(Cliente cliente)
{
    try
    {
        return await clientesRepo.RegistrarAsync(cliente);
    }
    catch (ClienteDuplicadoException)
    {
        return (await clientesRepo.BuscarPorDocumentoAsync(cliente.TipoDocumento, cliente.NumeroDocumento))!;
    }
}

async Task<Comprobante> EmitirAsync(TipoEmision tipo, List<DetalleComprobante> detalle, Cliente? cliente, int n)
{
    var comprobante = EmisionComprobante.Preparar(new SolicitudEmision(tipo, detalle, cliente));
    Firmar(comprobante, n);
    return await comprobantesRepo.EmitirAsync(comprobante);
}

void Firmar(Comprobante comprobante, int n)
{
    var terminal = terminales[n % terminales.Count];
    comprobante.TerminalId = terminal.Id;
    comprobante.TerminalNombre = terminal.Nombre;
    comprobante.Usuario = usuarios[n % usuarios.Length];
}

List<DetalleComprobante> Lineas(int maximoLineas, int maximaCantidad) =>
    Elegir(azar.Next(1, maximoLineas + 1)).Select(p => new DetalleComprobante
    {
        ProductoId = p.Id, Descripcion = p.Nombre, Unidad = p.Unidad, Cantidad = azar.Next(1, maximaCantidad + 1), PrecioUnitario = p.Precio,
    }).ToList();

static DateTimeOffset Min(DateTimeOffset a, DateTimeOffset b) => a < b ? a : b;

static decimal Total(IEnumerable<DetalleComprobante> detalle) =>
    CalculadoraVenta.Totales(detalle.Select(l => CalculadoraVenta.Importe(l.Cantidad, l.PrecioUnitario))).Total;

static DetalleComprobante Copia(DetalleComprobante l) => new()
{
    ProductoId = l.ProductoId, Descripcion = l.Descripcion, Unidad = l.Unidad, Cantidad = l.Cantidad, PrecioUnitario = l.PrecioUnitario,
};

IEnumerable<Producto> Elegir(int cantidad) => catalogo.OrderBy(_ => azar.Next()).Take(cantidad);

// Fechas en horario de atención (8:00 a 19:00 de Perú), de la más antigua a la más reciente.
List<DateTimeOffset> FechasAscendentes(int cantidad, int diasAtras) =>
    Enumerable.Range(0, cantidad)
        .Select(_ =>
        {
            var dia = hoy.AddDays(-azar.Next(0, diasAtras + 1));
            var momento = new DateTimeOffset(dia.ToDateTime(new TimeOnly(azar.Next(8, 19), azar.Next(0, 60))), EmisionComprobante.HoraPeru);
            return momento > DateTimeOffset.UtcNow ? DateTimeOffset.UtcNow.AddMinutes(-azar.Next(5, 240)) : momento;
        })
        .Order()
        .ToList();

static RespuestaSunat Aceptada(string numero, string tipo) => new()
{
    Estado = EstadoSunat.Aceptado,
    Codigo = "0",
    Descripcion = $"La {tipo} número {numero}, ha sido aceptada (datos de demostración).",
    NombreArchivo = $"DEMO-{numero}",
};

string Dni() => azar.Next(10_000_000, 79_999_999).ToString();

string Ruc(string prefijo)
{
    var primerosDiez = prefijo + azar.Next(10_000_000, 99_999_999);
    return primerosDiez + ValidadorDocumento.DigitoVerificadorRuc(primerosDiez);
}

Task FechaAsync(string tabla, long id, DateTimeOffset fecha, string columna = "fecha") =>
    EjecutarAsync($"UPDATE {tabla} SET {columna} = @fecha WHERE id = @id", ("id", id), ("fecha", fecha));

async Task EjecutarAsync(string sql, params (string Nombre, object Valor)[] parametros)
{
    await using var conexion = await conexiones.AbrirAsync();
    await using var cmd = new NpgsqlCommand(sql, conexion);
    foreach (var (nombre, valor) in parametros)
        cmd.Parameters.AddWithValue(nombre, valor is DateTimeOffset fecha ? fecha.ToUniversalTime() : valor); // Npgsql exige UTC.
    await cmd.ExecuteNonQueryAsync();
}

async Task<long> ContarAsync(string sql)
{
    await using var conexion = await conexiones.AbrirAsync();
    await using var cmd = new NpgsqlCommand(sql, conexion);
    return Convert.ToInt64(await cmd.ExecuteScalarAsync());
}

static (string Nombre, string Direccion)[] Personas() =>
[
    ("Juan Carlos Mamani Quispe", "Calle Los Pinos 214, El Pedregal"),
    ("Rosa Elena Huamaní Torres", "Av. Las Américas 520, Majes"),
    ("Luis Alberto Condori Apaza", "Mz. F Lt. 12, Villa Pedregal"),
    ("María Isabel Ccallo Flores", "Jr. Arequipa 133, El Pedregal"),
    ("Pedro Pablo Chambi Ticona", "Sección E, parcela 45, Majes"),
    ("Carmen Rosa Quispe Mamani", "Av. Principal 890, Pedregal"),
    ("Jorge Luis Puma Ccahua", "Calle Lima 77, El Pedregal"),
    ("Ana Lucía Vilca Huanca", "Mz. B Lt. 3, Asoc. Santa María"),
    ("Edwin Hilario Calla Choque", "Sección C, parcela 112, Majes"),
    ("Silvia Marleni Turpo Cutipa", "Av. 1 de Mayo 341, Pedregal"),
    ("Fredy Ronald Yucra Mendoza", "Calle Moquegua 210, El Pedregal"),
    ("Gladys Noemí Arapa Larico", "Mz. K Lt. 8, Villa Hermosa"),
    ("Walter Julio Ancco Sucapuca", "Sección D, parcela 7, Majes"),
    ("Yolanda Beatriz Coaquira Paz", "Jr. Cusco 456, El Pedregal"),
    ("Raúl Ernesto Alanoca Ramos", "Av. Las Flores 102, Majes"),
    ("Nancy Elizabeth Pari Quispe", "Calle Tacna 18, El Pedregal"),
    ("Óscar David Laura Machaca", "Mz. A Lt. 21, Asoc. El Mirador"),
    ("Lucía Fernanda Cari Huarca", "Sección B, parcela 66, Majes"),
    ("Hugo Armando Soncco Taype", "Av. Ferrocarril 250, Pedregal"),
    ("Elena Patricia Ayma Quispe", "Calle Puno 301, El Pedregal"),
];

static (string Nombre, string Direccion)[] Empresas() =>
[
    ("Constructora Valle de Majes S.A.C.", "Av. Principal 450, Majes"),
    ("Inversiones Pedregal E.I.R.L.", "Jr. Arequipa 210, El Pedregal"),
    ("Agroindustrias Santa Rita S.A.C.", "Sección A, parcela 3, Majes"),
    ("Edificaciones del Sur S.R.L.", "Av. Ejército 1020, Arequipa"),
    ("Consorcio Vial Caylloma", "Km 3 Carretera Majes - Corire"),
    ("Municipalidad Distrital de Majes", "Plaza Principal s/n, Pedregal"),
    ("Granja Avícola Los Andes S.A.C.", "Sección F, parcela 88, Majes"),
    ("Servicios Generales Misti E.I.R.L.", "Calle Mercaderes 115, Arequipa"),
    ("Inmobiliaria Colca Verde S.A.C.", "Urb. Villa Pedregal Mz. C, Majes"),
    ("Taller Metalmecánico Quispe Hnos. S.R.L.", "Parque Industrial Mz. D Lt. 4, Majes"),
    ("Corporación Agrícola El Valle S.A.", "Sección C, parcela 201, Majes"),
    ("Constructora Chachani S.A.C.", "Av. Dolores 330, J. L. Bustamante y Rivero"),
];

static (string Razon, string Comercial, string Rubro)[] Proveedores() =>
[
    ("Aceros Arequipa S.A.", "Aceros Arequipa", "fierro"),
    ("Cementos Yura S.A.", "Yura", "cemento"),
    ("Pinturas Anypsa Corporation S.A.", "Anypsa", "pinturas"),
    ("Distribuidora Ferretera del Sur S.A.C.", "Ferresur", "ferretería"),
    ("Tubos y Conexiones Pavco Perú S.A.", "Pavco", "tuberías"),
    ("Corporación Eléctrica Indeco S.A.", "Indeco", "cables"),
    ("Celima Trebol S.A.", "Celima", "sanitarios"),
    ("Química Suiza Industrial S.A.C.", "Química Suiza", "adhesivos"),
    ("Productos de Acero Cassado S.A.", "Prodac", "alambres"),
    ("Herramientas Stanley Perú S.A.C.", "Stanley", "herramientas"),
    ("Clavos y Alambres Andinos S.A.C.", "Calanor", "clavos"),
    ("Maderera Pucallpa Sur E.I.R.L.", "Maderas del Sur", "madera"),
    ("Vidrios y Aluminios Arequipa S.R.L.", "Vialsa", "vidrios"),
    ("Sika Perú S.A.C.", "Sika", "aditivos"),
    ("Eternit Perú S.A.", "Eternit", "calaminas"),
    ("Ladrillera El Diamante S.A.C.", "El Diamante", "ladrillos"),
    ("Tecnoquímica Perú S.A.", "Tecnoquímica", "pinturas"),
    ("Grifería Vainsa S.A.", "Vainsa", "grifería"),
    ("Iluminación Philips Perú S.A.C.", "Philips", "iluminación"),
    ("Candados y Cerraduras Forte S.A.C.", "Forte", "cerraduras"),
    ("Bombas Hidráulicas Hidrostal S.A.", "Hidrostal", "bombas"),
    ("Plásticos Rey S.A.C.", "Rey", "plásticos"),
    ("Arenera San Juan E.I.R.L.", "Arenera San Juan", "agregados"),
    ("Soldaduras Oerlikon Perú S.A.C.", "Oerlikon", "soldaduras"),
    ("Mangueras y Riego Agrícola S.A.C.", "Riego Majes", "riego"),
    ("Distribuidora Truper Perú S.A.C.", "Truper", "herramientas"),
];

static (string Nombre, decimal Precio, string Unidad)[] ProductosBase() =>
[
    ("Cemento Portland tipo I x 42.5 kg", 32.50m, "BLS"), ("Fierro corrugado 1/2 in x 9 m", 38.00m, "VAR"),
    ("Fierro corrugado 3/8 in x 9 m", 22.00m, "VAR"), ("Alambre negro N° 16", 8.00m, "KG"),
    ("Clavo para madera 3 in", 7.50m, "KG"), ("Ladrillo King Kong 18 huecos", 1.20m, "UND"),
    ("Arena gruesa", 85.00m, "M"), ("Tubo PVC 1/2 in x 5 m", 9.50m, "UND"),
    ("Esmalte sintético blanco 1 gal", 58.00m, "GAL"), ("Pegamento para PVC 1/4 gal", 24.00m, "UND"),
    ("Cable eléctrico N° 12 x 100 m", 189.00m, "ROL"), ("Calamina galvanizada 3.6 m", 36.00m, "UND"),
    ("Yeso x 18 kg", 14.50m, "BLS"), ("Malla raschel 4.2 m", 6.80m, "M"),
    ("Lija al agua N° 100", 2.50m, "UND"), ("Brocha de 3 in", 9.00m, "UND"),
    ("Thinner acrílico 1 gal", 26.00m, "GAL"), ("Cinta aislante", 3.50m, "UND"),
    ("Candado de bronce 50 mm", 32.00m, "UND"), ("Bisagra de acero 3 in", 4.50m, "PZA"),
    ("Cerradura de embutir", 65.00m, "UND"), ("Llave de paso 1/2 in", 18.00m, "UND"),
    ("Manguera de riego 1/2 in x 25 m", 55.00m, "ROL"), ("Pala cuchara", 38.00m, "UND"),
    ("Carretilla buggy 5.5 ft3", 185.00m, "UND"), ("Wincha de 5 m", 15.00m, "UND"),
];
