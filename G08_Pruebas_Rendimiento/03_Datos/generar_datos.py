"""Genera los CSV que lee el plan JMeter de G08 (semilla fija: mismos datos en cada ejecución).

Uso: python generar_datos.py   (escribe en la carpeta de este script)

- usuarios.csv  : 12 vendedores (carga01-carga10, vendedor1, vendedor2). Cada hilo toma uno.
- consultas.csv : textos que escribe un vendedor en la búsqueda (3 a 12 letras, con y sin tildes).
                  Todos devuelven al menos un producto de preparar_bd_rendimiento.sql.
- ventas.csv    : 600 boletas de 1 a 3 líneas (ids 1-3000, cantidades 1-3). 80 % boleta simple y
                  20 % boleta con DNI de un cliente registrado (40000001-40000200). El total máximo
                  posible es 3 x 3 x S/ 59.99 = S/ 539.91, por debajo de S/ 700, así que ninguna
                  boleta simple exige DNI (regla de EmisionComprobante).
"""
import csv
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
azar = random.Random(20261101)

with open(AQUI / "usuarios.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["usuario", "clave"])
    for i in range(1, 11):
        w.writerow([f"carga{i:02d}", "Vendedor2026!"])
    w.writerow(["vendedor1", "Vendedor2026!"])
    w.writerow(["vendedor2", "Vendedor2026!"])

CONSULTAS = [
    "tor", "torn", "clav", "perno", "tuer", "aran", "tubo", "codo", "tee pvc", "cable",
    "cinta", "inter", "toma", "foco", "pint", "latex", "esmal", "sintetico", "broch", "rodi",
    "lija", "disco", "broca", "llave", "grif", "mang", "canda", "bisa", "cerra", "sili",
    "pega", "alam", "malla", "condor", "majes", "misti", "colca", "volcan", "1/2 in", "3/4 in",
    "10 mm", "pvc", "led", "acero", "galvan", "concreto", "corte", "agua", "doble", "hexag",
]
with open(AQUI / "consultas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["texto"])
    for texto in CONSULTAS:
        w.writerow([texto])

# ventas.csv usa ";" como separador y sin comillas: el detalle es JSON y lleva comas y comillas.
with open(AQUI / "ventas.csv", "w", newline="", encoding="utf-8") as f:
    f.write("tipo;dni;detalle\n")
    for _ in range(600):
        con_dni = azar.random() < 0.20
        lineas = azar.randint(1, 3)
        ids = azar.sample(range(1, 3001), lineas)
        detalle = ",".join(f'{{"productoId":{p},"cantidad":{azar.randint(1, 3)}}}' for p in ids)
        dni = str(40000000 + azar.randint(1, 200)) if con_dni else ""
        f.write(f"{'BOLETA_DNI' if con_dni else 'BOLETA'};{dni};{detalle}\n")
print("usuarios.csv, consultas.csv y ventas.csv generados en", AQUI)
