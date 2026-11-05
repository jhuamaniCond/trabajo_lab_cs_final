# -*- coding: utf-8 -*-
"""
generar_codigo.py
Compila con LaTeX (listings, en texlive.net) los fragmentos de código que van
como figura en el informe y en el manual técnico. Se ejecuta antes que los
guiones generar_*.py. El código se lee del archivo real por número de línea.

    python Docs/generar_codigo.py
"""

import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/informes-docx"))
from codigo_latex import renderizar  # noqa: E402

DOCS = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(DOCS)
FIG = os.path.join(DOCS, "figuras")
SIS = os.path.join(RAIZ, "Sistema_Logistico_Condor_final")
G07 = os.path.join(RAIZ, "G07_Pruebas_Unitarias", "01_Suite", "Condor.PruebasUnitarias")

TIPOS_CS = ["SolicitudEmision", "ErrorEmision", "CampoEmision", "TipoEmision",
            "TipoDocumento", "ValidadorDocumento", "EmisionComprobante",
            "IReadOnlyList", "List", "Datos", "Assert", "decimal"]

CODIGO = {
    # Regla CRQ-02 (boleta de más de S/ 700 exige DNI): la que altera DEF-02.
    "cod_regla_700": dict(
        bloques=[(os.path.join(SIS, "src", "Condor.Dominio", "Ventas", "EmisionComprobante.cs"), 104, 112),
                 (os.path.join(SIS, "src", "Condor.Dominio", "Ventas", "EmisionComprobante.cs"), 131, 135)],
        lenguaje="[Sharp]C", tipos=TIPOS_CS),
    # Casos PU-13 y PU-14: valor límite de la misma regla.
    "cod_pu13_pu14": dict(
        bloques=[(os.path.join(G07, "EmisionComprobanteTests.cs"), 13, 34)],
        lenguaje="[Sharp]C", tipos=TIPOS_CS, anotaciones=["[Fact]"]),
    # Parámetros del script de arranque (manual técnico).
    "cod_ejecutar_ps1": dict(
        bloques=[(os.path.join(SIS, "ejecutar.ps1"), 33, 47)],
        lenguaje="bash", tipos=["int", "switch", "CmdletBinding"]),
    # Archivo de configuración de cada PC (manual técnico).
    "cod_condor_json": dict(
        bloques=[(os.path.join(SIS, "src", "Condor.Escritorio", "condor.ejemplo.json"), 1, 21)],
        lenguaje="Java", tipos=[]),
    # Restauración de un respaldo (manual técnico), tomado de docs/respaldo.md.
    "cod_restaurar": dict(
        bloques=[(os.path.join(SIS, "docs", "respaldo.md"), 73, 83)],
        lenguaje="bash", tipos=[]),
    # Administración de usuarios sin pantalla (manual técnico), docs/seguridad.md.
    "cod_admin_sql": dict(
        bloques=[(os.path.join(SIS, "docs", "seguridad.md"), 80, 87)],
        lenguaje="SQL", tipos=[]),
}


def main():
    os.makedirs(FIG, exist_ok=True)
    for clave, cfg in CODIGO.items():
        salida = os.path.join(FIG, clave + ".png")
        renderizar(cfg["bloques"], salida, lenguaje=cfg["lenguaje"],
                   tipos=cfg.get("tipos"), anotaciones=cfg.get("anotaciones", ()))
        print("OK", salida)


if __name__ == "__main__":
    main()
