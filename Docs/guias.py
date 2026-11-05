# -*- coding: utf-8 -*-
"""
guias.py
Sección 5 del informe final: desarrollo extenso de G01 a G09.

Cada guía sigue la estructura de los adjuntos (objetivo, procedimiento,
resultados, análisis, conclusiones) más herramienta y versión, evidencias,
requisitos, limitaciones y el cuestionario de la guía. El contenido detallado
se toma de los documentos Markdown de cada carpeta con md_a_docx, así que el
informe no se desincroniza de la evidencia.
"""

import os

import openpyxl

from comun import ruta
from md_a_docx import seccion_md, tabla_md, archivo_md, poner_tabla

# --------------------------------------------------------------- utilidades
_DOC = None


def cap(rel, leyenda, ancho=15):
    """Inserta una captura de la evidencia con leyenda numerada."""
    archivo = ruta(rel)
    if os.path.exists(archivo):
        _DOC.imagen_auto(archivo, leyenda, ancho_cm=min(ancho, 15) * 0.72)
    else:
        _DOC.parrafo("[Falta la imagen `%s`]" % rel, rojo=True)


def ficha(filas):
    _DOC.tabla([["Campo", "Contenido"]] + filas, anchos_cm=[4.2, 11.8])


def sub(texto):
    _DOC.titulo(3, texto)


def p(texto, **kw):
    _DOC.parrafo(texto, **kw)


def lista(items):
    _DOC.vinetas(items)


def pasos(items):
    _DOC.numerada(items)


def cuestionario(rel):
    sub("Cuestionario de la guía aplicado al producto")
    p("Respuestas del equipo a las preguntas del adjunto, contextualizadas en el Sistema Cóndor (`%s`)." % rel)
    archivo_md(_DOC, rel, desde_nivel=2)


def hoja_xlsx(rel, hoja, max_filas=60, columnas=None):
    wb = openpyxl.load_workbook(ruta(rel), read_only=True, data_only=True)
    ws = wb[hoja]
    filas = []
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i >= max_filas:
            break
        celdas = ["" if c is None else str(c) for c in r]
        if columnas:
            celdas = [celdas[j] if j < len(celdas) else "" for j in columnas]
        if any(celdas):
            filas.append(celdas)
    return filas


# =================================================================== G01
def g01():
    G = "G01_Requerimientos/"
    _DOC.titulo(2, "5.1 G01 — Requerimientos")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC01 Requerimientos"],
        ["Herramientas y versión", "REMUS 1.3.0.0 (Universidad de Sevilla); Python 3.12.0 (generación de la ERS, tabulación del cuestionario); Microsoft Excel 16 + openpyxl 3.1.5 (cronograma)"],
        ["Evidencias", "`G01_Requerimientos/`: `01_ERS` (ERS 1.1 y 1.2), `02_Elicitacion` (ENT-01, CUE-01, OBS-01), `03_REMUS` (`condor.rem`, HTML, PDF, 17 capturas), `04_Cronograma`, `05_Organizacion`, `06_Herramientas`, `07_Revision`"],
        ["Requisitos vinculados", "Define la línea base: 16 RF, 8 RNF, 15 reglas CRQ, 9 IRQ, 7 interfaces y 6 conflictos"],
        ["Responsable", "Líder: Huamani Condori, J. S. · Revisores: Integrantes 3 y 4 (revisión 1), Integrantes 1 y 3 (revisión 2)"],
        ["Versión del producto", "1.0.0 (línea base) → 1.1.0 (CC-01) → 1.2.0 (CC-03)"],
    ])
    sub("Objetivo")
    p("Construir una especificación de requisitos del software (ERS) verificable para el Sistema Cóndor, tomando como "
      "referencia académica la estructura de IEEE Std 830-1998: identificar a los interesados, elicitar sus necesidades con "
      "al menos dos técnicas, especificar requisitos funcionales y no funcionales con identificador, fuente, prioridad y "
      "criterio de aceptación, definir indicadores medibles, registrar los conflictos y revisar la calidad del documento.")

    sub("Procedimiento realizado")
    p("**Paso 1. Identificación de interesados.** Se identificaron el cliente (gerente general), los usuarios (vendedores de "
      "mostrador y encargado general), un experto del dominio (contador externo) y el docente. Como el equipo no tuvo acceso "
      "continuo a la ferretería, las sesiones se hicieron con **usuarios representados** y así se declara en la ERS y en cada "
      "instrumento.")
    p("**Paso 2. Entrevista semiestructurada ENT-01.** Dos sesiones (gerente, 45 min; encargado, 40 min) con un guion de "
      "preguntas abiertas. El acta registra las respuestas resumidas y, al final, cada hallazgo con el requisito, la regla o el "
      "conflicto que originó.")
    p("**Hallazgos y requisitos derivados de la entrevista:**")
    tabla_md(_DOC, G + "02_Elicitacion/ENT-01_acta_entrevista.md", "Hallazgos")
    p("**Paso 3. Cuestionario CUE-01 a los vendedores.** Al ser cuatro vendedores, se aplicó un cuestionario a la población "
      "completa (no una encuesta por muestreo) con preguntas cerradas, una escala de 1 a 5 y dos preguntas abiertas. La "
      "tabulación la genera `tabular_cuestionario.py` a partir de `CUE-01_respuestas.csv`.")
    seccion_md(_DOC, G + "02_Elicitacion/CUE-01_tabulacion.md", "Interpretación")
    p("**Paso 4. Observación directa OBS-01.** Se cronometraron 12 ventas de tres productos con boleta manual en hora punta, "
      "anotando los pasos, los problemas y los errores. Esta observación fija la **línea base** contra la que se miden RNF-01 y "
      "RNF-06.")
    seccion_md(_DOC, G + "02_Elicitacion/OBS-01_ficha_observacion.md", "Resultados")
    seccion_md(_DOC, G + "02_Elicitacion/OBS-01_ficha_observacion.md", "Conclusiones para la ERS")
    p("**Paso 5. Modelado en REMUS.** Objetivos, actores, requisitos de información, reglas, casos de uso (uno por RF), "
      "requisitos no funcionales, conflictos y matrices se registraron en `condor.rem`. Para que REMUS y la ERS no diverjan, ambos "
      "se generan desde una única fuente versionada (`condor_datos.json`) con `generar_rem.ps1` y `generar_ers.py`.")
    cap(G + "03_REMUS/capturas/04_remus_RF04_general.png", "Caso de uso RF-04 en REMUS: datos generales", 14)
    cap(G + "03_REMUS/capturas/08_remus_RF04_rastreabilidad.png", "Rastreabilidad del RF-04 hacia objetivos en REMUS", 14)
    p("**Paso 6. Especificación.** La ERS documenta propósito, alcance, contexto, interfaces, supuestos y restricciones, y "
      "especifica cada requisito con descripción, fuente, prioridad, objetivo, flujo, excepciones y criterios Dado/Cuando/Entonces.")
    p("**Requisitos funcionales de la línea base (ERS 1.2):**")
    tabla_md(_DOC, G + "01_ERS/ERS_Condor_v1.2.md", "3.2 Requisitos funcionales")
    p("**Requisitos no funcionales medibles:**")
    tabla_md(_DOC, G + "01_ERS/ERS_Condor_v1.2.md", "3.3 Requisitos no funcionales")
    p("**Paso 7. Indicadores medibles y conflictos.**")
    seccion_md(_DOC, G + "01_ERS/ERS_Condor_v1.2.md", "4. Indicadores medibles")
    tabla_md(_DOC, G + "01_ERS/ERS_Condor_v1.2.md", "5. Conflictos")
    p("**Paso 8. Cronograma, organización y herramientas.** El cronograma se planificó en Excel con fórmulas visibles y un "
      "diagrama de Gantt por formato condicional; el organigrama y la matriz RACI documentan que cada integrante ejerce los "
      "cuatro roles; y se compararon herramientas de gestión de requisitos y de cronograma.")
    cap(G + "04_Cronograma/captura_excel_cronograma.png", "Cronograma editable en Excel (cronograma.xlsx)", 16)
    cap(G + "06_Herramientas/impedimento_REM_404.png", "Impedimento: el enlace oficial de descarga de REM devuelve 404", 13)
    p("**Paso 9. Revisión de la ERS.** Dos revisores que no redactaron el documento aplicaron una lista de comprobación con "
      "los atributos de calidad de IEEE 830 (claridad, consistencia, completitud, verificabilidad, trazabilidad y priorización).")
    seccion_md(_DOC, G + "07_Revision/lista_revision.md", "2. Observaciones")

    sub("Resultados obtenidos")
    lista([
        "ERS versionada: 0.9 (borrador) → 1.0 (línea base) → 1.1 (CC-01) → **1.2 (CC-03, línea base vigente)**, con control de versiones.",
        "Tres instrumentos de elicitación con sus resultados: acta ENT-01, cuestionario y tabulación CUE-01 (n = 4) y ficha OBS-01 (12 ventas).",
        "**16 RF y 8 RNF** con ID, descripción, fuente, prioridad y criterio de aceptación; 15 reglas, 9 requisitos de información, 7 interfaces.",
        "Línea base cuantitativa: mediana de **170 s por venta** y **16,7 %** de errores de IGV con el proceso manual.",
        "6 conflictos identificados y resueltos (CFL-01 a CFL-06).",
        "Revisión 1: 14 observaciones, todas corregidas; revisión 2: 0 observaciones abiertas.",
        "Proyecto REMUS, documento HTML y PDF exportados; cronograma, organigrama y comparación de herramientas.",
    ])
    seccion_md(_DOC, G + "07_Revision/lista_revision.md", "4. Comprobaciones globales")

    sub("Análisis de resultados")
    p("Cada técnica aportó un tipo de requisito distinto: la entrevista dio los objetivos y las reglas del negocio (roles, "
      "reporte, respaldo); el cuestionario confirmó y priorizó las necesidades de uso diario (búsqueda por nombre, teclado, lector "
      "de códigos) y cuantificó el acuerdo con cada una; y la observación entregó las cifras con las que se fijaron metas "
      "verificables. Sin OBS-01, RNF-06 habría quedado como «fácil de usar», que fue precisamente la observación OR-04 de la revisión.")
    p("La revisión concentró sus hallazgos en verificabilidad (4) y completitud (5): los RNF de la versión 0.9 estaban redactados "
      "sin unidades y varias funciones no definían el comportamiento ante errores. Corregirlos antes de diseñar evitó retrabajo: "
      "por ejemplo, el valor límite de S/ 700,00 (OR-02) se convirtió después en los casos PU-13 y PU-14 de G07 y en el defecto "
      "controlado DEF-02.")
    p("El conflicto CFL-01 (rapidez frente a control de acceso) es el que más impacto tuvo: su resolución exigió la solicitud de "
      "cambio CC-01 y una nueva línea base. El cuestionario lo sustentó con datos: el 100 % rechaza escribir la contraseña en cada "
      "venta, pero el 75 % la acepta una vez por turno.")
    sub("Conclusiones")
    pasos([
        "La ERS cumple el criterio de aceptación de G01: cada requisito tiene una condición observable de cumplimiento y puede vincularse con una prueba (24 de 24).",
        "Combinar tres técnicas de elicitación permitió obtener requisitos de negocio, de uso y normativos, y metas medibles contra una línea base real.",
        "Generar REMUS y la ERS desde una sola fuente versionada hizo posible mantener las tres versiones de la ERS sin incoherencias.",
        "La revisión por lista de comprobación es barata y eficaz: sus 14 observaciones se corrigieron antes de diseñar.",
    ])
    sub("Limitaciones y ubicación de evidencias")
    lista([
        "Las sesiones se hicieron con usuarios representados por integrantes del equipo; el cuestionario tiene n = 4.",
        "REM no pudo descargarse (404); se usó REMUS, sucesor con el mismo modelo, como sustitución documentada.",
        "REMUS es monousuario; el seguimiento de estados de los requisitos se hace en G02 con Redmine.",
    ])
    cuestionario(G + "08_Cuestionario_guia.md")


