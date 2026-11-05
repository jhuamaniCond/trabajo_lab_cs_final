# -*- coding: utf-8 -*-
"""
datos_trazabilidad.py
Fuente única de la matriz de trazabilidad (ERS 1.2: 16 RF y 8 RNF) que usan
generar_matriz_trazabilidad.py y generar_informe.py.

Orígenes de cada dato:
  - requisito, proceso, fuente, prioridad, objetivo: ERS 1.2 (secciones 3.2, 3.3 y 6.1)
  - diseño (clases, tablas, pantalla): SDD 1.1, sección 7
  - pruebas unitarias PU-xx: G07_Pruebas_Unitarias/02_Catalogo/catalogo_casos_prueba.xlsx
  - pruebas del producto (xUnit): ERS 1.2 sección 6.2 y dictamen de G09, sección 3
  - G06 (riesgos y salvaguardas): G06_Gestion_Riesgos/02_Matriz_y_Tratamiento
  - G08: G08_Pruebas_Rendimiento/06_Analisis/analisis_resultados.md
  - G09 (CP-xx): G09_Gestion_Calidad/01_Plan y 06_Dictamen
  - cambios y defectos: G02, G05, G09 (CC-01, CC-02, CC-03, DEF-01 a DEF-07, MEJ-01)
"""

# Cada prueba: (tipo, identificador, evidencia, versión probada, resultado)
X = "xUnit producto"
U = "Unitaria G07"
R = "Rendimiento G08"
C = "Control G06"
S = "Selenium G09"
M = "Medición"

XUNIT = "G09/04_Reportes/xunit_1.2.0-r32 (944 aprob., 0 fall., 5 omit.)"
G07E1 = "G07/03_Reportes/ejecucion_v1.1.1 (43/43)"
SEL = "G09/04_Reportes r32_final-3, r32_final-4, r32_edge-2 (14/14)"
G06V = "G06/04_Controles/verificacion_controles.md (18/18)"
G08C = "G08/04_Resultados/2_despues/carga (JMeter, .jtl y HTML)"

