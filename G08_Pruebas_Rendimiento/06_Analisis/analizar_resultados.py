"""Analiza los resultados de G08 (JMeter + monitoreo) y genera el libro y las gráficas del análisis.

Uso: python analizar_resultados.py
Lee   ../04_Resultados/<fase>/<escenario>/{resultado.jtl, monitoreo_windows.csv, monitoreo_postgres.csv}
Crea  resumen_resultados.xlsx (una hoja por tabla) y graficas/*.png, e imprime las tablas en Markdown.

Ventanas de análisis (segundos desde la primera muestra; ver 01_Plan, sección 3):
- carga y estabilidad: todo el escenario (como el dashboard) y la parte estable (desde 30 s).
- estrés: nivel 10 u [30, 210), nivel 25 u [220, 390), nivel 50 u [400, 570).
- pico: antes [30, 180), subida [180, 190), pico 50 u [190, 250), después [250, 420).
Percentiles por rango más cercano sobre los valores ordenados (el dashboard de JMeter puede interpolar el p99).
"""
import csv
import math
import statistics
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI.parent / "04_Resultados"
GRAFICAS = AQUI / "graficas"
FASES = {"1_antes": "Antes (línea base)", "2_despues": "Después (mejora)",
         "3_diagnostico_synchronous_commit_off": "Diagnóstico sin espera del COMMIT"}
ESCENARIOS = ["carga", "estres", "pico", "estabilidad"]
CAPACIDAD = [10, 25, 50, 100]  # hilos sin pausas (diagnóstico del cuello de botella, 05_Cuello_de_Botella)
T1, T2, LOGIN = "T1 Consultar productos", "T2 Registrar boleta", "00 Ingresar"
TRANSACCIONES = [T1, T2]
CPUS = 20  # hilos lógicos del i7-13650HX: typeperf da el % de un núcleo por proceso
UMBRAL_P95, UMBRAL_ERROR = 2000, 1.0

VENTANAS = {
    "carga": [("Todo el escenario (0:00-5:30)", 0, 1e9), ("Estable 10 u (0:30-5:30)", 30, 1e9)],
    "estres": [("Nivel 10 u (0:30-3:30)", 30, 210), ("Nivel 25 u (3:40-6:30)", 220, 390),
               ("Nivel 50 u (6:40-9:30)", 400, 570)],
    "pico": [("Antes 10 u (0:30-3:00)", 30, 180), ("Subida 10->50 (3:00-3:10)", 180, 190),
             ("Pico 50 u (3:10-4:10)", 190, 250), ("Después 10 u (4:10-7:00)", 250, 420)],
    "estabilidad": [("Todo el escenario (0:00-15:30)", 0, 1e9), ("Estable 10 u (0:30-15:30)", 30, 1e9)],
}
for _u in CAPACIDAD:
    VENTANAS[f"capacidad_{_u}u"] = [(f"{_u} hilos sin pausas (0:10-2:10)", 10, 1e9)]

AZUL, NARANJA, VERDE, GRIS = "#2a78d6", "#eb6834", "#2e9e6a", "#8a8984"
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"


def transaccion(etiqueta):
    for t in (T1, T2, LOGIN):
        if etiqueta.startswith(t):
            return t
    return etiqueta


