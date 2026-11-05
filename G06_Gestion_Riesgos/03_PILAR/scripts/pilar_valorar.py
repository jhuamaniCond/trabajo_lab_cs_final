"""Valora en PILAR (A.2. Valoración de los dominios) los activos esenciales de G06.

    python pilar_valorar.py <pid de PILAR>

Escala MAGERIT 0-10. Los valores y su justificación son los de
01_Inventario/inventario_activos.md (sección 3).
"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
PID = sys.argv[1]
SKILL = os.path.expandvars(r"%USERPROFILE%\.claude\skills\automatizar-gui")
JAB = os.path.join(SKILL, "jab.py")
JAR = os.path.join(SKILL, "java", "agente.jar")
JAVA = r"C:\Program Files\Java\jdk-26.0.2.1\bin\java.exe"

# Coordenadas físicas de las celdas de A.2 (ventana en 295,12; filas cada 20 px)
COL = {"D": 1089, "I": 1237, "C": 1385, "A": 1535, "T": 1683}
FILA = {"A01": 142, "A02": 162, "A03": 182}
VALORES = {
    "A01": {"D": (8, "~150 ventas/día y colas en hora punta (ENT-01 A2); medio día sin vender detiene los ingresos.")},
    "A02": {"D": (7, "El historial y el reenvío a la SUNAT dependen de estos datos."),
            "I": (9, "Importe o correlativo alterado = contingencia tributaria (CRQ-01, CRQ-05)."),
            "C": (5, "DNI y RUC de clientes: datos personales de sensibilidad media (Ley 29733)."),
            "A": (8, "Cada comprobante debe decir quién lo emitió (CRQ-11, CC-01)."),
            "T": (8, "Bitácora de accesos y autoría por comprobante (CRQ-11, IRQ-08).")},
    "A03": {"D": (4, "Las compras se registran después; una demora de horas es tolerable."),
            "I": (6, "Un costo alterado distorsiona el margen."),
            "C": (7, "Costos y egresos no deben verlos los vendedores (CFL-06, CRQ-12)."),
            "A": (5, "Se registra quién ingresó cada compra."),
            "T": (5, "Trazabilidad de compras para el contador.")},
}


def agente(titulo, *args):
    r = subprocess.run([JAVA, "-jar", JAR, PID, titulo, *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit(f"agente {args}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


for activo, dims in VALORES.items():
    for dim, (valor, comentario) in dims.items():
        subprocess.run([sys.executable, JAB, "-p", PID, "-w", "A.2. Valoración", "-dobleclic",
                        f"{COL[dim]},{FILA[activo]}", "-wait", "1500"], capture_output=True, text=True, check=True)
        titulo = f"[{activo}]"
        agente(titulo, "combo", "1", f"[{valor}]")
        agente(titulo, "texto", "1", comentario)
        agente(titulo, "pulsar", "aplicar")
        time.sleep(1)
        print(activo, dim, valor)
