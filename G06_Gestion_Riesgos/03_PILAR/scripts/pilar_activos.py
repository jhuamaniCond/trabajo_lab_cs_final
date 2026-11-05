"""Crea en PILAR (A.1. Identificación de activos) los activos del inventario de G06.

    python pilar_activos.py <pid de PILAR> [A01 A02 ...]

Usa jab.py de la skill automatizar-gui (Java Access Bridge + agente Swing):
no mueve el mouse ni usa el teclado del usuario.
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
SKILL = os.path.expandvars(r"%USERPROFILE%\.claude\skills\automatizar-gui")
sys.path.insert(0, SKILL)
import jab  # noqa: E402

PID = int(sys.argv[1])
JAB = os.path.join(SKILL, "jab.py")
A1W = "A.1. Identificación de activos"
DLG = "> activo"

# capa, código, nombre, clase a desplegar, subclases a marcar
ACTIVOS = [
    ("[B] Activos esenciales", "A01", "Servicio de venta y facturación (PN-01, PN-02)", "[essential]", ["[service] servicio"]),
    ("[B] Activos esenciales", "A02", "Datos de ventas y comprobantes electrónicos", "[essential]", ["[info] información"]),
    ("[B] Activos esenciales", "A03", "Datos de compras, costos y proveedores (PN-03)", "[essential]", ["[info] información"]),
    ("[SW] Aplicaciones", "A04", "Certificado digital y credenciales SOL de la SUNAT", "[keys]", ["[x509] certificados"]),
    ("[SW] Aplicaciones", "A05", "Aplicación Cóndor 1.1.1 (WPF + Condor.Api)", "[SW] Aplicaciones", ["[prp] desarrollo propio"]),
    ("[SW] Aplicaciones", "A06", "Base de datos PostgreSQL 16", "[SW] Aplicaciones", ["[std] estándar"]),
    ("[HW] Equipos", "A07", "PC principal (API, base de datos y caja 1)", "[HW] Equipamiento", ["[mid] equipos medios"]),
    ("[COM] Comunicaciones", "A08", "Red local e Internet (enlace a la SUNAT)", "[COM] Redes", ["[LAN] red local", "[WAN] red de área amplia"]),
    ("[AUX] Elementos auxiliares", "A09", "Disco externo de respaldos", "[Media] Soportes", ["[electronic] electrónicos"]),
    ("[P] Personal", "A10", "Personal y cuentas de usuario (vendedores, encargado)", "[P] Personal", ["[ui] usuarios internos"]),
]


def run(*args):
    r = subprocess.run([sys.executable, JAB, "-p", str(PID), *args], capture_output=True, text=True, encoding="utf-8")
    salida = (r.stdout + r.stderr).strip()
    if r.returncode:
        raise SystemExit(f"falló {args}: {salida}")
    return salida


def coords(titulo, selector):
    s = jab.Sesion(jab.arrancar_puente(), PID, 25, False)
    s.titulo = titulo
    ci = s.buscar(selector).context_info
    return ci.x, ci.y, ci.width, ci.height


solo = sys.argv[2:]
for capa, cod, nombre, clase, subclases in ACTIVOS:
    if solo and cod not in solo:
        continue
    run("-w", A1W, "-raton", f"nombre={capa}", "-wait", "400", "-ocultos",
        "-click", "rol=menu;nombre=nuevo activo", "-wait", "600", "-click", "rol=menu item;nombre=nuevo activo", "-wait", "2000")
    run("-w", DLG, "-set", "rol=text#1", cod, "-set", "rol=text#2", nombre,
        "-accion", f"rol=check box;nombre~={clase}", "toggleexpand", "-wait", "600")
    for sub in subclases:
        x, y, w, h = coords(DLG, f"rol=check box;nombre~={sub}")
        run("-w", DLG, "-raton", f"{x + 14},{y + h // 2}", "-wait", "500")
    run("-w", DLG, "-click", "descripcion=guarda los datos y cierra", "-wait", "1500")
    print(cod, nombre, "→", capa, subclases)