# =================================================================== G02
def g02():
    G = "G02_Proceso_Requerimientos/"
    C = G + "01_Redmine/capturas/"
    _DOC.titulo(2, "5.2 G02 — Proceso de requerimientos")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC02 Proceso de Requerimientos"],
        ["Herramientas y versión", "Redmine 7.0.1 (Rails 8.1.3.1, Ruby 4.0.6, SQLite) en Docker; Python 3.12.0 (carga por API REST e informe de seguimiento); Ruby (`configurar_redmine.rb`)"],
        ["Evidencias", "`G02_Proceso_Requerimientos/`: `01_Redmine` (respaldo `redmine.db`, exportaciones CSV/PDF, 22 capturas), `02_Flujo`, `03_Solicitudes_Cambio` (CC-01, CC-02), `04_Pruebas` (.trx y HTML), `05_Seguimiento`, `06_Herramientas`"],
        ["Requisitos vinculados", "Flujo completo: RF-01, RF-03, RF-07, RF-08, RF-15. CC-01 afecta RF-01, RF-02, RF-03, RF-07, RF-15, RNF-02, RNF-03"],
        ["Responsable", "Líder: Payehuanca Riquelme, J. J. · CCB: gerente general, Integrante 1 e Integrante 2"],
        ["Versión del producto", "1.0.0 → 1.1.0 (CC-01 implementado)"],
    ])
    sub("Objetivo")
    p("Controlar los requisitos y sus cambios durante el desarrollo: configurar un gestor con un flujo de estados, llevar al "
      "menos cinco requisitos por todo el flujo con evidencia en cada transición, tramitar dos solicitudes reales de cambio con "
      "análisis de impacto, implementar al menos una con todas sus consecuencias y obtener reportes de seguimiento.")
    sub("Procedimiento realizado")
    p("**Paso 1. Configuración de Redmine.** Se levantó Redmine 7.0.1 en un contenedor (`redmine-condor`, puerto 3010) y se "
      "configuró con un script Ruby reproducible: estados, tipos de petición (Requisito, Solicitud de cambio), campos "
      "personalizados (ID ERS, fuente, criterios, impacto, versión afectada), roles y un flujo de trabajo distinto por rol.")
    p("**Paso 2. Flujo de estados.** El flujo exigido por la guía (registrado → analizado → aprobado o rechazado → implementado "
      "→ verificado → cerrado) se dibujó y se configuró por rol: el analista registra y analiza, el CCB aprueba o rechaza, el "
      "desarrollador implementa y el evaluador verifica. Así, nadie puede saltarse un paso que no le corresponde.")
    cap(G + "02_Flujo/flujo_requerimientos.png", "Flujo de estados de un requisito y de una solicitud de cambio", 15)
    p("**Paso 3. Carga y recorrido de requisitos.** `cargar_redmine.py` registró por la API REST los 24 requisitos de la ERS. "
      "Cinco de ellos se llevaron por el flujo completo, cada transición con fecha, responsable y evidencia (análisis con la "
      "lista de revisión, aprobación del CCB, archivo de código, reporte de pruebas y cierre).")
    p("Se reproduce uno de los cinco recorridos (RF-07); los de RF-01, RF-03, RF-08 y RF-15 tienen la misma estructura y están en `05_Seguimiento/informe_seguimiento.md` y en las exportaciones PDF de cada petición.")
    p("**Paso 4. Solicitud de cambio CC-01 (aprobada e implementada).** Surgió del conflicto CFL-01 y de las exigencias del "
      "curso (autenticación, roles y rutas HTTP para JMeter). Se analizó su impacto en requisitos, diseño, costo, plazo, riesgos y "
      "pruebas; el CCB la aprobó, se implementó en el producto 1.1.0, se actualizaron la ERS (1.1), el diseño, el código y las "
      "pruebas, se repitió la suite y se cerró.")
    for s_ in ("1. Descripción", "3.1 Requisitos", "4. Decisión", "5. Implementación"):
        seccion_md(_DOC, G + "03_Solicitudes_Cambio/CC-01_ingreso_con_roles.md", s_)
    cap(C + "17_solicitud_CC-01.png", "Petición CC-01 en Redmine con su análisis y decisión", 15)
    p("**Paso 5. Solicitud de cambio CC-02 (rechazada con sustento).** Los vendedores pidieron poder aplicar descuentos "
      "manuales en la línea de venta.")
    for s_ in ("1. Descripción", "3.1 Requisitos", "3.5 Riesgos", "4. Decisión"):
        seccion_md(_DOC, G + "03_Solicitudes_Cambio/CC-02_descuento_en_venta.md", s_)
    p("**Paso 6. Repetición de pruebas tras CC-01.** Se ejecutó la suite completa sobre la versión 1.1.0 (`suite_completa_v1.1.0.trx`: "
      "923 aprobadas, 0 fallidas, 5 omitidas) y la regresión específica del cambio (`regresion_CC-01.trx`); los reportes HTML "
      "se adjuntaron a las peticiones.")
    p("**Paso 7. Seguimiento y comparación de herramientas.** `generar_informe_seguimiento.py` lee la API de Redmine y produce "
      "el informe de seguimiento; los reportes nativos de Redmine (resumen, estado por tipo, por asignado, hoja de ruta) se "
      "capturaron.")

    sub("Resultados obtenidos")
    seccion_md(_DOC, G + "05_Seguimiento/informe_seguimiento.md", "1. Estado de los requisitos")
    seccion_md(_DOC, G + "05_Seguimiento/informe_seguimiento.md", "3. Solicitudes de cambio")
    cap(C + "19_informe_resumen.png", "Reporte resumen de Redmine por tipo, prioridad, asignado y versión", 15)
    cap(C + "22_hoja_de_ruta_1.1.0.png", "Hoja de ruta de la versión 1.1.0 en Redmine", 15)
    p("**Comparación de la herramienta seleccionada con alternativas:**")
    seccion_md(_DOC, G + "06_Herramientas/comparacion_herramientas.md", "2. Redmine frente")
    seccion_md(_DOC, G + "06_Herramientas/comparacion_herramientas.md", "4. Conclusión")

    sub("Análisis de resultados")
    p("El flujo por rol convirtió el proceso en verificable: cada transición tiene un responsable con el rol adecuado y una "
      "evidencia adjunta, y Redmine no permite, por ejemplo, que un desarrollador apruebe su propio cambio. Al corte, ningún "
      "requisito quedó sin implementar; los 19 que estaban en «Implementado» esperaban la verificación que luego aportaron G06 a "
      "G09, y la matriz de trazabilidad final lo cierra.")
    p("Las dos solicitudes muestran que el análisis de impacto es la base de la decisión. CC-01 tenía alto impacto (reescribir "
      "RF-01, nuevos RF-02, RF-03 y RF-15, nueva arquitectura con backend REST) pero eliminaba riesgos (R01, R02) y era exigencia "
      "del curso, así que se aprobó. CC-02 tenía bajo costo técnico, pero contradecía CRQ-07, elevaba el riesgo R03 de "
      "manipulación de precios y reabría el conflicto CFL-03, así que se rechazó aunque la pedían tres de cuatro vendedores.")
    p("La regresión tras CC-01 (923/0/5 en la suite y 30/30 → 43/43 en la suite de G07) demostró que el cambio no rompió las "
      "funciones existentes. Esa misma disciplina se aplicó después a CC-03 (G09), que se registró con el mismo flujo.")
    sub("Conclusiones")
    pasos([
        "Se configuró un gestor operativo con el flujo exigido y se reconstruye el recorrido completo de cinco requisitos con fecha, responsable y evidencia.",
        "Se tramitaron dos cambios reales: CC-01 aprobado e implementado (conduce a la versión 1.1.0 y a pruebas verificables) y CC-02 rechazado con sustento.",
        "El seguimiento se obtiene de la herramienta, no a mano, y Redmine resultó más adecuado que las alternativas de la guía por su flujo configurable por rol y su API.",
    ])
    sub("Limitaciones y ubicación de evidencias")
    lista([
        "Las transiciones se registraron por script en una misma sesión de carga; las fechas reflejan la carga y no la duración real de cada etapa.",
        "El gerente y el CCB son representados por integrantes del equipo.",
    ])
    cuestionario(G + "07_Cuestionario_guia.md")


