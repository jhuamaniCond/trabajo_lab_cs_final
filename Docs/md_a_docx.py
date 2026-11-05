# -*- coding: utf-8 -*-
"""
md_a_docx.py
Inserta en el informe secciones de los documentos Markdown de cada guía
(G01 a G09) sin copiarlas a mano: el informe queda sincronizado con la
evidencia. Convierte párrafos, listas, tablas, citas e imágenes; los bloques
de código no se copian como texto (regla de la skill): se deja la referencia
al archivo.

Uso:
    from md_a_docx import seccion_md, tabla_md
    seccion_md(doc, "G04_Dimensionamiento/02_Memoria/memoria_calculo.md", "2. Conteo NESMA")
    tabla_md(doc, "G06_.../matriz_riesgos.md", "3. Escenarios")       # solo la 1.ª tabla
"""

import os
import re

from comun import RAIZ, seccion_horizontal, seccion_vertical

ANCHO_V = 16.0       # ancho útil vertical (cm)
ANCHO_H = 25.7       # ancho útil horizontal (cm)
COLS_HORIZONTAL = 10  # desde cuántas columnas la tabla va en página horizontal

_RE_TITULO = re.compile(r"^(#{1,6})\s+(.*)$")
_RE_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+\.)\s+(.*)$")
_RE_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_RE_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_RE_SUB = re.compile(r"(?<![\w`*])_([^_`\n]+?)_(?![\w`])")


def _limpiar(texto):
    t = _RE_IMG.sub(r"\1", texto)
    t = _RE_LINK.sub(r"\1", t)
    t = t.replace("\\|", "|").replace("<br>", " ").replace("<br/>", " ")
    t = _RE_SUB.sub(r"*\1*", t)
    t = t.replace("&nbsp;", " ")
    return t.strip()


# Reescrituras que aplica quien inserta (p. ej. el informe final) sin tocar el
# Markdown de la guía: lista de (patrón, reemplazo); reemplazo None = quitar la línea.
FILTROS = []


def _filtrar(lineas):
    salida = []
    for l in lineas:
        for patron, repl in FILTROS:
            if re.search(patron, l):
                if repl is None:
                    l = None
                    break
                l = re.sub(patron, repl, l)
        if l is not None:
            salida.append(l)
    return salida


def _leer(rel):
    ruta = os.path.join(RAIZ, *rel.split("/"))
    with open(ruta, encoding="utf-8") as f:
        return ruta, _filtrar(f.read().splitlines())


def _norm(s):
    s = re.sub(r"[*`_]", "", s).strip().lower()
    return s


def _cortar(lineas, encabezado):
    """Devuelve (nivel, líneas) de la sección cuyo título empieza por `encabezado`."""
    buscado = _norm(encabezado)
    en_codigo = False
    for i, l in enumerate(lineas):
        if l.strip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if en_codigo:
            continue
        m = _RE_TITULO.match(l)
        if m and _norm(m.group(2)).startswith(buscado):
            nivel = len(m.group(1))
            cuerpo = []
            codigo = False
            for l2 in lineas[i + 1:]:
                if l2.strip().startswith("```"):
                    codigo = not codigo
                m2 = _RE_TITULO.match(l2)
                if not codigo and m2 and len(m2.group(1)) <= nivel:
                    break
                cuerpo.append(l2)
            return nivel, cuerpo
    raise KeyError("No se encontró «%s»" % encabezado)


def _celdas(linea):
    l = linea.strip()
    if l.startswith("|"):
        l = l[1:]
    if l.endswith("|"):
        l = l[:-1]
    partes = re.split(r"(?<!\\)\|", l)
    return [_limpiar(p) for p in partes]


def _es_separador(linea):
    return re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", linea) is not None


def _anchos(filas, total):
    n = len(filas[0])
    pesos = []
    for j in range(n):
        largo = max(len(re.sub(r"[*`]", "", f[j])) if j < len(f) else 0 for f in filas)
        pesos.append(max(4, min(largo, 70)) ** 0.75)
    s = sum(pesos)
    anchos = [max(1.3, total * p / s) for p in pesos]
    factor = total / sum(anchos)
    return [a * factor for a in anchos]


def poner_tabla(doc, filas):
    n = max(len(f) for f in filas)
    filas = [f + [""] * (n - len(f)) for f in filas]
    if n >= COLS_HORIZONTAL:
        seccion_horizontal(doc)
        doc.tabla(filas, anchos_cm=_anchos(filas, ANCHO_H))
        seccion_vertical(doc)
    else:
        doc.tabla(filas, anchos_cm=_anchos(filas, ANCHO_V))


