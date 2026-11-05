```
Trabajo 3er Parcial de Calidad de Software
```
Desarrollo de un producto de software con aplicación de las nueve guías de laboratorio

**1 Propósito del trabajo**
Desarrolle un producto de software funcional que resuelva una necesidad de una organización o de un
grupo de usuarios. Aplique al mismo producto los procedimientos de las nueve guías de laboratorio y
demuestre, mediante archivos ejecutables y evidencias verificables, cómo gestiona su calidad desde los
requisitos hasta la entrega.

El resultado debe permitir comprobar qué se solicitó, cómo se diseñó e implementó, qué cambios se
realizaron, cómo se controlaron los riesgos y con qué resultados se probó el producto.

**2 Modalidad y alcance propuestos**
Trabajo ES GRUPAL (4 Alumnos). Cada alumno asume y documenta los roles de analista,
desarrollador, responsable de configuración y evaluador de calidad. Duración propuesta: al 2 – 12 - 2026 ;
el docente define las fechas de los hitos (Avances).

Aplicación web con interfaz de usuario, lógica de negocio y persistencia de datos. Puede ejecutarse
localmente; debe contar con rutas HTTP evaluables con JMeter y una interfaz automatizable con
Selenium.

- Mínimo 10 requisitos funcionales y 5 no funcionales medibles; al menos dos roles de usuario y tres
    procesos de negocio completos.
- Incluya autenticación, autorización según roles, validaciones, operaciones de registro y consulta, y
    un reporte o consulta consolidada. Los registros deben conservarse tras reiniciar la aplicación.
- Implemente los 10 requisitos funcionales incluidos en la línea base final. Use datos de prueba y
    documente cualquier servicio externo simulado.

**3 Elección del producto**
Puede desarrollar un sistema de pedidos e inventario, reservas de ambientes, préstamos de equipos,
atención de incidencias o citas. Describa el problema, usuarios, restricciones y beneficio esperado. El
docente valida el alcance antes de iniciar la construcción (primer entregable sustentado: 11- 11 - 2026)

Caso orientador: sistema de préstamos de equipos de laboratorio. Procesos: reservar un equipo, aprobar
y registrar el préstamo, y devolverlo. Roles: solicitante y encargado. Reglas: evitar reservas
superpuestas, restringir aprobaciones al encargado y registrar la devolución con su estado.

Las cantidades, plazos y umbrales de este enunciado son exigencias académicas propuestas para el
trabajo final; no se presentan como requisitos originales de las guías.


**4 Integración de las nueve guías
Guía y tema Aplicación al producto Evidencia principal
1 Requerimientos** Elicitar y especificar
necesidades

```
ERS y criterios de aceptación
```
```
2 Proceso de requerimientos Controlar requisitos y cambios Historial de cinco requisitos y
dos cambios
3 Análisis de sistemas Modelar estructura,
comportamiento e interfaz
```
```
SDD, UML y mockups
```
```
4 Dimensionamiento Estimar tamaño, esfuerzo, costo
y plazo
```
```
Cálculos editables y
comparación
5 Gestión de configuración Controlar elementos y versiones Repositorio SVN y recuperación
6 Gestión de riesgos Analizar activos, amenazas y
salvaguardas
```
```
Proyecto de riesgos y
tratamientos
7 Pruebas unitarias Verificar reglas de negocio Suite automatizada y cobertura
8 Pruebas de rendimiento Medir respuesta y capacidad Plan JMeter, resultados y
análisis
9 Gestión de calidad Automatizar aceptación y
regresión web
```
```
Suite Selenium y dictamen de
calidad
```
**5 Herramientas y entorno de trabajo**
Ruta de referencia: aplicación Java, un framework web elegido por el alumno, Maven o Gradle, una
base de datos y un IDE. Se prioriza Java para aplicar JUnit. Otro lenguaje requiere validación docente y
una herramienta equivalente de pruebas unitarias; JMeter y Selenium se mantienen.

