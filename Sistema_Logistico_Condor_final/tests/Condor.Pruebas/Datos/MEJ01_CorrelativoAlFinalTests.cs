using Condor.Datos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Ventas;
using Condor.Pruebas.Infraestructura;
using Npgsql;

namespace Condor.Pruebas.Datos;

/// <summary>
/// MEJ-01 (G08, 1.1.2): ComprobanteRepositorio.EmitirAsync reserva el número
/// de la serie al final de la transacción. Se comprueba que se mantiene la
/// regla de HU-16 (ningún número repetido ni saltado con tres PC a la vez,
/// ahora pasando por el repositorio real), que una emisión fallida no consume
/// número ni deja el número provisional, y que la serie solo queda bloqueada
/// en el último tramo de la emisión.
/// </summary>
[Collection(BaseDatos.Nombre)]
public class MEJ01_CorrelativoAlFinalTests
{
    private const int ComprobantesPorPc = 30;

    private readonly BaseDatosFixture _bd;

    public MEJ01_CorrelativoAlFinalTests(BaseDatosFixture bd) => _bd = bd;

    [FactConBD]
    public async Task Tres_PC_emitiendo_con_el_repositorio_no_repiten_ni_saltan_numeros()
    {
        await using var local = new TresPC();
        var codigo = await CrearSerieAsync();
        var producto = await CrearProductoAsync();
        var terminales = await Task.WhenAll(local.Pc.Select((pc, i) =>
            new TerminalRepositorio(pc).RegistrarAccesoAsync(DatosPrueba.NombreUnico($"MEJ01-PC-{i + 1}"))));

        using var largada = new Barrier(3);
        var tareas = local.Pc.Select((pc, i) => Task.Run(async () =>
        {
            var repositorio = new ComprobanteRepositorio(pc);
            largada.SignalAndWait();
            var numeros = new List<long>();
            for (var n = 0; n < ComprobantesPorPc; n++)
                numeros.Add((await repositorio.EmitirAsync(Boleta(producto, codigo, terminales[i].Id))).Numero);
            return numeros;
        }));
        var devueltos = (await Task.WhenAll(tareas)).SelectMany(x => x).Order().ToList();

        var total = 3 * ComprobantesPorPc;
        var guardados = await NumerosAsync(codigo);
        Assert.Equal(Enumerable.Range(1, total).Select(x => (long)x), guardados); // ni repetidos ni saltados
        Assert.Equal(guardados, devueltos);                                       // cada PC recibió el número guardado
        Assert.Equal(total, await UltimoCorrelativoAsync(codigo));
    }

    [FactConBD]
    public async Task Una_emision_que_falla_no_consume_numero_ni_deja_el_numero_provisional()
    {
        var codigo = await CrearSerieAsync();
        var producto = await CrearProductoAsync();
        var terminal = await new TerminalRepositorio(_bd.Conexiones).RegistrarAccesoAsync(DatosPrueba.NombreUnico("MEJ01-PC"));
        var repositorio = new ComprobanteRepositorio(_bd.Conexiones);

        // La segunda línea apunta a un producto que no existe: falla al guardar el detalle.
        var mala = Boleta(producto, codigo, terminal.Id);
        mala.Detalle.Add(new DetalleComprobante
        {
            Item = 2, ProductoId = long.MaxValue, Descripcion = "No existe", Cantidad = 1, PrecioUnitario = 1, Importe = 1,
        });
        mala.Total += 1;
        mala.OpGravada = decimal.Round(mala.Total / 1.18m, 2);
        mala.Igv = mala.Total - mala.OpGravada;
        await Assert.ThrowsAnyAsync<Exception>(() => repositorio.EmitirAsync(mala));

        Assert.Equal(0, await UltimoCorrelativoAsync(codigo));
        Assert.Empty(await NumerosAsync(codigo));

        var buena = await repositorio.EmitirAsync(Boleta(producto, codigo, terminal.Id));
        Assert.Equal(1, buena.Numero);
        Assert.Equal(new long[] { 1 }, await NumerosAsync(codigo));
    }