# =================================================================== G03
def g03():
    G = "G03_Analisis_Sistemas/"
    S = G + "01_SDD/SDD_Condor_v1.0.md"
    _DOC.titulo(2, "5.3 G03 — Análisis de sistemas")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC03 Análisis de Sistemas"],
        ["Herramientas y versión", "PlantUML 1.2024.7 con motor Smetana (sin Graphviz); módulo Salt para los mockups"],
        ["Evidencias", "`G03_Analisis_Sistemas/`: `01_SDD/SDD_Condor_v1.0.md` (versión 1.1 tras CC-03), `02_UML` (9 diagramas .puml, .png, .svg), `03_Mockups` (M01–M05), `04_Revision`, `05_Herramientas`"],
        ["Requisitos vinculados", "Los tres procesos: CU-01 (RF-07), CU-02 (RF-08), CU-03 (RF-12); trazabilidad de los 24 requisitos"],
        ["Responsable", "Líder: Condo Zamata, R. A. · Revisión: Integrante 4"],
        ["Versión del producto", "1.1.0 (diseño) → 1.1.1 (DEF-01) → 1.2.0 (DD-09, CC-03)"],
    ])
    sub("Objetivo")
    p("Elaborar la descripción del diseño de software (SDD) con IEEE 1016 como referencia: interesados, preocupaciones, puntos "
      "de vista, vistas y decisiones; presentar casos de uso, clases y comportamiento del proceso crítico; especificar tres casos "
      "de uso con sus mockups; y revisar el SDD contra los criterios de la referencia, manteniendo la coherencia de nombres "
      "entre requisitos, clases, tablas y pantallas.")
    sub("Procedimiento realizado")
    p("**Paso 1. Interesados, preocupaciones y puntos de vista.**")
    seccion_md(_DOC, S, "2. Interesados")
    seccion_md(_DOC, S, "3. Puntos de vista")
    p("**Paso 2. Vistas de diseño.** Cada vista responde a preocupaciones concretas y se apoya en un diagrama PlantUML cuya "
      "fuente está versionada.")
    seccion_md(_DOC, S, "4.1 Vista de contexto")
    seccion_md(_DOC, S, "4.2 Vista de composición")
    seccion_md(_DOC, S, "4.3 Vista lógica")
    seccion_md(_DOC, S, "4.5 Vista de interacción")
    seccion_md(_DOC, S, "4.6 Vista de estado dinámico")
    seccion_md(_DOC, S, "4.7.2 Interfaz de usuario")
    seccion_md(_DOC, S, "4.8 Vista de despliegue")
    p("**Paso 3. Especificación de los tres casos de uso** (uno por proceso de negocio), con precondiciones, flujo principal, "
      "alternativas, excepciones y poscondiciones:")
    seccion_md(_DOC, S, "CU-01 Emitir comprobante")
    seccion_md(_DOC, S, "CU-02 Convertir una proforma")
    seccion_md(_DOC, S, "CU-03 Registrar compra")
    p("**Paso 4. Decisiones de diseño y trazabilidad.**")
    seccion_md(_DOC, S, "6. Decisiones de diseño")
    p("**Paso 5. Revisión del SDD contra IEEE 1016-2009** y contra el código real del producto.")

    sub("Resultados obtenidos")
    lista([
        "SDD 1.0 (versión 1.1 tras CC-03) con 8 vistas, 3 casos de uso, 9 decisiones de diseño y trazabilidad requisito → caso de uso → clase → tabla → pantalla → prueba.",
        "9 diagramas UML (casos de uso, 2 de clases, secuencia, estados, 2 de actividad, componentes, despliegue) y modelo de datos, con fuente editable .puml y exportación PNG/SVG.",
        "5 mockups (M01 a M05) con los mismos textos, atajos y columnas que la aplicación.",
        "Revisión: 7 observaciones, 6 corregidas en el documento y **1 que resultó un defecto del producto (DEF-01)**.",
    ])
    seccion_md(_DOC, G + "04_Revision/revision_SDD.md", "4. Observaciones")
    seccion_md(_DOC, G + "04_Revision/revision_SDD.md", "5. Defecto encontrado")
    p("**Utilidad de los diagramas UML en este proyecto:**")
    seccion_md(_DOC, S, "8. Utilidad")

    sub("Análisis de resultados")
    p("El hallazgo más valioso de G03 no fue un diagrama, sino DEF-01: al contrastar la vista de interfaz con el código, la "
      "revisión encontró que la ruta usada por la aplicación de escritorio guardaba el precio enviado por la PC, en contra de "
      "CRQ-07. Ninguna prueba lo detectaba porque las pruebas verificaban la ruta pública. Se registró como defecto, se corrigió en "
      "una rama SVN y se cerró con tres pruebas que fallan con el código 1.1.0 (G05).")
    p("Mantener los mismos nombres en ERS, SDD, código y base de datos (observaciones OS-02 y OS-03) hizo posible la tabla de "
      "trazabilidad de la sección 7 del SDD, que luego reutilizó la matriz de trazabilidad final. Los diagramas más útiles fueron "
      "el de secuencia de la emisión (explica la transacción, la numeración y el envío posterior a la SUNAT) y el de estados del "
      "comprobante (fija los estados ante la SUNAT que verifican RF-10 y RNF-05).")
    sub("Conclusiones")
    pasos([
        "El diseño explica los tres procesos de negocio y sus elementos se rastrean hacia requisitos y código, criterio de aceptación de G03.",
        "Las decisiones DD-01 a DD-09 justifican la arquitectura cliente–API–base, la numeración sin huecos, el envío asíncrono a la SUNAT y el portal web.",
        "Revisar el diseño contra el código, y no solo contra los requisitos, encontró un defecto real que las pruebas no veían.",
    ])
    sub("Limitaciones y ubicación de evidencias")
    lista([
        "El SDD no incluye pseudocódigo de algoritmos; el cálculo del IGV queda en CRQ-01 y en `CalculadoraVenta` (criterio 5.12 pendiente).",
        "Los mockups se dibujaron con PlantUML Salt y no con Moqups; se justifica en la comparación de herramientas.",
    ])
    cuestionario(G + "06_Cuestionario_guia.md")


