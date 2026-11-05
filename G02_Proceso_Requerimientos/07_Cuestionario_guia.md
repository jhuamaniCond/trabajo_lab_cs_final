# Cuestionario de la guía PRAC02, aplicado al producto

## ¿Qué actividades se usan con frecuencia en la gestión de requerimientos y cuáles son esenciales?

En Cóndor se hicieron estas actividades, en este orden de frecuencia:

| Actividad | Cómo se hizo en Cóndor | Frecuencia |
|---|---|---|
| **Registrar y actualizar el estado** de cada requisito | Las 24 peticiones de Redmine (16 RF y 8 RNF) pasan por Registrado → Analizado → Aprobado → Implementado → Verificado → Cerrado; G06 a G09 movieron los pendientes con su evidencia | En cada avance |
| **Mantener la trazabilidad** requisito → diseño → código → prueba | Campo `ID ERS` en Redmine, sección 7 del SDD, catálogo de G07 y matriz del dictamen de G09 | En cada avance |
| **Analizar el impacto de los cambios** | CC-01, CC-02 y CC-03, con su impacto en requisitos, diseño, costo, plazo, riesgos y pruebas | Por cada solicitud |
| **Decidir en el CCB** (aprobar o rechazar) | CC-01 y CC-03 aprobadas; CC-02 rechazada porque contradice CRQ-07 | Por cada solicitud |
| **Versionar la línea base** | ERS 1.0 → 1.1 (CC-01) → 1.2 (CC-03, INT-07), con su versión de producto 1.1.0 y 1.2.0 | Por cada cambio aprobado |
| **Informar el seguimiento** | `05_Seguimiento/informe_seguimiento.md` y los reportes de Redmine (capturas 19 a 21) | En cada hito |

Las **esenciales** son tres. Sin ellas no se puede reconstruir el recorrido de un requisito, que es lo que pide la aceptación de G02:

1. **Control de cambios con análisis de impacto y decisión.** CC-01 afectó 7 de los 24 requisitos (29 % de la línea base). Si se hubiera aplicado sin análisis, el diseño, la estimación y las pruebas habrían quedado desfasados. El análisis de CC-02 sirvió para rechazarla con fundamento: dos riesgos altos sin mitigación y el hito del 25-11-2026 en peligro.
2. **Trazabilidad.** Permitió saber qué pruebas repetir tras CC-01 (130 pruebas afectadas) y qué requisito valida cada caso de G07, G08 y G09.
3. **Gestión de estados con responsable.** El flujo de Redmine solo deja hacer cada transición al rol autorizado: el desarrollador no aprueba y solo el CCB cierra.

## ¿Qué herramienta es de mejor utilidad para la gestión de requerimientos?

Para este producto, **Redmine**. La comparación completa está en `06_Herramientas/comparacion_herramientas.md`, frente a i-doit y Scarab (las de la guía) y Jira.

- Implementa **exactamente** los 7 estados del enunciado y las transiciones por rol. i-doit Open obliga a traducirlos a un ciclo de vida de CMDB, y Scarab ya no se puede instalar.
- Guarda el historial con fecha, usuario y nota de evidencia en cada transición. Con eso se reconstruyó el recorrido de RF-01, RF-03, RF-07, RF-08 y RF-15.
- Tiene un tipo propio de *Solicitud de cambio*, con los campos de impacto, y la relaciona con los requisitos que afecta.
- Es gratuito, corre en un contenedor y se respalda en un solo archivo (`01_Redmine/respaldo/redmine.db`). Además, su API REST permitió cargar las peticiones desde la misma fuente que la ERS.

Redmine no es un gestor de requisitos puro: no tiene plantilla IEEE 830 ni matriz automática. Esa parte la cubrió **REMUS** en G01. La combinación más útil fue esa: REMUS para especificar y Redmine para controlar el ciclo de vida y los cambios. Jira habría servido igual, pero es de pago para un uso continuo y deja los datos fuera del repositorio SVN.

## ¿Qué porcentaje de los recursos del proyecto es aceptable para la gestión de cambios?

Con los datos del proyecto:

| Cambio | Esfuerzo | Base de comparación |
|---|---|---|
| CC-01 Ingreso con roles y backend REST | 56 h estimadas (S/ 1 400) | 422 h reales de desarrollo hasta la versión 1.1.1 (G04) → **13 %** |
| CC-02 Descuento del vendedor | Solo el análisis; las 38 h estimadas no se gastaron porque se rechazó | — |
| CC-03 Portal web del mostrador | 17,5 h reales (S/ 440), incluida la suite Selenium | Plazo de un día; no movió el segundo entregable |

Para un proyecto como Cóndor, el equipo considera aceptable entre **10 % y 15 %** del esfuerzo, con dos condiciones:

- **El análisis de impacto se paga siempre, incluso si el cambio se rechaza.** Es barato frente a lo que evita: CC-02 costó solo su análisis y evitó 38 h y dos riesgos altos.
- **Un cambio no debe mover un hito sin decisión del CCB.** CC-01 se absorbió en el incremento 1 y CC-03 en un día.

Por encima del 15 % conviene revisar la elicitación: un volumen alto de cambios suele indicar requisitos mal capturados al inicio. En Cóndor, CC-01 nació de una necesidad que el gerente ya había mencionado en la entrevista (ENT-01, A5) y que la ERS 1.0 no tomó.

Este porcentaje es un criterio del equipo, deducido de las horas registradas, y no un valor normativo. Con un solo proyecto no se puede generalizar.
