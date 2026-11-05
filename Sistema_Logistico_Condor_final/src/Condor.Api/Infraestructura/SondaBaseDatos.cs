namespace Condor.Api.Infraestructura;

/// <summary>
/// Comprueba si la base de datos central responde (GET /api/salud). Es un
/// envoltorio para que las pruebas la reemplacen sin PostgreSQL.
/// </summary>
public sealed record SondaBaseDatos(Func<CancellationToken, Task<bool>> Probar);
