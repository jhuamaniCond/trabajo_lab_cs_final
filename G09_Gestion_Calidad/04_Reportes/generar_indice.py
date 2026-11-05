"""Genera indice_ejecuciones.md a partir de resultados.json de cada ejecución.

    python generar_indice.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MOTIVO = {
    "r30_primera": "Primera ejecución sobre la rama CC-03 (r30)",
    "r30_defectos": "Aserciones nuevas para DEF-03 y DEF-04 (vistos en la revisión de capturas): la suite los detecta",
    "r31_correccion": "Tras corregir DEF-03 y DEF-04 (r31): pasan; falla intermitente de la suite en CP-10 (DEF-06)",
    "r31_regresion": "Regresión en la rama tras corregir DEF-06 en la suite",
    "r32_final-1": "Trunk r32, Chrome — anulada para el dictamen: la suite tenía DEF-07 (CP-13 compraba dos veces cemento)",
    "r32_final-2": "Trunk r32, Chrome — anulada para el dictamen (DEF-07)",
    "r32_edge": "Trunk r32, Edge — anulada para el dictamen (DEF-07)",
    "r32_final-3": "**Regresión final** sobre trunk r32 con la suite corregida — Chrome (1.ª)",
    "r32_final-4": "**Regresión final** sobre trunk r32 — Chrome (2.ª, repetibilidad)",
    "r32_edge-2": "**Regresión final** sobre trunk r32 — Edge",
}
filas = []
for r in sorted(AQUI.glob("*/resultados.json")):
    d = json.loads(r.read_text(encoding="utf-8"))
    casos = d["casos"]
    ok = sum(c["estado"] == "APROBADO" for c in casos)
    malos = [f'{c["caso"]} ({c["estado"].lower()})' for c in casos if c["estado"] != "APROBADO"]
    nav = d["entorno"].get("navegador", {})
    cp07 = next((c["mediciones"] for c in casos if c["caso"] == "CP-07"), {})
    clave = next((k for k in MOTIVO if d["etiqueta"].endswith(k)), "")
    filas.append(f'| `{r.parent.name}` | {d["entorno"]["producto"].get("version", "?")} | {nav.get("navegador", "")} {nav.get("version", "")} '
                 f'| **{ok}/{len(casos)}** | {", ".join(malos) or "—"} | {cp07.get("RNF-01 sugerencias (ms)", "")} ms / {cp07.get("RNF-06 venta con teclado (s)", "")} s '
                 f'| {d["segundos"]:.0f} s | {MOTIVO.get(clave, "")} |')
texto = ["# Ejecuciones de la suite Selenium", "",
         "Cada carpeta tiene `reporte.html` (abrir en el navegador), `resultados.xml` (JUnit), `resultados.json`, `ejecucion.log`, `entorno.json` y `capturas/`.", "",
         "| Ejecución | Producto | Navegador | Aprobados | Fallidos | CP-07: RNF-01 / RNF-06 | Duración | Motivo |",
         "|---|---|---|---|---|---|---|---|", *filas, "",
         "`xunit_1.2.0-r32/`: suite xUnit del producto sobre trunk r32 (`.trx` y `.html`): 944 aprobadas, 0 fallidas, 5 omitidas.", ""]
(AQUI / "indice_ejecuciones.md").write_text("\n".join(texto), encoding="utf-8")
print("\n".join(filas))
