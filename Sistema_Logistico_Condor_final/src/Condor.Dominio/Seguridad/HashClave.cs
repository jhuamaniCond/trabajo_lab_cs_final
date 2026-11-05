using System.Security.Cryptography;
using System.Text;

namespace Condor.Dominio.Seguridad;

/// <summary>
/// Hash de contraseñas con PBKDF2-SHA256 (CC-01). La contraseña nunca se
/// guarda: en la base central queda "pbkdf2-sha256$iteraciones$sal$hash",
/// con la sal y el hash en Base64.
/// </summary>
public static class HashClave
{
    public const string Algoritmo = "pbkdf2-sha256";
    public const int Iteraciones = 100_000;
    public const int BytesSal = 16;
    public const int BytesHash = 32;

    /// <summary>Hash de la contraseña con una sal aleatoria nueva.</summary>
    public static string Generar(string clave) => Generar(clave, RandomNumberGenerator.GetBytes(BytesSal), Iteraciones);

    /// <summary>Hash con la sal y las iteraciones indicadas (para pruebas reproducibles).</summary>
    public static string Generar(string clave, byte[] sal, int iteraciones)
    {
        ArgumentNullException.ThrowIfNull(clave);
        if (sal.Length < 8)
            throw new ArgumentException("La sal debe tener al menos 8 bytes.", nameof(sal));
        if (iteraciones < 1)
            throw new ArgumentOutOfRangeException(nameof(iteraciones));

        var hash = Derivar(clave, sal, iteraciones);
        return $"{Algoritmo}${iteraciones}${Convert.ToBase64String(sal)}${Convert.ToBase64String(hash)}";
    }

    /// <summary>
    /// True si la contraseña corresponde al hash. Un hash vacío o mal formado
    /// nunca verifica. La comparación toma el mismo tiempo acierte o no.
    /// </summary>
    public static bool Verificar(string? clave, string? hashGuardado)
    {
        if (clave is null || string.IsNullOrWhiteSpace(hashGuardado))
            return false;

        var partes = hashGuardado.Split('$');
        if (partes.Length != 4 || partes[0] != Algoritmo || !int.TryParse(partes[1], out var iteraciones) || iteraciones < 1)
            return false;

        byte[] sal, esperado;
        try
        {
            sal = Convert.FromBase64String(partes[2]);
            esperado = Convert.FromBase64String(partes[3]);
        }
        catch (FormatException)
        {
            return false;
        }

        if (sal.Length == 0 || esperado.Length == 0)
            return false;

        var calculado = Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(clave), sal, iteraciones, HashAlgorithmName.SHA256,
            esperado.Length);
        return CryptographicOperations.FixedTimeEquals(calculado, esperado);
    }

    private static byte[] Derivar(string clave, byte[] sal, int iteraciones) =>
        Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(clave), sal, iteraciones, HashAlgorithmName.SHA256, BytesHash);
}
