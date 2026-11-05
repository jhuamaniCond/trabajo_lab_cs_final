# Comparación de herramientas — G03 Análisis de sistemas

El enunciado propone **PlantUML o diagrams.net** para el modelado y **Moqups** para los mockups. Se compara cada área con al menos dos opciones. Se instaló y usó PlantUML; diagrams.net y Moqups se evaluaron con su documentación oficial.

## 1. Modelado UML

| Criterio | **PlantUML 1.2024.7** (elegida) | diagrams.net (draw.io) | StarUML 6 |
|---|---|---|---|
| Forma de trabajo | Texto (`.puml`) → imagen | Editor gráfico (arrastrar y soltar) | Editor gráfico con modelo UML |
| Costo / licencia | Gratuita, GPL | Gratuita, Apache 2.0 | De pago (prueba sin límite de tiempo con marca de agua) |
| Fuente editable | `.puml` de texto plano | `.drawio` (XML comprimido) | `.mdj` (JSON) |
| Diferencias en SVN | **Línea por línea**: se ve qué relación o atributo cambió | XML difícil de leer en un diff | JSON extenso |
| Diagramas usados en G03 | Casos de uso, clases, secuencia, estados, actividad, componentes, despliegue y ER | Todos (como formas libres) | Todos los UML |
| Disposición | Automática (Smetana o Graphviz); poco control fino | Manual: control total | Manual, con ayudas |
| Validación UML | Sintaxis de PlantUML | Ninguna (son formas) | Sí, valida el modelo |
| Regenerar al cambiar el diseño | Editar el texto y volver a generar | Mover formas a mano | Editar el modelo |
| Exportación | PNG, SVG, PDF, LaTeX | PNG, SVG, PDF | PNG, SVG, PDF |

**Conclusión:** PlantUML encaja con la gestión de configuración del trabajo. Los diagramas son elementos de configuración de texto (G05): sus cambios se revisan en el historial de SVN, como pasó con las correcciones OS-01 a OS-03 de la revisión. Además, se regeneran en segundos cuando cambia el diseño. diagrams.net daría más control visual, pero sus archivos no se pueden comparar entre revisiones.

## 2. Mockups

| Criterio | **PlantUML Salt** (elegida) | Moqups | Balsamiq Wireframes |
|---|---|---|---|
| Forma de trabajo | Texto → imagen | Editor web gráfico | Editor gráfico (escritorio o web) |
| Costo | Gratuito | Plan gratuito limitado a 1 proyecto y 200 objetos; de pago para más | De pago (prueba de 30 días) |
| Cuenta en línea | No | Sí | Sí (web) / licencia (escritorio) |
| Fuente en SVN | `.puml` de texto | No hay archivo local editable, solo la exportación | `.bmpr` (SQLite) |
| Fidelidad visual | Baja-media (esquemática) | Alta | Media (estilo boceto) |
| Interacción / prototipo navegable | No | Sí (enlaces entre páginas) | Sí |
| Componentes de escritorio (pestañas, grillas, combos, radios) | Sí | Sí | Sí |

**Conclusión:** para G03 bastan mockups esquemáticos que muestren los campos, los atajos, las columnas y los mensajes de cada caso de uso. Salt los produce como texto versionable, sin cuenta ni límite de objetos. Moqups sería preferible si se necesitara un prototipo navegable para validar con el cliente real. La sustitución queda registrada en las fichas para que el docente la valide.