    [FactConBD]
    public async Task La_serie_se_bloquea_solo_al_numerar_no_durante_toda_la_emision()
    {
        await using var local = new TresPC();
        var codigo = await CrearSerieAsync();

        // PC-1 tiene la fila de la serie bloqueada (está numerando y aún no confirma).
        await using var conexion1 = await local.Pc[0].AbrirAsync();
        var tx1 = await conexion1.BeginTransactionAsync();
        Assert.Equal(1, await SerieRepositorio.SiguienteCorrelativoAsync(conexion1, tx1, codigo));

        // PC-2 guarda la cabecera de su comprobante sin esperar a la PC-1:
        // antes de MEJ-01 el número se pedía primero y esta sentencia esperaba el bloqueo.
        await using var conexion2 = await local.Pc[1].AbrirAsync();
        await using var tx2 = await conexion2.BeginTransactionAsync();
        await using (var cmd = new NpgsqlCommand("SET LOCAL lock_timeout = '1s'", conexion2, tx2))
            await cmd.ExecuteNonQueryAsync();
        var terminal = await new TerminalRepositorio(_bd.Conexiones).RegistrarAccesoAsync(DatosPrueba.NombreUnico("MEJ01-PC"));
        await using (var cmd = new NpgsqlCommand(
            """
            INSERT INTO comprobante (id, serie_id, numero, terminal_id, op_gravada, igv, total)
            SELECT n.id, s.id, -n.id, @t, 8.47, 1.53, 10.00
            FROM serie s, (SELECT nextval('comprobante_id_seq') AS id) n
            WHERE s.codigo = @s
            RETURNING id
            """, conexion2, tx2))
        {
            cmd.Parameters.AddWithValue("s", codigo);
            cmd.Parameters.AddWithValue("t", terminal.Id);
            var id = (long)(await cmd.ExecuteScalarAsync())!;

            // Solo el paso final (numerar) espera a la PC-1, y recibe el número siguiente.
            var numerar = SerieRepositorio.NumerarComprobanteAsync(conexion2, tx2, codigo, id);
            await Task.Delay(300);
            Assert.False(numerar.IsCompleted);
            await tx1.CommitAsync();
            Assert.Equal(2, await numerar);
        }
        await tx2.RollbackAsync();
    }

    private static Comprobante Boleta(Producto producto, string codigo, int terminalId)
    {
        var boleta = EmisionComprobante.Preparar(new SolicitudEmision(TipoEmision.Boleta, new[]
        {
            new DetalleComprobante
            {
                ProductoId = producto.Id, Descripcion = producto.Nombre, Unidad = producto.Unidad,
                Cantidad = 2, PrecioUnitario = producto.Precio,
            },
        }));
        boleta.SerieCodigo = codigo;
        boleta.TerminalId = terminalId;
        boleta.Usuario = "vendedor1";
        return boleta;
    }

    private async Task<Producto> CrearProductoAsync() =>
        await new ProductoRepositorio(_bd.Conexiones).RegistrarAsync(DatosPrueba.Nuevo(DatosPrueba.NombreUnico("MEJ01 Tornillo"), 4.50m));

    private async Task<string> CrearSerieAsync()
    {
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand(
            """
            INSERT INTO serie (tipo_comprobante, codigo)
            SELECT '03', 'M' || lpad(n::text, 3, '0')
            FROM generate_series(1, 999) AS n
            WHERE NOT EXISTS (SELECT 1 FROM serie WHERE codigo = 'M' || lpad(n::text, 3, '0'))
            LIMIT 1
            RETURNING codigo
            """, conexion);
        return (string)(await cmd.ExecuteScalarAsync())!;
    }

    private async Task<List<long>> NumerosAsync(string codigo)
    {
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand(
            "SELECT c.numero FROM comprobante c JOIN serie s ON s.id = c.serie_id WHERE s.codigo = @s ORDER BY c.numero", conexion);
        cmd.Parameters.AddWithValue("s", codigo);
        var numeros = new List<long>();
        await using var lector = await cmd.ExecuteReaderAsync();
        while (await lector.ReadAsync())
            numeros.Add(lector.GetInt64(0));
        return numeros;
    }

    private async Task<long> UltimoCorrelativoAsync(string codigo)
    {
        await using var conexion = await _bd.Conexiones.AbrirAsync();
        await using var cmd = new NpgsqlCommand("SELECT ultimo_correlativo FROM serie WHERE codigo = @s", conexion);
        cmd.Parameters.AddWithValue("s", codigo);
        return (long)(await cmd.ExecuteScalarAsync())!;
    }
}