# =================================================================== G04
def g04():
    G = "G04_Dimensionamiento/"
    M = G + "02_Memoria/memoria_calculo.md"
    C = G + "03_Capturas/"
    _DOC.titulo(2, "5.4 G04 — Dimensionamiento y estimación")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC04 Dimensionamiento – Puntos de Función"],
        ["Herramientas y versión", "Microsoft Excel 16.0 (compilación 14334); Python 3.12.0 + openpyxl 3.1.5 (libro con fórmulas) y pywin32 (capturas por COM)"],
        ["Evidencias", "`G04_Dimensionamiento/`: `01_Libro/estimacion_condor.xlsx` (todas las cifras son fórmulas), `horas_reales_desarrollo.json`, `contar_sloc.py`, `02_Memoria/memoria_calculo.md`, `03_Capturas` (16 vistas de valores y fórmulas)"],
        ["Requisitos vinculados", "Línea base ERS 1.1 (16 RF, 8 RNF), producto 1.1.0; estimación de CC-03"],
        ["Responsable", "Líder: Chaisa Fernández, A. L. · Revisó: Integrante 1"],
    ])
    sub("Objetivo")
    p("Estimar el tamaño, el esfuerzo, el costo y el plazo del producto con NESMA, COSMIC y COCOMO II, manteniendo separadas "
      "las magnitudes (tamaño funcional, tamaño en código, esfuerzo, duración y costo), calcular escenarios de una y tres personas, "
      "analizar la sensibilidad ±20 % y confrontar la estimación con las horas reales registradas.")
    sub("Procedimiento realizado y resultados")
    p("La memoria de cálculo documenta cada paso; el libro `estimacion_condor.xlsx` contiene las fórmulas, de modo que el docente "
      "puede recalcular cualquier valor cambiando las celdas amarillas. Se reproduce la memoria completa:")
    seccion_md(_DOC, M, "1. Frontera")
    seccion_md(_DOC, M, "2. Conteo NESMA")
    cap(C + "05_nesma_formulas.png", "Vista de fórmulas del conteo NESMA (IF e INDEX/MATCH sobre las matrices)", 15)
    cap(C + "06_nesma_resumen.png", "Resumen del conteo NESMA detallado: 222 PF", 14)
    seccion_md(_DOC, M, "3. Medición COSMIC")
    cap(C + "08_cosmic.png", "Medición COSMIC: 35 procesos funcionales y 183 CFP", 15)
    seccion_md(_DOC, M, "4. Estimación con COCOMO")
    cap(C + "10_cocomo_resultados.png", "Resultados de COCOMO II desde NESMA y desde el tamaño real", 15)
    seccion_md(_DOC, M, "5. Costo y plazo")
    seccion_md(_DOC, M, "6. Sensibilidad")
    cap(C + "14_sensibilidad.png", "Análisis de sensibilidad ±20 %", 15)
    seccion_md(_DOC, M, "7. Comparación")
    cap(C + "16_cuadro_comparativo.png", "Cuadro comparativo de los métodos", 15)
    seccion_md(_DOC, M, "8. Limitaciones")
    p("**Estimación de un cambio con el modelo calibrado.** Para CC-03 (portal web, G09) se estimaron 17 h con la productividad "
      "observada del equipo y se registraron 17,5 h reales (S/ 440 a S/ 25/h): un error de 3 %, frente al 1 491 % del modelo sin "
      "calibrar. Es la primera validación de la calibración local.")
    sub("Análisis de resultados")
    p("Los métodos de tamaño coinciden entre sí y con la realidad: NESMA estimado se desvía −2,7 % del detallado y la conversión "
      "a código (12,0 KSLOC) acierta el tamaño real (11,8 KSLOC) con un 1,3 % de diferencia. El indicativo sobreestima porque el "
      "producto tiene pocos archivos lógicos para muchas transacciones. COSMIC da otra unidad, más sensible a los procesos con "
      "muchos movimientos de datos (emisión, envío a la SUNAT, reporte), y no se convierte en PF.")
    p("Donde el modelo falla es en la **productividad**: COCOMO II supone un equipo industrial y meses de trabajo normal, y este "
      "equipo trabajó 11 días intensivos con frameworks, contenedores y asistencia de IA. Por eso la duración real queda fuera del "
      "rango de compresión en que el modelo es válido. La calibración local (A = 0,185) corrige el sesgo para trabajos similares, "
      "con la debilidad de basarse en un solo proyecto.")
    sub("Conclusiones")
    pasos(["El libro permite recalcular todos los valores y distingue tamaño funcional (PF, CFP), tamaño en código (KSLOC), esfuerzo (PM, horas), duración (meses) y costo (soles), criterio de aceptación de G04.",
           "Con tres personas la duración baja a 16,9 meses (−62 %), no a la tercera parte, y el costo sube un 15 % por la coordinación.",
           "El resultado es más sensible al tamaño y al factor de conversión que a los multiplicadores, por la deseconomía de escala.",
           "Frente a las horas reales, el modelo sin calibrar sobreestima unas 16 veces; la constante calibrada se validó con CC-03."])
    sub("Limitaciones y ubicación de evidencias")
    lista(["COCOMO II no está calibrado para equipos estudiantiles ni para el uso intensivo de frameworks y asistentes.",
           "La tarifa y la dedicación son supuestos del equipo; la calibración local se apoya en un solo proyecto.",
           "El método «wine» de la guía no está definido y no se aplicó (aclaración del enunciado)."])
    cuestionario(G + "05_Cuestionario_guia.md")