REQUISITOS = [
    dict(id="RF-01", nombre="Iniciar sesión", proceso="Soporte", prioridad="Alta",
         fuente="Gerente general, Encargado (ENT-01)", objetivo="OBJ-03",
         diseno="`ServicioAutenticacion`, `HashClave`, `LoginViewModel` · tablas `usuario`, `acceso_usuario` · M01",
         riesgo="R02, R12 (S1)", cambio="CC-01 (ERS 1.1, producto 1.1.0)",
         pruebas=[(U, "PU-19, PU-21", G07E1, "1.1.1", "Aprobada"),
                  (X, "ServicioAutenticacionTests, LoginViewModelTests, UsuarioRepositorioTests, ApiTests", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S1: bloqueo al 5.º intento (423)", G06V, "1.1.1", "Cumple"),
                  (S, "CP-01 acceso correcto, CP-02 credenciales inválidas", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-02", nombre="Cerrar sesión", proceso="Soporte", prioridad="Media",
         fuente="Encargado (ENT-01, OBS-01)", objetivo="OBJ-03",
         diseno="`MainViewModel` (Cerrar sesión) · M02 (menú)",
         riesgo="R02", cambio="CC-01",
         pruebas=[(X, "CC01_IngresoConRolesTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-14 cierre de sesión", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-03", nombre="Restringir módulos según el rol", proceso="Soporte", prioridad="Alta",
         fuente="Gerente, Encargado (ENT-01)", objetivo="OBJ-03",
         diseno="`Roles`, `PermisosModulo`, política `Encargado` · `usuario.rol` · M05",
         riesgo="R01, R02 (S1)", cambio="CC-01; CC-03 (portal)",
         pruebas=[(X, "CC01_IngresoConRolesTests, ApiTests, PortalWebTests (403)", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S1: 6 de 6 rutas del Encargado responden 403 al Vendedor", G06V, "1.1.1", "Cumple"),
                  (S, "CP-03 restricción por rol; CP-12, CP-13 (Encargado)", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-04", nombre="Registrar producto en el catálogo", proceso="Soporte", prioridad="Alta",
         fuente="Encargado, Vendedores (ENT-01, CUE-01)", objetivo="OBJ-01",
         diseno="`ValidadorProducto`, `NuevoProductoViewModel`, `ProductoRepositorio` · `producto`",
         riesgo="R11", cambio="—",
         pruebas=[(X, "HU01_RegistrarProductoTests, HU13_LectorCodigoBarrasTests, ValidadorProductoTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-05 datos inválidos (precio 0, nombre vacío), CP-06 producto válido", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-05", nombre="Buscar producto para la venta", proceso="PN-01", prioridad="Alta",
         fuente="Vendedores (CUE-01, OBS-01)", objetivo="OBJ-01",
         diseno="`BuscadorProductoViewModel`, `IConsultaProductos` · `producto` (índice trigram) · M02",
         riesgo="—", cambio="—",
         pruebas=[(X, "HU02_BuscarProductoTests, HU13_LectorCodigoBarrasTests", XUNIT, "1.2.0", "Aprobada"),
                  (R, "T1 Consultar productos: p95 11–12 ms, 0 % error", G08C, "1.1.1 y 1.1.2", "Cumple"),
                  (S, "CP-05, CP-06, CP-07 (sugerencias)", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-06", nombre="Registrar y buscar cliente por DNI o RUC", proceso="PN-01", prioridad="Alta",
         fuente="Vendedores, Contador (CUE-01, OBS-01)", objetivo="OBJ-01, OBJ-02",
         diseno="`ValidadorDocumento`, `ClienteVentaViewModel` · `cliente` · M02",
         riesgo="R11", cambio="—",
         pruebas=[(U, "PU-07 a PU-12 (RUC módulo 11, DNI de 8 dígitos)", G07E1, "1.1.1", "Aprobada"),
                  (X, "HU03_ClienteTests, ValidadorDocumentoTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-04 cliente válido, CP-05 DNI/RUC inválidos, CP-08", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-07", nombre="Emitir comprobante de venta", proceso="PN-01", prioridad="Alta",
         fuente="Gerente, Vendedores, Contador (ENT-01, CUE-01, OBS-01)", objetivo="OBJ-01 a OBJ-03",
         diseno="CU-01 · `EmisionComprobante`, `CalculadoraVenta`, `ComprobanteRepositorio` · `serie`, `comprobante`, `comprobante_detalle` · M02",
         riesgo="R03 (S2), R11", cambio="DEF-01 (1.1.1), MEJ-01 (1.1.2)",
         pruebas=[(U, "PU-01 a PU-06, PU-13 a PU-16 (IGV, límites, S/ 700, factura)", G07E1, "1.1.1", "Aprobada"),
                  (U, "DEF-02 controlado: PU-13 falla con «>=» y pasa al restaurar", "G07/04_Defecto_Controlado", "1.1.1 + DEF-02", "Falla esperada / Aprobada"),
                  (X, "HU05_*, HU06_*, HU08_*, EmisionComprobanteTests, ClienteApiTests (DEF-01)", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S2: precio manipulado S/ 0.10 → se guarda S/ 30.80; 4 rechazos 400", G06V, "1.1.1", "Cumple"),
                  (R, "T2 Registrar boleta: p95 21–22 ms, 0 % error", G08C, "1.1.1 y 1.1.2", "Cumple"),
                  (S, "CP-07 boleta, CP-08 factura, CP-09 reglas de emisión", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-08", nombre="Emitir proforma y convertirla en venta", proceso="PN-02", prioridad="Media",
         fuente="Gerente, Vendedores (ENT-01, CUE-01)", objetivo="OBJ-01",
         diseno="CU-02 · `ProformasViewModel`, `EmisionComprobante` · `comprobante.proforma_id` · M03",
         riesgo="R03", cambio="CC-03 (rutas de proformas); DEF-04 (r31)",
         pruebas=[(U, "PU-17 (ya convertida), PU-18 (vigencia 7 días)", G07E1, "1.1.1", "Aprobada"),
                  (X, "HU09_ProformasTests, PortalWebTests (conversión, doble conversión)", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-10 cambio de estado Vigente → Convertida", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-09", nombre="Imprimir y reimprimir el ticket", proceso="PN-01", prioridad="Alta",
         fuente="Vendedores (OBS-01)", objetivo="OBJ-01",
         diseno="`FormatoTicket`, `MontoEnLetras`, `ImpresoraWindows` · `comprobante.impresiones`",
         riesgo="—", cambio="—",
         pruebas=[(X, "HU12_ImprimirTicketTests, HU18_HistorialTests, Impresion/*, MontoEnLetras", XUNIT, "1.2.0", "Aprobada"),
                  (M, "Sin prueba web: solo app de escritorio (observación O-7)", "Demostración en la sustentación", "1.2.0", "Pendiente de demostración")]),
    dict(id="RF-10", nombre="Enviar comprobantes a la SUNAT y reenviar pendientes", proceso="PN-01", prioridad="Alta",
         fuente="Gerente, Contador (ENT-01)", objetivo="OBJ-02",
         diseno="`ServicioEnvioSunat`, `ReenvioPendientes` · `comprobante_sunat` · pie de M02",
         riesgo="R04, R07", cambio="—",
         pruebas=[(X, "HU07_EnviarSunatTests, HU17_ReenvioAutomaticoTests, Sunat/* (SUNAT simulada)", XUNIT, "1.2.0", "Aprobada"),
                  (M, "Sin prueba web; SUNAT beta sin configurar (O-7)", "Demostración en la sustentación", "1.2.0", "Pendiente de demostración")]),
    dict(id="RF-11", nombre="Registrar proveedor", proceso="PN-03", prioridad="Media",
         fuente="Encargado (ENT-01)", objetivo="OBJ-04",
         diseno="`ValidadorProveedor`, `NuevoProveedorViewModel` · `proveedor` · M04",
         riesgo="R01 (S1)", cambio="—",
         pruebas=[(X, "HU04_ProveedoresTests, ValidadorProveedorTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-13 proveedor registrado y RUC repetido rechazado", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-12", nombre="Registrar compra a proveedor", proceso="PN-03", prioridad="Media",
         fuente="Encargado, Contador (ENT-01)", objetivo="OBJ-04",
         diseno="CU-03 · `ValidadorCompra`, `NuevaCompraViewModel`, `CompraRepositorio` · `compra`, `compra_detalle` · M04",
         riesgo="R01 (S1)", cambio="CC-03 (rutas de compras); DEF-03 (r31)",
         pruebas=[(X, "HU11_ComprasTests, ValidadorCompraTests, PortalWebTests (409, 400, 403)", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-13 compra S/ 205.00, compra repetida y fecha futura", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-13", nombre="Emitir guía de remisión electrónica", proceso="PN-01", prioridad="Media",
         fuente="Encargado, Contador (ENT-01)", objetivo="OBJ-02",
         diseno="`ValidadorGuia`, `ServicioGuiaSunat`, `GuiasViewModel` · `guia_remision`, `guia_detalle`",
         riesgo="—", cambio="—",
         pruebas=[(X, "HU10_GuiasRemisionTests, ValidadorGuiaTests", XUNIT, "1.2.0", "Aprobada"),
                  (M, "Sin prueba web: solo app de escritorio (O-7)", "Demostración en la sustentación", "1.2.0", "Pendiente de demostración")]),
    dict(id="RF-14", nombre="Consultar historial de ventas", proceso="Consultas", prioridad="Media",
         fuente="Encargado, Vendedores (ENT-01, CUE-01)", objetivo="OBJ-05",
         diseno="`ComprobanteRepositorio.BuscarAsync` · `comprobante`",
         riesgo="—", cambio="—",
         pruebas=[(X, "HU18_HistorialTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-07 (boleta en el historial), CP-11 filtros y período invertido", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-15", nombre="Generar reporte consolidado de ventas", proceso="Consultas", prioridad="Media",
         fuente="Gerente (ENT-01)", objetivo="OBJ-05",
         diseno="`ReporteVentas`, `ReporteVentasRepositorio`, `GET /api/reportes/ventas` · `comprobante`",
         riesgo="R11", cambio="CC-01",
         pruebas=[(U, "PU-25, PU-26, PU-27 (proformas, 366 días, día de Perú)", G07E1, "1.1.1", "Aprobada"),
                  (X, "ReporteVentasTests, ApiTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-12 reporte consolidado", SEL, "1.2.0", "Aprobada")]),
    dict(id="RF-16", nombre="Generar respaldo de la base de datos", proceso="Soporte", prioridad="Media",
         fuente="Gerente, Encargado (ENT-01)", objetivo="OBJ-06",
         diseno="`ServicioRespaldo`, `RespaldoViewModel` · `respaldo`",
         riesgo="R05, R09, R10 (S3)", cambio="—",
         pruebas=[(X, "HU15_RespaldoTests", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S3: pg_dump + pg_restore, conteos idénticos en 8 tablas", G06V, "1.1.1", "Cumple")]),
    # ---------------------------------------------------------------- RNF
    dict(id="RNF-01", nombre="Sugerencias en menos de 1 s (3 000 productos)", proceso="Rendimiento", prioridad="Alta",
         fuente="Vendedores (CUE-01, OBS-01)", objetivo="OBJ-01",
         diseno="Índice trigram en `producto` (V003), espera de 220 ms del buscador",
         riesgo="—", cambio="—",
         pruebas=[(X, "HU02_BuscarProductoTests", XUNIT, "1.2.0", "Aprobada"),
                  (S, "CP-07: 570–585 ms en 10 ejecuciones (< 1 000 ms)", SEL, "1.2.0", "Cumple")]),
    dict(id="RNF-02", nombre="p95 ≤ 2 s y error ≤ 1 % con 10 usuarios", proceso="Rendimiento", prioridad="Media",
         fuente="Gerente, Docente (ENT-01)", objetivo="OBJ-01",
         diseno="DD-02 (cliente–API–base), pool de Npgsql",
         riesgo="—", cambio="MEJ-01 (1.1.2)",
         pruebas=[(R, "Carga esperada: T1 p95 11–12 ms, T2 p95 21–22 ms, 0 % error", G08C, "1.1.1 y 1.1.2", "Cumple"),
                  (R, "Estrés, pico y estabilidad sin degradación ni errores", "G08/04_Resultados", "1.1.1 y 1.1.2", "Cumple")]),
    dict(id="RNF-03", nombre="Seguridad de credenciales y roles", proceso="Seguridad", prioridad="Alta",
         fuente="Gerente, Docente (ENT-01)", objetivo="OBJ-03",
         diseno="DD-07: PBKDF2-SHA256 100 000 iteraciones, JWT 480 min",
         riesgo="R01, R02, R12 (S1)", cambio="CC-01",
         pruebas=[(U, "PU-20, PU-22, PU-23, PU-24", G07E1, "1.1.1", "Aprobada"),
                  (X, "HashClaveTests, ServicioAutenticacionTests, ApiTests", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S1: 3 de 3 contraseñas con hash; 100 % de rutas protegidas", G06V, "1.1.1", "Cumple"),
                  (S, "CP-02, CP-03", SEL, "1.2.0", "Aprobada")]),
    dict(id="RNF-04", nombre="0 números repetidos y 0 saltados con 3 PC", proceso="Fiabilidad", prioridad="Alta",
         fuente="Encargado, Contador (ENT-01, OBS-01)", objetivo="OBJ-06",
         diseno="DD-03: `UPDATE serie … RETURNING` + `UNIQUE (serie_id, numero)`",
         riesgo="—", cambio="MEJ-01 (1.1.2)",
         pruebas=[(X, "HU16_ConcurrenciaTests, MEJ01_CorrelativoAlFinalTests (90 boletas, 1 a 90)", XUNIT, "1.2.0", "Aprobada"),
                  (R, "Capacidad sin pausas: sin repetidos ni huecos", "G08/04_Resultados/*/capacidad_*", "1.1.1 y 1.1.2", "Cumple")]),
    dict(id="RNF-05", nombre="Venta sin internet y reenvío del 100 %", proceso="Disponibilidad", prioridad="Alta",
         fuente="Gerente, Contador (ENT-01)", objetivo="OBJ-02",
         diseno="DD-05: envío fuera de la transacción, `FOR UPDATE SKIP LOCKED`",
         riesgo="R07 (aceptado)", cambio="—",
         pruebas=[(X, "HU07_EnviarSunatTests, HU17_ReenvioAutomaticoTests", XUNIT, "1.2.0", "Aprobada")]),
    dict(id="RNF-06", nombre="Venta de 3 productos ≤ 60 s solo con teclado", proceso="Usabilidad", prioridad="Media",
         fuente="Vendedores (OBS-01, CUE-01)", objetivo="OBJ-01",
         diseno="DD-08: atajos F1–F11 y `AutomationId` estables",
         riesgo="—", cambio="—",
         pruebas=[(M, "OBS-01: línea base manual 2 min 50 s (mediana)", "G01/02_Elicitacion/OBS-01_ficha_observacion.md", "Proceso manual", "Línea base"),
                  (S, "CP-07: venta solo con teclado, 1,2–1,8 s de sistema", SEL, "1.2.0", "Cumple con observación O-4")]),
    dict(id="RNF-07", nombre="Persistencia y recuperación", proceso="Fiabilidad", prioridad="Alta",
         fuente="Gerente, Encargado (ENT-01)", objetivo="OBJ-06",
         diseno="PostgreSQL 16 con volumen persistente; `pg_dump`/`pg_restore`",
         riesgo="R05, R06, R08 (S3)", cambio="—",
         pruebas=[(X, "HU15_RespaldoTests, Datos/* ([FactConBD])", XUNIT, "1.2.0", "Aprobada"),
                  (C, "S3: restauración con conteos idénticos", G06V, "1.1.1", "Cumple"),
                  (S, "CP-04, CP-06, CP-07: lo registrado aparece después en otra pantalla", SEL, "1.2.0", "Aprobada")]),
    dict(id="RNF-08", nombre="Cobertura ≥ 80 % en Condor.Dominio", proceso="Mantenibilidad", prioridad="Media",
         fuente="Docente", objetivo="OBJ-06",
         diseno="DD-01 y DD-04: reglas sin infraestructura, dobles de prueba",
         riesgo="—", cambio="—",
         pruebas=[(U, "Cobertura de líneas de Condor.Dominio: 95,6 % (coverlet + ReportGenerator)", "G07/03_Reportes/cobertura_RNF-08", "1.1.1", "Cumple")]),
]


def filas_resumen():
    """Una fila por requisito: tipos de prueba y estado final."""
    filas = []
    for r in REQUISITOS:
        tipos = []
        for t in r["pruebas"]:
            if t[0] not in tipos:
                tipos.append(t[0])
        pendiente = any("Pendiente" in t[4] for t in r["pruebas"])
        estado = "Verificado (xUnit); demostración pendiente" if pendiente else "Verificado"
        if r["id"].startswith("RNF"):
            estado = "Cumple con observación" if r["id"] == "RNF-06" else "Cumple"
        filas.append([r["id"], r["nombre"], ", ".join(tipos), estado])
    return filas