```
Uso Herramienta de referencia Condición de uso
Requisitos y cambios REM, OSMRT o Gatherspace;
gestor de incidencias
equivalente
```
```
Elegir una opción operativa;
registrar IDs, estados,
responsables y cambios.
Modelado PlantUML o diagrams.net;
Moqups para mockups
```
```
Entregar fuente editable y
exportación legible.
Estimación Excel o LibreOffice Calc Mostrar fórmulas, parámetros,
unidades y fuentes.
Configuración Apache Subversion y
TortoiseSVN
```
```
SVN obligatorio en el ejercicio
de la guía 5; GitHub es
comparativo.
Riesgos PILAR; alternativas de la guía:
RiskyProject o Pirani
```
```
PILAR es la ruta de referencia
para MAGERIT; justificar
equivalencia de otra
herramienta.
Pruebas JUnit, JMeter y Selenium
WebDriver
```
```
Guardar versiones y
dependencias compatibles con
el entorno.
```
Prepare una ficha por herramienta: nombre, versión exacta, finalidad, requisitos de instalación,
procedencia, licencia o restricciones de acceso, configuración, procedimiento de ejecución y archivos


generados. Compare al menos dos opciones por área de las guías 1 a 6; no necesita instalar todas las
alternativas.

Si una herramienta de la guía no puede utilizarse, registre el impedimento y solicite al docente validar
una sustitución que conserve la actividad y la evidencia. No basta con incluir una captura de instalación.

**6 Requisitos y gestión de cambios**

**Guía 1 Requerimientos**
Objetivo: construir una especificación de requisitos del software o ERS verificable, tomando IEEE 830
de la guía como referencia académica de estructura.

- Identifique al cliente, usuarios e interesados. Aplique al menos dos técnicas de elicitación, como
    entrevista y observación o cuestionario. Conserve instrumentos y resultados; declare si se utilizó un
    usuario representado.
- Documente propósito, alcance, contexto, interfaces, supuestos y restricciones. Especifique al menos
    10 RF y 5 RNF con ID, descripción, fuente, prioridad y criterio de aceptación.
- Defina indicadores medibles para rendimiento, seguridad, usabilidad u otros atributos pertinentes.
    Identifique conflictos y registre su resolución.
- Elabore cronograma, organigrama de roles y comparación de herramientas. Realice una revisión de
    claridad, consistencia, completitud y verificabilidad.

Entregables G01: ERS versionada, instrumentos de elicitación, cronograma, roles y lista de revisión.
Aceptación: cada requisito tiene una condición observable de cumplimiento y puede vincularse con una
prueba.

**Guía 2 Proceso de requerimientos**

- Configure la herramienta elegida y dibuje el flujo: registrado, analizado, aprobado o rechazado,
    implementado, verificado y cerrado.
- Gestione al menos cinco requisitos de G01 en ese flujo y muestre el historial con fecha, responsable
    y evidencia en cada transición aplicable.
- Genere dos solicitudes reales de cambio durante el desarrollo. Para cada una, describa motivo,
    impacto en diseño, costo, plazo, riesgos y pruebas, decisión y versión afectada.
- Implemente al menos un cambio aprobado; actualice ERS, diseño, código y pruebas. Repita las
    pruebas afectadas y registre el cierre. El otro cambio puede aprobarse o rechazarse con sustento.
- Obtenga reportes de seguimiento y compare la herramienta seleccionada con una alternativa.

Entregables G02: exportación del gestor, flujo, dos solicitudes, análisis de impacto e informe de
seguimiento. Aceptación: se reconstruye el recorrido de los cinco requisitos y el cambio implementado
conduce a una versión y una prueba verificable.

**Ejemplo de continuidad**
RF-03: impedir una reserva superpuesta. CC-01: agregar un tiempo de preparación entre préstamos. El
alumno analiza el impacto, actualiza el criterio de aceptación, modifica el servicio de reservas, registra
una revisión SVN y ejecuta pruebas unitarias y Selenium sobre la nueva regla.


**7 Análisis del sistema y dimensionamiento**

**Guía 3 Análisis de sistemas**

- Elabore una descripción del diseño de software o SDD, usando IEEE 1016 de la guía como
    referencia. Identifique interesados, preocupaciones, vistas y decisiones de diseño.
