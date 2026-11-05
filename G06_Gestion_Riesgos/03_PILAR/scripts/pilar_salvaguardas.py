"""Fija en PILAR (A.5.1. Salvaguardas) la madurez actual (current) y objetivo (target)
de cada grupo de salvaguardas, con la justificación del plan de tratamiento de G06.

    python pilar_salvaguardas.py <pid de PILAR>

Escala de madurez de PILAR: L0 inexistente · L1 inicial · L2 reproducible ·
L3 proceso definido · L4 gestionado y medible · L5 optimizado.
"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
PID = sys.argv[1]
JAR = os.path.expandvars(r"%USERPROFILE%\.claude\skills\automatizar-gui\java\agente.jar")
JAVA = r"C:\Program Files\Java\jdk-26.0.2.1\bin\java.exe"

# Tabla de A.5.1 en píxeles físicos (jab.py -info): x 157..1761, y 105..625, filas de 20 px
Y0, ALTO = 105, 20
X_CUR, X_TAR = 1623, 1677
NIVEL = {0: "L0 - inexistente", 1: "L1 - inicial / ad hoc", 2: "L2 - reproducible, pero intuitivo",
         3: "L3 - proceso definido", 4: "L4 - gestionado y medible"}
# fila, grupo, actual, objetivo, evidencia o motivo
GRUPOS = [
    (1, "[IA] Identificación y autenticación", 3, 4, "S1 implantado y verificado: PBKDF2, bloqueo al 5.º intento, bitácora"),
    (2, "[AC] Control de acceso lógico", 3, 4, "S1: 100 % de rutas del Encargado responden 403 al Vendedor"),
    (3, "[D] Protección de la información", 2, 3, "Respaldo manual sin cifrar; objetivo: cifrado y copia fuera del local"),
    (4, "[K] Protección de claves criptográficas", 1, 3, "Certificado en la PC principal sin protección formal"),
    (6, "[SW] Protección de las aplicaciones", 3, 4, "S2 implantado: validación en el servidor (DEF-01, CRQ-14), 930 pruebas"),
    (7, "[HW] Protección de los equipos", 1, 2, "Sin inventario ni mantenimiento planificado"),
    (8, "[COM] Protección de las comunicaciones", 1, 3, "API por HTTP en la LAN; objetivo: HTTPS"),
    (9, "[M] Protección de los soportes", 1, 3, "Disco externo sin cifrar guardado en el local"),
    (10, "[AUX] Elementos auxiliares", 0, 2, "Sin UPS; objetivo: UPS en la PC principal"),
    (11, "[PPE] Protección física de los equipos", 1, 2, "PC principal en el mostrador, sin resguardo"),
    (13, "[P] Gestión del personal", 1, 2, "Sin capacitación en seguridad; objetivo: inducción de 1 h"),
    (14, "[IM] Gestión de incidentes", 0, 2, "No hay procedimiento; objetivo: registro y respuesta básica"),
    (15, "[tools] Herramientas de seguridad", 1, 2, "Solo el antivirus de Windows"),
    (16, "[V] Gestión de vulnerabilidades", 1, 2, "Actualizaciones sin calendario"),
    (17, "[A] Registro y auditoría", 2, 3, "Bitácora de accesos y usuario por comprobante; falta revisión periódica"),
    (18, "[BC] Continuidad del negocio", 2, 3, "S3 verificado (restauración) y venta sin internet; falta plan escrito"),
    (19, "[G] Organización", 1, 2, "Roles definidos en el sistema, sin política escrita"),
    (20, "[E] Relaciones externas", 1, 2, "Sin acuerdo formal con proveedor de internet ni OSE"),
    (21, "[NEW] Adquisición / desarrollo", 3, 3, "Proceso definido: requisitos, cambios, SVN, pruebas y revisión (G01-G09)"),
]


def agente(titulo, *args):
    r = subprocess.run([JAVA, "-jar", JAR, PID, titulo, *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit(f"agente {args}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


for fila, grupo, actual, objetivo, motivo in GRUPOS:
    y = Y0 + ALTO * fila + ALTO // 2
    for x, nivel in ((X_CUR, actual), (X_TAR, objetivo)):
        agente("A.5.1", "derecho", str(x), str(y))
        time.sleep(0.8)
        agente("", "pulsar", NIVEL[nivel])
        time.sleep(0.8)
    print(f"{grupo}: L{actual} -> L{objetivo} ({motivo})")