# =================================================================== G05
def g05():
    G = "G05_Gestion_Configuracion/"
    P = G + "01_Politica/politica_configuracion.md"
    C = G + "04_Evidencias/capturas/"
    _DOC.titulo(2, "5.5 G05 — Gestión de configuración")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC05 Gestión de Configuración"],
        ["Herramientas y versión", "Apache Subversion 1.14.5 (`svn`, `svnadmin`, `svnserve`, `svnlook`), TortoiseSVN 1.14.9.29743 de 64 bits, Windows 11; script de prueba en Docker"],
        ["Evidencias", "`G05_Gestion_Configuracion/`: `01_Politica`, `02_Repositorio/condor` (repositorio FSFS portable), `03_Respaldo` (volcados r16, r35, r44), `04_Evidencias` (historial, conflicto, recuperación, etiquetas, permisos, pruebas), `05_Herramientas`, `06_Scripts`"],
        ["Requisitos vinculados", "Todos los elementos de configuración EC-01 a EC-11; DEF-01 (RF-07), MEJ-01 (RNF-02, RNF-04), CC-03"],
        ["Responsable", "Líder y responsable de configuración: Payehuanca Riquelme, J. J. (`jpayehuanca`, único con escritura en `/tags`)"],
        ["Versión entregada", "`tags/v1.0.1` (r44) = producto 1.2.0"],
    ])
    sub("Objetivo")
    p("Controlar los elementos de configuración del trabajo y sus versiones con Apache Subversion: definir los elementos, la "
      "estructura, los permisos y la política de nombres; registrar revisiones significativas durante todo el proyecto; trabajar "
      "con ramas, integrar y resolver un conflicto de forma controlada; etiquetar la versión final y demostrar la recuperación de "
      "una revisión anterior sin perder la entrega vigente.")
    sub("Procedimiento realizado")
    p("**Paso 1. Instalación.** Se instalaron TortoiseSVN 1.14.9 y sus herramientas de línea de comandos (Subversion 1.14.5) en "
      "Windows 11. El repositorio se sirve con `svnserve` en `svn://127.0.0.1/condor`.")
    cap(C + "01_tortoisesvn_about.png", "Versión instalada de TortoiseSVN y Subversion", 11)
    p("**Paso 2. Política de configuración.** Se definieron los elementos de configuración, la estructura, los permisos, la política "
      "de nombres, los procedimientos y las líneas base:")
    seccion_md(_DOC, P, "2. Elementos de configuración")
    seccion_md(_DOC, P, "4. Permisos")
    seccion_md(_DOC, P, "5. Política de nombres")
    p("**Paso 3. Creación, importación y ciclo de trabajo.** Se creó el repositorio FSFS, se importó la estructura `trunk/branches/tags` "
      "con el producto 1.1.0 (r1–r2) y cada integrante hizo checkout, update, cambios y commit con su propio usuario. El hook "
      "`pre-commit` rechaza mensajes de menos de 10 caracteres y `authz` impide que alguien distinto del responsable cree etiquetas "
      "(pruebas en `prueba_permisos_y_hook.txt`).")
    cap(C + "04_repo_browser.png", "Navegador del repositorio: trunk, branches y tags", 15)
    p("**Paso 4. Rama, integración y conflicto controlado.** El defecto DEF-01 se corrigió en `branches/DEF-01-precio-catalogo` "
      "(r8, r10) mientras otro integrante cambiaba el mismo método en trunk para CRQ-14 (r9). Al fusionar la rama en trunk (r11) "
      "se produjo un conflicto real en `EndpointsEscritorio.cs`. Se conservaron como evidencia la base común (r7), la versión del "
      "trunk (*mine*), la de la rama (*theirs*), el archivo con marcas y el resultado; la decisión fue conservar ambas validaciones "
      "y se explicó en el mensaje del commit. Antes y después se ejecutaron las pruebas: las de DEF-01 fallan contra el código sin "
      "corregir y pasan tras la integración.")
    cap(C + "06_tortoisemerge_conflicto.png", "Conflicto entre trunk (CRQ-14) y la rama DEF-01 en TortoiseMerge", 16)
    p("**Paso 5. Más ramas.** La mejora de rendimiento MEJ-01 (r23–r25) y el portal web CC-03 (r28–r31, integrado en r32 sin "
      "conflictos) siguieron el mismo procedimiento.")
    p("**Paso 6. Etiquetas y respaldo.** Se crearon `v0.1.0` (avance 1), `v0.2.0` (avance 2), `v1.0.0` (entrega final) y "
      "`v1.0.1` (entrega final corregida, la que se entrega). Cada etiqueta se acompañó de un volcado `svnadmin dump` comprimido, "
      "verificado cargándolo en un repositorio vacío y con `svnadmin verify`.")
    p("**Paso 7. Recuperación.** Se exportó la revisión r2 en una carpeta aparte (`svn export -r 2`) sin tocar trunk ni etiquetas, "
      "y se borró y restauró un archivo con su historia mediante `svn copy ^/trunk/<ruta>@N` (r13–r14). Las salidas completas "
      "están en `04_Evidencias/recuperacion/`.")
    sub("Resultados obtenidos")
    lista([
        "**45 revisiones** significativas (r1 a r45) a lo largo del proyecto, con mensajes que empiezan por el ID del cambio.",
        "Tres ramas (DEF-01, MEJ-01, CC-03), una con conflicto real resuelto y documentado.",
        "Cuatro etiquetas inmutables; la versión entregada es `tags/v1.0.1` y su código coincide con `v1.0.0`.",
        "Recuperación de una revisión anterior y de un archivo borrado demostradas sin perder la entrega vigente.",
        "Repositorio portable y tres volcados verificados.",
    ])
    cap(C + "03_grafico_revisiones.png", "Gráfico de revisiones con ramas, fusiones y etiquetas", 16)
    seccion_md(_DOC, P, "8. Manifiesto")
    p("**Comparación de SVN con Git (tecnología) y GitHub (plataforma):**")
    seccion_md(_DOC, G + "05_Herramientas/comparacion_svn_git_github.md", "1. Subversion frente a Git")
    seccion_md(_DOC, G + "05_Herramientas/comparacion_svn_git_github.md", "3. Conclusión")
    sub("Análisis de resultados")
    p("El conflicto de r11 no fue simulado: surgió porque dos cambios legítimos tocaron el mismo método en paralelo. Conservar "
      "los cuatro archivos y repetir las pruebas antes y después permitió demostrar que la resolución no perdió ninguna de las dos "
      "validaciones. La separación entre la numeración de entregas (etiquetas) y la del software (versión del producto) evitó "
      "confusiones cuando hubo que corregir la entrega final sin modificar una etiqueta: se creó `v1.0.1` y se comprobó con `svn "
      "diff --summarize` que el código no cambió.")
    p("SVN resultó adecuado para un equipo pequeño que necesita permisos por ruta y etiquetas de solo lectura; Git ofrece trabajo "
      "distribuido y ramas más baratas, y GitHub añade revisión de código e integración continua (el equipo usó GitHub en los "
      "sprints iniciales).")
    sub("Conclusiones")
    pasos(["El código entregado coincide con la etiqueta final `v1.0.1` y permite reconstruir la versión, criterio de aceptación de G05.",
           "Ramas, integración, conflicto, etiquetas y recuperación quedaron demostrados con evidencia del estado anterior, la decisión y el resultado.",
           "El manifiesto relaciona cada evidencia de G01 a G09 con su revisión y la versión del producto."])
    sub("Limitaciones y ubicación de evidencias")
    lista(["Los commits r28 a r34 y r36 a r43 se hicieron con la cuenta `rcondo` por falta de credenciales de los demás integrantes en el equipo de trabajo (observación O-8).",
           "El servidor `svnserve` corre en local; en el local de la ferretería requeriría una PC dedicada o un servicio con respaldo."])
    cuestionario(G + "07_Cuestionario_guia.md")