- Presente un diagrama de casos de uso, un diagrama de clases y al menos un diagrama de
    comportamiento: secuencia, actividad o estados. Este último debe describir un proceso crítico.
- Especifique al menos tres casos de uso con precondiciones, flujo principal, alternativas, excepciones
    y poscondiciones. Diseñe mockups de sus pantallas.
- Añada arquitectura y modelo de datos suficientes para comprender la implementación. Mantenga
    coherencia entre nombres, reglas, clases, tablas y pantallas.
- Incluya una tabla de utilidad de los diagramas UML y una revisión del SDD contra los criterios de la
    referencia adoptada. Identifique criterios cumplidos, pendientes y evidencia.

Entregables G03: SDD, fuentes UML, mockups y revisión. Aceptación: el diseño explica los tres
procesos del producto y sus elementos pueden rastrearse hacia requisitos y código.

**Guía 4 Dimensionamiento y estimación**

- Defina la frontera del sistema y una línea base de requisitos. Realice un conteo NESMA indicando el
    tipo de conteo, componentes, reglas y cálculo; documente las hipótesis del método seleccionado.
- Realice una medición COSMIC del mismo alcance: procesos funcionales y movimientos de datos de
    entrada, salida, lectura y escritura. Mantenga sus unidades separadas de las del conteo NESMA.
- Estime esfuerzo y duración con COCOMO. Declare variante, tamaño de entrada, parámetros y
    fuentes. Si convierte puntos de función a líneas de código, justifique el factor y analice su
    sensibilidad.
- Calcule costo en soles y plazo para escenarios de una y tres personas. Separe esfuerzo de duración y
    explicite dedicación, horas por mes, tarifa y coordinación. No divida automáticamente el plazo entre
    tres.
- Compare los resultados, exponga limitaciones de calibración y confronte la estimación con las horas
    reales registradas. Analice el efecto de variar un parámetro relevante en ±20 %.

Entregables G04: libro editable con fórmulas, memoria de cálculo y cuadro comparativo. Aceptación: el
docente puede recalcular los valores y reconocer tamaño funcional, esfuerzo, duración y costo como
magnitudes distintas.

Aclaración de alcance: la guía menciona “wine” sin definir el método ni su aplicación. No se le asignará
una fórmula supuesta; si el docente precisa ese recurso, se añadirá como comparación. NESMA,
COSMIC y COCOMO constituyen el mínimo evaluable de este trabajo.


**8 Configuración y gestión de riesgos**

**Guía 5 Gestión de configuración**

- Instale Apache Subversion y TortoiseSVN en Windows. En otro sistema operativo, use un cliente
    SVN compatible y documente el procedimiento equivalente.
- Defina elementos de configuración: requisitos, diseño, código, base de datos, scripts, pruebas y
    documentación. Configure trunk, branches y tags, permisos y política de nombres de versiones.
- Demuestre creación e importación del repositorio, checkout, update, cambios y commit; registre
    como mínimo ocho revisiones significativas a lo largo del proyecto.
- Cree una rama para un cambio, integre sus modificaciones y demuestre la resolución controlada de
    un conflicto. Conserve evidencia del estado anterior, decisión y resultado.
- Genere una etiqueta de versión final v1.0.0 y demuestre recuperación de una revisión anterior sin
    perder la entrega vigente. Compare SVN con Git como tecnología y GitHub como plataforma.

Entregables G05: historial, respaldo portable del repositorio, política de configuración y evidencia de
rama, integración, conflicto, etiqueta y recuperación. Aceptación: el código entregado coincide con la
etiqueta final y permite reconstruir la versión.

**Guía 6 Gestión de riesgos**

- Aplique MAGERIT al sistema de información que soporta el producto. Identifique al menos cinco
    activos, sus dependencias y las dimensiones de seguridad relevantes.
- Registre al menos ocho escenarios activo-amenaza. Evalúe probabilidad o frecuencia, degradación,
    impacto y riesgo con escalas documentadas; explique la información utilizada.
