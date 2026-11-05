"""Genera condor_rendimiento.jmx, el plan JMeter 5.6.3 de G08 (cuatro escenarios en un solo plan).

Uso: python generar_plan.py   (escribe condor_rendimiento.jmx junto a este script)

Cada grupo de hilos lleva el mismo flujo de un vendedor de mostrador:
  1. Ingreso una sola vez por hilo (Once Only Controller): POST /api/auth/login, JSON Extractor $.token.
  2. En cada iteración, sorteo 1-100: <= 70 consulta productos (T1) y > 70 registra una boleta (T2).
  3. Antes de cada transacción, pausa de 1 a 3 s (Uniform Random Timer): tiempo de digitación.
     pausa.min y pausa.rango (ms) la cambian; la prueba de capacidad las pone en 0.
El número de hilos de cada grupo es una propiedad (-J...) que vale 0 por omisión; ejecutar_escenario.ps1
pone solo las del escenario elegido, así que los demás grupos no arrancan.

Se genera con un script, en vez de editarlo a mano en la GUI, para que los siete grupos tengan
exactamente el mismo flujo; el .jmx resultante se abre y se edita normalmente en JMeter.
"""
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent


def prop(nombre, tipo, valor):
    return f'<{tipo}Prop name="{nombre}">{escape(str(valor))}</{tipo}Prop>'


def s(nombre, valor):
    return prop(nombre, "string", valor)


def b(nombre, valor):
    return prop(nombre, "bool", "true" if valor else "false")


def arbol(*hijos):
    return "<hashTree>" + "".join(hijos) + "</hashTree>"


def cabeceras(nombre, pares):
    filas = "".join(
        f'<elementProp name="" elementType="Header">{s("Header.name", k)}{s("Header.value", v)}</elementProp>'
        for k, v in pares)
    return (f'<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="{nombre}">'
            f'<collectionProp name="HeaderManager.headers">{filas}</collectionProp></HeaderManager>')


def codigo(nombre, esperado):
    return (f'<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="{nombre}">'
            f'<collectionProp name="Asserion.test_strings"><stringProp name="1">{esperado}</stringProp></collectionProp>'
            f'{s("Assertion.custom_message", f"Se esperaba HTTP {esperado}")}'
            f'{s("Assertion.test_field", "Assertion.response_code")}{b("Assertion.assume_success", False)}'
            f'<intProp name="Assertion.test_type">8</intProp></ResponseAssertion>')


def json_existe(nombre, ruta):
    return (f'<JSONPathAssertion guiclass="JSONPathAssertionGui" testclass="JSONPathAssertion" testname="{nombre}">'
            f'{s("JSON_PATH", ruta)}{s("EXPECTED_VALUE", "")}{b("JSONVALIDATION", False)}'
            f'{b("EXPECT_NULL", False)}{b("INVERT", False)}{b("ISREGEX", False)}</JSONPathAssertion>')


def pausa():
    return ('<UniformRandomTimer guiclass="UniformRandomTimerGui" testclass="UniformRandomTimer" '
            'testname="Pausa de digitación 1-3 s">' + s("ConstantTimer.delay", "${__P(pausa.min,1000)}") +
            s("RandomTimer.range", "${__P(pausa.rango,2000)}") + '</UniformRandomTimer>')


def http(nombre, metodo, ruta, cuerpo=None, parametros=()):
    if cuerpo is not None:
        args = ('<boolProp name="HTTPSampler.postBodyRaw">true</boolProp>'
                '<elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments">'
                f'<elementProp name="" elementType="HTTPArgument">{b("HTTPArgument.always_encode", False)}'
                f'{s("Argument.value", cuerpo)}{s("Argument.metadata", "=")}</elementProp>'
                '</collectionProp></elementProp>')
    else:
        filas = "".join(
            f'<elementProp name="{k}" elementType="HTTPArgument">{b("HTTPArgument.always_encode", True)}'
            f'{s("Argument.value", v)}{s("Argument.metadata", "=")}{b("HTTPArgument.use_equals", True)}'
            f'{s("Argument.name", k)}</elementProp>' for k, v in parametros)
        args = ('<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" '
                f'testclass="Arguments"><collectionProp name="Arguments.arguments">{filas}</collectionProp></elementProp>')
    return (f'<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{nombre}">'
            f'{args}{s("HTTPSampler.path", ruta)}{s("HTTPSampler.method", metodo)}'
            f'{b("HTTPSampler.follow_redirects", True)}{b("HTTPSampler.use_keepalive", True)}'
            f'{s("HTTPSampler.contentEncoding", "UTF-8")}</HTTPSamplerProxy>')


