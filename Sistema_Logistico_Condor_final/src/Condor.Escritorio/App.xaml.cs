using System.IO;
using System.Windows;
using System.Windows.Threading;
using Condor.ClienteApi;
using Condor.Dominio.Contratos;
using Condor.Dominio.Entidades;
using Condor.Dominio.Impresion;
using Condor.Dominio.Seguridad;
using Condor.Dominio.Sunat;
using Condor.Escritorio.Impresion;
using Condor.Escritorio.Vistas;
using Condor.Impresion;
using Condor.Presentacion.ViewModels;
using Condor.Sunat;

namespace Condor.Escritorio;

public partial class App : Application
{
    /// <summary>
    /// Conexión con el backend (Condor.Api) en la PC principal, compartida por
    /// toda la aplicación. Desde CC-01 las PC ya no se conectan a PostgreSQL:
    /// todo pasa por la API, que es la única que tiene la clave de la base.
    /// </summary>
    public static ClienteServidor? Servidor { get; private set; }

    private ConfiguracionApi? _config;
    private MainViewModel? _vm;
    private DispatcherTimer? _monitorConexion;
    private DispatcherTimer? _avisoCatalogo;
    private DispatcherTimer? _temporizadorReenvio;
    private DispatcherTimer? _temporizadorGuias;
    private ConfiguracionSunat? _sunat;
    private bool _sesionLista;
    private long? _versionCatalogo;
    private CuentaUsuario? _cuenta;

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        try
        {
            _config = ConfiguracionApi.Cargar();
        }
        catch (Exception ex) when (ex is FileNotFoundException or InvalidDataException)
        {
            MessageBox.Show(ex.Message, "Configuración de la conexión con la PC principal",
                MessageBoxButton.OK, MessageBoxImage.Error);
            Shutdown(1);
            return;
        }

        var nombreEquipo = Environment.MachineName;
        Servidor = new ClienteServidor(_config);

        // Hasta abrir Nueva venta no hay ventana principal: la app no debe
        // cerrarse al cerrar el aviso de arranque ni el diálogo Ingresar.
        ShutdownMode = ShutdownMode.OnExplicitShutdown;

        // PC principal: si el backend no está corriendo, se arranca solo (opción
        // Api > Backend de condor.json), así basta con abrir CondorVentas.exe.
        await ArrancarBackendSiHaceFaltaAsync();

        // CC-01 (reemplaza el ingreso directo de HU-14): antes de abrir Nueva
        // venta se pide usuario y contraseña, que comprueba la API.
        _cuenta = PedirIngreso();
        if (_cuenta is null)
        {
            Shutdown(0);
            return;
        }

        var comprobantes = new ComprobanteRepositorioApi(Servidor);
        var empresa = new EmpresaRepositorioApi(Servidor);
        _vm = new MainViewModel(new ProductoRepositorioApi(Servidor), new ClienteRepositorioApi(Servidor), comprobantes,
            new ProveedorRepositorioApi(Servidor), new CompraRepositorioApi(Servidor)) { ExigirIngreso = true };
        _vm.IniciarSesion(Sesion.Local(nombreEquipo, _cuenta));
        _vm.SesionCerrada += AlCerrarSesion;

        // T-06: cada 5 s se comprueba la PC principal (GET /api/salud); si no
        // responde se muestra el aviso con Reintentar y no se borra nada de la pantalla.
        _vm.Conexion = new EstadoConexionViewModel(Servidor.ProbarAsync);
        _vm.Conexion.ConexionRecuperada += async () => await PrepararSesionAsync();
        _monitorConexion = new DispatcherTimer { Interval = TimeSpan.FromSeconds(5) };
        _monitorConexion.Tick += async (_, _) => await _vm.Conexion.ActualizarAsync();
        _monitorConexion.Start();

        // T-13: cada 3 s se pregunta a la API si cambió el catálogo (antes, LISTEN/NOTIFY directo a PostgreSQL).
        _avisoCatalogo = new DispatcherTimer { Interval = TimeSpan.FromSeconds(3) };
        _avisoCatalogo.Tick += async (_, _) => await RevisarCatalogoAsync();