- Utilice PILAR o una alternativa validada. Si añade una matriz simplificada de probabilidad e
    impacto, preséntela como complemento y explique su relación con el análisis; no la denomine
    implementación completa de MAGERIT.
- Priorice los riesgos, establezca salvaguardas, responsable, fecha, costo o esfuerzo, indicador y riesgo
    residual previsto. Distinga controles propuestos de controles implantados.
- Implemente y verifique al menos dos tratamientos vinculados al producto, como autorización por
    roles, validación de entradas o respaldo y restauración. No declare reducción efectiva sin evidencia.
- Compare actividades que cubren RMAT y PILAR según la guía, indicando la fuente o
    documentación usada. Si RMAT no se encuentra identificado de manera inequívoca, registre la
    limitación para validación docente.

Entregables G06: archivo del proyecto o exportación de la herramienta, inventario, matriz de riesgos,
plan de tratamiento y evidencia de controles. Aceptación: cada riesgo priorizado tiene responsable y
respuesta; los dos controles implantados tienen prueba de funcionamiento.


**9 Pruebas unitarias del producto**

**Guía 7 Pruebas unitarias**
Pruebe clases o funciones de negocio reales del producto. Los ejemplos Rectangle de la guía sirven para
aprender la herramienta, pero deben reemplazarse por pruebas que aporten evidencia sobre su
aplicación.

- Configure JUnit y el ejecutor de compilación. Registre la versión y las dependencias elegidas; no
    mezcle anotaciones o APIs incompatibles de distintas versiones.
- Diseñe al menos 15 casos de prueba sobre tres componentes de negocio como mínimo. Incluya
    escenarios válidos, inválidos, valores límite y excepciones, con resultados esperados explícitos.
- Aísle las unidades de dependencias externas mediante dobles de prueba cuando sea necesario.
    Prepare datos reproducibles y evite que el orden de ejecución determine el resultado.
- Vincule los casos con requisitos y riesgos. Ejecute la suite mediante un comando documentado,
    conserve el reporte y repítala después de un cambio de G02.
- Genere un reporte de cobertura con una herramienta compatible, por ejemplo JaCoCo para Java. La
    meta académica es al menos 80 % de líneas del paquete de lógica de negocio, cuyas inclusiones y
    exclusiones deben quedar declaradas.
- Introduzca temporalmente un defecto controlado en una regla de negocio, compruebe que una
    prueba falla y restaure el código. Entregue evidencia del fallo y del resultado posterior correcto.

**Precaución al adaptar el ejemplo**
El código de ejemplo de la guía captura AssertionError y solo imprime el mensaje. No copie ese patrón:
la aserción fallida debe propagarse al ejecutor para que el caso se registre como fallido. Un mensaje
impreso no demuestra que JUnit haya detectado el defecto.

**Estructura mínima de cada caso
Campo Contenido requerido
ID y requisito** PU-01 y RF o RNF relacionado
**Unidad y objetivo** Clase o función y comportamiento evaluado
**Datos y preparación** Entradas, estado inicial y dobles utilizados
**Resultado esperado** Valor, excepción o cambio de estado observable
**Ejecución** Fecha, versión probada, estado y reporte
**Defecto y cierre** Incidencia, corrección y repetición cuando
corresponda
Entregables G07: código de pruebas, catálogo de casos, reportes de ejecución y cobertura, registro del
defecto controlado y regresión. Aceptación: el docente ejecuta la suite, verifica aserciones y reproduce el
fallo controlado siguiendo las instrucciones. Alcanzar cobertura no sustituye comprobar el
comportamiento.


**10 Rendimiento y automatización funcional**

**Guía 8 Pruebas de rendimiento**

- Seleccione al menos dos transacciones críticas, como consultar disponibilidad y registrar una
    reserva. Defina mezcla de operaciones, datos, autenticación, validaciones de respuesta y tiempos de
    espera.
- Registre equipo, memoria, sistema operativo, red, base de datos, tamaño del conjunto de datos,
    versión del producto y configuración del generador de carga.