# =================================================================== G06
def g06():
    G = "G06_Gestion_Riesgos/"
    C = G + "03_PILAR/capturas/"
    _DOC.titulo(2, "5.6 G06 — Gestión de riesgos")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC06 Gestión de Riesgos"],
        ["Herramientas y versión", "PILAR Basic 2026.1.1 (biblioteca INFOSEC 22.7.2023); Excel 16 + openpyxl 3.1.5 (matriz MAGERIT y plantilla docente); Python 3 (verificación de controles)"],
        ["Evidencias", "`G06_Gestion_Riesgos/`: `01_Inventario`, `02_Matriz_y_Tratamiento` (matriz, plan, libros .xlsx), `03_PILAR` (`CONDOR.mgr`, 12 capturas, scripts), `04_Controles`, `05_Comparacion_RMAT_PILAR`, `06_Herramientas`"],
        ["Requisitos vinculados", "RF-01, RF-03, RF-07, RF-16, RNF-03, RNF-07 (salvaguardas S1, S2, S3)"],
        ["Responsable", "Líder: Chaisa Fernández, A. L. · Revisó: Integrante 2 · Validó: gerente (representado)"],
        ["Versión del producto", "1.1.1"],
    ])
    sub("Objetivo")
    p("Aplicar MAGERIT v3 al sistema de información que soporta el producto: identificar activos, dependencias y dimensiones, "
      "registrar escenarios activo–amenaza, evaluar frecuencia, degradación, impacto y riesgo con escalas documentadas, priorizar, "
      "planificar salvaguardas con responsable, fecha, costo e indicador, e implantar y verificar al menos dos tratamientos.")
    sub("Procedimiento realizado")
    p("**Paso 1. Inventario de activos y dependencias.**")
    seccion_md(_DOC, G + "01_Inventario/inventario_activos.md", "1. Activos")
    p("**Paso 2. Proyecto en PILAR.** Se creó el proyecto `CONDOR.mgr` y se recorrieron las fases A.1 (activos), A.2 "
      "(valoración), A.4 (amenazas), A.5 (salvaguardas) y A.6 (riesgo potencial, actual y objetivo).")
    cap(C + "03_pilar_A1_activos.png", "PILAR, fase A.1: árbol de activos", 15)
    p("**Paso 3. Matriz de riesgos MAGERIT.** Además de PILAR, la matriz se construyó con el análisis mediante tablas de MAGERIT "
      "en un libro editable, con las mismas tres situaciones (potencial, actual, objetivo).")
    seccion_md(_DOC, G + "02_Matriz_y_Tratamiento/matriz_riesgos.md", "1. Método")
    seccion_md(_DOC, G + "02_Matriz_y_Tratamiento/matriz_riesgos.md", "3. Escenarios")
    cap(C + "08_pilar_A6_riesgo_actual.png", "PILAR, fase A.6: riesgo actual", 15)
    p("**Paso 4. Plan de tratamiento.**")
    seccion_md(_DOC, G + "02_Matriz_y_Tratamiento/plan_tratamiento.md", "1. Salvaguardas")
    seccion_md(_DOC, G + "02_Matriz_y_Tratamiento/plan_tratamiento.md", "3. Controles propuestos")
    p("**Paso 5. Implantación y verificación de los controles.** S1 (autorización por roles y bloqueo), S2 (validación de entradas "
      "en el servidor) y S3 (respaldo y restauración) se verificaron contra el sistema en ejecución con `verificar_controles.py`:")
    tabla_md(_DOC, G + "04_Controles/verificacion_controles.md", "Verificación")
    p("**Paso 6. Comparación de RMAT y PILAR.**")
    seccion_md(_DOC, G + "05_Comparacion_RMAT_PILAR/comparacion_RMAT_PILAR.md", "2. Matriz", imagenes=False)
    seccion_md(_DOC, G + "05_Comparacion_RMAT_PILAR/comparacion_RMAT_PILAR.md", "3. Conclusión")
    sub("Resultados obtenidos")
    lista(["10 activos con dependencias y valor acumulado; 12 escenarios activo–amenaza con escalas documentadas.",
           "Riesgo potencial, actual y objetivo en PILAR y en la matriz MAGERIT; matriz P × I solo como complemento.",
           "Plan con 11 salvaguardas: S1, S2 y S3 implantadas y verificadas (**18 de 18** comprobaciones); S4 a S11 propuestas.",
           "Comparación RMAT–PILAR con la limitación de identificación registrada."])
    sub("Análisis de resultados")
    p("El análisis distingue con cuidado lo implantado de lo propuesto: el riesgo actual de R01, R03 y R05 baja porque S1, S2 y "
      "S3 se probaron contra el sistema en ejecución, mientras que el riesgo objetivo de los demás es **previsto** hasta implantar "
      "su salvaguarda. R02 sigue alto: el bloqueo impide adivinar claves, pero no que un vendedor preste la suya, un problema "
      "organizativo y no técnico.")
    p("La gestión de riesgos influyó en el producto: la salvaguarda S2 nació del defecto DEF-01 (precio aceptado desde la PC) y "
      "el portal de CC-03 aumentó la exposición de R12, por lo que la salvaguarda S10 (HTTPS) pasó a ser condición de la "
      "liberación (observación O-2).")
    sub("Conclusiones")
    pasos(["Cada riesgo priorizado tiene responsable y respuesta, y los controles implantados tienen prueba de funcionamiento, criterio de aceptación de G06.",
           "Se usó PILAR, la herramienta de referencia de MAGERIT; la matriz simplificada se presenta solo como complemento.",
           "No se declara reducción efectiva sin evidencia: S4 a S11 quedan con riesgo residual previsto."])
    sub("Limitaciones y ubicación de evidencias")
    lista(["Las frecuencias son estimaciones del equipo; la ferretería no lleva registro de incidentes.",
           "PILAR se usó en su edición Basic con licencia de evaluación.",
           "RMAT no se identifica de manera inequívoca; la comparación queda para validación docente."])
    cuestionario(G + "07_Cuestionario_guia.md")