        // HU-12: ticketera de condor.json o, si no hay, vista previa en pantalla.
        var ticketera = CargarTicketera();
        IImpresoraTickets impresora = ticketera.Configurada
            ? new ImpresoraWindows(ticketera.Nombre!, TimeSpan.FromSeconds(ticketera.EsperaSegundos))
            : new ImpresoraVistaPrevia();
        _vm.Impresion = new ImpresionViewModel(impresora, empresa, comprobantes, ticketera.Columnas);

        // HU-07: cada boleta se envía a la SUNAT al emitirla desde esta PC (si
        // tiene la sección Sunat en condor.json); el resultado se anota por la API.
        var sunat = CargarSunat();
        _sunat = sunat;
        var servicioSunat = sunat.Configurada ? new ServicioEnvioSunat(sunat) : null;
        var registroSunat = new EnvioSunatRepositorioApi(Servidor);
        _vm.EnvioSunat = new EnvioSunatViewModel(servicioSunat, empresa, registroSunat);

        // HU-17: los pendientes se reenvían solos cada ReenvioMinutos. Las PC
        // sin la SUNAT configurada solo muestran cuántos quedan.
        IReenvioPendientes? reenvio = servicioSunat is not null && sunat.ReenviaPendientes
            ? new ReenvioPendientes(servicioSunat, registroSunat, comprobantes, empresa, nombreEquipo)
            : null;
        _vm.ReenvioSunat = new ReenvioSunatViewModel(reenvio, registroSunat);
        if (reenvio is not null)
        {
            _temporizadorReenvio = new DispatcherTimer { Interval = TimeSpan.FromMinutes(sunat.ReenvioMinutos) };
            _temporizadorReenvio.Tick += async (_, _) => await _vm.ReenvioSunat.ReenviarAsync();
        }

        // HU-10: las guías las emite el Encargado; se envían desde la PC que
        // tiene las credenciales de la API de guías, y sus pendientes se
        // consultan o reenvían cada ReenvioMinutos.
        IEnvioGuiaSunat? servicioGuias = sunat.GuiasConfiguradas ? new ServicioGuiaSunat(sunat) : null;
        _vm.ConfigurarGuias(new GuiaRemisionRepositorioApi(Servidor), empresa, servicioGuias);
        if (servicioGuias is not null && sunat.ReenviaPendientes)
        {
            _temporizadorGuias = new DispatcherTimer { Interval = TimeSpan.FromMinutes(sunat.ReenvioMinutos) };
            _temporizadorGuias.Tick += async (_, _) => await ReenviarGuiasAsync();
        }

        // HU-15: el respaldo lo genera la API en la PC principal, donde está el
        // disco externo (sección Respaldo de su appsettings.json).
        var respaldo = await ConfiguracionRespaldoAsync();
        _vm.ConfigurarRespaldo(respaldo.Configurado ? new GeneradorRespaldoApi(Servidor) : null,
            new RespaldoRepositorioApi(Servidor), respaldo.Configurado ? respaldo.Carpeta : null, respaldo.AvisoHoras);

        var ventana = new MainWindow { DataContext = _vm };
        MainWindow = ventana;
        ShutdownMode = ShutdownMode.OnMainWindowClose;
        ventana.Show();
        _vm.Mensaje = $"Sesión iniciada: {_cuenta.NombreCompleto} ({Roles.Nombre(_cuenta.Rol)}).";