def _bloques(cuerpo):
    """Agrupa las líneas en bloques: ('p', texto) ('lista', items, numerada)
    ('tabla', filas) ('img', alt, ruta) ('titulo', nivel, texto) ('codigo',)"""
    bloques = []
    i = 0
    while i < len(cuerpo):
        l = cuerpo[i]
        s = l.strip()
        if not s or s in ("---", "***"):
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            while i < len(cuerpo) and not cuerpo[i].strip().startswith("```"):
                i += 1
            i += 1
            bloques.append(("codigo",))
            continue
        m = _RE_TITULO.match(l)
        if m:
            bloques.append(("titulo", len(m.group(1)), _limpiar(m.group(2))))
            i += 1
            continue
        if s.startswith("|"):
            filas = []
            imgs = []
            while i < len(cuerpo) and cuerpo[i].strip().startswith("|"):
                if not _es_separador(cuerpo[i]):
                    imgs += _RE_IMG.findall(cuerpo[i])
                    filas.append(_celdas(cuerpo[i]))
                i += 1
            bloques.append(("tabla", filas))
            # imágenes dentro de celdas (p. ej. mockups del SDD): van debajo de la tabla
            for alt, ruta_img in imgs:
                bloques.append(("img", alt, ruta_img))
            continue
        mi = _RE_IMG.fullmatch(s)
        if mi:
            bloques.append(("img", mi.group(1), mi.group(2)))
            i += 1
            continue
        if _RE_ITEM.match(l):
            items = []
            numerada = bool(re.match(r"^\s*\d+\.", l))
            while i < len(cuerpo):
                l2 = cuerpo[i]
                m2 = _RE_ITEM.match(l2)
                if m2:
                    sangria = len(m2.group(1))
                    texto = m2.group(2)
                    items.append(("— " if sangria >= 2 else "") + texto)
                    i += 1
                elif l2.strip() and (l2.startswith("  ") or l2.startswith("\t")) and items \
                        and not l2.strip().startswith("|") and not l2.strip().startswith("```"):
                    items[-1] += " " + l2.strip()
                    i += 1
                elif not l2.strip():
                    # una línea en blanco entre ítems no corta la lista
                    if i + 1 < len(cuerpo) and _RE_ITEM.match(cuerpo[i + 1]):
                        i += 1
                    else:
                        break
                else:
                    break
            bloques.append(("lista", [_limpiar(t) for t in items], numerada))
            continue
        # párrafo (o cita)
        texto = []
        while i < len(cuerpo):
            l2 = cuerpo[i].strip()
            if not l2 or l2.startswith("|") or l2.startswith("```") or _RE_TITULO.match(cuerpo[i]) \
                    or _RE_ITEM.match(cuerpo[i]) or _RE_IMG.fullmatch(l2):
                break
            l2 = re.sub(r"^>\s?", "", l2)
            l2 = re.sub(r"^#{1,6}\s+", "", l2)
            texto.append(l2)
            i += 1
        if texto:
            bloques.append(("p", _limpiar(" ".join(texto))))
        else:
            i += 1
    return bloques


def _pintar(doc, bloques, base_dir, nivel_base, imagenes=True, tablas=True):
    for b in bloques:
        if b[0] == "p":
            if b[1]:
                doc.parrafo(b[1])
        elif b[0] == "lista":
            (doc.numerada if b[2] else doc.vinetas)(b[1])
        elif b[0] == "tabla" and tablas:
            if b[1]:
                poner_tabla(doc, b[1])
        elif b[0] == "titulo":
            doc.parrafo("**%s**" % b[2].replace("**", ""))
        elif b[0] == "img" and imagenes:
            ruta = os.path.normpath(os.path.join(base_dir, b[2]))
            if os.path.exists(ruta):
                doc.imagen_auto(ruta, b[1] or os.path.basename(ruta))


def seccion_md(doc, rel, encabezado, imagenes=True, tablas=True, omitir=()):
    """Inserta el contenido de la sección `encabezado` del archivo `rel`.
    `omitir`: textos de subtítulos cuyo contenido no se copia."""
    ruta, lineas = _leer(rel)
    nivel, cuerpo = _cortar(lineas, encabezado)
    bloques = _bloques(cuerpo)
    if omitir:
        filtrados, saltar = [], None
        for b in bloques:
            if b[0] == "titulo":
                saltar = b[1] if any(_norm(b[2]).startswith(_norm(o)) for o in omitir) else None
                if saltar:
                    continue
            elif saltar:
                continue
            filtrados.append(b)
        bloques = filtrados
    _pintar(doc, bloques, os.path.dirname(ruta), nivel, imagenes, tablas)


def tabla_md(doc, rel, encabezado, n=1):
    """Inserta solo la n-ésima tabla de la sección."""
    _, lineas = _leer(rel)
    _, cuerpo = _cortar(lineas, encabezado)
    k = 0
    for b in _bloques(cuerpo):
        if b[0] == "tabla":
            k += 1
            if k == n:
                poner_tabla(doc, b[1])
                return b[1]
    raise KeyError("Sin tabla %d en «%s»" % (n, encabezado))


def filas_md(rel, encabezado, n=1):
    _, lineas = _leer(rel)
    _, cuerpo = _cortar(lineas, encabezado)
    k = 0
    for b in _bloques(cuerpo):
        if b[0] == "tabla":
            k += 1
            if k == n:
                return b[1]
    raise KeyError(encabezado)


def archivo_md(doc, rel, desde_nivel=2, omitir=(), imagenes=True):
    """Inserta todo el archivo desde el primer título de nivel `desde_nivel`."""
    ruta, lineas = _leer(rel)
    i0 = 0
    for i, l in enumerate(lineas):
        m = _RE_TITULO.match(l)
        if m and len(m.group(1)) == desde_nivel:
            i0 = i
            break
    bloques = _bloques(lineas[i0:])
    if omitir:
        filtrados, saltar = [], False
        for b in bloques:
            if b[0] == "titulo":
                saltar = any(_norm(b[2]).startswith(_norm(o)) for o in omitir)
                if saltar:
                    continue
            elif saltar:
                continue
            filtrados.append(b)
        bloques = filtrados
    _pintar(doc, bloques, os.path.dirname(ruta), desde_nivel - 1, imagenes)