# =================================================================== G07
def g07():
    G = "G07_Pruebas_Unitarias/"
    C = G + "03_Reportes/capturas/"
    X = G + "02_Catalogo/catalogo_casos_prueba.xlsx"
    _DOC.titulo(2, "5.7 G07 — Pruebas unitarias")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC07 Pruebas Unitarias"],
        ["Herramientas y versión", "xUnit 2.9.2, xunit.runner.visualstudio 2.8.2, Microsoft.NET.Test.Sdk 17.11.1, coverlet.collector 6.0.2, ReportGenerator 5.3.11; .NET SDK 8.0.425 (Docker Desktop 29.7.2)"],
        ["Evidencias", "`G07_Pruebas_Unitarias/`: `01_Suite` (proyecto de pruebas, `ejecutar_suite.ps1`), `02_Catalogo` (catálogo .xlsx), `03_Reportes` (.trx, HTML, cobertura), `04_Defecto_Controlado` (parche, bitácora, reportes), `05_Regresion`, `06_Herramientas`"],
        ["Requisitos y riesgos", "RF-01, RF-06, RF-07, RF-08, RF-15, RNF-03, RNF-08; reglas CRQ-01 a CRQ-07, CRQ-14, CRQ-15; riesgos R02, R03, R11"],
        ["Responsable", "Líder: Huamani Condori, J. S."],
        ["Versión del producto", "1.1.1 (y 1.0.0 en la regresión)"],
    ])
    sub("Objetivo")
    p("Verificar las reglas de negocio reales del producto con una suite automatizada: al menos 15 casos sobre tres componentes "
      "con escenarios válidos, inválidos, límite y de excepción; aislar dependencias con dobles; vincular cada caso con requisitos "
      "y riesgos; medir la cobertura del paquete de lógica de negocio; repetir tras un cambio de G02; e introducir un defecto "
      "controlado que una prueba debe detectar.")
    sub("Procedimiento realizado")
    p("**Paso 1. Configuración.** Se usó xUnit, el equivalente de JUnit para .NET, con las mismas versiones que la suite del "
      "producto para no mezclar APIs. La suite se ejecuta con el SDK local o, si no está, dentro del contenedor oficial de .NET 8.")
    p("**Paso 2. Diseño de 27 casos sobre cinco componentes.** Cada caso indica requisito, riesgo de G06, unidad, objetivo, tipo "
      "de escenario, datos, dobles y resultado esperado. El catálogo completo (con fecha, versión, estado y reporte de cada "
      "ejecución) está en `catalogo_casos_prueba.xlsx`:")
    filas = hoja_xlsx(X, "Catálogo", columnas=[0, 1, 2, 3, 4, 5, 8])
    poner_tabla(_DOC, filas)
    p("**Paso 3. Aislamiento y datos reproducibles.** `RepositorioUsuariosFalso` sustituye a PostgreSQL y registra las búsquedas "
      "y actualizaciones (espía); `RelojFalso` fija la hora para probar el bloqueo de 15 minutos sin esperar; `Datos` construye "
      "líneas y clientes de prueba. Ningún caso depende de otro ni del orden de ejecución.")
    p("**Paso 4. Ejemplo de regla y de sus casos de valor límite.** La regla CRQ-02 exige el DNI en boletas de más de S/ 700,00. "
      "La %s muestra la regla y la %s los casos PU-13 (exactamente 700,00, se emite) y PU-14 (700,01, se rechaza)."
      % ("Figura " + _DOC.fig("cod_regla_700"), "Figura " + _DOC.fig("cod_pu13_pu14")))
    _DOC.imagen(ruta("Docs/figuras/cod_regla_700.png"), ancho_cm=16, etiqueta="cod_regla_700",
                leyenda="Regla CRQ-02 en EmisionComprobante.Errores (src/Condor.Dominio/Ventas). Se omiten las líneas 113 a 130 (boleta con DNI y factura).")
    _DOC.imagen(ruta("Docs/figuras/cod_pu13_pu14.png"), ancho_cm=16, etiqueta="cod_pu13_pu14",
                leyenda="Casos PU-13 y PU-14 de valor límite (G07, EmisionComprobanteTests.cs).")
    p("**Paso 5. Ejecución y cobertura.** `ejecutar_suite.ps1` compila, ejecuta, guarda el `.trx` y el HTML y, con `-SuiteProducto`, "
      "mide la cobertura de `Condor.Dominio` sumando la suite de G07 y la del producto. Inclusiones y exclusiones: se incluye solo el "
      "ensamblado `Condor.Dominio`; se excluyen infraestructura (Datos, Api, Sunat, Impresion), presentación y pruebas.")
    p("**Paso 6. Defecto controlado DEF-02.** Se cambió temporalmente «>» por «>=» en la regla de S/ 700 con un parche "
      "(`DEF-02_boleta_700.patch`), se ejecutó la suite (falla PU-13), se restauró el código y se volvió a ejecutar (pasa). La "
      "aserción fallida se propaga al ejecutor: no se copió el patrón de la guía que captura `AssertionError` e imprime el mensaje.")
    p("**Paso 7. Regresión tras CC-01.** Con `-Version 1.0.0` la suite compila contra una copia del producto anterior al cambio "
      "(`05_Regresion/producto_1.0.0`) para mostrar la línea base, y luego contra la 1.1.1.")
    sub("Resultados obtenidos")
    poner_tabla(_DOC, hoja_xlsx(X, "Ejecuciones"))
    cap(C + "01_ejecucion_v1.1.1_43_aprobadas.png", "Reporte de la ejecución E1: 43 de 43 aprobadas en la versión 1.1.1", 15)
    cap(C + "04_cobertura_paquete_Condor.Dominio_RNF-08.png", "Cobertura del paquete Condor.Dominio con ambas suites: 95,6 % de líneas (RNF-08)", 15)
    p("**Comparación con alternativas:**")
    seccion_md(_DOC, G + "06_Herramientas/fichas_herramientas.md", "Comparación")
    sub("Análisis de resultados")
    p("La cobertura de 95,6 % supera la meta de 80 %, pero el resultado más significativo es el del defecto controlado: el cambio "
      "de un solo carácter solo lo detectó el caso de valor límite exacto (PU-13). Una suite con cobertura alta y sin casos de "
      "límite habría dejado pasar el defecto, lo que confirma que alcanzar cobertura no sustituye comprobar el comportamiento.")
    p("Los dobles de prueba hicieron posible probar reglas dependientes del tiempo (bloqueo y desbloqueo a los 15 minutos exactos) "
      "y verificar que los datos incompletos no consultan la base (espía con 0 búsquedas). La regresión R1/R2 mostró que CC-01 no "
      "alteró las reglas existentes.")
    sub("Conclusiones")
    pasos(["Se diseñaron 27 casos sobre cinco componentes reales, vinculados con requisitos y riesgos, con escenarios válidos, inválidos, límite y de excepción.",
           "El docente puede ejecutar la suite con un comando documentado, verificar las aserciones y reproducir el fallo controlado con `reproducir_defecto.ps1`.",
           "La cobertura del paquete de lógica de negocio (95,6 %) cumple RNF-08, con inclusiones y exclusiones declaradas."])
    sub("Limitaciones y ubicación de evidencias")
    lista(["La suite de G07 se midió sobre la versión 1.1.1; para la 1.2.0 la regresión es la suite del producto (944/0/5).",
           "La cobertura mide líneas, no ramas ni mutaciones; el defecto controlado complementa esa limitación."])
    cuestionario(G + "08_Cuestionario_guia.md")


# =================================================================== G08
def g08():
    G = "G08_Pruebas_Rendimiento/"
    C = G + "06_Analisis/capturas/"
    F = G + "06_Analisis/graficas/"
    _DOC.titulo(2, "5.8 G08 — Pruebas de rendimiento")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC08 Pruebas de Performance"],
        ["Herramientas y versión", "Apache JMeter 5.6.3 (modo no gráfico); typeperf de Windows 11; Docker Desktop 29.7.2 (`docker stats`); PostgreSQL 16.15 (`pg_stat_activity`); Python 3.12 + matplotlib 3.11.2 + openpyxl 3.1.5 (análisis)"],
        ["Evidencias", "`G08_Pruebas_Rendimiento/`: `01_Plan`, `02_Scripts` (`condor_rendimiento.jmx`, ejecutores), `03_Datos` (CSV y SQL), `04_Resultados` (.jtl, dashboards HTML, monitoreo, antes y después), `05_Cuello_de_Botella`, `06_Analisis` (libro, gráficas, capturas)"],
        ["Requisitos vinculados", "RNF-02 (umbral), RNF-04; T1 → RF-05, T2 → RF-07"],
        ["Responsable", "Líder: Condo Zamata, R. A."],
        ["Versión del producto", "1.1.1 (línea base, r22) y 1.1.2 (después de MEJ-01, r25)"],
    ])
    sub("Objetivo")
    p("Medir el tiempo de respuesta y la capacidad de las transacciones críticas del producto con JMeter en cuatro escenarios "
      "(carga, estrés, pico y estabilidad), contrastar los resultados con el umbral de RNF-02, localizar un cuello de botella, "
      "aplicar una mejora y repetir la prueba en condiciones equivalentes.")
    sub("Procedimiento realizado: plan de pruebas")
    for s_ in ("1. Transacciones", "3. Escenarios", "4. Criterios"):
        seccion_md(_DOC, G + "01_Plan/plan_pruebas_rendimiento.md", s_)
    sub("Resultados obtenidos y análisis")
    archivo_md(_DOC, G + "06_Analisis/analisis_resultados.md", desde_nivel=2, omitir=("7. Conclusiones", "8. Limitaciones"))
    cap(C + "02_dashboard_carga_despues.png", "Dashboard de JMeter, carga esperada en la versión 1.1.2", 16)
    cap(C + "04_estres_despues_tiempos.png", "Estrés escalonado 10 → 25 → 50 usuarios: tiempos de respuesta", 16)
    sub("Cuello de botella y mejora MEJ-01")
    for s_ in ("1. Cómo se localizó", "2. Mejora aplicada", "4. Resultado antes y después"):
        seccion_md(_DOC, G + "05_Cuello_de_Botella/MEJ-01_correlativo_al_final.md", s_)
    cap(C + "11_capacidad_50u_despues_estadisticas.png", "Estadísticas de capacidad con 50 hilos después de MEJ-01", 16)
    sub("Conclusiones")
    seccion_md(_DOC, G + "06_Analisis/analisis_resultados.md", "7. Conclusiones")
    sub("Limitaciones y ubicación de evidencias")
    seccion_md(_DOC, G + "06_Analisis/analisis_resultados.md", "8. Limitaciones")
    cuestionario(G + "09_Cuestionario_guia.md")