- Ejecute en JMeter cuatro escenarios: carga esperada, estrés escalonado, pico y estabilidad. Perfil
    académico inicial: carga de 10 usuarios por 5 minutos con rampa de 30 segundos; estrés de 10, 25 y
    50 usuarios por 3 minutos cada nivel; pico de 10 a 50 y retorno a 10; estabilidad de 10 usuarios
    durante 15 minutos. Documente tiempos exactos de transición del pico.
- Antes de ejecutar, adapte y acuerde el perfil con el docente si el entorno lo exige. Como criterio
    inicial para carga esperada: p95 ≤ 2 segundos y tasa de error ≤ 1 %. Mida por transacción y defina
    qué respuestas se consideran error.
- Ejecute la carga en modo no gráfico y conserve .jmx, .jtl y reporte HTML. Mida percentiles,
    throughput, errores, CPU y memoria con una herramienta de monitoreo identificada.
- Localice un cuello de botella, aplique una mejora pertinente y repita la prueba con condiciones
    equivalentes. Si no logra cumplir el objetivo, presente los datos, causa probable y acciones
    pendientes.

Entregables G08: plan, scripts, datos, resultados antes y después y análisis. Aceptación: los umbrales se
contrastan con datos; se distinguen carga, estrés, pico y estabilidad. Una ejecución de 15 minutos solo
permite conclusiones sobre ese intervalo.

**Guía 9 Gestión de calidad con Selenium**

- Configure Selenium WebDriver, navegador y mecanismo compatible de gestión del controlador.
    Documente dependencias y modo de ejecución.
- Automatice al menos ocho casos web: acceso correcto, credenciales inválidas, restricción por rol,
    registro válido, datos inválidos, consulta, cambio de estado y cierre de sesión. Adapte las
    operaciones al producto y cubra los tres procesos.
- Use aserciones sobre resultados observables, selectores estables, esperas explícitas y datos aislados.
    Conserve reportes, capturas de fallos y registro de defectos.
- Ejecute la regresión en la versión final. Integre resultados de requisitos, riesgos, pruebas unitarias y
    rendimiento en un dictamen de liberación: apto, apto con observaciones o no apto, con sustento.

Entregables G09: suite Selenium, datos, reportes y dictamen. Aceptación: las pruebas verifican
resultados del producto y pueden repetirse. En esta guía se aplica Selenium; la mención repetida de
instalar JMeter se atiende en G08. (Segundo Entregable: 25 - 11 - 2026)


**11 Cronograma y entrega final**

La gestión de cambios, configuración, riesgos y pruebas acompaña todo el desarrollo. Los hitos indican
entregas de avance, no actividades que deban ejecutarse una sola vez.

**Paquete de entrega**

- Informe final en PDF y formato editable, organizado según el índice indicado debajo.
- Código fuente del producto, esquema o migraciones y datos de prueba; README con instalación,
    configuración, ejecución, credenciales de demostración y comandos de pruebas.
- Carpeta por guía G01 a G09 con documentos, fuentes editables, scripts, exportaciones y resultados.
    Incluya archivos originales generados por las herramientas, además de capturas.
- Repositorio SVN portable y ubicación de la etiqueta v1.0.0. Incluya un manifiesto con revisión,
    fecha y versión del producto utilizada por cada evidencia.
- Manuales breves de usuario y técnico, matriz de trazabilidad, registro de defectos y dictamen final.
    Declare limitaciones, componentes de terceros y asistencia de IA utilizada.

**Índice del informe**

1. Problema, usuarios y alcance. 2. Objetivos y organización. 3. Arquitectura y descripción del producto.
4. Herramientas y configuración. 5. Desarrollo de G01 a G09. 6. Trazabilidad y resultados consolidados.
7. Evaluación de cumplimiento y decisión de liberación. 8. Conclusiones y mejoras. 9. Referencias y
anexos.

Dentro de cada guía mantenga la estructura de los adjuntos: objetivo, procedimiento realizado,
resultados obtenidos, análisis y conclusiones. Agregue herramienta y versión, ubicación de evidencias,
requisito vinculado y limitaciones. Responda los cuestionarios aplicables al producto; justifique los
puntos no aplicables.