BEARER = ("Authorization", "Bearer ${token}")
JSON = ("Content-Type", "application/json")


def flujo_vendedor():
    login = http("00 Ingresar (POST /api/auth/login)", "POST", "/api/auth/login",
                 cuerpo='{"usuario":"${usuario}","clave":"${clave}"}')
    extractor = ('<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Token JWT ($.token)">'
                 f'{s("JSONPostProcessor.referenceNames", "token")}{s("JSONPostProcessor.jsonPathExprs", "$.token")}'
                 f'{s("JSONPostProcessor.match_numbers", "1")}{s("JSONPostProcessor.defaultValues", "SIN_TOKEN")}'
                 '</JSONPostProcessor>')
    una_vez = ('<OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" '
               'testname="Ingreso: una vez por hilo"/>')
    ingreso = una_vez + arbol(login, arbol(cabeceras("Cabeceras JSON", [JSON]), "<hashTree/>",
                                           codigo("HTTP 200", 200), "<hashTree/>", extractor, "<hashTree/>"))

    t1 = http("T1 Consultar productos (GET /api/productos)", "GET", "/api/productos",
              parametros=[("texto", "${texto}"), ("limite", "20")])
    si_t1 = ('<IfController guiclass="IfControllerPanel" testclass="IfController" testname="70 % consulta">'
             f'{s("IfController.condition", "${__jexl3(${__Random(1,100,azar)} <= 70)}")}'
             f'{b("IfController.evaluateAll", False)}{b("IfController.useExpression", True)}</IfController>')
    consulta = si_t1 + arbol(t1, arbol(cabeceras("Token", [BEARER]), "<hashTree/>", pausa(), "<hashTree/>",
                                       codigo("HTTP 200", 200), "<hashTree/>",
                                       json_existe("Al menos un producto ($[0].id)", "$[0].id"), "<hashTree/>"))

    t2 = http("T2 Registrar boleta (POST /api/comprobantes)", "POST", "/api/comprobantes",
              cuerpo='{"tipo":"${tipo}","documentoCliente":"${dni}","detalle":[${detalle}]}')
    si_t2 = ('<IfController guiclass="IfControllerPanel" testclass="IfController" testname="30 % registro">'
             f'{s("IfController.condition", "${__jexl3(${azar} > 70)}")}'
             f'{b("IfController.evaluateAll", False)}{b("IfController.useExpression", True)}</IfController>')
    registro = si_t2 + arbol(t2, arbol(cabeceras("Token y JSON", [BEARER, JSON]), "<hashTree/>", pausa(), "<hashTree/>",
                                       codigo("HTTP 201", 201), "<hashTree/>",
                                       json_existe("Boleta numerada ($.numero)", "$.numero"), "<hashTree/>"))
    return ingreso + consulta + registro


def grupo(nombre, hilos, rampa, duracion, retraso, comentario):
    return (f'<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="{escape(nombre)}">'
            f'{s("TestPlan.comments", comentario)}{s("ThreadGroup.on_sample_error", "continue")}'
            '<elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" '
            f'testclass="LoopController">{b("LoopController.continue_forever", False)}{s("LoopController.loops", "-1")}</elementProp>'
            f'{s("ThreadGroup.num_threads", hilos)}{s("ThreadGroup.ramp_time", rampa)}'
            f'{b("ThreadGroup.scheduler", True)}{s("ThreadGroup.duration", duracion)}{s("ThreadGroup.delay", retraso)}'
            f'{b("ThreadGroup.same_user_on_next_iteration", True)}</ThreadGroup>' + arbol(flujo_vendedor()))


def csv_datos(nombre, archivo, variables, separador=","):
    return (f'<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="{nombre}">'
            f'{s("filename", "${__P(datos,../03_Datos)}/" + archivo)}{s("fileEncoding", "UTF-8")}'
            f'{s("variableNames", variables)}{b("ignoreFirstLine", True)}{s("delimiter", separador)}'
            f'{b("quotedData", False)}{b("recycle", True)}{b("stopThread", False)}{s("shareMode", "shareMode.all")}'
            '</CSVDataSet>')


def listener(nombre, clase, gui):
    return (f'<ResultCollector guiclass="{gui}" testclass="ResultCollector" testname="{nombre}" enabled="false">'
            f'{b("ResultCollector.error_logging", False)}{s("filename", "")}</ResultCollector>')


