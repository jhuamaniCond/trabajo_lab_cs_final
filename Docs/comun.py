# -*- coding: utf-8 -*-
"""
comun.py
Utilidades compartidas por los guiones que generan los documentos finales
(informe, manuales y matriz de trazabilidad) con docx_builder.py.

Cada documento declara tres diccionarios:
  FIGURAS : clave -> (ruta relativa a la raiz del trabajo, leyenda, ancho_cm)
  PASOS   : clave -> pasos para tomar la captura si el archivo no existe
  PROMPTS : clave -> prompt para dibujarla si no es una captura
y llama a figura(doc, clave, ...) en el punto exacto donde va la figura.
"""

import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/informes-docx"))
from docx_builder import Documento  # noqa: E402,F401

from docx.enum.section import WD_ORIENT, WD_SECTION  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt  # noqa: E402

DOCS = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(DOCS)                      # carpeta "Trabajo Grupal"
SALIDA = os.path.join(DOCS, "salida")
FIG_CODIGO = os.path.join(DOCS, "figuras")

PRODUCTO = "Sistema de Ventas y Facturación Cóndor"
CLIENTE = "Ferretería Cóndor Majes S.A.C."
VERSION = "1.2.0"
ETIQUETA = "tags/v1.0.1 (r44)"
FECHA = "4 de noviembre de 2026"

INTEGRANTES = [
    ("Huamani Condori, Jeanpiero Sixto", "G01, G07, dictamen de G09",
     "Coordinación del proyecto, cronograma y entregas"),
    ("Payehuanca Riquelme, Jhastyn Jefferson", "G02, G05, suite de G09",
     "Comité de cambios y repositorio SVN"),
    ("Condo Zamata, Richard Alberto", "G03, G08",
     "Diseño (SDD, UML) y rendimiento"),
    ("Chaisa Fernández, Anthony Leonel", "G04, G06",
     "Estimación y riesgos"),
]

PENDIENTES = []          # figuras que no se pudieron colocar (se imprimen al final)


def ruta(rel):
    return os.path.join(RAIZ, *rel.split("/"))


def figura(doc, clave, FIGURAS, PASOS=None, PROMPTS=None):
    """Inserta la imagen si existe; si no, deja en rojo el prompt o los pasos."""
    PASOS = PASOS or {}
    PROMPTS = PROMPTS or {}
    rel, leyenda, ancho = FIGURAS[clave]
    archivo = ruta(rel) if not os.path.isabs(rel) else rel
    if os.path.exists(archivo):
        doc.imagen(archivo, ancho_cm=ancho, leyenda=leyenda, etiqueta=clave)
        return
    PENDIENTES.append(clave)
    if clave in PROMPTS:
        doc.parrafo("[FIGURA PENDIENTE — generar con este prompt y guardarla en `%s`]"
                    % rel, rojo=True)
        doc.parrafo(PROMPTS[clave], rojo=True)
    elif clave in PASOS:
        doc.parrafo("[CAPTURA PENDIENTE — guardarla en `%s`. Pasos:]" % rel, rojo=True)
        doc.numerada(PASOS[clave], rojo=True)
    else:
        doc.parrafo("[Falta la figura `%s`]" % rel, rojo=True)
    doc._leyenda(leyenda, clave)


def portada(doc, titulo, subtitulo, extra=None):
    doc.espacio(30)
    doc.titulo_portada("UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA")
    doc.titulo_portada("Facultad de Ingeniería de Producción y Servicios")
    doc.titulo_portada("Escuela Profesional de Ingeniería de Sistemas", espacio_despues=36)
    doc.titulo_portada("Calidad de Software — Laboratorio, semestre 2026-B",
                       negrita=False, espacio_despues=36)
    doc.titulo_portada(titulo, espacio_despues=10)
    doc.titulo_portada(subtitulo, negrita=False, espacio_despues=10)
    doc.titulo_portada("%s — %s" % (PRODUCTO, CLIENTE), negrita=False,
                       espacio_despues=6)
    doc.titulo_portada("Versión del producto %s · etiqueta SVN %s" % (VERSION, ETIQUETA),
                       negrita=False, espacio_despues=36)
    if extra:
        for linea in extra:
            doc.titulo_portada(linea, negrita=False)
        doc.espacio(12)
    doc.titulo_portada("Integrantes", espacio_despues=6)
    for nombre, _, _ in INTEGRANTES:
        doc.titulo_portada(nombre, negrita=False, espacio_despues=2)
    doc.espacio(24)
    doc.titulo_portada("Docente: José Rafael Delgado Bastidas", negrita=False)
    doc.titulo_portada("Arequipa, %s" % FECHA, negrita=False)
    doc.salto_pagina()


def indice(doc, titulo="Índice"):
    """Campo TOC de Word: se rellena al abrir el documento (F9) o al exportar
    a PDF con exportar_pdf.py, que actualiza los campos."""
    doc.parrafo("**%s**" % titulo, espacio_despues=12)
    p = doc.doc.add_paragraph()
    run = p.add_run()
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    texto = OxmlElement("w:t")
    texto.text = "Actualice el índice con clic derecho > Actualizar campo (F9)."
    fin = OxmlElement("w:fldChar")
    fin.set(qn("w:fldCharType"), "end")
    for el in (inicio, instr, sep, texto, fin):
        run._r.append(el)
    doc.salto_pagina()


def pie_paginado(doc, texto):
    """Pie de página con el nombre del documento y el número de página."""
    for seccion in doc.doc.sections:
        pie = seccion.footer
        p = pie.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.text = ""
        r = p.add_run(texto + " — página ")
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r2 = p.add_run()
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)
        for tipo, txt in (("begin", None), ("instr", "PAGE"), ("end", None)):
            if tipo == "instr":
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = txt
            else:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), tipo)
            r2._r.append(el)


def seccion_horizontal(doc):
    """Abre una sección A4 horizontal (para tablas anchas)."""
    sec = doc.doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width = Cm(29.7)
    sec.page_height = Cm(21.0)
    for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, lado, Cm(2.0))
    return sec


def seccion_vertical(doc):
    sec = doc.doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, lado, Cm(2.5))
    return sec


def informar(ruta_docx):
    print("Generado:", ruta_docx)
    if PENDIENTES:
        print("  Figuras pendientes (%d): %s" % (len(PENDIENTES), ", ".join(PENDIENTES)))
    else:
        print("  Todas las figuras quedaron incrustadas.")


class DocumentoInforme(Documento):
    """Documento con numeración de figuras dinámica: la etiqueta recibe su
    número la primera vez que se cita o se inserta (en el informe cada cita
    va justo antes de su figura, así que el orden coincide)."""

    def __init__(self):
        Documento.__init__(self, figuras=[])
        self._auto = 0

    def fig(self, etiqueta):
        if etiqueta not in self._figuras:
            self._figuras[etiqueta] = len(self._figuras) + 1
        return str(self._figuras[etiqueta])

    def imagen_auto(self, ruta, leyenda, ancho_cm=None):
        """Inserta una imagen tomada de un documento Markdown de la guía."""
        self._auto += 1
        etiqueta = "auto_%d" % self._auto
        if ancho_cm is None:
            try:
                from PIL import Image
                with Image.open(ruta) as im:
                    w, h = im.size
                ancho_cm = 12.0 if h / float(w) < 1.0 else (9.0 if h / float(w) < 1.6 else 6.5)
            except Exception:
                ancho_cm = 15.0
        self.imagen(ruta, ancho_cm=ancho_cm, leyenda=leyenda.rstrip(".") + ".", etiqueta=etiqueta)
