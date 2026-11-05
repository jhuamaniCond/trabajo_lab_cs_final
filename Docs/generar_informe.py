# -*- coding: utf-8 -*-
"""
generar_informe.py
Informe final del trabajo del 3er parcial (índice de la sección 11 del
enunciado). Antes ejecutar generar_codigo.py.

    python Docs/generar_codigo.py
    python Docs/generar_informe.py
"""

import os

from comun import (DocumentoInforme, Documento, SALIDA, PRODUCTO, CLIENTE, VERSION, ETIQUETA,
                   INTEGRANTES, portada, indice, pie_paginado, figura, informar)
from datos_trazabilidad import filas_resumen

# ----------------------------------------------------------------- figuras
FIGURAS = {
    "fig_organigrama": ("G01_Requerimientos/05_Organizacion/organigrama.png",
                        "Organigrama del equipo: cada integrante ejerce los cuatro roles y lidera sus guías.", 13),
    "fig_cronograma": ("G01_Requerimientos/04_Cronograma/cronograma.png",
                       "Cronograma del proyecto con los tres hitos de entrega (G01, libro cronograma.xlsx).", 16),
    "fig_componentes": ("G03_Analisis_Sistemas/02_UML/07_componentes.png",
                        "Diagrama de componentes del producto 1.2.0 (proyectos .NET y portal web).", 16),
    "fig_despliegue": ("G03_Analisis_Sistemas/02_UML/08_despliegue.png",
                       "Diagrama de despliegue: PC principal con la API, PostgreSQL y el disco de respaldos.", 15),
    "fig_app_portal": ("G09_Gestion_Calidad/00_Solicitud_Cambio/capturas/02_portal_nueva_venta.png",
                       "Pantalla Nueva venta del portal web (CC-03), con el mismo aspecto y los mismos identificadores que la app WPF.", 15),
    "fig_remus": ("G01_Requerimientos/03_REMUS/capturas/02_remus_arbol_requisitos_funcionales.png",
                  "Proyecto condor.rem en REMUS 1.3: árbol de requisitos funcionales.", 14),
    "fig_flujo": ("G02_Proceso_Requerimientos/02_Flujo/flujo_requerimientos.png",
                  "Flujo de estados de un requisito configurado en Redmine.", 15),
    "fig_redmine": ("G02_Proceso_Requerimientos/01_Redmine/capturas/13_historial_RF-03.png",
                    "Historial de la petición RF-03 en Redmine: fecha, responsable y evidencia por transición.", 15),
    "fig_casos_uso": ("G03_Analisis_Sistemas/02_UML/01_casos_uso.png",
                      "Diagrama de casos de uso con los roles Vendedor y Encargado general.", 15),
    "fig_secuencia": ("G03_Analisis_Sistemas/02_UML/03_secuencia_emitir_comprobante.png",
                      "Diagrama de secuencia del proceso crítico Emitir comprobante (CU-01).", 16),
    "fig_nesma": ("G04_Dimensionamiento/03_Capturas/06_nesma_resumen.png",
                  "Resumen del conteo NESMA detallado en el libro estimacion_condor.xlsx (222 PF).", 15),
    "fig_comparativo": ("G04_Dimensionamiento/03_Capturas/16_cuadro_comparativo.png",
                        "Cuadro comparativo de NESMA, COSMIC y COCOMO en el libro editable.", 15),
    "fig_svn": ("G05_Gestion_Configuracion/04_Evidencias/capturas/03_grafico_revisiones.png",
                "Gráfico de revisiones de TortoiseSVN: trunk, ramas DEF-01, MEJ-01 y CC-03 y etiquetas.", 16),
    "fig_conflicto": ("G05_Gestion_Configuracion/04_Evidencias/capturas/06_tortoisemerge_conflicto.png",
                      "Conflicto entre la rama DEF-01 y el trunk (CRQ-14) en TortoiseMerge, resuelto en r11.", 16),
    "fig_pilar": ("G06_Gestion_Riesgos/03_PILAR/capturas/08_pilar_A6_riesgo_actual.png",
                  "Riesgo actual por activo en PILAR Basic 2026.1.1 (fase A.6).", 16),
    "cod_regla_700": ("Docs/figuras/cod_regla_700.png",
                      "Regla CRQ-02 en EmisionComprobante.Errores (src/Condor.Dominio/Ventas). Se omiten las líneas 113 a 130, que tratan la boleta con DNI y la factura.", 16),
    "cod_pu13_pu14": ("Docs/figuras/cod_pu13_pu14.png",
                      "Casos PU-13 y PU-14 de valor límite sobre la regla de S/ 700 (G07, EmisionComprobanteTests.cs).", 16),
    "fig_cobertura": ("G07_Pruebas_Unitarias/03_Reportes/capturas/04_cobertura_paquete_Condor.Dominio_RNF-08.png",
                      "Reporte de cobertura del paquete Condor.Dominio: 95,6 % de líneas (RNF-08).", 15),
    "fig_jmeter": ("G08_Pruebas_Rendimiento/06_Analisis/capturas/02_dashboard_carga_despues.png",
                   "Dashboard HTML de JMeter del escenario de carga esperada sobre la versión 1.1.2.", 16),
    "fig_selenium": ("G09_Gestion_Calidad/04_Reportes/20261104_1919_1.2.0-r32_final-3/capturas/CP-07_02_boleta_emitida.png",
                     "Captura automática de CP-07 en la regresión final r32_final-3: boleta emitida en el portal.", 15),
}
ORDEN = list(FIGURAS)
PASOS = {
    "cod_regla_700": ["Ejecutar `python Docs/generar_codigo.py` (requiere internet para texlive.net)."],
    "cod_pu13_pu14": ["Ejecutar `python Docs/generar_codigo.py`."],
}
PROMPTS = {}


