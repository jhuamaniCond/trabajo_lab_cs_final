# Política de gestión de configuración — Sistema Cóndor

| Campo | Valor |
|---|---|
| Versión | 1.0 (2026-10-30) |
| Responsable de configuración | Integrante 2 — Payehuanca Riquelme, Jhastyn Jefferson (usuario SVN `jpayehuanca`) |
| Repositorio | Apache Subversion 1.14.5 (FSFS), servido con `svnserve`: `svn://127.0.0.1/condor` |
| Ubicación física | `G05_Gestion_Configuracion/02_Repositorio/condor` (portable: carpeta del repositorio más el volcado de `03_Respaldo/`) |
| Cliente | TortoiseSVN 1.14.9 (interfaz gráfica) y `svn` 1.14.5 (línea de comandos) |
| Copia de trabajo de integración | La carpeta `Trabajo Grupal` es una copia de trabajo de `/trunk` |

## 1. Objetivo y alcance

Controlar los elementos del trabajo, desde los requisitos hasta las pruebas. Cada entrega tiene que poder reconstruirse a partir de una etiqueta, y cada cambio tiene que poder rastrearse hasta su solicitud (CC) o defecto (DEF), su revisión SVN y sus pruebas.

## 2. Elementos de configuración (EC)

| ID | Elemento | Ruta en `/trunk` | Tipo | Responsable | Se congela en |
|---|---|---|---|---|---|
| EC-01 | ERS y proyecto REMUS | `G01_Requerimientos/01_ERS`, `03_REMUS` | Requisitos | Integrante 1 | Cada versión de la ERS (1.0, 1.1) |
| EC-02 | Instrumentos de elicitación, cronograma, roles | `G01_Requerimientos/02_…` a `07_…` | Requisitos / gestión | Integrante 1 | v0.1.0 |
| EC-03 | Configuración y respaldo del gestor de requisitos, solicitudes de cambio | `G02_Proceso_Requerimientos` | Cambios | Integrante 2 | Cada solicitud cerrada |
| EC-04 | SDD, fuentes UML, mockups | `G03_Analisis_Sistemas` | Diseño | Integrante 3 | v0.1.0 |
| EC-05 | Libro de estimación y memoria | `G04_Dimensionamiento` | Estimación | Integrante 4 | v0.1.0 |
| EC-06 | Código fuente | `Sistema_Logistico_Condor_final/src` | Código | Desarrolladores | Cada etiqueta |
| EC-07 | Base de datos (migraciones V001…) | `Sistema_Logistico_Condor_final/db` | Base de datos | Desarrolladores | Cada etiqueta |
| EC-08 | Scripts de ejecución y de carga | `Sistema_Logistico_Condor_final/ejecutar.ps1`, `herramientas/`; scripts de cada guía | Scripts | Responsable de cada guía | Cada etiqueta |
| EC-09 | Pruebas automatizadas | `Sistema_Logistico_Condor_final/tests`; G07 a G09 | Pruebas | Evaluadores | Cada etiqueta |
| EC-10 | Documentación técnica y de usuario | `Sistema_Logistico_Condor_final/docs`, `README.md`, `CHANGELOG.md` | Documentación | Todos | Cada etiqueta |
| EC-11 | Política y evidencias de configuración | `G05_Gestion_Configuracion` (salvo `02_Repositorio`) | Configuración | Integrante 2 | v0.1.0 |

**No son elementos de configuración** (se excluyen con `svn:global-ignores` en la raíz del trunk):

- `bin`, `obj`, `.ejecutar`, `.vs`, `TestResults`, `*.user`, `*.suo`: se generan al compilar o al ejecutar.
- `G05_Gestion_Configuracion/02_Repositorio` (`svn:ignore`): es el propio repositorio, y no se versiona dentro de sí mismo.

## 3. Estructura del repositorio

```
/trunk      línea principal = contenido de la carpeta "Trabajo Grupal"
/branches   una rama por solicitud de cambio o defecto que toque el código
/tags       líneas base inmutables (entregas)
```

## 4. Permisos (`conf/authz`)

| Ruta | Equipo (4 integrantes) | Responsable de configuración | Docente |
|---|---|---|---|
| `/` | lectura | lectura y escritura (administra la estructura) | lectura |
| `/trunk` | lectura y escritura | lectura y escritura | lectura |
| `/branches` | lectura y escritura | lectura y escritura | lectura |
| `/tags` | lectura | **solo él crea etiquetas** | lectura |

- No hay acceso anónimo (`anon-access = none`).
- Cada integrante confirma con su propio usuario, así el historial muestra quién hizo cada cambio.
- El hook `pre-commit` rechaza los mensajes de menos de 10 caracteres.
- Las pruebas de permisos y del hook están en `04_Evidencias/prueba_permisos_y_hook.txt`.

## 5. Política de nombres

| Elemento | Formato | Ejemplos |
|---|---|---|
| Etiqueta de entrega del trabajo | `tags/vMAYOR.MENOR.PARCHE` (SemVer) | `v0.1.0` = avance 1 (G01–G05); `v0.2.0` = avance 2; `v1.0.0` = entrega final; **`v1.0.1` = corrección de la entrega final** |
| Versión del producto | `MAYOR.MENOR.PARCHE` en `CHANGELOG.md` | 1.1.0 (CC-01); 1.1.1 (corrección de DEF-01) |
| Rama | `branches/<ID>-<descripcion-corta>` | `branches/DEF-01-precio-catalogo` |
| Mensaje de commit | `<ID>: <qué cambia y por qué>`; el ID es el requisito, la solicitud o el defecto, si lo hay | `DEF-01: el servidor toma el precio del catálogo (CRQ-07)` |

