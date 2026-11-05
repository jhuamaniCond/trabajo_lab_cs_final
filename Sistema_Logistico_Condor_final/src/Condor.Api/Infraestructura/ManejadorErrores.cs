using Condor.Dominio.Contratos;
using Condor.Dominio.Validacion;
using Condor.Dominio.Ventas;
using Microsoft.AspNetCore.Diagnostics;

namespace Condor.Api.Infraestructura;

/// <summary>
/// Convierte las excepciones de las reglas de negocio en respuestas HTTP
/// (application/problem+json), para que JMeter y los clientes distingan un
/// dato inválido (400) de un duplicado (409) o de la base caída (503).
/// </summary>
internal sealed class ManejadorErrores : IExceptionHandler
{
    private readonly ILogger<ManejadorErrores> _log;

    public ManejadorErrores(ILogger<ManejadorErrores> log) => _log = log;

    public async ValueTask<bool> TryHandleAsync(HttpContext http, Exception ex, CancellationToken ct)
    {
        var (estado, titulo, errores) = Clasificar(ex);
        if (estado == StatusCodes.Status500InternalServerError)
            _log.LogError(ex, "Error no controlado en {Ruta}", http.Request.Path);

        // "tipo" deja que el cliente de la app de escritorio vuelva a lanzar la misma excepción.
        var extensiones = new Dictionary<string, object?> { ["tipo"] = ex.GetType().Name };
        if (errores is not null)
            extensiones["errores"] = errores;
        await Results.Problem(title: titulo, statusCode: estado, extensions: extensiones).ExecuteAsync(http);
        return true;
    }

    internal static (int Estado, string Titulo, IReadOnlyList<string>? Errores) Clasificar(Exception ex) => ex switch
    {
        SinConexionException => (StatusCodes.Status503ServiceUnavailable, "Sin conexión con la base de datos central.", null),
        ProductoInvalidoException e => (StatusCodes.Status400BadRequest, "El producto no es válido.", e.Errores),
        ClienteInvalidoException e => (StatusCodes.Status400BadRequest, "El cliente no es válido.", e.Errores),
        ProveedorInvalidoException e => (StatusCodes.Status400BadRequest, "El proveedor no es válido.", e.Errores),
        ComprobanteInvalidoException e => (StatusCodes.Status400BadRequest, "El comprobante no se puede emitir.",
            e.Errores.Select(x => x.Mensaje).ToList()),
        CompraInvalidaException or GuiaInvalidaException => (StatusCodes.Status400BadRequest, ex.Message, null),
        ProductoDuplicadoException or CodigoBarrasDuplicadoException or ClienteDuplicadoException
            or ProveedorDuplicadoException or ProformaYaConvertidaException or CompraDuplicadaException
            => (StatusCodes.Status409Conflict, ex.Message, null),
        // Reglas que los repositorios hacen cumplir (serie que no corresponde, PC sin registrar...).
        RespaldoException or InvalidOperationException => (StatusCodes.Status409Conflict, ex.Message, null),
        BadHttpRequestException => (StatusCodes.Status400BadRequest, "La solicitud está mal formada.", null),
        ArgumentException => (StatusCodes.Status400BadRequest, ex.Message, null),
        _ => (StatusCodes.Status500InternalServerError, "Error interno del servidor.", null),
    };
}
