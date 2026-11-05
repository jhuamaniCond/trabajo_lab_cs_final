# Cuestionario de la guía PRAC07, aplicado al producto

## a) ¿Qué tipo de prueba se realiza con las pruebas unitarias y qué aspecto de la calidad mide?

Es una prueba **dinámica de caja blanca o gris, en el nivel más bajo** (unidad: una clase o función), **automatizada** y **aislada** de sus dependencias. Ejecuta el código y compara el resultado con uno esperado explícito.

En Cóndor la suite xUnit de G07 tiene **27 casos (PU-01 a PU-27), con 43 ejecuciones** contando los datos de las pruebas parametrizadas, sobre 5 componentes de `Condor.Dominio`: `CalculadoraVenta`, `EmisionComprobante`, `ValidadorDocumento`, `ServicioAutenticacion` y `ReporteVentas`. Las dependencias (repositorios, reloj, hash de claves) se reemplazan por **dobles de prueba** (`Dobles/Datos.cs`, `CC01/DoblesAutenticacion.cs`), así que no hacen falta la base de datos ni la SUNAT.

Mide principalmente dos características de ISO/IEC 25010:

| Característica (subcaracterística) | Cómo la mide la suite |
|---|---|
| **Adecuación funcional** (corrección) | Cada caso verifica una regla de negocio con valores válidos, inválidos, límite y excepciones. Por ejemplo, PU-13: una boleta de **exactamente S/ 700** se emite sin DNI (CRQ-02) |
| **Mantenibilidad** (capacidad de prueba y de modificación) | La cobertura de líneas de `Condor.Dominio` es la métrica de RNF-08: **95,6 %** (861 de 900 líneas, 88,5 % de ramas), con la suite en verde. La regresión R1 → R2 demuestra que el código se puede modificar (CC-01) sin romper lo que ya funcionaba |

También aporta evidencia de **fiabilidad** (madurez), porque detecta defectos antes de que lleguen al usuario. Lo demuestra el defecto controlado **DEF-02**: al cambiar `>` por `>=` en la regla de los S/ 700, PU-13 falló (42 de 43) y la suite volvió a 43 de 43 al restaurar el código (`04_Defecto_Controlado/bitacora_DEF-02.txt`).

La cobertura por sí sola no mide la calidad: indica qué se ejecutó, no qué se verificó. Por eso cada caso tiene aserciones sobre valores, excepciones o cambios de estado, y el defecto controlado comprueba que esas aserciones detectan errores.

## b) ¿Las pruebas unitarias son obligatorias? ¿Por qué?

Ninguna norma las impone en todos los proyectos. ISO/IEC/IEEE 29119 y CMMI (área de Verificación) piden verificar el producto, pero no fijan la técnica. **En la práctica, y en este proyecto, sí son necesarias**, por cuatro razones:

1. **Son la única forma económica de verificar cada regla de negocio por separado.** Cóndor tiene reglas tributarias (IGV, boleta de más de S/ 700 con DNI, RUC con dígito verificador) que, si fallan, generan comprobantes inválidos ante la SUNAT. Probarlas solo con Selenium sería lento y no ubicaría el error.
2. **Permiten cambiar el código con seguridad.** Tras CC-01 la suite se repitió: R1 sobre el producto 1.0.0 (30 de 30) y R2 sobre el 1.1.1 (43 de 43, con los casos nuevos de autenticación y reporte). La suite del producto (944 pruebas en la 1.2.0) se ejecutó en cada integración de rama: DEF-01, MEJ-01 y CC-03.
3. **Son la condición de un requisito.** RNF-08 exige al menos 80 % de cobertura de líneas en la lógica de negocio, y G06 usa las pruebas como evidencia de los controles S1 y S2.
4. **Encuentran los defectos donde es más barato corregirlos**: en el momento de escribir el código y no en la aceptación.

Su límite es que no sustituyen a las pruebas de integración, de rendimiento ni de aceptación. Un producto con 100 % de cobertura unitaria puede fallar en la base de datos o en el navegador. En Cóndor, DEF-03 y DEF-04 aparecieron recién en la suite Selenium de G09.

## c) ¿Qué modelos de calidad utilizan los resultados de las pruebas unitarias?

| Modelo | Cómo usa los resultados | Uso en Cóndor |
|---|---|---|
| **ISO/IEC 25010** (que reemplazó a ISO/IEC 9126) y **ISO/IEC 25023** (métricas) | Métricas de corrección funcional, capacidad de prueba (cobertura) y madurez (defectos detectados) | RNF-08 (cobertura ≥ 80 %), clasificado como mantenibilidad en la ERS |
| **McCall** | Factores de *corrección*, *fiabilidad* y *facilidad de prueba* (testability), medidos con métricas como los defectos y la proporción de código probado | Defecto controlado DEF-02 y cobertura |
| **Boehm** | Característica de *capacidad de prueba* dentro de la mantenibilidad | Pruebas aisladas con dobles (decisión DD-04 del SDD) |
| **CMMI** (Verificación) y **TMMi** (madurez del proceso de pruebas) | Evalúan si las pruebas se planifican, ejecutan, registran y se usan para decidir | Catálogo con requisito y riesgo por caso, reportes `.trx`/HTML, regresión tras el cambio y registro de defectos |
| **ISO/IEC/IEEE 29119** | Documentación y proceso de prueba: casos, procedimientos, informes | Estructura de cada caso (ID, unidad, datos, resultado esperado, ejecución, defecto y cierre) |

En el dictamen de liberación de G09, los resultados unitarios (suite del producto 944/0/5 en la 1.2.0 y la cobertura de RNF-08) son una de las cuatro fuentes de la decisión, junto con los requisitos, los riesgos y el rendimiento.
