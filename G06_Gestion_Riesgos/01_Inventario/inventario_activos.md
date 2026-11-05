# Inventario de activos y dependencias — MAGERIT v3

| Campo | Valor |
|---|---|
| Sistema de información | Sistema de Ventas y Facturación Cóndor 1.1.1 — Ferretería Cóndor Majes S.A.C. |
| Alcance | Procesos PN-01 (venta y facturación), PN-02 (cotización) y PN-03 (abastecimiento), con la infraestructura de la ferretería (3 PC, red local, enlace a la SUNAT) |
| Horizonte | Próximos 12 meses |
| Método | MAGERIT v3 (Libro I: método; Libro II: catálogo de elementos; Libro III: técnicas) |
| Herramienta | PILAR Basic 2026.1.1, biblioteca `BASIC_es` (proyecto `03_PILAR/CONDOR.mgr`) |
| Responsable | Integrante 4 — Chaisa Fernández, Anthony Leonel (líder de G06) · validó: gerente general (representado) |
| Fecha | 2026-10-31 |

## 1. Activos

Clases según el catálogo de MAGERIT (Libro II, capítulo 2).

| ID | Activo | Capa / clase MAGERIT | Propietario | Descripción |
|---|---|---|---|---|
| A01 | Servicio de venta y facturación | [essential] [service] servicio | Gerente general | Procesos PN-01 y PN-02: buscar productos, emitir boletas, facturas, notas de venta y proformas, imprimir y enviar a la SUNAT |
| A02 | Datos de ventas y comprobantes | [essential] [info] información | Gerente general / contador | Comprobantes con su detalle, clientes (DNI, RUC), XML firmados y CDR de la SUNAT; tienen valor tributario durante 5 años |
| A03 | Datos de compras, costos y proveedores | [essential] [info] información | Encargado general | Proceso PN-03: compras, costos unitarios y proveedores; confidenciales frente a los vendedores (CFL-06) |
| A04 | Certificado digital y credenciales SOL | [K] claves criptográficas | Gerente general | Certificado con el que se firman los XML UBL y usuario SOL de la SUNAT |
| A05 | Aplicación Cóndor (WPF + Condor.Api) | [SW] aplicaciones · [prp] desarrollo propio | Equipo de desarrollo | Versión 1.1.1; la API es la única que accede a la base |
| A06 | Base de datos PostgreSQL 16 | [SW] aplicaciones · [dbms] sistema de gestión de bases de datos | Encargado general | Base central `condor` en un contenedor Docker de la PC principal |
| A07 | PC principal (servidor) | [HW] equipamiento · [host] equipos medios | Encargado general | Aloja la API, la base y el disco de respaldos; también es caja 1 |
| A08 | Red local e Internet | [COM] redes de comunicaciones · [LAN] red local, [Internet] | Encargado general | Une las 3 PC con la API; enlace a la SUNAT para enviar comprobantes |
| A09 | Disco externo de respaldos | [Media] soportes de información · [disk] discos | Encargado general | Guarda los archivos `.backup` de RF-16 |
| A10 | Personal y cuentas de usuario | [P] personal · [ui] usuarios internos | Gerente general | 2 a 3 vendedores por turno y el encargado general, con sus cuentas (`vendedor1`, `vendedor2`, `encargado`) |

## 2. Dependencias

Un activo superior depende de uno inferior si un fallo del inferior afecta al superior. PILAR propaga el valor de los activos esenciales hacia abajo por estas dependencias.

| Activo superior | Depende de | Motivo |
|---|---|---|
| A01 Servicio de venta | A05, A08, A10 | Sin la aplicación, la red o el personal no se vende |
| A02 Datos de ventas | A05, A06, A04, A09 | Se crean con la aplicación, se guardan en la base, se firman con el certificado y se respaldan en el disco |
| A03 Datos de compras | A05, A06, A09 | Igual que A02, sin firma |
| A05 Aplicación | A07, A06, A08 | La API corre en la PC principal y usa la base; las PC llegan a ella por la red |
| A06 Base de datos | A07 | Corre en un contenedor de la PC principal |
| A04 Certificado | A07 | Instalado en la PC principal |
| A09 Disco de respaldos | A07 | Se conecta a la PC principal |
| A07 PC principal | A08 | Expone la API a las otras PC |

```
           A01 Servicio de venta ─────────────┐
            │            │                    │
   A02 Datos de ventas  A03 Datos de compras  A10 Personal y cuentas
     │   │    │   │       │    │    │
     │   │   A04  └─A09───┘    │    │
     │   │    │      │         │    │
     └── A05 Aplicación ───────┘    │
           │        │               │
          A06 Base de datos         │
           │                        │
          A07 PC principal ─── A08 Red local e Internet
```

## 3. Valoración de los activos esenciales

**Escala de MAGERIT** (Libro II, capítulo 4), la misma que usa PILAR: 0 despreciable · 1 muy bajo · 2–3 bajo · 4–5 medio · 6–8 alto · 9 muy alto · 10 extremo.

**Dimensiones:** [D] disponibilidad · [I] integridad · [C] confidencialidad · [A] autenticidad · [T] trazabilidad.

| Activo | [D] | [I] | [C] | [A] | [T] | Justificación (fuente) |
|---|---|---|---|---|---|---|
| A01 Servicio de venta y facturación | **8** | — | — | — | — | Unas 150 ventas al día y hasta 250 en campaña; en hora punta hay colas de 5 o 6 personas (ENT-01, A2). Una caída de medio día detiene los ingresos del local y empuja a los clientes de obra a la competencia (alto). |
| A02 Datos de ventas y comprobantes | 7 | **9** | 5 | **8** | **8** | [I] Un importe o correlativo alterado tiene consecuencias tributarias con la SUNAT (CRQ-01, CRQ-05): muy alto. [A] y [T] Cada comprobante debe decir quién lo emitió (CRQ-11, CC-01). [C] DNI y RUC de clientes son datos personales, pero de sensibilidad media (Ley 29733). [D] El historial y el reenvío a la SUNAT dependen de ellos. |
| A03 Datos de compras y costos | 4 | 6 | **7** | 5 | 5 | [C] Los costos y egresos no deben conocerlos los vendedores (CFL-06, CRQ-12): alto. [I] Un costo alterado distorsiona el margen. |
| A04 Certificado digital (valoración propia) | 6 | 8 | **9** | **9** | 6 | Con el certificado y la clave SOL se pueden emitir comprobantes a nombre de la ferretería: [C] y [A] muy altos. |

Los activos de soporte (A05 a A10) **no se valoran directamente**: PILAR les asigna el valor acumulado de los esenciales que dependen de ellos (Libro I, 3.1.3).

## 4. Información utilizada

- Entrevista ENT-01 al gerente y al encargado, cuestionario CUE-01 a los vendedores y observación OBS-01 (G01): volumen de ventas, horas punta, cortes de internet y prácticas de respaldo.
- Requisitos de la ERS 1.1 (CRQ-01 a CRQ-15, RNF-03 a RNF-07) y conflictos CFL-02, CFL-05 y CFL-06.
- Diseño (SDD de G03): arquitectura cliente – API – base, despliegue en la PC principal y modelo de datos.
- Historia del producto: defecto DEF-01 (precio aceptado desde la PC), corregido en 1.1.1 (G05).
- Catálogo de amenazas de MAGERIT (Libro II, capítulo 5) y biblioteca `BASIC_es` de PILAR.
