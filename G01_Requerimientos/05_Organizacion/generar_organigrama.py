"""Dibuja organigrama.png (organigrama de roles del proyecto).

    python generar_organigrama.py

Los nombres de los integrantes se editan en INTEGRANTES.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AQUI = Path(__file__).resolve().parent

INTEGRANTES = {
    1: "Huamani Condori, Jeanpiero Sixto",
    2: "Payehuanca Riquelme, Jhastyn Jefferson",
    3: "Condo Zamata, Richard Alberto",
    4: "Chaisa Fernández, Anthony Leonel",
}
GUIAS = {1: "G01 · G07 · dictamen G09", 2: "G02 · G05 · suite G09", 3: "G03 · G08", 4: "G04 · G06"}

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")


def caja(x, y, w, h, titulo, texto, gruesa=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="white", edgecolor="black", linewidth=1.8 if gruesa else 1))
    ax.text(x, y + h / 2 - 0.22, titulo, ha="center", va="top", fontsize=10, fontweight="bold")
    ax.text(x, y + h / 2 - 0.55, texto, ha="center", va="top", fontsize=8.5, linespacing=1.35)


def linea(x1, y1, x2, y2, estilo="-"):
    ax.plot([x1, x2], [y1, y2], color="black", linewidth=1, linestyle=estilo)


# Nivel 1: cliente y docente
caja(4.0, 7.15, 4.2, 1.2, "Gerente general (PAR-01)", "Ferretería Cóndor Majes S.A.C.\nPatrocinador: aprueba alcance y cambios")
caja(10.0, 7.15, 4.2, 1.2, "Docente del curso (PAR-06)", "Valida el alcance y evalúa\nlas evidencias de calidad")
# Nivel 2: coordinación y comité de cambios
caja(7.0, 5.35, 4.6, 1.35, "Coordinación del proyecto", f"Integrante 1 — {INTEGRANTES[1]}\nPlanificación, seguimiento y entregas", gruesa=True)
caja(11.6, 5.35, 3.6, 1.35, "Comité de cambios (CCB)", "Gerente + Integrante 1 + Integrante 2\nAprueba o rechaza CC-01, CC-02")
# Nivel 3: integrantes
xs = [2.0, 5.3, 8.7, 12.0]
for i, x in zip(range(1, 5), xs):
    caja(x, 2.75, 3.1, 2.3, f"Integrante {i}", f"{INTEGRANTES[i]}\n\nAnalista · Desarrollador\nResp. de configuración\nEvaluador de calidad\n\nLíder de: {GUIAS[i]}")
# Usuarios
caja(7.0, 0.55, 8.0, 0.8, "Usuarios: Encargado general (PAR-02) · Vendedores (PAR-03) · Contador externo (PAR-04)",
     "")

linea(4.0, 6.55, 4.0, 6.3); linea(10.0, 6.55, 10.0, 6.3); linea(4.0, 6.3, 10.0, 6.3); linea(7.0, 6.3, 7.0, 6.03)
linea(9.3, 5.35, 9.8, 5.35, "--")
linea(7.0, 4.67, 7.0, 4.3); linea(2.0, 4.3, 12.0, 4.3)
for x in xs:
    linea(x, 4.3, x, 3.9)
linea(7.0, 1.6, 7.0, 0.95, "--")
ax.text(7.15, 1.27, "validan requisitos y pruebas de aceptación", fontsize=8, style="italic")
ax.set_title("Organigrama de roles — Trabajo Grupal Sistema Cóndor", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(AQUI / "organigrama.png", dpi=150)
print("organigrama.png generado")