**Sustentación propuesta de 20 minutos**
Presente el problema y alcance en 3 minutos; demuestre los tres procesos en 6; muestre un cambio, una
recuperación SVN y una ejecución de pruebas en 6; explique resultados de calidad y atienda preguntas
en 5. El docente puede solicitar modificar una regla o repetir una prueba para comprobar dominio
individual. (Tercer entregable: 2 – 12 – 2026 )

**12 Evaluación del trabajo final**

Rúbrica propuesta sobre 100 puntos, convertible a escala vigesimal mediante nota = puntaje / 5. Cada
criterio se valora con la escala común al pie de la tabla.

**.......**

**Escala común de desempeño**
......

Puntaje por criterio = máximo × factor. Un resultado de prueba desfavorable correctamente medido no
equivale a ausencia de trabajo: se evalúan diseño, ejecución, análisis y corrección. El incumplimiento
funcional se refleja en el criterio del producto y en el dictamen de liberación.


**1 3 Formatos de control y fuentes**

**Condiciones de cierre**

Las nueve guías deben aplicarse al mismo producto. Una guía sin evidencia recibe cero en su criterio y
queda pendiente de subsanación antes del cierre de la entrega integral. La aprobación del curso se rige
por el sílabo; esta propuesta no reemplaza sus reglas. La simple instalación de herramientas o
reproducción de ejemplos ajenos no acredita aplicación al producto.

**Matriz de trazabilidad obligatoria**

Registre una fila por requisito y amplíela cuando tenga varias pruebas. Debe cubrir los 10 RF y 5 RNF
de la línea base final. Los identificadores del ejemplo son ilustrativos; el alumno los sustituye por
evidencias reales.

**.........**

**Registro de defectos**

Campos mínimos: ID, fecha, versión, requisito, pasos de reproducción, datos, resultado esperado y
obtenido, severidad, responsable, estado, corrección y prueba de cierre. Distinga severidad de prioridad.
Un defecto crítico impide un proceso esencial o expone información; uno mayor afecta una función
importante; uno menor tiene impacto limitado.

**Lista de verificación de entrega**

- El producto se instala y ejecuta con las instrucciones entregadas.
- Los tres procesos pueden demostrarse y los requisitos tienen pruebas vinculadas.
- G01 a G09 incluyen evidencia propia y los resultados identifican la versión probada.
- Los cambios, riesgos, defectos y limitaciones están documentados.
- La etiqueta final, el código del paquete y la versión demostrada coinciden.
- Las pruebas se ejecutan sin ocultar fallos y el dictamen refleja sus resultados.

**Fuentes del enunciado**

Fuente principal: las nueve guías adjuntas de Calidad de Software, semestre 8, atribuidas en su portada a
Jesús Martín Silva Fernández: PRAC01 Requerimientos; PRAC02 Proceso de Requerimientos; PRAC
Análisis de Sistemas; PRAC04 Dimensionamiento Puntos de Función; PRAC05 Gestión de
Configuración; PRAC06 Gestión de Riesgos; PRAC07 Pruebas Unitarias; PRAC08 Pruebas de
Performance; PRAC09 Gestión de Calidad.

Las guías citan anexos y recursos adicionales no incluidos en todos los archivos recibidos, como
Ejemplo.doc, plan_riesgo.xls y manuales. Este trabajo traslada sus actividades al producto elegido y
define evidencias autónomas. Las referencias IEEE se usan según lo indicado en las guías; no se declara
certificación ni conformidad normativa completa.

Documentación oficial de apoyo consultada el 28 de octubre de 2026:

JUnit User Guide — https://docs.junit.org/6.0.0/writing-tests/assertions.html


Apache JMeter Best Practices — https://jmeter.apache.org/usermanual/best-practices.html

Selenium WebDriver — https://www.selenium.dev/documentation/webdriver/

CCN PILAR y MAGERIT — https://pilar.ccn-cert.cni.es/pilar/


Info Adicional:
El docente menciono que los alumnos pueden usar sus propias tecnologias (no importa si es web o java o cualquiera que tengan) lo que importa es cumplir con todo lo que se hizo en los laboratorios.