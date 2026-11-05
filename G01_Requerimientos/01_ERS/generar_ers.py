"""Genera la ERS (IEEE 830) en Markdown a partir de la misma fuente que usa REMUS.

    python generar_ers.py            -> ERS_Condor_v1.2.md (la versión sale de condor_datos.json)

La fuente única es ../03_REMUS/condor_datos.json: lo que cambie allí cambia a la
vez en el documento de REMUS (generar_rem.ps1) y en esta ERS. Aquí solo viven
las secciones de IEEE 830 que REMUS no modela (perspectiva, interfaces,
supuestos, control de versiones).
"""
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent / "03_REMUS" / "condor_datos.json"

d = json.loads(DATOS.read_text(encoding="utf-8"))
doc = d["documento"]
VERSION = f'{doc["versionMajor"]}.{doc["versionMinor"]}'
SALIDA = AQUI / f"ERS_Condor_v{VERSION}.md"

PRIORIDAD = {"vital": "Alta", "importante": "Media", "quedaría bien": "Baja"}
TECNICAS = {"ENT-01": "Entrevista", "CUE-01": "Cuestionario", "OBS-01": "Observación"}

part = {p["id"]: p["nombre"] for p in d["participantes"]}
obj = {o["id"]: o for o in d["objetivos"]}
act = {a["id"]: a["nombre"] for a in d["actores"]}
uc = {u["id"]: u for u in d["casosUso"]}


def remus_id(logico):
    """UC-07 -> UC-0007, como numera REMUS."""
    pre, num = logico.split("-")
    return f"{pre}-{int(num):04d}"


def fuentes(x):
    nombres = [part[f] for f in x.get("fuentes", [])]
    tec = [TECNICAS[t] for t in x.get("tecnicas", [])]
    s = ", ".join(nombres)
    return s + (f" ({', '.join(tec)})" if tec else "")


