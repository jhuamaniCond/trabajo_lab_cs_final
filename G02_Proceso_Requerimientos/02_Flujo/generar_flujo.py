"""Dibuja flujo_requerimientos.png: el flujo de estados configurado en Redmine
para requisitos y solicitudes de cambio, con el rol que hace cada transición
y la evidencia que se exige.

    python generar_flujo.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

AQUI = Path(__file__).resolve().parent

fig, ax = plt.subplots(figsize=(16, 6.2))
ax.set_xlim(0, 16)
ax.set_ylim(0.3, 6.5)
ax.axis("off")

W, H = 1.65, 0.9
ESTADOS = {  # nombre: (x, y, cerrado)
    "Registrado": (1.4, 4.6, False),
    "Analizado": (4.0, 4.6, False),
    "Aprobado": (6.6, 4.6, False),
    "Rechazado": (6.6, 1.6, True),
    "Implementado": (9.2, 4.6, False),
    "Verificado": (11.8, 4.6, False),
    "Cerrado": (14.6, 4.6, True),
}


def estado(nombre):
    x, y, cerrado = ESTADOS[nombre]
    ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.02,rounding_size=0.25",
                                facecolor="#e8e8e8" if cerrado else "white", edgecolor="black",
                                linewidth=2.2 if cerrado else 1.3))
    ax.text(x, y, nombre, ha="center", va="center", fontsize=11, fontweight="bold")


def flecha(de, a, rol, evidencia, curva=0.0, dy=0.0, ancla=None):
    x1, y1, _ = ESTADOS[de]
    x2, y2, _ = ESTADOS[a]
    if y1 == y2:
        p1, p2 = (x1 + W / 2, y1 + dy), (x2 - W / 2, y2 + dy)
        if x2 < x1:
            p1, p2 = (x1 - W / 2, y1 + dy), (x2 + W / 2, y2 + dy)
    else:
        p1, p2 = (x1, y1 - H / 2), (x2, y2 + H / 2)
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16, linewidth=1.2, color="black",
                                 connectionstyle=f"arc3,rad={curva}"))
    mx, my = ancla or ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    ax.text(mx, my + 1.05, rol, ha="center", va="bottom", fontsize=8.6, fontweight="bold")
    ax.text(mx, my + 0.55, evidencia, ha="center", va="bottom", fontsize=7.6, linespacing=1.25)


for e in ESTADOS:
    estado(e)

# Inicio
ax.plot(0.2, 4.6, "o", color="black", markersize=10)
ax.add_patch(FancyArrowPatch((0.28, 4.6), (1.4 - W / 2, 4.6), arrowstyle="-|>", mutation_scale=14, color="black"))
ax.text(0.1, 4.0, "Alta", ha="left", fontsize=8.6, fontweight="bold")

flecha("Registrado", "Analizado", "Analista", "claridad, consistencia\ny verificabilidad")
flecha("Analizado", "Aprobado", "CCB", "decisión en la nota;\nlínea base o CC")
flecha("Aprobado", "Implementado", "Desarrollador", "versión y archivos\nde código")
flecha("Implementado", "Verificado", "Evaluador de calidad", "reporte de pruebas\n(.trx / .html)")
flecha("Verificado", "Cerrado", "CCB", "trazabilidad\ncompleta")
flecha("Analizado", "Rechazado", "", "", curva=0.0)
ax.text(4.55, 3.0, "CCB", ha="center", fontsize=8.6, fontweight="bold")
ax.text(4.55, 2.85, "decisión y sustento\n(campo Decisión)", ha="center", fontsize=7.6, va="top")
# Regreso cuando la verificación falla
x1, y1, _ = ESTADOS["Verificado"]
x2, y2, _ = ESTADOS["Implementado"]
ax.add_patch(FancyArrowPatch((x1 - 0.4, y1 - H / 2), (x2 + 0.4, y2 - H / 2), arrowstyle="-|>", mutation_scale=16,
                             linewidth=1.1, color="black", linestyle="--", connectionstyle="arc3,rad=-0.55"))
ax.text(10.5, 3.25, "Evaluador de calidad: la prueba falla\n→ se registra el defecto y vuelve a Implementado",
        ha="center", va="top", fontsize=7.6, style="italic")

# Leyenda
ax.add_patch(FancyBboxPatch((9.0, 0.45), 6.6, 1.65, boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor="white", edgecolor="#888888", linewidth=0.8))
ax.text(9.2, 1.9, "Tipos de petición en Redmine: Requisito y Solicitud de cambio (mismo flujo)", fontsize=8.4,
        va="top", fontweight="bold")
ax.text(9.2, 1.5, "Recuadro gris = estado cerrado (Rechazado, Cerrado).\n"
                  "CCB = gerente general + Integrante 1 + Integrante 2.\n"
                  "Cada transición deja en el historial la fecha, el usuario y una nota con la evidencia.",
        fontsize=8, va="top", linespacing=1.4)

ax.set_title("Flujo del proceso de requerimientos y cambios — Sistema Cóndor (Redmine 7.0.1)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(AQUI / "flujo_requerimientos.png", dpi=150)
print("flujo_requerimientos.png generado")
