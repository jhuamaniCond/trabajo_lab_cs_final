using Condor.Dominio.Contratos;

namespace Condor.Api.Infraestructura;

/// <summary>
/// Respaldo de la base central (HU-15) desde la API: pg_dump corre en la PC
/// principal, que tiene el disco externo. Sin la sección Respaldo de
/// appsettings.json el generador es null y la app avisa que no está configurado.
/// </summary>
public sealed record ServicioRespaldo(IGeneradorRespaldo? Generador, string Carpeta, int AvisoHoras);
