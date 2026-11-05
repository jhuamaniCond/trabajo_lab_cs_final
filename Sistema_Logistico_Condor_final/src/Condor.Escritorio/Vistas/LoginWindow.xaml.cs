using System.Windows;
using Condor.Presentacion.ViewModels;

namespace Condor.Escritorio.Vistas;

public partial class LoginWindow : Window
{
    public LoginWindow(LoginViewModel vm)
    {
        InitializeComponent();
        DataContext = vm;
        // Asignar DialogResult cierra la ventana abierta con ShowDialog.
        vm.Cerrar += ingreso => DialogResult = ingreso;
        // Tras un intento fallido se borra la contraseña y el cursor vuelve a ella.
        vm.ClaveRechazada += () =>
        {
            CampoClave.Clear();
            CampoClave.Focus();
        };

#if DEBUG
        // Solo en compilación Debug (capturas y pruebas de interfaz): Windows no
        // deja escribir en un PasswordBox sin el teclado real. No existe en Release.
        if (Environment.GetEnvironmentVariable("CONDOR_DEMO_USUARIO") is { Length: > 0 } usuario)
        {
            vm.Usuario = usuario;
            CampoClave.Password = Environment.GetEnvironmentVariable("CONDOR_DEMO_CLAVE") ?? string.Empty;
        }
#endif
    }

    // El PasswordBox no se puede enlazar: la contraseña pasa al ViewModel aquí.
    private void CampoClave_PasswordChanged(object sender, RoutedEventArgs e) =>
        ((LoginViewModel)DataContext).Clave = CampoClave.Password;
}