# =================================================================== G09
def g09():
    G = "G09_Gestion_Calidad/"
    R = G + "04_Reportes/20261104_1919_1.2.0-r32_final-3/capturas/"
    _DOC.titulo(2, "5.9 G09 — Gestión de calidad con Selenium")
    sub("Datos de la guía")
    ficha([
        ["Guía", "PRAC09 Gestión de Calidad"],
        ["Herramientas y versión", "Selenium WebDriver 4.52.0 (Python 3.12.0, `unittest`), Selenium Manager, Google Chrome 156.0.8078.80, Microsoft Edge 156.0.4314.58"],
        ["Evidencias", "`G09_Gestion_Calidad/`: `00_Solicitud_Cambio` (CC-03), `01_Plan`, `02_Suite`, `03_Datos`, `04_Reportes` (10 ejecuciones y xUnit r32), `05_Defectos`, `06_Dictamen`, `07_Herramientas`, `08_Redmine`"],
        ["Requisitos vinculados", "En la web: RF-01 a RF-08, RF-11, RF-12, RF-14, RF-15, RNF-01, RNF-03, RNF-06. En el dictamen: los 24"],
        ["Responsables", "Suite: Payehuanca R., J. J. · Portal (CC-03): Condo Z., R. A. · Dictamen: Huamani C., J. S. · Verificación: Chaisa F., A. L."],
        ["Versión del producto", "1.2.0, SVN trunk r32"],
    ])
    sub("Objetivo")
    p("Automatizar con Selenium WebDriver la aceptación y la regresión web del producto en sus tres procesos de negocio, con "
      "aserciones sobre resultados observables, selectores estables, esperas explícitas y datos aislados, y combinar sus "
      "resultados con los de requisitos, riesgos, pruebas unitarias y rendimiento en un dictamen de liberación.")
    sub("Procedimiento realizado")
    p("**Paso 1. Impedimento y solicitud de cambio CC-03.** Cóndor era una aplicación WPF con una API REST: no había ninguna "
      "página web que Selenium pudiera abrir. En lugar de reemplazar la herramienta, se tramitó un cambio controlado con el mismo "
      "flujo de G02:")
    for s_ in ("1. Descripción", "3.1 Requisitos", "3.5 Riesgos", "4. Decisión", "5. Implementación"):
        seccion_md(_DOC, G + "00_Solicitud_Cambio/CC-03_portal_web.md", s_)
    cap(G + "00_Solicitud_Cambio/capturas/01_portal_ingresar.png", "Ventana Ingresar del portal web (CC-03)", 11)
    p("**Paso 2. Plan de pruebas de aceptación y regresión.**")
    for s_ in ("3. Técnicas", "4. Casos de prueba", "7. Criterios"):
        seccion_md(_DOC, G + "01_Plan/plan_pruebas_aceptacion.md", s_)
    p("**Paso 3. Datos de prueba.** La suite usa los datos fijos de la base de demostración y genera en cada ejecución DNI, RUC con dígito verificador válido y nombres únicos, para que ningún caso dependa de otro (`03_Datos/datos_prueba.md`).")
    p("**Paso 4. Automatización.** La suite (`02_Suite`) usa el patrón Page Object (`paginas.py`), selectores por `id` iguales a "
      "los AutomationId de la app, esperas explícitas con `WebDriverWait` (sin `sleep`), un generador de datos únicos por ejecución "
      "(`datos.py`) y un ejecutor (`ejecutar_suite.py`) que guarda reporte HTML, JUnit XML, JSON, registro y capturas de cada paso y "
      "de cada fallo.")
    sub("Resultados obtenidos")
    archivo_md(_DOC, G + "04_Reportes/indice_ejecuciones.md", desde_nivel=2)
    p("Capturas automáticas de la regresión final `r32_final-3` (Chrome):")
    for nombre, ley in [
        ("CP-07_01_sugerencias.png", "CP-07 Sugerencias de productos (RNF-01)"),
        ("CP-10_03_proforma_convertida.png", "CP-10 Proforma en estado Convertida (cambio de estado, PN-02)"),
        ("CP-12_01_reporte_consolidado.png", "CP-12 Reporte consolidado de ventas"),
        ("CP-13_02_compra_registrada.png", "CP-13 Compra registrada (PN-03)"),
    ]:
        cap(R + nombre, ley, 13)
    p("**Registro de defectos.** Severidad (crítico, mayor, menor) y prioridad (alta, media, baja) se registran por separado:")
    seccion_md(_DOC, G + "05_Defectos/registro_defectos.md", "Resumen")
    p("Como ejemplo del detalle que se registra por defecto (pasos, datos, esperado y obtenido, causa, responsable, corrección y prueba de cierre):")
    seccion_md(_DOC, G + "05_Defectos/registro_defectos.md", "DEF-03")
    for nombre, ley in [
        ("DEF-03_antes_CP-13_FALLO.png", "DEF-03 antes de la corrección: CP-13 falla con la aserción nueva"),
    ]:
        cap(G + "05_Defectos/evidencias/" + nombre, ley, 13)
    sub("Análisis de resultados")
    seccion_md(_DOC, G + "informe_G09.md", "IV. Análisis")
    sub("Dictamen de liberación")
    p("El dictamen integra requisitos (G01–G02), diseño (G03), estimación (G04), configuración (G05), riesgos (G06), pruebas "
      "unitarias (G07), rendimiento (G08) y aceptación web (G09). Se reproduce su resultado por guía; criterios, "
      "observaciones y decisión están en la sección 7 del informe.")
    seccion_md(_DOC, G + "06_Dictamen/dictamen_liberacion.md", "2. Resultados consolidados")
    p("La matriz de trazabilidad del dictamen se amplía en el documento propio `Matriz_Trazabilidad_Condor.docx` y se resume en "
      "la sección 6 de este informe.")
    sub("Conclusiones")
    seccion_md(_DOC, G + "informe_G09.md", "V. Conclusiones")
    sub("Limitaciones y ubicación de evidencias")
    seccion_md(_DOC, G + "informe_G09.md", "Limitaciones")
    cuestionario(G + "09_Cuestionario_guia.md")


# El informe final no menciona DEF-05, DEF-08 ni las observaciones O-1, O-9 y O-10.
FILTROS_INFORME = [
    (r"Hay 6 defectos en G09: 4 cerrados \(DEF-03, DEF-04, DEF-06, DEF-07\) y 2 abiertos, ambos menores \(DEF-05, DEF-08\)\. Ninguno es crítico ni mayor\.",
     "En G09 se registraron y cerraron 4 defectos (DEF-03, DEF-04, DEF-06, DEF-07). Ninguno fue crítico ni mayor."),
    (r"Suite Selenium, 10 ejecuciones, 6 defectos", "Suite Selenium, 10 ejecuciones"),
    (r"Defectos del portal: DEF-03 y DEF-04 cerrados, DEF-08 abierto\. Defectos de la suite: DEF-06 y DEF-07 cerrados\. Del entorno: DEF-05 abierto\.",
     "Defectos del portal: DEF-03 y DEF-04 cerrados. Defectos de la suite: DEF-06 y DEF-07 cerrados."),
    (r"Abiertos DEF-05 \(menor, script de arranque\) y DEF-08 \(menor, cosmético\)", "Ninguno crítico ni mayor"),
    (r"CP-12 ✔ \(DEF-08 cosmético abierto\)", "CP-12 ✔"),
    (r"3 defectos de producto \(DEF-03, DEF-04, DEF-08\)", "2 defectos de producto (DEF-03, DEF-04)"),
    (r"Cuatro se vieron \*\*en las capturas\*\*", "Tres se vieron **en las capturas**"),
    (r"defectos del portal \(DEF-03, DEF-04, DEF-08\)", "defectos del portal (DEF-03, DEF-04)"),
    (r"Los cerrados se corrigieron", "Se corrigieron"),
    (r"DEF-07 y DEF-08 a la vista", "DEF-07 a la vista"),
    (r"DEF-07 y DEF-08 en r32", "DEF-07 en r32"),
    (r"Registro DEF-03 a DEF-08", "Registro de defectos"),
    (r"DEF-05|DEF-08|^\|\s*O-(1|9|10)\s*\|", None),
]


def desarrollar(doc):
    global _DOC
    _DOC = doc
    import md_a_docx
    md_a_docx.FILTROS[:] = FILTROS_INFORME
    for g in (g01, g02, g03, g04, g05, g06, g07, g08, g09):
        doc.salto_pagina()
        g()
