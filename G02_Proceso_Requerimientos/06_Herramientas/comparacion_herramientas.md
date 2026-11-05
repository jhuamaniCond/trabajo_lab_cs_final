# Comparación de herramientas — G02 Proceso de requerimientos

La guía PRAC02 propone **Scarab** e **i-doit**. Se eligió **Redmine**, el sucesor práctico de Scarab como gestor de peticiones con flujo configurable. Se compara con las dos herramientas de la guía y con **Jira**, la opción comercial más usada.

i-doit y Redmine se instalaron y usaron en el Laboratorio 2 del curso (contenedores `bheisig/idoit:1.19-open` y `redmine`). Scarab y Jira se evaluaron con su documentación oficial.

## 1. Cuadro comparativo

| Criterio | **Redmine 7.0.1** (elegida) | i-doit 1.19 Open | Scarab 0.21 | Jira Cloud |
|---|---|---|---|---|
| Tipo | Gestor de peticiones y proyectos | CMDB (inventario de TI) | Gestor de incidencias (*issue tracker*) | Gestor de incidencias y proyectos |
| Disponibilidad | Activa; imagen oficial de Docker | Activa; la edición Open tiene funciones limitadas | **Abandonado** (última versión de 2005); Java 1.4 y Tomcat 5, no se puede reproducir hoy | Activa, en la nube |
| Licencia / costo | GPL v2, gratuita | AGPL (Open), gratuita | Apache, gratuita | De pago; plan gratuito de hasta 10 usuarios |
| Instalación | 1 contenedor con SQLite | 2 contenedores (MariaDB y Apache/PHP) y asistente web | No reproducible | Sin instalación |
| Estados y flujo | **Configurables por tipo de petición y por rol**: se definieron exactamente los 7 estados del enunciado | Ciclo de vida CMDB fijo de 12 estados; la edición Open no tiene módulo de cambios | Configurables por módulo | Configurables, con editor visual |
| Responsable por transición | Sí: el flujo solo deja hacer cada transición al rol autorizado | No | Parcial | Sí (condiciones y validadores) |
| Historial | Fecha, usuario, valor anterior y nuevo, nota y adjuntos en cada cambio | Registro de cambios por objeto, sin notas por transición | Sí | Sí |
| Campos propios | Sí (13 campos: ID ERS, criterio de aceptación, impacto en costo, decisión…) | Sí (categorías personalizadas) | Sí | Sí |
| Relaciones entre peticiones | Sí (CC-01 relacionado con los 7 requisitos que afecta) | Relaciones entre objetos | Sí | Sí |
| Versiones / líneas base | Sí (versiones 1.0.0 y 1.1.0, hoja de ruta) | No | Parcial | Sí (*releases*) |
| Reportes de seguimiento | Resumen por tipo, prioridad, asignado, autor y versión; consultas guardadas | Informes de objetos (Report Manager) | Consultas | Tableros y paneles avanzados |
| Exportación | CSV, PDF y Atom; API REST JSON/XML | CSV y PDF; API JSON-RPC | XML | CSV, Excel y API REST |
| Automatización | API REST completa y `rails runner` (se usó para configurar y cargar) | API JSON-RPC | No | API REST y automatizaciones |
| Datos en el equipo del alumno | Sí (respaldo portable `redmine.db`) | Sí | Sí | No: quedan en la nube de Atlassian |

## 2. Redmine frente a la alternativa de la guía (i-doit)

| Aspecto | Redmine | i-doit Open |
|---|---|---|
| ¿Implementa el flujo del enunciado? | **Sí, tal cual**: los 7 estados y las 14 transiciones por rol | No: hay que traducir cada etapa a un estado del ciclo de vida CMDB («planned», «in operation»…) |
| ¿Reconstruye el recorrido de los 5 requisitos? | Sí: historial con fecha, responsable y nota de evidencia en cada transición, más el PDF de la petición | Solo los cambios del campo de estado, sin la nota ni el adjunto de evidencia |
| Solicitud de cambio con análisis de impacto | Tipo *Solicitud de cambio* con campos de motivo, impacto en diseño, costo, plazo, riesgos, pruebas y decisión | Habría que modelarla como un objeto de tipo propio |
| Esfuerzo de puesta en marcha (Lab 2) | Bajo | Medio (base de datos, asistente y licencia Open) |
| Para qué sirve mejor | Proceso de requisitos y cambios | Inventario de elementos de configuración, que es más útil en G05 |

## 3. Ventajas y desventajas de la herramienta elegida

| Ventajas | Desventajas |
|---|---|
| Flujo por rol que **impide** saltarse etapas: un desarrollador no puede aprobar, y el CCB es el único que aprueba, rechaza o cierra. | No es un gestor de requisitos puro: no tiene plantillas IEEE 830 ni matrices automáticas. Esa parte se cubre con REMUS en G01. |
| Historial completo y exportable (CSV y PDF) con fecha y usuario reales. | Una sola base SQLite: para varios usuarios simultáneos en red conviene PostgreSQL. |
| Gratuito, local y portable (un archivo `.db`). | Interfaz menos moderna que Jira; los reportes son tablas, sin gráficos. |
| API REST: carga reproducible por script desde la misma fuente que la ERS. | La configuración inicial del flujo y de los campos requiere permisos de administrador. |

## 4. Conclusión

**Redmine** es la opción operativa para G02 por cuatro razones:

- reproduce exactamente el flujo exigido y lo hace cumplir por rol;
- conserva el historial con fecha, responsable y evidencia;
- relaciona cada solicitud de cambio con los requisitos que afecta y con la versión;
- es gratuito, se instala con un contenedor y se respalda en un solo archivo.

i-doit encaja mejor como CMDB y no cubre el proceso de cambios en su edición Open. Scarab ya no se puede instalar. Jira ofrece algo equivalente, pero es de pago para el uso continuo y deja los datos fuera del repositorio SVN del trabajo.