GRUPOS = [
    ("Carga esperada (10 u, 5 min)", "${__P(carga.usuarios,0)}", "${__P(carga.rampa,30)}", "${__P(carga.duracion,330)}", "0",
     "10 hilos, rampa 0:00-0:30, 10 usuarios estables 0:30-5:30 (300 s). RNF-02."),
    ("Estrés E1: 10 u (0:00-9:30)", "${__P(estres.e1,0)}", "30", "570", "0",
     "Escalón 1: 10 hilos de 0:00 a 9:30; nivel de 10 usuarios 0:30-3:30."),
    ("Estrés E2: +15 u = 25 (3:30-9:30)", "${__P(estres.e2,0)}", "10", "360", "210",
     "Escalón 2: +15 hilos desde 3:30 (rampa 10 s); nivel de 25 usuarios 3:30-6:30."),
    ("Estrés E3: +25 u = 50 (6:30-9:30)", "${__P(estres.e3,0)}", "10", "180", "390",
     "Escalón 3: +25 hilos desde 6:30 (rampa 10 s); nivel de 50 usuarios 6:30-9:30."),
    ("Pico base: 10 u (0:00-7:00)", "${__P(pico.base,0)}", "30", "420", "0",
     "Base de 10 usuarios todo el escenario: rampa 0:00-0:30, 10 u hasta 3:00, pico, 10 u de 4:10 a 7:00."),
    ("Pico ráfaga: +40 u = 50 (3:00-4:10)", "${__P(pico.rafaga,0)}", "10", "70", "180",
     "Ráfaga: +40 hilos en 10 s (3:00-3:10), 50 usuarios 3:10-4:10, a las 4:10 se detienen y se vuelve a 10."),
    ("Estabilidad (10 u, 15 min)", "${__P(estabilidad.usuarios,0)}", "30", "${__P(estabilidad.duracion,930)}", "0",
     "10 hilos, rampa 0:00-0:30, 10 usuarios estables 0:30-15:30 (900 s)."),
    ("Capacidad (sin pausas, diagnóstico)", "${__P(capacidad.usuarios,0)}", "10", "${__P(capacidad.duracion,130)}", "0",
     "Diagnóstico del cuello de botella (05_Cuello_de_Botella): N hilos sin pausas (pausa.min=0, pausa.rango=0) "
     "durante 2 min tras 10 s de rampa. No es uno de los cuatro escenarios del perfil académico."),
]


def plan():
    defaults = ('<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="Condor.Api (valores por omisión)">'
                '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments">'
                '<collectionProp name="Arguments.arguments"/></elementProp>'
                f'{s("HTTPSampler.domain", "${__P(host,localhost)}")}{s("HTTPSampler.port", "${__P(puerto,5080)}")}'
                f'{s("HTTPSampler.protocol", "http")}{s("HTTPSampler.contentEncoding", "UTF-8")}'
                f'{s("HTTPSampler.connect_timeout", "5000")}{s("HTTPSampler.response_timeout", "10000")}'
                f'{s("HTTPSampler.implementation", "HttpClient4")}</ConfigTestElement>')
    hijos = [defaults, "<hashTree/>",
             csv_datos("Vendedores (usuarios.csv)", "usuarios.csv", "usuario,clave"), "<hashTree/>",
             csv_datos("Textos de búsqueda (consultas.csv)", "consultas.csv", "texto"), "<hashTree/>",
             csv_datos("Boletas (ventas.csv)", "ventas.csv", "tipo,dni,detalle", ";"), "<hashTree/>"]
    hijos += [grupo(*g) for g in GRUPOS]
    hijos += [listener("Summary Report (solo GUI)", "", "SummaryReport"), "<hashTree/>",
              listener("View Results Tree (solo GUI)", "", "ViewResultsFullVisualizer"), "<hashTree/>"]
    test_plan = ('<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="G08 Condor.Api - rendimiento">'
                 f'{s("TestPlan.comments", "Sistema Logístico Cóndor 1.1.1. Escenarios: carga, estrés, pico y estabilidad (ver 01_Plan). Ejecutar con 02_Scripts/ejecutar_escenario.ps1.")}'
                 f'{b("TestPlan.functional_mode", False)}{b("TestPlan.tearDown_on_shutdown", True)}'
                 f'{b("TestPlan.serialize_threadgroups", False)}'
                 '<elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" '
                 'testclass="Arguments"><collectionProp name="Arguments.arguments"/></elementProp></TestPlan>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">' + arbol(test_plan, arbol(*hijos)) +
            '</jmeterTestPlan>\n')


if __name__ == "__main__":
    salida = AQUI / "condor_rendimiento.jmx"
    from xml.dom import minidom
    salida.write_text(minidom.parseString(plan()).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8"), encoding="utf-8")
    print("Plan generado:", salida)