def fig(doc, clave):
    figura(doc, clave, FIGURAS, PASOS, PROMPTS)


def ficha(doc, filas):
    doc.tabla([["Campo", "Contenido"]] + filas, anchos_cm=[4.2, 11.8])


# ======================================================================
def construir():
    doc = DocumentoInforme()
    portada(doc, "INFORME FINAL",
            "Trabajo del 3er parcial: desarrollo de un producto de software con la "
            "aplicación de las nueve guías de laboratorio")
    indice(doc)

    # ------------------------------------------------------------------ 1
    doc.titulo(1, "1. Problema, usuarios y alcance")
    doc.titulo(2, "1.1 Problema")
    doc.parrafo(
        "La **%s** (Majes, Arequipa) vende al público y a obras de construcción desde tres PC de "
        "mostrador. Antes del proyecto las ventas se anotaban en un cuaderno, las boletas se "
        "llenaban a mano en talonarios, los precios se consultaban en una lista impresa que se "
        "desactualizaba y la facturación electrónica se hacía aparte, al final del día, en el "
        "portal de la SUNAT." % CLIENTE)
    doc.parrafo(
        "Eso provocaba colas en horas punta, errores de precio y de cálculo del IGV, comprobantes "
        "informados tarde a la SUNAT, compras sin registro ordenado y ninguna información "
        "consolidada para el gerente. Tampoco se sabía qué vendedor emitía cada comprobante. La "
        "observación OBS-01 midió la línea base: una venta de tres productos con boleta manual "
        "tomaba una **mediana de 2 min 50 s**, y en **2 de 12** boletas observadas el IGV estaba mal "
        "calculado.")
    doc.titulo(2, "1.2 Usuarios e interesados")
    doc.tabla([
        ["Interesado", "Rol en el sistema", "Necesidad principal"],
        ["Vendedores de mostrador (2 a 3 por turno)", "Vendedor", "Vender rápido, solo con teclado, sin calcular el IGV"],
        ["Encargado general", "Encargado general", "Compras, proveedores, guías, respaldos y reporte"],
        ["Gerente general (cliente)", "Encargado general (consulta)", "Saber quién vende, cuánto y desde qué caja"],
        ["Contador externo", "Sin cuenta", "Comprobantes válidos e informados a tiempo a la SUNAT"],
        ["Docente del curso", "—", "Evidencias verificables de las nueve guías"],
    ], anchos_cm=[5.0, 4.0, 7.0])
    doc.parrafo(
        "Las sesiones de elicitación se hicieron con **usuarios representados**: integrantes del "
        "equipo asumieron los papeles de gerente, encargado y vendedores a partir del conocimiento "
        "del negocio recogido en el Product Backlog (HU-01 a HU-18). Se declara así en la ERS.")
    doc.titulo(2, "1.3 Alcance y restricciones")
    doc.parrafo(
        "El producto, **%s %s**, registra las ventas del mostrador, emite boletas, facturas, notas "
        "de venta y proformas, imprime el ticket en la ticketera térmica, envía los comprobantes "
        "electrónicos a la SUNAT, registra proveedores, compras y guías de remisión, ofrece el "
        "historial y un reporte consolidado de ventas y genera respaldos de la base de datos. Tiene "
        "**16 requisitos funcionales y 8 no funcionales** medibles en la línea base final (ERS 1.2), "
        "dos roles de usuario y tres procesos de negocio completos:" % (PRODUCTO, VERSION))
    doc.vinetas([
        "**PN-01 Venta y facturación electrónica:** buscar productos, identificar al cliente, emitir el "
        "comprobante, imprimir el ticket y enviarlo a la SUNAT (RF-05, RF-06, RF-07, RF-09, RF-10).",
        "**PN-02 Cotización y conversión en venta:** emitir una proforma con vigencia de 7 días y "
        "convertirla en venta una sola vez (RF-08, RF-07).",
        "**PN-03 Abastecimiento:** registrar al proveedor y sus compras sin duplicar comprobantes "
        "(RF-11, RF-12).",
    ])
    doc.parrafo(
        "**Fuera de alcance:** control de stock e inventario valorizado, cuentas por cobrar, notas de "
        "crédito y débito, pagos con tarjeta integrados, venta por internet y pantalla de "
        "administración de usuarios. **Restricciones:** Windows 10/11, .NET 8, PostgreSQL 16 en la PC "
        "principal, red local, ticketera ESC/POS de 80 mm y comprobantes UBL 2.1 firmados. **Servicios "
        "externos simulados:** la SUNAT y la API de guías se sustituyen por dobles (`SunatFalsa`, API "
        "de guías falsa) en las pruebas; sin la sección `Sunat` en `condor.json` los comprobantes "
        "quedan PENDIENTE.")
    doc.parrafo(
        "**Beneficio esperado:** atender una venta en menos de un minuto, eliminar los errores de "
        "cálculo del IGV, informar a tiempo todos los comprobantes a la SUNAT, saber qué usuario y "
        "qué terminal emitió cada comprobante y disponer de un reporte consolidado.")

    # ------------------------------------------------------------------ 2
    doc.titulo(1, "2. Objetivos y organización")
    doc.titulo(2, "2.1 Objetivo general")
    doc.parrafo(
        "Desarrollar un sistema de ventas y facturación funcional para la ferretería y aplicar sobre "
        "él los procedimientos de las nueve guías de laboratorio, demostrando con archivos "
        "ejecutables y evidencias verificables cómo se gestiona su calidad desde los requisitos "
        "hasta la entrega.")
    doc.titulo(2, "2.2 Objetivos de negocio (ERS 1.2)")
    doc.tabla([
        ["ID", "Objetivo", "Meta verificable", "Requisitos"],
        ["OBJ-01", "Agilizar la venta en mostrador", "Venta con comprobante en menos de un minuto", "RF-04 a RF-09, RNF-01, RNF-02, RNF-06"],
        ["OBJ-02", "Cumplir con la facturación electrónica", "Envío a la SUNAT dentro de 3 días aunque falle internet", "RF-06, RF-07, RF-10, RF-13, RNF-05"],
        ["OBJ-03", "Controlar el acceso y la trazabilidad", "Usuario y terminal en cada comprobante; funciones por rol", "RF-01 a RF-03, RF-07, RNF-03"],
        ["OBJ-04", "Ordenar el abastecimiento", "Proveedores y compras sin duplicados", "RF-11, RF-12"],
        ["OBJ-05", "Disponer de información consolidada", "Reporte por día, tipo, terminal y usuario", "RF-14, RF-15"],
        ["OBJ-06", "Proteger la información del negocio", "0 registros perdidos; 0 números repetidos o saltados", "RF-16, RNF-04, RNF-07, RNF-08"],
    ], anchos_cm=[1.6, 4.6, 5.4, 4.4])
    doc.titulo(2, "2.3 Organización del equipo")
    doc.parrafo(
        "Por exigencia del enunciado, **cada integrante asume y documenta los cuatro roles**: analista, "
        "desarrollador, responsable de configuración y evaluador de calidad. Además, cada uno lidera "
        "las guías que se le asignan y responde por su evidencia (matriz RACI en "
        "`G01_Requerimientos/05_Organizacion/roles.md`). La %s muestra el organigrama." % ("Figura " + doc.fig("fig_organigrama")))
    doc.tabla([["N.º", "Integrante", "Guías que lidera", "Coordinación"]] +
              [[str(i + 1), n, g, c] for i, (n, g, c) in enumerate(INTEGRANTES)],
              anchos_cm=[1.0, 5.6, 4.2, 5.2])
    fig(doc, "fig_organigrama")
    doc.parrafo(
        "El trabajo se planificó en tres hitos: primer entregable el 11-11-2026 (G01 a G05), segundo el "
        "25-11-2026 (G06 a G09) y entrega final el 02-12-2026. El equipo registró **422 horas** reales "
        "de desarrollo del producto entre el 20 y el 30 de octubre (107, 99, 107 y 109 h por "
        "integrante). La %s resume el cronograma." % ("Figura " + doc.fig("fig_cronograma")))
    fig(doc, "fig_cronograma")

    # ------------------------------------------------------------------ 3
    doc.titulo(1, "3. Arquitectura y descripción del producto")
    doc.parrafo(
        "Cóndor es un sistema C# .NET 8 de arquitectura **cliente – API – base de datos**. La app de "
        "escritorio WPF (`CondorVentas.exe`) y el portal web del mostrador hablan por HTTP con el "
        "backend `Condor.Api` (ASP.NET Core 8, puerto 5080) de la PC principal, que es el único que se "
        "conecta a PostgreSQL 16. Las reglas de negocio viven en `Condor.Dominio`, sin dependencias de "
        "infraestructura, y las usan tanto la app como la API (decisión DD-01). La %s y la %s muestran "
        "los componentes y el despliegue." % ("Figura " + doc.fig("fig_componentes"),
                                              "Figura " + doc.fig("fig_despliegue")))
    fig(doc, "fig_componentes")
    doc.tabla([
        ["Componente", "Responsabilidad", "Requisitos"],
        ["`Condor.Dominio`", "Entidades, reglas (`EmisionComprobante`, `CalculadoraVenta`, validadores, `ServicioAutenticacion`, `ReporteVentas`) y contratos", "Todos los CRQ; RF-01, RF-07, RF-08, RF-12, RF-15"],
        ["`Condor.Presentacion`", "ViewModels MVVM sin dependencias de WPF", "RF-02 a RF-14, RNF-06"],
        ["`Condor.Escritorio`", "Ventanas WPF, atajos F1–F11 y AutomationId estables", "RNF-06"],
        ["`Condor.ClienteApi`", "Repositorios de la app que llaman a `/api/escritorio/*`", "CC-01, RNF-03"],
        ["`Condor.Api`", "JWT, política Encargado, rutas REST, portal web en `wwwroot`", "RF-01, RF-03, RF-15, RNF-02, RNF-03, INT-07"],
        ["`Condor.Datos`", "Repositorios con Npgsql, migraciones V001–V014, respaldo con `pg_dump`", "RNF-04, RNF-07, RF-16"],
        ["`Condor.Sunat`", "XML UBL 2.1, firma, `sendBill` / `getStatusCdr`, guías, reenvío", "RF-10, RF-13, RNF-05"],
        ["`Condor.Impresion`", "Ticket ESC/POS para la ticketera de 80 mm", "RF-09"],
    ], anchos_cm=[3.6, 8.2, 4.2])
    fig(doc, "fig_despliegue")
    doc.parrafo(
        "Los registros se guardan en un volumen persistente de PostgreSQL y se conservan al reiniciar "
        "la app, la API o la PC (RNF-07). Las PC secundarias no conocen la clave de la base: solo "
        "tienen la URL de la API en su `condor.json`. La versión 1.2.0 agrega el **portal web del "
        "mostrador** (CC-03, %s), que reproduce las pantallas de la app con los mismos `id` que sus "
        "AutomationId y no tiene reglas propias: toda validación la aplica la API." % ("Figura " + doc.fig("fig_app_portal")))
    fig(doc, "fig_app_portal")
    doc.tabla([
        ["Versión", "Cambio", "Qué agrega"],
        ["1.0.0", "Línea base", "Catálogo, clientes, proveedores, comprobantes, proformas, ticketera, SUNAT, guías, historial, compras y respaldo"],
        ["1.1.0", "CC-01", "Ingreso con usuario y contraseña, roles Vendedor y Encargado, backend REST con JWT y reporte consolidado"],
        ["1.1.1", "DEF-01", "El servidor toma el precio del catálogo en la ruta de escritorio (CRQ-07) y valida CRQ-14"],
        ["1.1.2", "MEJ-01 (G08)", "Correlativo asignado al final de la transacción para reducir el bloqueo de la serie"],
        ["**1.2.0**", "CC-03 (G09)", "Portal web del mostrador; corrige DEF-03 y DEF-04"],
    ], anchos_cm=[2.0, 3.0, 11.0])

    # ------------------------------------------------------------------ 4
    doc.titulo(1, "4. Herramientas y configuración")
    doc.parrafo(
        "El docente aceptó que cada grupo use su propia tecnología mientras cumpla las actividades de "
        "los laboratorios. El equipo eligió C# .NET 8; como equivalente de JUnit se usa **xUnit** "
        "(sección 5 del enunciado). JMeter y Selenium se mantienen. Cada carpeta de guía tiene su "
        "`fichas_herramientas.md` con nombre, versión exacta, finalidad, instalación, procedencia, "
        "licencia, configuración, ejecución y archivos generados.")
    doc.tabla([
        ["Área (guía)", "Herramienta usada y versión", "Alternativa comparada", "Evidencia"],
        ["Requisitos (G01)", "REMUS 1.3.0.0 (Universidad de Sevilla)", "REM (descarga caída: 404), OSMRT, Gatherspace", "`G01/03_REMUS/condor.rem`"],
        ["Cambios (G02)", "Redmine 7.0.1 en Docker", "OSMRT, Gatherspace, GitHub Issues", "`G02/01_Redmine/respaldo/redmine.db`"],
        ["Modelado (G03)", "PlantUML 1.2024.7 (UML y mockups Salt)", "diagrams.net, Moqups", "`G03/02_UML/*.puml`, `03_Mockups/*.puml`"],
        ["Estimación (G04)", "Microsoft Excel 16.0 + openpyxl 3.1.5", "LibreOffice Calc", "`G04/01_Libro/estimacion_condor.xlsx`"],
        ["Configuración (G05)", "Apache Subversion 1.14.5 y TortoiseSVN 1.14.9", "Git y GitHub (comparativo)", "`G05/02_Repositorio/condor`"],
        ["Riesgos (G06)", "PILAR Basic 2026.1.1 (MAGERIT v3)", "RiskyProject, Pirani, RMAT", "`G06/03_PILAR/CONDOR.mgr`"],
        ["Pruebas unitarias (G07)", "xUnit 2.9.2, coverlet 6.0.2, ReportGenerator 5.3.11", "NUnit, MSTest", "`G07/01_Suite`, `03_Reportes`"],
        ["Rendimiento (G08)", "Apache JMeter 5.6.3, typeperf, pg_stat_activity", "k6, Gatling", "`G08/02_Scripts/condor_rendimiento.jmx`"],
        ["Aceptación web (G09)", "Selenium WebDriver 4.52.0 (Python 3.12), Chrome y Edge 156", "Playwright, Appium/WinAppDriver", "`G09/02_Suite`"],
        ["Producto", ".NET SDK 8.0.425, PostgreSQL 16.15, Docker Desktop 29.7.2", "—", "`Sistema_Logistico_Condor_final`"],
    ], anchos_cm=[3.0, 5.0, 4.0, 4.0])
    doc.titulo(2, "4.1 Impedimentos y sustituciones")
    doc.vinetas([
        "**REM (G01):** el enlace de descarga de la guía responde 404 (`G01/06_Herramientas/impedimento_REM_404.png`). "
        "Se usó REMUS, sucesor de REM de la misma universidad, con el mismo modelo de requisitos.",
        "**JUnit (G07):** el producto es C#; se usa xUnit, el equivalente para .NET, con la misma estructura de "
        "aserciones y dobles de prueba. Validación del docente: uso de tecnologías propias.",
        "**Selenium sobre una app WPF (G09):** Selenium necesita un navegador y WinAppDriver no se mantiene desde "
        "2020. Se tramitó la solicitud de cambio **CC-03** para agregar un portal web sobre la misma API.",
        "**RMAT (G06):** no se identifica de manera inequívoca; se interpretó como la herramienta del "
        "ecosistema EAR/PILAR y se registró la limitación para validación docente.",
    ])

    # ------------------------------------------------------------------ 5
    doc.titulo(1, "5. Desarrollo de las guías G01 a G09")
    doc.parrafo(
        "Cada guía mantiene la estructura de los adjuntos: objetivo, procedimiento realizado, "
        "resultados, análisis y conclusiones, con herramienta y versión, ubicación de evidencias, "
        "requisitos vinculados y limitaciones. Al final de cada guía se responde su cuestionario "
        "aplicado al producto, justificando los puntos no aplicables. Las tablas y textos de detalle se "
        "toman de los documentos de evidencia de cada carpeta (G01 a G09), que se citan en cada paso.")

    import guias
    guias.desarrollar(doc)
    doc.salto_pagina()

    # ------------------------------------------------------------------ 6
    doc.titulo(1, "6. Trazabilidad y resultados consolidados")
    doc.parrafo(
        "La matriz de trazabilidad completa se entrega como **documento propio** "
        "(`Docs/salida/Matriz_Trazabilidad_Condor.docx`), con una fila por requisito y una fila por prueba, "
        "diseño, riesgos, cambios y versión probada. Este es su resumen:")
    doc.tabla([["Requisito", "Nombre", "Tipos de prueba", "Estado en 1.2.0"]] + filas_resumen(),
              anchos_cm=[1.8, 5.6, 5.2, 3.4])
    doc.titulo(2, "6.1 Resultados consolidados de pruebas")
    doc.tabla([
        ["Suite", "Versión", "Resultado"],
        ["xUnit del producto (unitarias, integración y aceptación)", "1.2.0, trunk r32", "944 aprobadas, 0 fallidas, 5 omitidas (requieren base)"],
        ["Suite G07 (27 casos PU)", "1.1.1", "43/43; cobertura de Condor.Dominio 95,6 %"],
        ["Controles de G06", "1.1.1", "18/18 comprobaciones"],
        ["JMeter, carga esperada (RNF-02)", "1.1.1 y 1.1.2", "p95 11–12 ms y 21–22 ms; 0 % de error"],
        ["Selenium (14 casos)", "1.2.0, trunk r32", "14/14 en Chrome ×2 y en Edge"],
    ], anchos_cm=[6.6, 3.4, 6.0])
    doc.titulo(2, "6.2 Registro de defectos")
    doc.parrafo("Severidad (crítico, mayor, menor) y prioridad se registran por separado. El detalle con pasos, datos, resultado esperado y obtenido, responsable, corrección y prueba de cierre está en `G09_Gestion_Calidad/05_Defectos/registro_defectos.md`.")
    doc.tabla([
        ["ID", "Origen", "Requisito", "Severidad / prioridad", "Estado", "Corrección y cierre"],
        ["DEF-01", "Revisión del SDD (G03)", "RF-07", "Mayor / alta", "Cerrado", "1.1.1, r11; ClienteApiTests"],
        ["DEF-02", "Defecto controlado (G07)", "RF-07", "— (controlado)", "Restaurado", "PU-13 falla y pasa al restaurar"],
        ["DEF-03", "Capturas de Selenium", "RF-12", "Menor / media", "Cerrado", "r31; CP-13"],
        ["DEF-04", "Capturas de Selenium", "RF-08", "Menor / baja", "Cerrado", "r31; CP-10"],
        ["DEF-06", "Suite G09", "—", "Menor / alta", "Cerrado", "Esperas que ignoran elementos obsoletos"],
        ["DEF-07", "Suite G09", "RF-12", "Menor / alta", "Cerrado", "Espera por la búsqueda actual"],
    ], anchos_cm=[1.6, 3.6, 1.8, 3.2, 2.0, 3.8])

    # ------------------------------------------------------------------ 7
    doc.titulo(1, "7. Evaluación de cumplimiento y decisión de liberación")
    doc.tabla([
        ["#", "Criterio de liberación", "Resultado", "¿Cumple?"],
        ["C1", "Todos los RF y RNF con una prueba aprobada", "24/24", "Sí"],
        ["C2", "Suite xUnit sin fallos en la versión evaluada", "944/0/5", "Sí"],
        ["C3", "Selenium 14/14 en la versión final, repetible", "Chrome ×2 y Edge", "Sí"],
        ["C4", "Tres procesos demostrados de punta a punta", "CP-07/08, CP-10, CP-13", "Sí"],
        ["C5", "Ningún defecto crítico o mayor abierto", "Ninguno crítico ni mayor", "Sí"],
        ["C6", "Umbral de rendimiento contrastado con datos", "RNF-02 cumplido", "Sí"],
        ["C7", "Riesgos con respuesta; controles con prueba", "S1–S3 verificados; S4–S11 propuestos", "Sí, con O-3"],
        ["C8", "La versión entregada coincide con una etiqueta", "`tags/v1.0.1` (r44)", "Sí"],
    ], anchos_cm=[1.0, 7.0, 5.0, 3.0])
    doc.parrafo("**Lista de verificación de entrega (sección 13 del enunciado).**")
    doc.tabla([
        ["Comprobación", "Estado", "Evidencia"],
        ["El producto se instala y ejecuta con las instrucciones entregadas", "Sí", "README, Manual técnico"],
        ["Los tres procesos pueden demostrarse y los requisitos tienen pruebas", "Sí", "Matriz de trazabilidad"],
        ["G01 a G09 incluyen evidencia propia e identifican la versión probada", "Sí", "Carpetas G01–G09; manifiesto"],
        ["Cambios, riesgos, defectos y limitaciones documentados", "Sí", "G02, G06, registro de defectos, sección 8"],
        ["La etiqueta final, el código y la versión demostrada coinciden", "Sí", "`tags/v1.0.1` = producto 1.2.0"],
        ["Las pruebas se ejecutan sin ocultar fallos y el dictamen las refleja", "Sí", "Ejecuciones anuladas por DEF-07 conservadas"],
    ], anchos_cm=[7.6, 4.0, 4.4])
    doc.parrafo("**Decisión: APTO CON OBSERVACIONES.** Ninguna observación impide los tres procesos de negocio; O-2 debe resolverse antes de instalar en el local.", negrita=False)
    doc.tabla([
        ["ID", "Observación", "Responsable", "Plazo"],
        ["O-2", "API y portal por HTTP en la LAN (R12); implantar S10 (HTTPS)", "Payehuanca R., J. J.", "Antes de instalar (2026-12-10)"],
        ["O-3", "Salvaguardas S4–S11 propuestas", "Responsables del plan de G06", "Fechas del plan"],
        ["O-4", "RNF-06: cronometrar a un vendedor real con la 1.2.0", "Huamani C., J. S.", "Sustentación"],
        ["O-6", "Capacidad limitada por el COMMIT con la serie bloqueada", "Condo Z., R. A.", "Sin plazo (supera la necesidad)"],
        ["O-7", "RF-09, RF-10, RF-13 y RF-16 sin prueba web: demostrarlos en la app", "Huamani C., J. S.", "Sustentación"],
        ["O-8", "Commits de CC-03 y G09 con la cuenta `rcondo`", "Payehuanca R., J. J.", "—"],
    ], anchos_cm=[1.2, 8.0, 3.6, 3.2])
    doc.parrafo("La observación O-5 (falta de etiqueta de la entrega) quedó cerrada el 4-11-2026 con `tags/v0.2.0` y `tags/v1.0.1`.")

    # ------------------------------------------------------------------ 8
    doc.titulo(1, "8. Conclusiones y mejoras")
    doc.titulo(2, "8.1 Conclusiones")
    doc.numerada([
        "Se desarrolló un producto funcional (%s) con 16 RF y 8 RNF, dos roles y tres procesos de negocio completos, "
        "con autenticación, autorización por roles, validaciones, registro y consulta, reporte consolidado y "
        "persistencia tras reinicios." % VERSION,
        "Las nueve guías se aplicaron al mismo producto y cada una dejó evidencia propia, con la versión probada identificada.",
        "La gestión de cambios funcionó en ambos sentidos: CC-01 y CC-03 se aprobaron e implementaron con todo el ciclo "
        "(ERS, diseño, código, pruebas, rama SVN, cierre) y CC-02 se rechazó con sustento.",
        "Las técnicas de calidad se complementaron: la revisión del SDD halló DEF-01, que ninguna prueba detectaba; los "
        "valores límite detectaron DEF-02; JMeter localizó el cuello de botella de la serie; y la revisión de las capturas "
        "de Selenium halló defectos que las aserciones dejaban pasar.",
        "Todos los requisitos tienen al menos una prueba aprobada en la versión entregada y no queda abierto ningún "
        "defecto crítico ni mayor: el dictamen es apto con observaciones.",
        "COCOMO II sin calibrar sobreestimó el esfuerzo de este equipo unas 16 veces; el tamaño funcional sí fue correcto. "
        "La constante calibrada (A = 0,185) sirve, con prudencia, para los próximos incrementos.",
    ])
    doc.titulo(2, "8.2 Mejoras propuestas")
    doc.vinetas([
        "Implantar HTTPS en la LAN (S10) y el resto de salvaguardas propuestas (S4–S11).",
        "Agregar aserciones visuales o de diseño a la suite Selenium para no depender solo de la revisión manual de capturas.",
        "Llevar al portal web las guías de remisión y la generación del respaldo para cubrirlos con pruebas web.",
        "Reducir el tramo bloqueado del COMMIT (WAL en disco de baja latencia, series por terminal o `commit_delay`) si el local crece.",
        "Cronometrar a vendedores reales (RNF-06) y repetir la elicitación con usuarios no representados.",
    ])

    # ------------------------------------------------------------------ 9
    doc.titulo(1, "9. Referencias y anexos")
    doc.titulo(2, "9.1 Referencias")
    doc.vinetas([
        "Silva Fernández, J. M. Guías de laboratorio PRAC01 a PRAC09 de Calidad de Software, semestre 8, UNSA.",
        "IEEE Std 830-1998, *IEEE Recommended Practice for Software Requirements Specifications*.",
        "IEEE Std 1016-2009, *IEEE Standard for Information Technology — Software Design Descriptions*.",
        "NESMA. *Definitions and counting guidelines for the application of function point analysis*, versión 2.x.",
        "COSMIC. *The COSMIC Functional Size Measurement Method, Measurement Manual*, versión 4.0.2.",
        "Boehm, B. et al. *COCOMO II Model Definition Manual*, versión 2000.",
        "QSM. *Function Point Languages Table*, versión 5.0.",
        "Ministerio de Hacienda y Administraciones Públicas. *MAGERIT v3: Metodología de Análisis y Gestión de Riesgos*, libros I a III, 2012.",
        "CCN-CERT. PILAR — https://pilar.ccn-cert.cni.es/pilar/",
        "JUnit User Guide — https://docs.junit.org/6.0.0/writing-tests/assertions.html (equivalencias con xUnit).",
        "Apache JMeter Best Practices — https://jmeter.apache.org/usermanual/best-practices.html",
        "Selenium WebDriver — https://www.selenium.dev/documentation/webdriver/",
        "SUNAT. Resolución de Superintendencia N.° 097-2012/SUNAT y modificatorias (comprobantes electrónicos).",
    ])
    doc.titulo(2, "Anexo A. Ubicación de las evidencias")
    doc.tabla([
        ["Entregable", "Ubicación"],
        ["Informe final (editable y PDF)", "`Docs/salida/Informe_Final_Condor.docx` y `.pdf`"],
        ["Manual de usuario y manual técnico", "`Docs/salida/Manual_Usuario_Condor.docx`, `Manual_Tecnico_Condor.docx`"],
        ["Matriz de trazabilidad", "`Docs/salida/Matriz_Trazabilidad_Condor.docx`"],
        ["Registro de defectos y dictamen", "`G09_Gestion_Calidad/05_Defectos`, `06_Dictamen`"],
        ["Código fuente, migraciones y datos de prueba", "`Sistema_Logistico_Condor_final/src`, `db/migraciones`, `herramientas/Condor.DatosDemo`"],
        ["README con instalación, credenciales y comandos", "`Sistema_Logistico_Condor_final/README.md`"],
        ["Carpetas por guía", "`G01_Requerimientos` a `G09_Gestion_Calidad`"],
        ["Repositorio SVN portable", "`G05_Gestion_Configuracion/02_Repositorio/condor` y `03_Respaldo/condor_r44.dump.gz`"],
        ["Guiones que generan estos documentos", "`Docs/generar_*.py`, `Docs/exportar_pdf.py`"],
    ], anchos_cm=[6.0, 10.0])
    doc.titulo(2, "Anexo B. Manifiesto de versiones")
    doc.tabla([
        ["Evidencia", "Revisión SVN", "Versión del producto"],
        ["G01 a G04", "r3 a r6", "1.1.0"],
        ["Rama DEF-01, fusión con conflicto y cierre", "r8 a r12", "1.1.0 → 1.1.1"],
        ["Línea base del avance 1", "`tags/v0.1.0` (r16)", "1.1.1"],
        ["G06 (riesgos y controles)", "r20", "1.1.1"],
        ["G07 (suite, cobertura, defecto controlado)", "r21 a r22", "1.1.1"],
        ["Rama MEJ-01 e integración en trunk", "r23 a r25", "1.1.1 → 1.1.2"],
        ["G08 (rendimiento)", "r26 a r27", "1.1.1 y 1.1.2"],
        ["CC-03 (rama r28–r31) y G09", "r28 a r34", "1.2.0"],
        ["Línea base del avance 2 / entrega final", "`tags/v0.2.0` (r41) / `tags/v1.0.0` (r35)", "1.2.0"],
        ["**Entrega final corregida (versión entregada)**", "**`tags/v1.0.1` (r44)**", "**1.2.0**"],
    ], anchos_cm=[7.0, 5.0, 4.0])
    doc.titulo(2, "Anexo C. Cuestionarios de las guías")
    doc.parrafo("Los cuestionarios de cada guía se respondieron sobre el producto; los puntos no aplicables están justificados en el mismo archivo:")
    doc.vinetas([
        "`G01_Requerimientos/08_Cuestionario_guia.md`", "`G02_Proceso_Requerimientos/07_Cuestionario_guia.md`",
        "`G03_Analisis_Sistemas/06_Cuestionario_guia.md`", "`G04_Dimensionamiento/05_Cuestionario_guia.md`",
        "`G05_Gestion_Configuracion/07_Cuestionario_guia.md`", "`G06_Gestion_Riesgos/07_Cuestionario_guia.md`",
        "`G07_Pruebas_Unitarias/08_Cuestionario_guia.md`", "`G08_Pruebas_Rendimiento/09_Cuestionario_guia.md`",
        "`G09_Gestion_Calidad/09_Cuestionario_guia.md`",
    ])
    doc.titulo(2, "Anexo D. Componentes de terceros")
    doc.tabla([
        ["Componente", "Uso", "Licencia"],
        [".NET 8, ASP.NET Core, WPF", "Plataforma de la app y la API", "MIT"],
        ["Npgsql", "Acceso a PostgreSQL", "PostgreSQL License"],
        ["PostgreSQL 16", "Base de datos central", "PostgreSQL License"],
        ["xUnit, coverlet, ReportGenerator", "Pruebas y cobertura", "Apache 2.0 / MIT"],
        ["Modelo UBL de Greenter / sunat-manager", "Referencia para el XML UBL 2.1", "MIT"],
        ["Apache JMeter, Selenium WebDriver", "Pruebas de rendimiento y aceptación", "Apache 2.0"],
        ["Redmine, Subversion, TortoiseSVN, PlantUML", "Herramientas de las guías", "GPL v2 / Apache 2.0 / GPL"],
        ["PILAR Basic, REMUS", "Herramientas de las guías", "Licencia de evaluación / académica"],
    ], anchos_cm=[6.0, 6.0, 4.0])
    doc.titulo(2, "Anexo E. Declaración de asistencia de IA")
    doc.parrafo(
        "Cada integrante usó un asistente de IA distinto como herramienta de apoyo:")
    doc.tabla([
        ["Integrante", "Asistente de IA"],
        ["Huamani Condori, Jeanpiero Sixto", "Claude (Anthropic)"],
        ["Payehuanca Riquelme, Jhastyn Jefferson", "DeepSeek"],
        ["Condo Zamata, Richard Alberto", "Codex (OpenAI)"],
        ["Chaisa Fernández, Anthony Leonel", "Codex (OpenAI)"],
    ], anchos_cm=[8.0, 8.0])
    doc.parrafo(
        "La IA se usó principalmente para ayudar a localizar y corregir defectos y para generar fragmentos de "
        "código. La mayor parte del trabajo la hicieron los integrantes: el análisis del negocio, los requisitos, "
        "el diseño, la aplicación de las nueve guías, la ejecución de las pruebas y la revisión de sus resultados. "
        "El equipo revisó y validó todo lo que se apoyó en la IA, y las cifras del informe provienen de los "
        "archivos de resultados de cada guía (.trx, .jtl, resultados.json, libros de Excel), no de las "
        "herramientas de IA.")

    pie_paginado(doc, "Informe final — Sistema Cóndor %s" % VERSION)
    os.makedirs(SALIDA, exist_ok=True)
    salida = os.path.join(SALIDA, "Informe_Final_Condor.docx")
    doc.guardar(salida)
    informar(salida)


if __name__ == "__main__":
    construir()