La versión del producto incluida en cada etiqueta se anota en el manifiesto (sección 8).

## 6. Procedimientos

1. **Ciclo de trabajo:** `update` → cambio → pruebas locales → `commit`. Un commit por cambio lógico, con su mensaje.
2. **Cambios en el código:** cada CC o DEF aprobado se desarrolla en su rama. El responsable de configuración la fusiona al trunk solo con la suite de pruebas en verde.
3. **Conflictos:** se resuelven en la copia de trabajo del integrador. Se conservan los archivos de conflicto (`.mine`, `.merge-left`, `.merge-right` y el archivo con marcas) como evidencia, y la decisión se explica en el mensaje del commit.
4. **Etiquetas:** las crea solo el responsable de configuración, con `svn copy` desde el trunk en una revisión con las pruebas en verde. No se modifican: si hace falta corregir algo, se crea otra etiqueta (`v0.1.1`).
5. **Recuperación:** una versión anterior se obtiene con `svn export -r N` o con una copia de trabajo aparte (`update -r N`), sin tocar el trunk ni las etiquetas. Un archivo borrado se restaura con su historia mediante `svn copy ^/trunk/<ruta>@N`.
6. **Respaldo:** `svnadmin dump` comprimido en cada etiqueta y antes de cada entrega. Se verifica cargándolo en un repositorio vacío y con `svnadmin verify`.

## 7. Líneas base

| Línea base | Contenido | Etiqueta / revisión | Fecha |
|---|---|---|---|
| LB-0 | Producto 1.1.0 importado | r2 | 2026-10-30 |
| LB-1 | Avance 1: G01 a G05 y producto 1.1.1 (DEF-01 corregido) | `tags/v0.1.0` = `trunk@15` (copia en r16) | 2026-10-30 |
| LB-2 | Avance 2: G06 a G09 | `tags/v0.2.0` = `trunk@34` (copia en r41) | 2026-11-04 |
| LB-F | Entrega final: G01 a G09 y producto 1.2.0 (CC-03) | `tags/v1.0.0` = `trunk@34` (copia en r35) | 2026-11-04 |
| LB-F.1 | **Entrega final corregida**: lo mismo que LB-F más los cuestionarios G02–G08, las fotos de elicitación, el README actualizado y las evidencias de G05 (r36–r42). Código, base de datos y pruebas idénticos a `v1.0.0` | **`tags/v1.0.1` = `trunk@43` (copia en r44)** | 2026-11-04 |

La etiqueta numera la **entrega del trabajo** y la versión del producto numera **el software**; son independientes. Por eso `tags/v1.0.0` (entrega final) contiene el producto **1.2.0**. Evidencia: `04_Evidencias/05_etiqueta_v1.0.0.txt`.

Después de `v1.0.0` se confirmaron en el trunk documentos que forman parte del paquete (r36–r40). Como las etiquetas no se modifican (procedimiento 4), se creó `tags/v1.0.1` y esa es la **etiqueta de la versión entregada**. `svn diff --summarize ^/tags/v1.0.0 ^/tags/v1.0.1` no muestra cambios en `src/`, `db/` ni `tests/`: el producto 1.2.0 es el mismo. Evidencia: `04_Evidencias/06_etiqueta_v1.0.1.txt`.

## 8. Manifiesto de evidencias (se completa en cada etiqueta)

| Evidencia | Revisión SVN | Fecha | Versión del producto |
|---|---|---|---|
| G01 Requerimientos | r3 | 2026-10-30 | 1.1.0 |
| G02 Proceso de requerimientos | r4 | 2026-10-30 | 1.1.0 |
| G03 Análisis de sistemas | r5 | 2026-10-30 | 1.1.0 |
| G04 Dimensionamiento | r6 | 2026-10-30 | 1.1.0 |
| Rama DEF-01 (creación, corrección) | r8, r10 | 2026-10-30 | 1.1.0 → 1.1.1 |
| CRQ-14 en el servidor (trunk) | r9 | 2026-10-30 | 1.1.0 |
| Fusión con conflicto resuelto | r11 | 2026-10-30 | 1.1.1 |
| Cierre de DEF-01 y evidencias | r12 | 2026-10-30 | 1.1.1 |
| Demostración de recuperación (borrado y restauración) | r13, r14 | 2026-10-30 | 1.1.1 |
| G05: herramientas, recuperación y manifiesto | r15 | 2026-10-30 | 1.1.1 |
| **Línea base del avance 1** | **`tags/v0.1.0` (r16)** | 2026-10-30 | **1.1.1** |
| Cuestionarios G02–G08, fotos de elicitación, README 1.2.0, historial | r36–r40 | 2026-11-04 | 1.2.0 |
| **Línea base del avance 2** | **`tags/v0.2.0` (r41, copia de `trunk@34`)** | 2026-11-04 | **1.2.0** |
| Línea base de la entrega final | `tags/v1.0.0` (r35, copia de `trunk@34`) | 2026-11-04 | 1.2.0 |
| Política, README y dictamen apuntan a `v1.0.1` (r43: saltos de línea CRLF restaurados) | r42, r43 | 2026-11-04 | 1.2.0 |
| **Línea base de la entrega final corregida (versión entregada)** | **`tags/v1.0.1` (r44, copia de `trunk@43`)** | 2026-11-04 | **1.2.0** |
| Respaldo `condor_r44.dump.gz`, evidencia de `v1.0.1` e historial r1–r44 | r45 | 2026-11-04 | 1.2.0 |
