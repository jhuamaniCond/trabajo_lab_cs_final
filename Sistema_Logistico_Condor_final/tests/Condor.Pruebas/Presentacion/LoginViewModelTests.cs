using Condor.Dominio.Contratos;
using Condor.Dominio.Seguridad;
using Condor.Presentacion.ViewModels;
using Condor.Pruebas.Infraestructura;

namespace Condor.Pruebas.Presentacion;

/// <summary>CC-01: ventana Ingresar de la app de escritorio.</summary>
public class LoginViewModelTests
{
    private readonly UsuarioRepositorioEnMemoria _usuarios = UsuarioRepositorioEnMemoria.ConUsuariosDemo();

    private LoginViewModel Crear(Func<Task>? preparar = null) => new(new ServicioAutenticacion(_usuarios), "PC-1", preparar);

    [Fact]
    public void Ingresar_esta_deshabilitado_hasta_escribir_usuario_y_clave()
    {
        var vm = Crear();
        Assert.False(vm.IngresarCommand.CanExecute(null));

        vm.Usuario = "vendedor1";
        Assert.False(vm.IngresarCommand.CanExecute(null));

        vm.Clave = "x";
        Assert.True(vm.IngresarCommand.CanExecute(null));
    }

    [Fact]
    public async Task Con_la_clave_correcta_se_cierra_con_la_cuenta()
    {
        var vm = Crear();
        bool? cerrado = null;
        vm.Cerrar += ok => cerrado = ok;
        vm.Usuario = "encargado";
        vm.Clave = "Encargado2026!";

        await vm.IngresarCommand.EjecutarAsync();

        Assert.True(cerrado);
        Assert.Equal("encargado", vm.Cuenta!.NombreUsuario);
        Assert.Null(vm.Error);
    }

    [Fact]
    public async Task Con_la_clave_equivocada_muestra_el_error_y_pide_borrar_la_clave()
    {
        var vm = Crear();
        var borrar = false;
        var cerrado = false;
        vm.ClaveRechazada += () => borrar = true;
        vm.Cerrar += _ => cerrado = true;
        vm.Usuario = "vendedor1";
        vm.Clave = "mal";

        await vm.IngresarCommand.EjecutarAsync();

        Assert.Equal(ServicioAutenticacion.MensajeInvalidas, vm.Error);
        Assert.True(borrar);
        Assert.False(cerrado);
        Assert.Null(vm.Cuenta);
    }

    [Fact]
    public async Task Escribir_de_nuevo_borra_el_error()
    {
        var vm = Crear();
        vm.Usuario = "vendedor1";
        vm.Clave = "mal";
        await vm.IngresarCommand.EjecutarAsync();

        vm.Clave = "otra";

        Assert.Null(vm.Error);
    }

    [Fact]
    public async Task Sin_conexion_avisa_y_permite_reintentar()
    {
        _usuarios.Error = new SinConexionException(new TimeoutException());
        var vm = Crear();
        vm.Usuario = "vendedor1";
        vm.Clave = "Vendedor2026!";

        await vm.IngresarCommand.EjecutarAsync();

        Assert.Contains("Sin conexión", vm.Error);
        Assert.True(vm.IngresarCommand.CanExecute(null));
    }

    [Fact]
    public async Task Antes_de_ingresar_prepara_la_base_de_datos()
    {
        var preparada = 0;
        var vm = Crear(() => { preparada++; return Task.CompletedTask; });
        vm.Usuario = "vendedor1";
        vm.Clave = "Vendedor2026!";

        await vm.IngresarCommand.EjecutarAsync();

        Assert.Equal(1, preparada);
    }

    [Fact]
    public async Task Reiniciar_borra_la_clave_la_cuenta_y_el_error()
    {
        var vm = Crear();
        vm.Usuario = "vendedor1";
        vm.Clave = "Vendedor2026!";
        await vm.IngresarCommand.EjecutarAsync();

        vm.Reiniciar();

        Assert.Null(vm.Cuenta);
        Assert.Equal(string.Empty, vm.Clave);
        Assert.Equal("vendedor1", vm.Usuario);
    }
}
