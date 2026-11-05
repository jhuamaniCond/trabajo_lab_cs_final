# -*- coding: utf-8 -*-
"""
generar_matriz_trazabilidad.py
Matriz de trazabilidad obligatoria (sección 13 del enunciado) como documento
propio: una fila por requisito, ampliada con una fila por prueba.

    python Docs/generar_matriz_trazabilidad.py
"""

import os
from collections import Counter

from comun import (Documento, SALIDA, PRODUCTO, VERSION, ETIQUETA, portada,
                   indice, pie_paginado, seccion_horizontal, informar)
from datos_trazabilidad import REQUISITOS

ANCHO = 25.7    # ancho útil en A4 horizontal con márgenes de 2 cm

CAMBIOS = [
    ["CC-01", "Ingreso con usuario, contraseña y roles; backend REST; reporte consolidado",
     "RF-01, RF-02, RF-03, RF-07, RF-15, RNF-02, RNF-03", "Aprobada e implementada",
     "Producto 1.1.0 (importado en r2)", "Suite 923/0/5; regresión G07 R1 (1.0.0) y R2 (1.1.1)"],
    ["CC-02", "Descuento manual del vendedor en la línea de venta",
     "RF-07, CRQ-07, CFL-03", "Rechazada con sustento (contradice CRQ-07 y eleva R03)",
     "—", "—"],
    ["CC-03", "Portal web del mostrador para Selenium (INT-07)",
     "RF-01 a RF-08, RF-11, RF-12, RF-14, RF-15", "Aprobada e implementada",
     "Rama CC-03 r28–r31, trunk r32 (1.2.0)", "PortalWebTests (11); Selenium 14/14"],
    ["DEF-01", "La ruta de escritorio guardaba el precio enviado por la PC (CRQ-07)",
     "RF-07", "Mayor · cerrado", "Rama DEF-01 r8–r10, fusión con conflicto r11 (1.1.1)",
     "ClienteApiTests (3 de DEF-01 y 4 de CRQ-14)"],
    ["DEF-02", "Defecto controlado: «>» cambiado por «>=» en la regla de S/ 700",
     "RF-07, CRQ-02", "Controlado · restaurado", "Parche G07/04_Defecto_Controlado",
     "PU-13 falla (D1) y pasa al restaurar (D2)"],
    ["MEJ-01", "Correlativo de la serie reservado al final de la emisión",
     "RNF-02, RNF-04", "Implementada (mejora parcial)", "Rama MEJ-01, r23–r25 (1.1.2)",
     "MEJ01_CorrelativoAlFinalTests; G08 antes y después"],
    ["DEF-03", "La lista de Compras mostraba 0 líneas", "RF-12", "Menor · cerrado", "r31",
     "CP-13 en r31 y regresión r32"],
    ["DEF-04", "Aviso de la emisión anterior visible al convertir proforma", "RF-08",
     "Menor · cerrado", "r31", "CP-10 en r31 y regresión r32"],
    ["DEF-06", "Falla intermitente de la suite en CP-10 (elemento obsoleto)", "— (suite)",
     "Menor · cerrado", "Suite G09", "CP-10 en las 7 ejecuciones siguientes"],
    ["DEF-07", "CP-13 registraba dos veces cemento", "RF-12 (dato de la prueba)",
     "Menor · cerrado", "Suite G09", "CP-13 en r32_final-3, r32_final-4, r32_edge-2"],
]