def leer_jtl(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for r in filas:
        r["t"] = transaccion(r["label"])
        r["ts"] = int(r["timeStamp"])
        r["ms"] = int(r["elapsed"])
        r["ok"] = r["success"] == "true"
        r["hilos"] = int(r["allThreads"])
    inicio = min(r["ts"] for r in filas)
    for r in filas:
        r["seg"] = (r["ts"] - inicio) / 1000
    return filas


def percentil(valores, p):
    """Percentil por rango más cercano."""
    v = sorted(valores)
    return v[max(0, math.ceil(p / 100 * len(v)) - 1)]


def resumir(filas):
    if not filas:
        return None
    t = [r["ms"] for r in filas]
    inicio = min(r["ts"] for r in filas)
    fin = max(r["ts"] + r["ms"] for r in filas)
    errores = sum(not r["ok"] for r in filas)
    return {
        "n": len(filas), "media": statistics.mean(t), "mediana": percentil(t, 50),
        "p90": percentil(t, 90), "p95": percentil(t, 95), "p99": percentil(t, 99),
        "min": min(t), "max": max(t), "errores": errores, "error_pct": 100 * errores / len(filas),
        "throughput": len(filas) / max(1e-9, (fin - inicio) / 1000),
    }


def leer_typeperf(ruta):
    if not ruta.exists():
        return []
    with open(ruta, newline="", encoding="utf-8-sig", errors="replace") as f:
        lector = csv.reader(f)
        cab = next(lector)
        filas = []
        for r in lector:
            if len(r) != len(cab):
                continue
            fila = {"hora": datetime.strptime(r[0], "%m/%d/%Y %H:%M:%S.%f")}
            for nombre, valor in zip(cab[1:], r[1:]):
                clave = nombre.split("\\", 3)[-1]
                try:
                    fila[clave] = float(valor)
                except ValueError:
                    fila[clave] = None
            filas.append(fila)
    return filas


def serie(filas, prefijo, sufijo, combinar=max):
    """Valor por muestra de los contadores que empiezan por prefijo y terminan en sufijo (java* puede dar varios)."""
    salida = []
    for f in filas:
        vals = [v for k, v in f.items() if k != "hora" and k.startswith(prefijo) and k.endswith(sufijo) and v is not None]
        salida.append(combinar(vals) if vals else None)
    return salida


def resumir_monitoreo(carpeta):
    tp = leer_typeperf(carpeta / "monitoreo_windows.csv")
    m = {}
    if tp:
        def stats(vals, escala=1.0):
            v = [x * escala for x in vals if x is not None]
            return (statistics.mean(v), max(v)) if v else (float("nan"), float("nan"))
        m["cpu_total"] = stats(serie(tp, "Processor(_Total)", "% Processor Time"))
        m["cpu_api"] = stats(serie(tp, "Process(CondorApi)", "% Processor Time"), 1 / CPUS)
        mem = [x / 2**20 for x in serie(tp, "Process(CondorApi)", "Working Set - Private") if x]
        m["mem_api"] = (mem[0], mem[-1], max(mem)) if mem else (float("nan"),) * 3
        hilos = [x for x in serie(tp, "Process(CondorApi)", "Thread Count") if x]
        m["hilos_api"] = max(hilos) if hilos else float("nan")
        libre = [x for x in serie(tp, "Memory", "Available MBytes") if x]
        m["mem_libre_min"] = min(libre) if libre else float("nan")
    jm = carpeta / "monitoreo_jmeter.csv"
    if jm.exists():
        with open(jm, newline="", encoding="utf-8-sig") as f:
            v = [float(r["cpu_jmeter_pct"]) for r in csv.DictReader(f) if r.get("cpu_jmeter_pct")]
        if v:
            m["cpu_java"] = (statistics.mean(v), max(v))
    else:
        m["cpu_java"] = (float("nan"), float("nan"))  # línea base: typeperf no capturó el java de JMeter
    pg = carpeta / "monitoreo_postgres.csv"
    if pg.exists():
        with open(pg, newline="", encoding="utf-8-sig") as f:
            filas = [r for r in csv.DictReader(f) if r.get("conexiones_api")]
        num = lambda k: [float(r[k]) for r in filas if r[k] not in ("", None)]
        if filas:
            m["cpu_pg"] = (statistics.mean(num("cpu_postgres_pct")) / CPUS, max(num("cpu_postgres_pct")) / CPUS)
            m["mem_pg"] = max(num("memoria_postgres_mib"))
            m["con_max"] = max(num("conexiones_api"))
            m["activas_max"] = max(num("activas"))
            m["bloqueo_max"] = max(num("esperando_bloqueo"))
    return m, tp


def num(x, d=0):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------- gráficas

def estilo(ax, titulo, ylabel, xlabel="Tiempo desde el inicio (min)"):
    ax.set_title(titulo, loc="left", fontsize=11.5, color=TINTA, pad=10)
    ax.set_xlabel(xlabel, color=TINTA2)
    ax.set_ylabel(ylabel, color=TINTA2)
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA2)
    ax.tick_params(colors=TINTA2)


