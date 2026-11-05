using Condor.Dominio.Entidades;
using Condor.Dominio.Seguridad;
using Condor.Presentacion.ViewModels;
using Condor.Pruebas.Infraestructura;

namespace Condor.Pruebas.Aceptacion;

/// <summary>
/// CC-01: ingreso con usuario, contraseña y rol (reemplaza el perfil único de HU-14).
/// Criterio 1: cada rol abre solo sus módulos; el Vendedor no abre Compras,
/// Proveedores, Guías ni Respaldo, y se le avisa por qué.
/// Criterio 2: cada comprobante queda con el usuario que lo emitió y su terminal.
/// Criterio 3: cerrar sesión descarta la venta en curso y vuelve a pedir ingreso.
/// </summary>
public class CC01_IngresoConRolesTests
{
    private static CuentaUsuario Cuenta(string usuario, string rol) =>
        new() { Id = 1, NombreUsuario = usuario, NombreCompleto = $"Usuario {usuario}", Rol = rol };

    private static MainViewModel ConSesion(string rol, ComprobanteRepositorioEnMemoria? comprobantes = null)
    {
        var vm = new MainViewModel(new ProductoRepositorioEnMemoria(DatosPrueba.Catalogo()), new ClienteRepositorioEnMemoria(),
            comprobantes ?? new ComprobanteRepositorioEnMemoria(), new ProveedorRepositorioEnMemoria(),
            new CompraRepositorioEnMemoria()) { ExigirIngreso = true };
        vm.ConfigurarRespaldo(null, new RespaldoRepositorioEnMemoria(), null);
        vm.IniciarSesion(new Sesion(new Terminal { Id = 7, Nombre = "PC-2" },
            Cuenta(rol == Roles.Encargado ? "encargado" : "vendedor1", rol)));
        return vm;
    }

    [Theory]
    [InlineData(Modulo.Compras)]
    [InlineData(Modulo.Proveedores)]
    [InlineData(Modulo.Guias)]
    [InlineData(Modulo.Respaldo)]
    public void CA1_el_vendedor_no_abre_los_modulos_del_encargado(Modulo modulo)
    {
        var vm = ConSesion(Roles.Vendedor);

        Assert.False(vm.IrA(modulo));
        Assert.Equal(Modulo.Venta, vm.ModuloActual);
        Assert.StartsWith("Acceso denegado", vm.Mensaje);
    }

    [Theory]
    [InlineData(Modulo.Catalogo)]
    [InlineData(Modulo.Clientes)]
    [InlineData(Modulo.Proformas)]
    public void CA1_el_vendedor_abre_los_modulos_del_mostrador(Modulo modulo)
    {
        var vm = ConSesion(Roles.Vendedor);

        Assert.True(vm.IrA(modulo));
        Assert.Equal(modulo, vm.ModuloActual);
    }

    [Theory]
    [InlineData(Modulo.Compras)]
    [InlineData(Modulo.Proveedores)]
    [InlineData(Modulo.Respaldo)]
    public void CA1_el_encargado_abre_todos_los_modulos(Modulo modulo)
    {
        var vm = ConSesion(Roles.Encargado);

        Assert.True(vm.IrA(modulo));
    }

    [Fact]
    public void CA1_el_pie_muestra_el_usuario_y_el_rol()
    {
        var vm = ConSesion(Roles.Vendedor);

        Assert.Equal("vendedor1", vm.Usuario);
        Assert.Equal("Vendedor", vm.Rol);
        Assert.False(vm.EsEncargado);
    }

    [Fact]
    public void CA1_si_se_exige_ingreso_sin_sesion_no_se_abre_ningun_modulo()
    {
        var vm = new MainViewModel(new ProductoRepositorioEnMemoria()) { ExigirIngreso = true };
        vm.IniciarSesion(Sesion.Local("PC-1"));

        Assert.False(vm.IrA(Modulo.Catalogo));
        Assert.Equal("Ingrese con su usuario y contraseña.", vm.Mensaje);
    }

    [Fact]
    public async Task CA2_el_comprobante_queda_con_el_usuario_y_la_terminal()
    {
        var comprobantes = new ComprobanteRepositorioEnMemoria();
        var vm = ConSesion(Roles.Vendedor, comprobantes);
        vm.Venta.ProductoPorAgregar = new Producto { Id = 1, Nombre = "Cemento Portland tipo I x 42.5 kg", Precio = 32.50m, Unidad = "BLS" };
        vm.Venta.CantidadTexto = "2";
        vm.Venta.Agregar();

        await vm.Emision!.EmitirCommand.EjecutarAsync();

        var emitido = Assert.Single(comprobantes.Comprobantes);
        Assert.Equal("vendedor1", emitido.Usuario);
        Assert.Equal(7, emitido.TerminalId);
    }

    [Fact]
    public void CA3_cerrar_sesion_descarta_la_venta_y_avisa_al_arranque()
    {
        var vm = ConSesion(Roles.Encargado);
        vm.IrA(Modulo.Proveedores);
        vm.Venta.ProductoPorAgregar = new Producto { Id = 1, Nombre = "Cemento", Precio = 30m };
        vm.Venta.CantidadTexto = "1";
        vm.Venta.Agregar();
        var avisado = false;
        vm.SesionCerrada += () => avisado = true;

        Assert.True(vm.CerrarSesion());

        Assert.True(avisado);
        Assert.Empty(vm.Venta.Detalle);
        Assert.Equal(Modulo.Venta, vm.ModuloActual);
        Assert.False(vm.Sesion!.Autenticada);
        Assert.Equal("PC-2", vm.Terminal);
    }

    [Fact]
    public void PermisosModulo_lista_los_modulos_de_cada_rol()
    {
        Assert.Equal(Enum.GetValues<Modulo>(), PermisosModulo.De(Roles.Encargado));
        Assert.Equal(new[] { Modulo.Venta, Modulo.Catalogo, Modulo.Clientes, Modulo.Historial, Modulo.Proformas },
            PermisosModulo.De(Roles.Vendedor));
        Assert.Equal(new[] { Modulo.Venta }, PermisosModulo.De("OTRO"));
    }
}