def celda(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def parrafo(titulo):
    for p in d["parrafos"]:
        if p["titulo"] == titulo:
            return "\n".join(p["texto"])
    raise KeyError(titulo)


def paso(p):
    if p["tipo"] == "actor":
        return f'El actor **{act[p["actor"]]}** {p["descripcion"]}.'
    if p["tipo"] == "incluye":
        u = uc[p["casoUso"]]
        return f'Se realiza **{u["codigo"]} {u["nombre"]}**.'
    return f'El sistema {p["descripcion"]}.'


L = []
w = L.append

# ------------------------------------------------------------------ portada
w(f"# Especificación de Requisitos de Software (ERS)")
w("")
w("## Sistema de Ventas y Facturación Cóndor — Ferretería Cóndor Majes S.A.C.")
w("")
w("| Campo | Valor |")
w("|---|---|")
w(f"| Versión | **{VERSION}** (línea base vigente) |")
w(f"| Fecha | {doc['fecha']} |")
w("| Estado | Aprobada — línea base final para G02 a G09 |")
w("| Norma de referencia | IEEE Std 830-1998 (referencia académica de estructura) |")
w("| Preparado para | Ferretería Cóndor Majes S.A.C. (Gerente general) |")
w("| Preparado por | Equipo de desarrollo — Calidad de Software 2026-B, EPIS UNSA |")
w("| Herramienta de gestión | REMUS 1.3 (Universidad de Sevilla) — `03_REMUS/condor.rem` |")
w("| Fuente única | `03_REMUS/condor_datos.json` (este documento se genera con `generar_ers.py`) |")
w("")
w("### Control de versiones")
w("")
w("| Versión | Fecha | Autor | Cambios | Estado |")
w("|---|---|---|---|---|")
w("| 0.9 | 2026-10-29 | Equipo (analistas) | Borrador: requisitos derivados del Product Backlog (HU-01 a HU-18) y de la elicitación ENT-01, CUE-01 y OBS-01. | Revisado (ver `07_Revision`) |")
w("| 1.0 | 2026-10-29 | Equipo | Corrección de las 14 observaciones de la revisión. Línea base inicial: acceso con el perfil único MAESTRO, sin credenciales (HU-14). | Línea base |")
w("| 1.1 | 2026-10-30 | Equipo | Solicitud de cambio **CC-01** aprobada: ingreso con usuario, contraseña y roles, backend REST y reporte consolidado (ver Apéndice B). | Línea base |")
w("| 1.2 | 2026-11-04 | Equipo | Solicitud de cambio **CC-03** aprobada: portal web del mostrador sobre `Condor.Api` (interfaz INT-07) para las pruebas de aceptación con Selenium (G09). No cambia los RF ni los RNF; agrega una interfaz y cuatro rutas de la API (ver Apéndice C). | **Línea base vigente** |")
w("")

# ------------------------------------------------------------ 1 introducción
w("## 1. Introducción")
w("")
w("### 1.1 Propósito")
w("")
w(parrafo("Propósito"))
w("")
w("Está dirigido al gerente general (aprobación del alcance), al encargado general y a los vendedores (validación), al contador externo (reglas tributarias), al equipo de desarrollo (diseño, construcción y pruebas) y al docente (validación del alcance académico).")
w("")
w("### 1.2 Alcance")
w("")
w(parrafo("Ámbito del sistema"))
w("")
w("**Beneficios esperados:** atender una venta en menos de un minuto, eliminar los errores de cálculo del IGV, informar a tiempo todos los comprobantes a la SUNAT, saber qué usuario y qué terminal emitió cada comprobante, y disponer de un reporte consolidado de ventas.")
w("")
w("**Procesos de negocio cubiertos:**")
w("")
w(parrafo("Procesos de negocio cubiertos"))
w("")
w("### 1.3 Definiciones, acrónimos y abreviaturas")
w("")
w(parrafo("Definiciones y acrónimos"))
w("")
w("### 1.4 Referencias")
w("")
w(parrafo("Referencias"))
w("")
w("### 1.5 Visión general del documento")
w("")
w("La sección 2 describe el producto en su contexto; la sección 3 especifica los requisitos funcionales, no funcionales, reglas de negocio y requisitos de información; la sección 4 reúne los indicadores medibles; la sección 5 los conflictos y su resolución, y la sección 6 la trazabilidad con objetivos, procesos y pruebas. Los apéndices dan la correspondencia con los identificadores de REMUS y el detalle del cambio de la versión 1.0 a la 1.1.")
w("")

# ------------------------------------------------------- 2 descripción general
w("## 2. Descripción general")
w("")
w("### 2.1 Perspectiva del producto")
w("")
w(parrafo("Situación actual y problema"))
w("")
w("Cóndor reemplaza el cuaderno de ventas, los talonarios y la facturación manual en el portal de la SUNAT. Es un sistema nuevo e independiente que se relaciona con tres sistemas o dispositivos externos:")
w("")
w("```")
w("  PC-1 / PC-2 / PC-3 (CondorVentas.exe, WPF)        Ticketera térmica 80 mm (PC de caja)")
w("            │  HTTP + JWT                                  ▲ ESC/POS por el spooler")
w("            ▼                                              │")
w("  PC principal: Condor.Api (ASP.NET Core 8, :5080) ───────┘")
w("            │  Npgsql                        │  HTTPS (sendBill, getStatusCdr, API de guías)")
w("            ▼                                ▼")
w("  PostgreSQL 16 (base central)        SUNAT (ambiente beta; simulada en las pruebas)")
w("```")
w("")
w("### 2.2 Funciones del producto")
w("")
w("| Proceso | Requisitos funcionales |")
w("|---|---|")
procesos = {}
for u in d["casosUso"]:
    procesos.setdefault(u["proceso"], []).append(f'{u["codigo"]} {u["nombre"]}')
nombres_proc = {"PN-01": "PN-01 Venta y facturación electrónica", "PN-02": "PN-02 Cotización y conversión en venta",
                "PN-03": "PN-03 Abastecimiento", "Consulta": "Consultas e información consolidada",
                "Soporte": "Soporte (acceso, catálogo y respaldo)"}
for k in ["PN-01", "PN-02", "PN-03", "Consulta", "Soporte"]:
    w(f"| {nombres_proc[k]} | {'; '.join(procesos[k])} |")
w("")
w("### 2.3 Características de los usuarios")
w("")
w("| Usuario | Rol en el sistema | Perfil | Frecuencia de uso |")
w("|---|---|---|---|")
w("| Vendedores de mostrador (2 a 3 por turno) | Vendedor | Secundaria completa, manejo básico de PC, conocen los productos; trabajan de pie y con prisa en horas punta. | Todo el turno |")
w("| Encargado general | Encargado general | Técnico o experiencia administrativa; maneja compras, proveedores y guías. | Diaria |")
w("| Gerente general | Encargado general (consulta) | Dueño del negocio; usa el reporte consolidado. | Semanal |")
w("| Contador externo | Sin cuenta | Revisa comprobantes y estados ante la SUNAT a través del encargado. | Mensual |")
w("")
w("### 2.4 Restricciones")
w("")
w("- **Plataforma:** Windows 10/11 en las tres PC; .NET 8; PostgreSQL 16 en la PC principal; red local (LAN) del local.")
w("- **Hardware:** ticketera térmica de 80 mm compatible ESC/POS (página de códigos 850); lector de código de barras que emula teclado.")
w("- **Normativa:** comprobantes electrónicos en formato UBL 2.1 firmados con certificado digital, según la normativa de la SUNAT.")
w("- **Seguridad:** solo la API conoce la clave de la base de datos; las PC acceden a los datos únicamente a través de la API.")
w("- **Académicas:** rutas HTTP evaluables con JMeter, interfaz automatizable para las pruebas de aceptación (G09) y pruebas unitarias con una herramienta equivalente a JUnit (xUnit), aprobada por el docente.")
w("- **Plazo:** entregas el 11-11-2026, el 25-11-2026 y el 02-12-2026.")
w("")
w("### 2.5 Supuestos y dependencias")
w("")
w("- **SUP-01** La PC principal permanece encendida durante el horario de atención (aloja la API y la base de datos).")
w("- **SUP-02** La ferretería obtiene su certificado digital y su usuario SOL antes de pasar a producción; mientras tanto se usa el ambiente beta de la SUNAT.")
w("- **SUP-03** En las pruebas, la SUNAT y la API de guías se sustituyen por **servicios simulados** (`SunatFalsa`, API de guías falsa), documentados en el código de pruebas.")
w("- **SUP-04** El catálogo inicial se carga desde la lista de precios en CSV que entrega la ferretería (`db/datos/lista_precios.csv`).")
w("- **SUP-05** Existe un disco externo conectado a la PC principal para los respaldos.")
w("- **DEP-01** Bibliotecas de terceros: Npgsql, ASP.NET Core, xUnit; la generación del XML UBL se basa en el modelo de Greenter / sunat-manager.")
w("")
w("### 2.6 Fuentes de elicitación")
w("")
w(parrafo("Fuentes de elicitación empleadas"))
w("")

# --------------------------------------------------------- 3 requisitos
w("## 3. Requisitos específicos")
w("")
w("### 3.1 Interfaces externas")
w("")
w("| ID | Tipo | Descripción |")
w("|---|---|---|")
w("| INT-01 | Usuario | Aplicación de escritorio WPF: ventana Ingresar, ventana principal con Nueva venta y módulos F2 a F9 en el panel derecho; operable solo con teclado (atajos F1 a F11, Enter, Esc). |")
w("| INT-02 | Usuario / software | API REST `Condor.Api` (HTTP + JSON, JWT Bearer) con las rutas públicas de `docs/api.md`; la usan JMeter y las integraciones. |")
w("| INT-03 | Hardware | Ticketera térmica de 80 mm por el spooler de Windows (comandos ESC/POS); lector de código de barras como teclado. |")
w("| INT-04 | Software | PostgreSQL 16 mediante Npgsql; migraciones SQL versionadas en `db/migraciones`. |")
w("| INT-05 | Comunicaciones | Servicios web de la SUNAT: `sendBill` y `getStatusCdr` (SOAP) para comprobantes y API REST de guías (OAuth2). |")
w("| INT-06 | Software | `pg_dump` / `pg_restore` para el respaldo y la restauración de la base de datos. |")
w("| INT-07 | Usuario | Portal web del mostrador (CC-03), servido por `Condor.Api` en `http://<PC principal>:5080/`: mismas pantallas, atajos y reglas que INT-01 para venta, catálogo, clientes, historial y proformas, y para el Encargado general compras, proveedores, reporte consolidado y respaldos. Controles con `id` estables para Selenium WebDriver (G09). |")
w("")

# 3.2 RF
w("### 3.2 Requisitos funcionales")
w("")
w("Cada requisito funcional se modela en REMUS como un caso de uso (RF-xx = UC-00xx). Prioridad: Alta = imprescindible para liberar; Media = necesaria, puede diferirse un incremento.")
w("")
w("| ID | Nombre | Descripción | Fuente | Prioridad | Origen |")
w("|---|---|---|---|---|---|")
for u in d["casosUso"]:
    w(f'| **{u["codigo"]}** | {u["nombre"]} | El sistema deberá {celda(u["descripcion"])}. | {celda(fuentes(u))} | {PRIORIDAD[u["importancia"]]} | {u["hu"]} |')
w("")
for u in d["casosUso"]:
    w(f'#### {u["codigo"]} {u["nombre"]}')
    w("")
    w("| Campo | Contenido |")
    w("|---|---|")
    w(f'| Descripción | El sistema deberá {celda(u["descripcion"])}. |')
    w(f'| Proceso | {nombres_proc[u["proceso"]]} |')
    w(f'| Fuente | {celda(fuentes(u))} |')
    w(f'| Prioridad | {PRIORIDAD[u["importancia"]]} (urgencia: {u["urgencia"]}; estabilidad: {u["estabilidad"]}) |')
    w(f'| Objetivos | {", ".join(o + " " + obj[o]["nombre"] for o in u["objetivos"])} |')
    w(f'| Origen | {u["hu"]} — REMUS {remus_id(u["id"])} |')
    w(f'| Evento | Cuando {celda(u["evento"])}. |')
    w(f'| Precondición | {celda(u["precondicion"])} |')
    w(f'| Frecuencia | {u["frecuenciaValor"]} veces por {u["frecuenciaUnidad"]} |')
    w("")
    w("**Flujo principal**")
    w("")
    for i, p in enumerate(u["pasos"], 1):
        w(f"{i}. {paso(p)}")
    w("")
    if u.get("excepciones"):
        w("**Excepciones**")
        w("")
        for e in u["excepciones"]:
            w(f'- Paso {e["paso"]}: si {e["condicion"]}, el sistema {e["accion"]}; el caso de uso {e["terminacion"]}.')
        w("")
    w(f'**Postcondición:** {u["postcondicion"]}')
    w("")
    w("**Criterios de aceptación**")
    w("")
    for i, c in enumerate(u["criterios"], 1):
        w(f'- **CA-{u["codigo"][3:]}.{i}** {c}')
    w("")
    w(f'**Pruebas vinculadas:** {", ".join("`" + t + "`" for t in u["pruebas"])}')
    w("")

# 3.3 RNF
w("### 3.3 Requisitos no funcionales")
w("")
w("| ID | Atributo | Descripción | Fuente | Prioridad |")
w("|---|---|---|---|---|")
for n in d["noFuncionales"]:
    texto = re.sub(r"\*\*(.+?)\*\*", r"**\1**", n["descripcion"])
    w(f'| **{n["codigo"]}** | {n["atributo"]} | El sistema deberá {celda(texto)}. | {celda(fuentes(n) or "Docente del curso")} | {PRIORIDAD[n["importancia"]]} |')
w("")
w("**Criterios de aceptación de los RNF**")
w("")
for n in d["noFuncionales"]:
    for i, c in enumerate(n["criterios"], 1):
        w(f'- **CA-{n["codigo"]}.{i}** {c} Verificación: {", ".join("`" + t + "`" for t in n["pruebas"])}.')
w("")

# 3.4 reglas
w("### 3.4 Reglas de negocio y restricciones")
w("")
w("| ID | Regla | Fuente | Objetivos |")
w("|---|---|---|---|")
for r in d["restricciones"]:
    w(f'| **{r["id"]}** | El sistema deberá respetar: {celda(r["descripcion"])}. | {celda(fuentes(r))} | {", ".join(r["objetivos"])} |')
w("")

# 3.5 información
w("### 3.5 Requisitos de información")
w("")
w("| ID | Concepto | Datos específicos | Ocurrencias (media / máx.) | Vida (media / máx.) |")
w("|---|---|---|---|---|")
for r in d["requisitosInformacion"]:
    w(f'| **{r["id"]}** | {r["nombre"]} | {celda("; ".join(r["datos"]))} | {r["ocurrenciasMedias"]:,} / {r["ocurrenciasMaximas"]:,} | {r["vidaMediaValor"]} / {r["vidaMaxValor"]} {r["vidaMaxUnidad"]} |'.replace(",", " "))
w("")

# 4 indicadores
w("## 4. Indicadores medibles")
w("")
w("| RNF | Atributo | Indicador | Meta | Cómo se mide |")
w("|---|---|---|---|---|")
for n in d["noFuncionales"]:
    w(f'| {n["codigo"]} | {n["atributo"]} | {celda(n["indicador"])} | **{celda(n["meta"])}** | {celda(", ".join(n["pruebas"]))} |')
w("")
w("Línea base de la situación actual (ficha OBS-01): una venta de 3 productos con boleta manual toma una mediana de 2 min 50 s y en 2 de 12 boletas observadas hubo error en el cálculo del IGV. Las metas de RNF-01 y RNF-06 se fijaron contra esa línea base.")
w("")

# 5 conflictos
w("## 5. Conflictos identificados y su resolución")
w("")
w("| ID | Conflicto | Partes | Resolución | Estado |")
w("|---|---|---|---|---|")
for k in d["conflictos"]:
    partes = ", ".join(part[p] for p in k["participantes"])
    w(f'| **{k["id"]}** | **{k["nombre"]}.** {celda(k["descripcion"])} | {partes} | {celda(k["solucion"])} | {k["estado"].capitalize()} |')
w("")

# 6 trazabilidad
w("## 6. Trazabilidad")
w("")
w("### 6.1 Requisitos frente a objetivos")
w("")
cols = [o["id"] for o in d["objetivos"]]
w("| Requisito | " + " | ".join(cols) + " |")
w("|---|" + "---|" * len(cols))
for x in d["casosUso"] + d["noFuncionales"]:
    marcas = ["✔" if c in x["objetivos"] else "" for c in cols]
    w(f'| {x["codigo"]} | ' + " | ".join(marcas) + " |")
w("")
w("### 6.2 Requisitos frente a pruebas")
w("")
w("La matriz de trazabilidad final del trabajo amplía esta tabla con los identificadores de las pruebas de G07, G08 y G09 y su resultado.")
w("")
w("| Requisito | Criterios | Pruebas existentes en el producto | Pruebas previstas en las guías |")
w("|---|---|---|---|")
for x in d["casosUso"] + d["noFuncionales"]:
    exist = [t for t in x["pruebas"] if not t.startswith("G0")]
    prev = [t for t in x["pruebas"] if t.startswith("G0")]
    w(f'| {x["codigo"]} | {len(x["criterios"])} | {", ".join("`" + t + "`" for t in exist) or "—"} | {"; ".join(prev) or "G07 (regresión unitaria)"} |')
w("")

# apéndices
w("## Apéndice A. Correspondencia con los identificadores de REMUS")
w("")
w("| ERS | REMUS | ERS | REMUS |")
w("|---|---|---|---|")
pares = [(u["codigo"], remus_id(u["id"])) for u in d["casosUso"]] + [(n["codigo"], remus_id(n["id"])) for n in d["noFuncionales"]]
mitad = (len(pares) + 1) // 2
for a, b in zip(pares[:mitad], pares[mitad:] + [("", "")]):
    w(f"| {a[0]} | {a[1]} | {b[0]} | {b[1]} |")
w("")
w("Objetivos (OBJ), requisitos de información (IRQ), reglas (CRQ), actores (ACT) y conflictos (CFL) conservan su número con cuatro dígitos en REMUS (OBJ-01 = OBJ-0001).")
w("")
w("## Apéndice B. Cambios de la versión 1.0 a la 1.1 (CC-01)")
w("")
w("| Elemento | Versión 1.0 | Versión 1.1 |")
w("|---|---|---|")
w("| RF-01 | Acceder con el perfil único MAESTRO: el sistema abre Nueva venta sin usuario ni contraseña (HU-14). | **Iniciar sesión** con usuario y contraseña, bloqueo tras 5 intentos y bitácora. |")
w("| RF-02 | — | **Cerrar sesión** (nuevo). |")
w("| RF-03 | — | **Restringir módulos según el rol** (nuevo). |")
w("| RF-07 | El comprobante guarda el usuario MAESTRO. | El comprobante guarda el usuario de la sesión (CRQ-11). |")
w("| RF-15 | — | **Reporte consolidado de ventas** (nuevo, en la API). |")
w("| CRQ-11, CRQ-12 | — | Nuevas reglas de autoría y de funciones exclusivas del Encargado general. |")
w("| RNF-02, RNF-03 | — | Nuevos: capacidad de la API y protección de credenciales. |")
w("| IRQ-08 | — | Nueva información de usuarios y accesos. |")
w("| CFL-01 | Abierto | Resuelto con CC-01. |")
w("")
w("El análisis de impacto, la decisión y el cierre de CC-01 están en `G02_Proceso_Requerimientos`.")
w("")
w("## Apéndice C. Cambios de la versión 1.1 a la 1.2 (CC-03)")
w("")
w("| Elemento | Versión 1.1 | Versión 1.2 |")
w("|---|---|---|")
w("| INT-07 | — | **Portal web del mostrador** (nuevo): interfaz web sobre la misma API, con las reglas de `Condor.Dominio`. |")
w("| RF-01 a RF-08, RF-11, RF-12, RF-14, RF-15 | Criterios verificados en la app de escritorio y en la API. | Los mismos criterios se verifican también en el portal web con la suite Selenium de G09 (casos CP-01 a CP-14). |")
w("| RF-08 | Conversión de la proforma desde la app de escritorio. | Además, `GET /api/proformas` y `POST /api/proformas/{id}/convertir` con las mismas reglas (una sola conversión, sin convertir en otra proforma). |")
w("| RF-12 | Registro de compras desde la app de escritorio. | Además, `GET/POST /api/compras` (solo Encargado) con `ValidadorCompra`. |")
w("| RF-09, RF-10, RF-13, RF-16 | — | Sin cambio: ticketera, envío a la SUNAT, guías y generación del respaldo siguen solo en la app de escritorio. |")
w("")
w("El análisis de impacto, la decisión y el cierre de CC-03 están en `G09_Gestion_Calidad/00_Solicitud_Cambio`.")
w("")

SALIDA.write_text("\n".join(L), encoding="utf-8")
print(f"ERS generada: {SALIDA.name} ({len(d['casosUso'])} RF, {len(d['noFuncionales'])} RNF, "
      f"{len(d['restricciones'])} reglas, {len(d['conflictos'])} conflictos)")