def grafica_tiempo(filas, titulo, archivo, paso=10):
    """p95 por ventana de 10 s de T1 y T2 y usuarios activos (eje derecho)."""
    fin = max(r["seg"] for r in filas)
    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=150)
    for t, color in ((T1, AZUL), (T2, NARANJA)):
        xs, ys = [], []
        for i in range(int(fin // paso) + 1):
            v = [r["ms"] for r in filas if r["t"] == t and i * paso <= r["seg"] < (i + 1) * paso]
            if v:
                xs.append((i + 0.5) * paso / 60)
                ys.append(percentil(v, 95))
        ax.plot(xs, ys, color=color, lw=1.8, label=f"p95 {t}")
    ax.axhline(UMBRAL_P95, color=TINTA2, lw=1, ls="--")
    ax.annotate("umbral RNF-02: 2 000 ms", (0, UMBRAL_P95), textcoords="offset points", xytext=(4, 4),
                fontsize=8.5, color=TINTA2)
    estilo(ax, titulo, "p95 por ventana de 10 s (ms)")
    ax2 = ax.twinx()
    xs = [r["seg"] / 60 for r in filas]
    ax2.step(xs, [r["hilos"] for r in filas], where="post", color=GRIS, lw=1, alpha=0.8, label="Usuarios activos")
    ax2.set_ylabel("Usuarios activos", color=TINTA2)
    ax2.set_ylim(0, 60)
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(colors=TINTA2)
    techo = max(UMBRAL_P95 * 1.15, max(ax.get_ylim()[1], 1))
    ax.set_ylim(0, techo)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", fontsize=8.5, ncol=3)
    fig.tight_layout()
    fig.savefig(GRAFICAS / archivo)
    plt.close(fig)


def grafica_monitoreo(tp, titulo, archivo):
    if not tp:
        return
    t0 = tp[0]["hora"]
    xs = [(f["hora"] - t0).total_seconds() / 60 for f in tp]
    fig, ax = plt.subplots(figsize=(9, 4.0), dpi=150)
    for vals, color, etiqueta in (
            (serie(tp, "Processor(_Total)", "% Processor Time"), GRIS, "CPU total del equipo"),
            ([None if v is None else v / CPUS for v in serie(tp, "Process(CondorApi)", "% Processor Time")], AZUL, "CPU de CondorApi")):
        ax.plot(xs, [v if v is not None else float("nan") for v in vals], color=color, lw=1.4, label=etiqueta)
    estilo(ax, titulo, "% de CPU (20 hilos lógicos = 100 %)")
    ax2 = ax.twinx()
    mem = [None if v is None else v / 2**20 for v in serie(tp, "Process(CondorApi)", "Working Set - Private")]
    ax2.plot(xs, [v if v is not None else float("nan") for v in mem], color=VERDE, lw=1.4, ls="--", label="Memoria privada CondorApi (MB)")
    ax2.set_ylabel("MB", color=TINTA2)
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(colors=TINTA2)
    ax2.set_ylim(0, max([v for v in mem if v] + [100]) * 1.3)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", fontsize=8.5, ncol=2)
    fig.tight_layout()
    fig.savefig(GRAFICAS / archivo)
    plt.close(fig)


def grafica_comparacion(tabla, archivo):
    """p95 por ventana antes y después de la mejora (estrés y pico)."""
    etiquetas = [f"{e}\n{v}" for (e, v, t) in tabla if t == T2]
    if not etiquetas:
        return
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150, sharey=False)
    for ax, t in zip(axs, TRANSACCIONES):
        filas = [(e, v, d) for (e, v, tt), d in tabla.items() if tt == t]
        pos = range(len(filas))
        ancho = 0.38
        antes = [d.get("1_antes", {}).get("p95", 0) for _, _, d in filas]
        despues = [d.get("2_despues", {}).get("p95", 0) for _, _, d in filas]
        ax.bar([p - ancho / 2 for p in pos], antes, ancho, color=GRIS, label="Antes")
        ax.bar([p + ancho / 2 for p in pos], despues, ancho, color=AZUL, label="Después")
        for p, a, d in zip(pos, antes, despues):
            ax.annotate(num(a), (p - ancho / 2, a), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=7.5, color=TINTA2)
            ax.annotate(num(d), (p + ancho / 2, d), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=7.5, color=TINTA2)
        ax.axhline(UMBRAL_P95, color=TINTA2, lw=1, ls="--")
        estilo(ax, f"p95 de {t}", "ms", "")
        ax.set_xticks(list(pos))
        ax.set_xticklabels([f"{e}\n{v.split(' (')[0]}" for e, v, _ in filas], fontsize=7.5)
        ax.legend(frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(GRAFICAS / archivo)
    plt.close(fig)


def grafica_capacidad(comparacion, archivo):
    """Prueba de capacidad: p95 y throughput de T1 y T2 según los hilos sin pausas, antes y después."""
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), dpi=150)
    for fase, ls, marca in (("1_antes", "--", "o"), ("2_despues", "-", "s"), ("3_diagnostico_synchronous_commit_off", ":", "^")):
        for t, color in ((T1, AZUL), (T2, NARANJA)):
            puntos = [(u, comparacion.get((f"capacidad_{u}u", f"{u} hilos sin pausas (0:10-2:10)", t), {}).get(fase))
                      for u in CAPACIDAD]
            puntos = [(u, s) for u, s in puntos if s]
            if not puntos:
                continue
            etiqueta = f"{t.split(' ', 1)[0]} {({'1_antes': 'antes 1.1.1', '2_despues': 'después 1.1.2', '3_diagnostico_synchronous_commit_off': 'diagnóstico (solo 50 h)'})[fase]}"
            axs[0].plot([u for u, _ in puntos], [s["p95"] for _, s in puntos], color=color, ls=ls, marker=marca,
                        ms=6, mec="white", lw=1.8, label=etiqueta)
            axs[1].plot([u for u, _ in puntos], [s["throughput"] for _, s in puntos], color=color, ls=ls, marker=marca,
                        ms=6, mec="white", lw=1.8, label=etiqueta)
    estilo(axs[0], "p95 según los hilos sin pausas", "p95 (ms)", "Hilos concurrentes sin pausas")
    estilo(axs[1], "Throughput según los hilos sin pausas", "Peticiones por segundo", "Hilos concurrentes sin pausas")
    for ax in axs:
        ax.set_xticks(CAPACIDAD)
        ax.set_ylim(bottom=0)
        ax.legend(frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(GRAFICAS / archivo)
    plt.close(fig)


# ---------------------------------------------------------------- libro Excel

def hoja(libro, nombre, cabecera, filas, nota=None):
    ws = libro.create_sheet(nombre[:31])
    fila0 = 1
    if nota:
        ws.cell(1, 1, nota).font = Font(italic=True, color="52514E")
        fila0 = 3
    for j, c in enumerate(cabecera, 1):
        celda = ws.cell(fila0, j, c)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="2A78D6")
        celda.alignment = Alignment(wrap_text=True, vertical="center")
    for i, f in enumerate(filas, fila0 + 1):
        for j, v in enumerate(f, 1):
            celda = ws.cell(i, j, v)
            if isinstance(v, float):
                celda.number_format = "0.00"
    for j in range(1, len(cabecera) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 34 if j <= 3 else 13
    ws.freeze_panes = ws.cell(fila0 + 1, 1)
    return ws


def main():
    GRAFICAS.mkdir(exist_ok=True)
    libro = Workbook()
    libro.remove(libro.active)
    cab = ["Fase", "Escenario / ventana", "Transacción", "Muestras", "Media (ms)", "Mediana (ms)", "p90 (ms)",
           "p95 (ms)", "p99 (ms)", "Máx (ms)", "Errores", "Error %", "Throughput (/s)", "Cumple p95 ≤ 2 s", "Cumple error ≤ 1 %"]
    filas_libro, filas_mon, filas_err, filas_min = [], [], [], []
    comparacion = {}
    md = []

    for fase, nombre_fase in FASES.items():
        for esc in ESCENARIOS + [f"capacidad_{u}u" for u in CAPACIDAD]:
            carpeta = RESULTADOS / fase / esc
            if not (carpeta / "resultado.jtl").exists():
                continue
            filas = leer_jtl(carpeta / "resultado.jtl")
            md.append(f"\n### {nombre_fase} — {esc}\n")
            md.append("| Ventana | Transacción | n | Media | p90 | p95 | p99 | Máx | Error % | Thr/s |")
            md.append("|---|---|---|---|---|---|---|---|---|---|")
            for ventana, a, b in VENTANAS[esc]:
                sel = [r for r in filas if a <= r["seg"] < b]
                for t in TRANSACCIONES + ["Total (T1+T2)"]:
                    sub = [r for r in sel if r["t"] in TRANSACCIONES] if t.startswith("Total") else [r for r in sel if r["t"] == t]
                    s = resumir(sub)
                    if not s:
                        continue
                    filas_libro.append([nombre_fase, f"{esc}: {ventana}", t, s["n"], s["media"], s["mediana"], s["p90"],
                                        s["p95"], s["p99"], s["max"], s["errores"], s["error_pct"], s["throughput"],
                                        "Sí" if s["p95"] <= UMBRAL_P95 else "No",
                                        "Sí" if s["error_pct"] <= UMBRAL_ERROR else "No"])
                    md.append(f"| {ventana} | {t} | {s['n']} | {num(s['media'])} | {s['p90']} | {s['p95']} | {s['p99']} | "
                              f"{s['max']} | {num(s['error_pct'], 2)} | {num(s['throughput'], 2)} |")
                    if t in TRANSACCIONES:
                        comparacion.setdefault((esc, ventana, t), {})[fase] = s
            login = resumir([r for r in filas if r["t"] == LOGIN])
            if login:
                md.append(f"| (preparación) | 00 Ingresar | {login['n']} | {num(login['media'])} | {login['p90']} | "
                          f"{login['p95']} | {login['p99']} | {login['max']} | {num(login['error_pct'], 2)} | - |")
            # errores por código / mensaje
            for r in filas:
                if not r["ok"]:
                    filas_err.append([nombre_fase, esc, r["t"], round(r["seg"], 1), r["hilos"], r["responseCode"],
                                      (r["failureMessage"] or r["responseMessage"])[:200]])
            # estabilidad: minuto a minuto
            if esc == "estabilidad":
                for minuto in range(int(max(r["seg"] for r in filas) // 60) + 1):
                    for t in TRANSACCIONES:
                        s = resumir([r for r in filas if r["t"] == t and minuto * 60 <= r["seg"] < (minuto + 1) * 60])
                        if s:
                            filas_min.append([nombre_fase, minuto + 1, t, s["n"], s["media"], s["p95"], s["max"], s["error_pct"]])
            m, tp = resumir_monitoreo(carpeta)
            if m:
                filas_mon.append([nombre_fase, esc,
                                  m.get("cpu_total", (None,) * 2)[0], m.get("cpu_total", (None,) * 2)[1],
                                  m.get("cpu_api", (None,) * 2)[0], m.get("cpu_api", (None,) * 2)[1],
                                  m.get("cpu_java", (None,) * 2)[0], m.get("cpu_java", (None,) * 2)[1],
                                  m.get("mem_api", (None,) * 3)[0], m.get("mem_api", (None,) * 3)[1], m.get("mem_api", (None,) * 3)[2],
                                  m.get("hilos_api"), m.get("mem_libre_min"),
                                  m.get("cpu_pg", (None,) * 2)[0], m.get("cpu_pg", (None,) * 2)[1], m.get("mem_pg"),
                                  m.get("con_max"), m.get("activas_max"), m.get("bloqueo_max")])
            grafica_tiempo(filas, f"{nombre_fase} — {esc}: p95 de cada transacción y usuarios activos",
                           f"{fase}_{esc}_tiempos.png")
            grafica_monitoreo(tp, f"{nombre_fase} — {esc}: CPU y memoria (typeperf)", f"{fase}_{esc}_monitoreo.png")

    hoja(libro, "Transacciones", cab, filas_libro,
         "Percentiles por transacción y por ventana de tiempo. RNF-02 se evalúa en carga esperada: p95 ≤ 2 000 ms y error ≤ 1 % por transacción.")
    hoja(libro, "Monitoreo", ["Fase", "Escenario", "CPU total media %", "CPU total máx %", "CPU API media %", "CPU API máx %",
                              "CPU JMeter media %", "CPU JMeter máx %", "Mem API inicio MB", "Mem API fin MB", "Mem API máx MB",
                              "Hilos API máx", "Mem libre mín MB", "CPU PostgreSQL media %", "CPU PostgreSQL máx %",
                              "Mem PostgreSQL máx MiB", "Conexiones API máx", "Activas máx", "En espera de bloqueo máx"],
         filas_mon, "typeperf cada 2 s (CPU por proceso dividida entre 20 hilos lógicos) y docker stats + pg_stat_activity cada 5 s.")
    hoja(libro, "Errores", ["Fase", "Escenario", "Transacción", "Segundo", "Usuarios activos", "Código", "Mensaje"], filas_err,
         "Cada muestra fallida del .jtl (código HTTP inesperado, aserción JSON fallida o tiempo de espera superado).")
    hoja(libro, "Estabilidad por minuto", ["Fase", "Minuto", "Transacción", "Muestras", "Media (ms)", "p95 (ms)", "Máx (ms)", "Error %"],
         filas_min, "Escenario de estabilidad minuto a minuto: una tendencia creciente indicaría degradación dentro de los 15 min.")
    filas_cmp = []
    for (esc, ventana, t), d in comparacion.items():
        a, b = d.get("1_antes"), d.get("2_despues")
        if a and b:
            filas_cmp.append([esc, ventana, t, a["p95"], b["p95"], 100 * (b["p95"] - a["p95"]) / max(1, a["p95"]),
                              a["error_pct"], b["error_pct"], a["throughput"], b["throughput"]])
    hoja(libro, "Antes vs después", ["Escenario", "Ventana", "Transacción", "p95 antes (ms)", "p95 después (ms)", "Variación p95 %",
                                     "Error % antes", "Error % después", "Thr/s antes", "Thr/s después"], filas_cmp,
         "Mismas condiciones (plan, datos, base reiniciada, API recién arrancada); solo cambia la mejora de 05_Cuello_de_Botella.")
    if filas_cmp:
        grafica_comparacion({k: v for k, v in comparacion.items() if k[0] in ("estres", "pico", "carga") and len(v) == 2},
                            "comparacion_antes_despues_p95.png")
    grafica_capacidad(comparacion, "capacidad_p95_throughput.png")
    libro.save(AQUI / "resumen_resultados.xlsx")

    print("\n".join(md))
    print("\n### Monitoreo\n")
    print("| Fase | Escenario | CPU total media/máx | CPU API media/máx | CPU JMeter máx | Mem API ini/fin/máx MB | CPU PG media/máx | Conex. máx | Activas máx | Esperando bloqueo máx |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for f in filas_mon:
        print(f"| {f[0]} | {f[1]} | {num(f[2], 1)} / {num(f[3], 1)} | {num(f[4], 1)} / {num(f[5], 1)} | {num(f[7], 1)} | "
              f"{num(f[8])} / {num(f[9])} / {num(f[10])} | {num(f[13], 1)} / {num(f[14], 1)} | {num(f[16])} | {num(f[17])} | {num(f[18])} |")
    if filas_cmp:
        print("\n### Antes vs después (p95 ms)\n")
        for f in filas_cmp:
            print(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {num(f[5], 1)} % | {num(f[6], 2)} | {num(f[7], 2)} | {num(f[8], 2)} | {num(f[9], 2)} |")
    print(f"\nErrores registrados: {len(filas_err)}. Libro: {AQUI / 'resumen_resultados.xlsx'}")


if __name__ == "__main__":
    main()
