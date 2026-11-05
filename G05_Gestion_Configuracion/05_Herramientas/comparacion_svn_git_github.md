# Comparación: SVN frente a Git (tecnología) y GitHub (plataforma)

Subversion es obligatorio en G05; Git y GitHub se comparan con su documentación oficial y con la experiencia del equipo. El producto Cóndor nació en un repositorio Git, del que quedan `.gitignore` y `.github/`.

## 1. Subversion frente a Git (sistemas de control de versiones)

| Criterio | **Subversion 1.14** (usado en G05) | Git 2.x |
|---|---|---|
| Modelo | Centralizado: un repositorio en el servidor y copias de trabajo | Distribuido: cada clon es un repositorio completo con todo el historial |
| Numeración | Revisión global y creciente (r1…r14): «la entrega está en r12» se entiende sin ambigüedad | Hash SHA por commit; el orden lo da el grafo |
| Trabajo sin conexión | Solo se edita; `log`, `diff` contra revisiones anteriores y `commit` necesitan el servidor | `log`, `diff`, `commit` y ramas, todo local |
| Ramas y etiquetas | Copias baratas (`svn copy`) en `/branches` y `/tags`; son carpetas del repositorio | Punteros livianos; crear y cambiar de rama es inmediato |
| Fusión | `svn merge` con `svn:mergeinfo`; buena para ramas de cambio de vida corta (como DEF-01) | Fusión de 3 vías muy madura; *rebase* |
| Permisos | **Por ruta** (`authz`): se pudo restringir `/tags` al responsable de configuración y dar solo lectura al docente | Por repositorio completo; los permisos por rama los da la plataforma (reglas de protección) |
| Etiquetas inmutables | Por permisos y hooks | Las etiquetas pueden moverse con `--force`, salvo que la plataforma lo impida |
| Archivos binarios grandes | Bien: solo se descarga la revisión pedida | Cada clon trae todo el historial; requiere Git LFS |
| Checkout parcial | Natural (`svn checkout …/trunk/Sistema_Logistico_Condor_final`, como en las copias de los integrantes) | *sparse-checkout*, menos directo |
| Curva de aprendizaje | Baja; TortoiseSVN cubre todo desde el Explorador | Media-alta (índice, *staging*, *remotes*, *rebase*) |
| Respaldo | `svnadmin dump` / `hotcopy` del servidor | Cualquier clon es un respaldo; `git bundle` |

## 2. GitHub como plataforma (frente a un servidor SVN propio)

| Criterio | Servidor SVN propio (`svnserve`) | GitHub |
|---|---|---|
| Qué es | Solo el servidor del repositorio | Plataforma en la nube sobre Git: alojamiento, *pull requests*, revisión de código, *issues*, *Actions* (CI), *Projects*, wiki, *releases* |
| Revisión de código antes de integrar | Manual (el integrador revisa y corre las pruebas, como en r11) | *Pull request* con comentarios por línea, aprobaciones obligatorias y estado de CI |
| Integración continua | Externa (aquí, `probar_en_docker.sh` a mano) | GitHub Actions: la suite corre en cada *push* o *pull request* |
| Gestión de incidencias | Externa (Redmine en G02) | *Issues* y *Projects* integrados con los commits («fixes #12») |
| Control de acceso | `authz` local; sin red externa | Equipos, roles, ramas protegidas, 2FA |
| Disponibilidad y datos | En la PC del equipo, portable, sin internet | En la nube: depende de internet y de una cuenta; los datos quedan en un tercero |
| Costo | Gratis | Gratis para repositorios públicos y privados con funciones básicas; de pago las funciones avanzadas |

## 3. Conclusión para el Sistema Cóndor

- **SVN cubrió bien lo que pide G05**, con dos ventajas concretas en este trabajo: los **permisos por ruta** (`/tags` protegido, docente de solo lectura) y la **revisión global**, que permite citar en cada evidencia la revisión exacta (manifiesto de la política). Además, el repositorio y su volcado son portables y no dependen de internet.
- **Git + GitHub serían preferibles** para un equipo que trabaja en paralelo y fuera de línea, o que quiere revisión de código con *pull requests* y CI automática. En SVN la integración (r11), las pruebas previas y el registro de defectos se hicieron con herramientas aparte: el script de Docker y Redmine.
- **Equivalencias entre ambos:** la rama `branches/DEF-01-precio-catalogo` equivale a una rama de *feature* con su *pull request*; la etiqueta `tags/v0.1.0` equivale a un *tag* o *release* de GitHub; el hook `pre-commit` equivale a una regla de protección de rama o a un *check* obligatorio.