def construir():
    doc = Documento(figuras=[])
    portada(doc, "MATRIZ DE TRAZABILIDAD",
            "Requisito → diseño → código → prueba → resultado",
            extra=["Línea base de requisitos: ERS 1.2 (16 RF y 8 RNF)",
                   "Responsables: analistas del equipo (los cuatro integrantes); "
                   "consolidó el Integrante 1"])
    indice(doc)

    doc.titulo(1, "1. Propósito y alcance")
    doc.parrafo(
        "Este documento es la matriz de trazabilidad obligatoria del trabajo final. Une cada "
        "requisito de la línea base vigente (ERS 1.2) con su fuente, el objetivo de negocio que "
        "atiende, los elementos de diseño y de código que lo implementan, los riesgos de G06 que "
        "lo afectan, los cambios y defectos que lo tocaron y **todas** las pruebas que lo "
        "verifican, con la evidencia, la versión probada y el resultado.")
    doc.parrafo(
        "El enunciado exige cubrir 10 RF y 5 RNF como mínimo. La línea base final del producto "
        "tiene **16 RF y 8 RNF**, y la matriz los cubre todos. Hay una fila por requisito en la "
        "matriz resumen (sección 3) y una fila por prueba en la matriz detallada (sección 4).")
    doc.tabla([
        ["Campo", "Valor"],
        ["Producto", "%s %s" % (PRODUCTO, VERSION)],
        ["Versión entregada", "SVN %s; producto probado en trunk r32" % ETIQUETA],
        ["Línea base de requisitos", "ERS 1.2 (`G01_Requerimientos/01_ERS/ERS_Condor_v1.2.md`)"],
        ["Fuente de los datos", "`Docs/datos_trazabilidad.py`, que cita el archivo de origen de cada columna"],
        ["Fecha de corte", "4 de noviembre de 2026"],
    ], anchos_cm=[4.5, 11.5])

    doc.titulo(1, "2. Cómo leer la matriz")
    doc.tabla([
        ["Tipo de prueba", "Qué es", "Dónde está la evidencia"],
        ["Unitaria G07", "Casos PU-01 a PU-27 sobre cinco componentes de `Condor.Dominio`",
         "`G07_Pruebas_Unitarias` (catálogo, reportes .trx/HTML y cobertura)"],
        ["xUnit producto", "Suite del producto `tests/Condor.Pruebas` (unitarias, integración y aceptación por historia)",
         "`G09_Gestion_Calidad/04_Reportes/xunit_1.2.0-r32`"],
        ["Control G06", "Comprobación de las salvaguardas S1, S2 y S3 contra el sistema en ejecución",
         "`G06_Gestion_Riesgos/04_Controles/verificacion_controles.md`"],
        ["Rendimiento G08", "Escenarios JMeter de carga, estrés, pico, estabilidad y capacidad",
         "`G08_Pruebas_Rendimiento/04_Resultados` y `06_Analisis`"],
        ["Selenium G09", "Casos web CP-01 a CP-14 sobre el portal del mostrador",
         "`G09_Gestion_Calidad/04_Reportes` (HTML, JUnit XML, JSON y capturas)"],
        ["Medición", "Observación o demostración manual (sin automatización)",
         "Ficha OBS-01 de G01 o sustentación"],
    ], anchos_cm=[3.2, 7.0, 5.8])
    doc.parrafo(
        "Procesos de negocio: **PN-01** Venta y facturación electrónica, **PN-02** Cotización y "
        "conversión en venta, **PN-03** Abastecimiento. Objetivos: OBJ-01 agilizar la venta, OBJ-02 "
        "cumplir con la facturación electrónica, OBJ-03 controlar el acceso y la trazabilidad, "
        "OBJ-04 ordenar el abastecimiento, OBJ-05 disponer de información consolidada, OBJ-06 "
        "proteger la información del negocio.")

    # ------------------------------------------------------------- resumen
    seccion_horizontal(doc)
    doc.titulo(1, "3. Matriz resumen: una fila por requisito")
    filas = [["ID", "Requisito", "Proceso · prioridad", "Fuente · objetivo",
              "Diseño y código (SDD §7)", "Riesgo (G06)", "Cambios / defectos", "Estado en 1.2.0"]]
    for r in REQUISITOS:
        pend = any("Pendiente" in t[4] for t in r["pruebas"])
        if r["id"].startswith("RNF"):
            estado = "Cumple con observación (O-4)" if r["id"] == "RNF-06" else "Cumple"
        else:
            estado = "Verificado (xUnit); demostrar en la app (O-7)" if pend else "Verificado"
        filas.append([r["id"], r["nombre"], "%s · %s" % (r["proceso"], r["prioridad"]),
                      "%s · %s" % (r["fuente"], r["objetivo"]), r["diseno"], r["riesgo"],
                      r["cambio"], estado])
    doc.tabla(filas, anchos_cm=[1.4, 3.2, 2.4, 3.4, 6.6, 2.2, 3.1, 3.4])

    # ------------------------------------------------------------ detallada
    doc.titulo(1, "4. Matriz detallada: una fila por prueba")
    doc.parrafo(
        "Cada requisito ocupa tantas filas como pruebas lo verifican. La columna «Versión» indica "
        "sobre qué versión del producto se obtuvo el resultado: 1.1.1 (trunk r22, G06 a G08), 1.1.2 "
        "(r25, después de MEJ-01) o 1.2.0 (trunk r32, regresión final de G09).")
    filas = [["Requisito", "Tipo", "Prueba (ID o clase)", "Evidencia", "Versión", "Resultado"]]
    for r in REQUISITOS:
        for i, (tipo, ident, evid, ver, res) in enumerate(r["pruebas"]):
            filas.append(["**%s** %s" % (r["id"], r["nombre"]) if i == 0 else "",
                          tipo, ident, evid, ver, res])
    doc.tabla(filas, anchos_cm=[4.0, 2.6, 7.6, 6.3, 2.2, 3.0])

    # ------------------------------------------------------------ cobertura
    doc.titulo(1, "5. Cobertura de la matriz")
    tipos = Counter()
    req_con = Counter()
    for r in REQUISITOS:
        vistos = set()
        for t in r["pruebas"]:
            tipos[t[0]] += 1
            vistos.add(t[0])
        for v in vistos:
            req_con[v] += 1
    orden = ["Unitaria G07", "xUnit producto", "Control G06", "Rendimiento G08",
             "Selenium G09", "Medición"]
    filas = [["Tipo de prueba", "Filas en la matriz", "Requisitos que cubre (de 24)"]]
    for o in orden:
        filas.append([o, str(tipos[o]), str(req_con[o])])
    filas.append(["**Total**", "**%d**" % sum(tipos.values()), "**24 de 24 con al menos una prueba aprobada**"])
    doc.tabla(filas, anchos_cm=[6.0, 5.0, 14.7])
    doc.vinetas([
        "**24 de 24 requisitos** tienen al menos una prueba automatizada aprobada en la versión evaluada "
        "(criterio C1 del dictamen de G09).",
        "**20 de 24** se verifican además por una vía independiente de la suite xUnit (G06, G07, G08 o G09).",
        "RF-09, RF-10 y RF-13 solo tienen verificación automática con xUnit, porque la ticketera, la SUNAT y "
        "las guías están únicamente en la app de escritorio. Se demuestran en la sustentación (observación O-7).",
        "RNF-06 cumple con observación: la automatización mide 1,2–1,8 s de sistema y 0 clics, pero falta "
        "cronometrar a un vendedor real con la versión 1.2.0 (O-4).",
    ])

    # -------------------------------------------------------------- cambios
    doc.titulo(1, "6. Trazabilidad de cambios, mejoras y defectos")
    doc.tabla([["ID", "Descripción", "Requisitos afectados", "Decisión / severidad · estado",
                "Revisión SVN / versión", "Prueba de cierre"]] + CAMBIOS,
              anchos_cm=[1.5, 6.6, 4.4, 4.2, 4.5, 4.5])
    doc.parrafo(
        "Los recorridos de las peticiones en Redmine (registrado → analizado → aprobado → "
        "implementado → verificado → cerrado) están en `G02_Proceso_Requerimientos/05_Seguimiento`; "
        "las revisiones, ramas y etiquetas en `G05_Gestion_Configuracion/04_Evidencias/historial_svn.txt`; "
        "y el detalle de cada defecto de G09 en `G09_Gestion_Calidad/05_Defectos/registro_defectos.md`.")

    doc.titulo(1, "7. Conclusión")
    doc.parrafo(
        "Todos los requisitos de la línea base final pueden seguirse desde su fuente de elicitación "
        "hasta una prueba ejecutada y aprobada en la versión entregada. Los únicos huecos son de "
        "**vía de verificación**, no de verificación: tres requisitos que solo existen en la app de "
        "escritorio no tienen prueba web y un requisito de usabilidad falta medir con un usuario real. "
        "Ambos quedan como observaciones O-7 y O-4 del dictamen de liberación, con responsable y plazo.")

    pie_paginado(doc, "Matriz de trazabilidad — Sistema Cóndor %s" % VERSION)
    os.makedirs(SALIDA, exist_ok=True)
    salida = os.path.join(SALIDA, "Matriz_Trazabilidad_Condor.docx")
    doc.guardar(salida)
    informar(salida)


if __name__ == "__main__":
    construir()
