# Cuestionario de la guía PRAC06, aplicado al producto

## a) ¿Qué atributos de riesgo se deben conocer?

MAGERIT v3 construye el riesgo a partir de atributos del **activo**, de la **amenaza** y de la **salvaguarda**. En Cóndor se registraron los siguientes (`02_Matriz_y_Tratamiento/matriz_riesgos.md` y `matriz_riesgos_magerit.xlsx`):

| Atributo | Qué indica | En Cóndor |
|---|---|---|
| **Activo y sus dependencias** | Qué se protege y de qué depende | 10 activos (A01–A10). Los de soporte heredan el **valor acumulado** de los esenciales que dependen de ellos: la PC principal (A07) vale lo que valen los datos de ventas y la base que aloja |
| **Dimensión de seguridad** | Qué propiedad se pierde | [C] confidencialidad, [I] integridad, [D] disponibilidad, [A] autenticidad y [T] trazabilidad. Por ejemplo, R03 (precio manipulado) afecta [I] |
| **Valor del activo** | Cuánto le importa a la organización | Escala 0–10 de MAGERIT en 5 niveles (MB a MA), valorada por el gerente general en A.2 de PILAR |
| **Amenaza** | Qué puede pasar, según el catálogo de MAGERIT | [A.5] suplantación, [A.8] ransomware, [I.6] corte eléctrico, [E.1] errores de los usuarios… (12 escenarios R01–R12) |
| **Frecuencia** (probabilidad) | Cada cuánto se materializa la amenaza | MA = a diario … MB = cada siglo, estimada con ENT-01, CUE-01 y OBS-01 |
| **Degradación** | Cuánto del activo se pierde | B ≈ 1 %, M ≈ 10 %, A ≈ 100 % |
| **Impacto** | Valor × degradación | Tabla de MAGERIT, Libro III §2.1.1 |
| **Riesgo** | Impacto × frecuencia, en tres momentos | **Potencial** (sin salvaguardas), **actual** (producto 1.1.1 con S1–S3) y **objetivo** (con el plan). Por ejemplo, R02 suplantación: MA → A → M |
| **Salvaguarda** | Control que reduce frecuencia o degradación | S1–S11: tipo (preventiva o de recuperación), madurez y estado (**implantado y verificado** o **propuesto**) |
| **Responsable, fecha, costo e indicador** | Quién responde, cuándo, cuánto cuesta y cómo se mide | Plan de tratamiento: costo del plan propuesto S/ 1 525 e indicadores como «100 % de rutas del Encargado con 403 al Vendedor» |
| **Riesgo residual** | Lo que queda tras tratar | Previsto mientras el control no se verifique; nunca se declara una reducción sin evidencia |

Los atributos mínimos son **valor, frecuencia y degradación**, porque de ellos se calculan el impacto y el riesgo. Los demás convierten el análisis en un plan que se puede ejecutar y verificar.

## b) ¿Cuál sería el protocolo para mitigar riesgos?

El que se siguió en Cóndor tiene siete pasos:

1. **Identificar y valorar los activos y sus dependencias.** Inventario A01–A10 (`01_Inventario`) y proyecto PILAR (`03_PILAR/CONDOR.mgr`, fases A.1 y A.2).
2. **Identificar las amenazas por activo** y estimar su frecuencia y degradación con información documentada: 12 escenarios, con datos de G01, del SDD de G03 y del defecto real DEF-01.
3. **Calcular el impacto y el riesgo potencial y actual**, y **priorizar**. Prioridad 1 (actual MA): R04 certificado y R09 ransomware. Prioridad 2: R02, R05, R11, R08 y R10. Prioridad 3: el resto.
4. **Elegir la respuesta para cada riesgo:** mitigar, aceptar, transferir o evitar. En Cóndor se mitigaron 11 y se **aceptó** R07 (corte de Internet), con un control ya implantado (venta sin Internet), porque no hay un segundo proveedor en la zona.
5. **Definir la salvaguarda con responsable, fecha, costo e indicador** (S1–S11 en `plan_tratamiento.md`), y distinguir lo **implantado** de lo **propuesto**.
6. **Implantar y verificar con una prueba de funcionamiento.** S1 (roles), S2 (validación de entradas) y S3 (respaldo y restauración) se probaron contra la API y la base reales: 18 de 18 comprobaciones (`04_Controles/verificacion_controles.md`), más 122 pruebas automatizadas relacionadas.
7. **Recalcular el riesgo residual y hacer seguimiento.** Revisión mensual del estado de S4–S11 y de sus indicadores, y análisis completo cada 12 meses o cuando cambie la arquitectura. El gerente acepta formalmente los residuales.

La regla principal del protocolo es la del paso 6: **un control sin prueba no reduce el riesgo**. Por eso R04, R06, R08, R09, R10, R11 y R12 siguen con un residual *previsto* hasta implantar y probar sus salvaguardas.
