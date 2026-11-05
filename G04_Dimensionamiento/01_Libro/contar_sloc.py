"""Cuenta las líneas lógicas de código (sin blancos ni comentarios) del producto,
por proyecto y lenguaje. Es el tamaño real que usa la hoja Parámetros.

    python contar_sloc.py ..\\..\\Sistema_Logistico_Condor_final
"""
import os
import sys
from collections import Counter

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "..", "Sistema_Logistico_Condor_final")
OMITIR = {"bin", "obj", ".ejecutar", "TestResults"}


def lineas(ruta, ext):
    n, bloque = 0, False
    with open(ruta, encoding="utf-8", errors="ignore") as f:
        for linea in f:
            s = linea.strip()
            if not s:
                continue
            if ext == ".cs":
                if bloque:
                    bloque = "*/" not in s
                    continue
                if s.startswith("/*"):
                    bloque = "*/" not in s
                    continue
                if s.startswith("//"):
                    continue
            if ext == ".sql" and s.startswith("--"):
                continue
            if ext == ".xaml" and s.startswith("<!--"):
                continue
            n += 1
    return n


for carpeta, exts in [("src", {".cs", ".xaml"}), ("db/migraciones", {".sql"}), ("tests", {".cs"})]:
    total = Counter()
    for d, ds, fs in os.walk(os.path.join(RAIZ, carpeta)):
        ds[:] = [x for x in ds if x not in OMITIR]
        proyecto = os.path.relpath(d, os.path.join(RAIZ, carpeta)).split(os.sep)[0]
        for f in fs:
            ext = os.path.splitext(f)[1]
            if ext in exts:
                total[(proyecto, ext)] += lineas(os.path.join(d, f), ext)
    for (p, ext), n in sorted(total.items()):
        print(f"{carpeta}/{p} {ext}: {n}")
