using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;
using Condor.Presentacion.Mvvm;

namespace Condor.Presentacion.ViewModels;

/// <summary>
/// Ventana Ingresar (CC-01): usuario y contraseña antes de abrir Nueva venta.
/// Reemplaza el ingreso directo con el perfil MAESTRO de HU-14.
/// </summary>
public sealed class LoginViewModel : ObservableObject
{
    private readonly IAutenticador _autenticacion;
    private readonly string _terminal;
    private readonly Func<Task>? _preparar;
    private string _usuario = string.Empty;
    private string _clave = string.Empty;
    private string? _error;

    /// <param name="autenticacion">Quien comprueba la contraseña: el backend (app de escritorio) o el servicio local.</param>
    /// <param name="terminal">Nombre de esta PC, para la bitácora de accesos.</param>
    /// <param name="preparar">
    /// Se llama antes de cada intento (las migraciones, que crean la tabla de
    /// usuarios la primera vez); debe ser idempotente.
    /// </param>
    public LoginViewModel(IAutenticador autenticacion, string terminal, Func<Task>? preparar = null)
    {
        _autenticacion = autenticacion;
        _terminal = terminal;
        _preparar = preparar;
        IngresarCommand = new AsyncRelayCommand(IngresarAsync, PuedeIngresar);
        CancelarCommand = new RelayCommand(() => Cerrar?.Invoke(false));
    }

    /// <summary>Lo escucha la ventana para cerrarse: true si ingresó.</summary>
    public event Action<bool>? Cerrar;

    public string Usuario
    {
        get => _usuario;
        set
        {
            if (SetProperty(ref _usuario, value ?? string.Empty))
                AlCambiarDatos();
        }
    }

    /// <summary>Lo escribe la vista desde el PasswordBox (no se puede enlazar).</summary>
    public string Clave
    {
        get => _clave;
        set
        {
            if (SetProperty(ref _clave, value ?? string.Empty))
                AlCambiarDatos();
        }
    }

    /// <summary>Mensaje en rojo bajo el formulario; null si no hay error.</summary>
    public string? Error
    {
        get => _error;
        private set => SetProperty(ref _error, value);
    }

    /// <summary>Quien ingresó; null mientras no ingrese.</summary>
    public CuentaUsuario? Cuenta { get; private set; }

    /// <summary>Tras un intento fallido la vista borra la contraseña escrita.</summary>
    public event Action? ClaveRechazada;

    public AsyncRelayCommand IngresarCommand { get; }

    public RelayCommand CancelarCommand { get; }

    /// <summary>Vacía el formulario para volver a mostrarlo al cerrar sesión.</summary>
    public void Reiniciar()
    {
        Cuenta = null;
        Clave = string.Empty;
        Error = null;
    }

    private bool PuedeIngresar() => !string.IsNullOrWhiteSpace(Usuario) && Clave.Length > 0;

    private void AlCambiarDatos()
    {
        Error = null;
        IngresarCommand.NotificarCambio();
    }

    private async Task IngresarAsync()
    {
        try
        {
            if (_preparar is not null)
                await _preparar();

            var resultado = await _autenticacion.AutenticarAsync(Usuario, Clave, _terminal);
            if (!resultado.Exitoso)
            {
                Error = resultado.Mensaje;
                ClaveRechazada?.Invoke();
                return;
            }

            Cuenta = resultado.Cuenta;
            Cerrar?.Invoke(true);
        }
        catch (SinConexionException)
        {
            Error = "Sin conexión con la PC principal. Revise la red y pulse Ingresar para reintentar.";
        }
        catch (Exception ex)
        {
            Error = $"No se pudo ingresar: {ex.Message}";
        }
    }
}