        if (await _vm.Conexion.ActualizarAsync())
            await PrepararSesionAsync();
        else
            _vm.Mensaje = $"Sin conexión con la PC principal ({_config}). Revise la red.";
    }

    /// <summary>
    /// Arranca CondorApi.exe en segundo plano si condor.json lo indica y la API
    /// no responde; espera hasta 40 s a que /api/salud diga que está lista. Si
    /// no lo logra, la ventana Ingresar mostrará el aviso de sin conexión.
    /// </summary>
    private async Task ArrancarBackendSiHaceFaltaAsync()
    {
        if (_config?.RutaBackend() is not { } ruta || await Servidor!.ProbarAsync())
            return;
        if (!File.Exists(ruta))
        {
            MessageBox.Show($"No se encontró el backend en {ruta}. Revise Api > Backend en condor.json.",
                "Backend", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var aviso = new Window
        {
            Title = "Ferretería Cóndor", Width = 360, Height = 120, ResizeMode = ResizeMode.NoResize,
            WindowStartupLocation = WindowStartupLocation.CenterScreen, WindowStyle = WindowStyle.ToolWindow,
            Content = new System.Windows.Controls.TextBlock
            {
                Text = "Iniciando el servidor de la PC principal…", Margin = new Thickness(20),
                VerticalAlignment = VerticalAlignment.Center, FontSize = 14,
            },
        };
        aviso.Show();
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(ruta)
            {
                WorkingDirectory = Path.GetDirectoryName(ruta)!,
                UseShellExecute = false,
                CreateNoWindow = true,
            });
            var limite = DateTime.UtcNow.AddSeconds(40);
            while (DateTime.UtcNow < limite && !await Servidor!.ProbarAsync())
                await Task.Delay(1000);
        }
        catch (Exception ex) when (ex is System.ComponentModel.Win32Exception or InvalidOperationException)
        {
            MessageBox.Show($"No se pudo iniciar el backend ({ruta}):\n{ex.Message}", "Backend",
                MessageBoxButton.OK, MessageBoxImage.Warning);
        }
        finally
        {
            aviso.Close();
        }
    }

    /// <summary>
    /// Ventana Ingresar (CC-01). Devuelve la cuenta que ingresó o null si se
    /// pulsó Salir. La contraseña la comprueba la API, que entrega el token.
    /// </summary>
    private static CuentaUsuario? PedirIngreso()
    {
        var login = new LoginViewModel(new AutenticadorApi(Servidor!), Environment.MachineName);
        return new LoginWindow(login).ShowDialog() == true ? login.Cuenta : null;
    }

    /// <summary>
    /// Cerrar sesión (CC-01): se detienen las tareas de fondo, se olvida el
    /// token, se oculta la ventana principal y se vuelve a pedir usuario y
    /// contraseña; con Salir se cierra el programa.
    /// </summary>
    private void AlCerrarSesion()
    {
        if (_vm is null)
            return;

        DetenerTareas();
        MainWindow?.Hide();
        var cuenta = PedirIngreso();
        if (cuenta is null)
        {
            Shutdown(0);
            return;
        }

        _cuenta = cuenta;
        _vm.IniciarSesion(new Sesion(_vm.Sesion?.Terminal ?? new Terminal { Nombre = Environment.MachineName }, cuenta));
        _vm.Mensaje = $"Sesión iniciada: {cuenta.NombreCompleto} ({Roles.Nombre(cuenta.Rol)}).";
        IniciarTareas();
        MainWindow?.Show();
        MainWindow?.Activate();
    }

    /// <summary>Sección Ticketera de condor.json; si está mal escrita se avisa y se usa la vista previa.</summary>
    private static ConfiguracionTicketera CargarTicketera()
    {
        try
        {
            return ConfiguracionTicketera.Cargar();
        }
        catch (InvalidDataException ex)
        {
            MessageBox.Show($"{ex.Message}\nLos tickets se mostrarán en pantalla hasta corregir condor.json.",
                "Configuración de la ticketera", MessageBoxButton.OK, MessageBoxImage.Warning);
            return new ConfiguracionTicketera();
        }
    }

    /// <summary>Sección Sunat de condor.json; si está mal escrita se avisa y los comprobantes quedan pendientes.</summary>
    private static ConfiguracionSunat CargarSunat()
    {
        try
        {
            return ConfiguracionSunat.Cargar();
        }
        catch (InvalidDataException ex)
        {
            MessageBox.Show($"{ex.Message}\nLos comprobantes quedarán pendientes de envío a la SUNAT hasta corregir condor.json.",
                "Configuración de la SUNAT", MessageBoxButton.OK, MessageBoxImage.Warning);
            return new ConfiguracionSunat();
        }
    }

    /// <summary>Si la API no responde al arrancar, el respaldo figura como no configurado.</summary>
    private static async Task<ConfiguracionRespaldoApi> ConfiguracionRespaldoAsync()
    {
        try
        {
            return await GeneradorRespaldoApi.ConfiguracionAsync(Servidor!) ?? new ConfiguracionRespaldoApi(false, string.Empty, 24);
        }
        catch (SinConexionException)
        {
            return new ConfiguracionRespaldoApi(false, string.Empty, 24);
        }
    }

    /// <summary>
    /// Registro de la terminal y tareas de fondo. Se hace una vez: al arrancar
    /// o, si arrancó sin red, cuando vuelve la conexión.
    /// </summary>
    private async Task PrepararSesionAsync()
    {
        if (_sesionLista || Servidor is null || _vm is null)
            return;

        try
        {
            var terminal = await new TerminalRepositorioApi(Servidor).RegistrarAccesoAsync(Environment.MachineName);
            _vm.IniciarSesion(new Sesion(terminal, _cuenta));
            _versionCatalogo = await AvisoCatalogoApi.VersionAsync(Servidor);

            _sesionLista = true;
            _vm.Mensaje = $"Conectado a la PC principal ({_config}). Sesión: {_cuenta?.NombreCompleto} ({Roles.Nombre(_cuenta?.Rol)}).";

            // T-99: en producción, avisar lo que falta para facturar de verdad.
            if (_sunat is { EsProduccion: true } sunat)
            {
                var pendientes = ChequeoProduccion.Pendientes(sunat, await new EmpresaRepositorioApi(Servidor).ObtenerAsync());
                if (pendientes.Count > 0)
                    MessageBox.Show("Antes de facturar en producción falta:\n\n• " + string.Join("\n• ", pendientes),
                        "Puesta en producción", MessageBoxButton.OK, MessageBoxImage.Warning);
            }

            // HU-15, criterio 2: si el último respaldo tiene más de 24 horas, se avisa al Encargado.
            if (_vm.AvisoRespaldo is { } avisoRespaldo)
                await avisoRespaldo.RevisarAsync();

            IniciarTareas();
            // HU-17: primera vuelta del reenvío al abrir y luego cada ReenvioMinutos.
            if (_vm.ReenvioSunat is { } reenvio)
            {
                await reenvio.ActualizarAsync();
                _ = reenvio.ReenviarAsync();
            }
        }
        catch (SinConexionException)
        {
            _vm.Conexion?.MarcarSinConexion();
            _vm.Mensaje = $"Se perdió la conexión con la PC principal ({_config}).";
        }
        catch (Exception ex)
        {
            MessageBox.Show($"No se pudo preparar la sesión con la PC principal:\n{ex.Message}",
                "Conexión", MessageBoxButton.OK, MessageBoxImage.Error);
            Shutdown(2);
        }
    }

    private void IniciarTareas()
    {
        if (!_sesionLista)
            return;
        _avisoCatalogo?.Start();
        _temporizadorReenvio?.Start();
        _temporizadorGuias?.Start();
    }

    private void DetenerTareas()
    {
        _avisoCatalogo?.Stop();
        _temporizadorReenvio?.Stop();
        _temporizadorGuias?.Stop();
    }

    /// <summary>T-13: si otra PC cambió el catálogo, se refresca el buscador. Sin red, espera a la siguiente vuelta.</summary>
    private async Task RevisarCatalogoAsync()
    {
        if (Servidor is null || _vm is null)
            return;
        try
        {
            var version = await AvisoCatalogoApi.VersionAsync(Servidor);
            if (_versionCatalogo is { } anterior && version != anterior)
                _vm.AlCambiarCatalogo();
            _versionCatalogo = version;
        }
        catch (Exception ex) when (ex is SinConexionException or SesionVencidaException)
        {
            // El monitor de conexión ya muestra el aviso; la sesión vencida se avisa al usarla.
        }
    }

    /// <summary>Vuelta del reenvío de guías (HU-10); sin la PC principal o sin internet, espera a la siguiente.</summary>
    private async Task ReenviarGuiasAsync()
    {
        if (_vm?.EnvioGuias is not { Configurado: true } envio)
            return;
        try
        {
            var resultado = await envio.ReenviarPendientesAsync();
            if (resultado.Aceptadas + resultado.Rechazadas > 0)
                _vm.Mensaje = resultado.Resumen;
        }
        catch (SinConexionException)
        {
            _vm.Conexion?.MarcarSinConexion();
        }
        catch (SesionVencidaException ex)
        {
            _vm.Mensaje = ex.Message;
        }
    }

    protected override void OnExit(ExitEventArgs e)
    {
        DetenerTareas();
        _monitorConexion?.Stop();
        Servidor?.Dispose();
        base.OnExit(e);
    }
}
