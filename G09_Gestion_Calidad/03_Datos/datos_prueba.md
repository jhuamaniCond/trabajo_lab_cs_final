# Datos de prueba de la suite Selenium (G09)

Fuente: `02_Suite/datos.py`. Hay tres tipos de datos.

## 1. Datos fijos de la base de demostración

| Dato | Valor | Origen | Casos |
|---|---|---|---|
| Encargado general | `encargado` / `Encargado2026!` | Migración `V014__usuarios_y_roles.sql` (docs/seguridad.md) | CP-01, CP-12, CP-13 |
| Vendedor | `vendedor1` / `Vendedor2026!` | V014 | CP-03 a CP-11, CP-14 |
| Vendedor para el intento fallido | `vendedor2` (clave errada `ClaveEquivocada1`, luego la correcta) | V014 | Solo CP-02 |
| Producto que siempre existe | búsqueda «cemento» (Cemento Portland tipo I e IP x 42.5 kg) | `db/datos/lista_precios.csv` | CP-05, CP-07 a CP-10, CP-13 |
| Producto para la compra | búsqueda «clavo» | `lista_precios.csv` | CP-13 |
| Usuario inexistente | `usuario_que_no_existe` | — | CP-02 |

## 2. Datos aislados, generados en cada ejecución

Cada ejecución usa un sufijo `MMDDhhmmss` (`datos.SUFIJO`) y números aleatorios. Ningún caso usa lo que creó otro caso ni otra ejecución, y el orden de los casos no cambia el resultado.

| Dato | Regla de generación | Por qué cumple la regla del dominio | Casos |
|---|---|---|---|
| DNI nuevo | `9` + 7 dígitos aleatorios | 8 dígitos (`ValidadorDocumento`). Ningún DNI de la demostración empieza con 9 | CP-04, CP-05, CP-10 |
| RUC nuevo | `20` + 8 dígitos + dígito verificador módulo 11 con pesos 5-4-3-2-7-6-5-4-3-2 | Mismo cálculo que `ValidadorDocumento.DigitoVerificadorRuc` | CP-08, CP-13 |
| Nombre de cliente | `Cliente G09 <sufijo>-<3 dígitos>` | ≤ 200 caracteres | CP-04, CP-10 |
| Nombre de producto | `Producto G09 prueba <sufijo>-<3 dígitos>` | Nombre único (409 si se repite) | CP-05, CP-06 |
| Razón social | `Constructora G09 <sufijo> S.A.C.`, `Distribuidora G09 <sufijo> S.A.C.` | — | CP-08, CP-13 |
| Compra | Serie `F` + 3 últimos dígitos del sufijo; número aleatorio de 8 dígitos; fecha de ayer | Serie de 4 caracteres; número de 1 a 99 999 999; fecha no futura (`ValidadorCompra`) | CP-13 |

## 3. Datos inválidos (particiones y límites)

| Dato | Valor | Regla que lo rechaza | Mensaje esperado | Caso |
|---|---|---|---|---|
| DNI corto | `1234` | Largo 8 u 11 (portal y `ValidadorDocumento`) | «El documento debe ser un DNI de 8 dígitos o un RUC de 11.» | CP-05 |
| DNI no registrado | DNI nuevo sin registrar | Búsqueda 404 | «Ese documento no está registrado. Pulse Nuevo cliente…» | CP-05 |
| RUC con dígito errado | RUC nuevo con el último dígito + 1 | `ValidadorDocumento` (servidor) | «El RUC no es válido: revise los números (el dígito verificador no coincide).» | CP-05 |
| Cantidad límite | `0` | Cantidad > 0, ≤ 99 999, 3 decimales | «La cantidad debe ser mayor que cero…» | CP-05 |
| Precio límite | `0` | `ValidadorProducto` | «El precio debe ser mayor que cero.» | CP-05 |
| Nombre vacío | — | `ValidadorProducto` | «El nombre es obligatorio.» | CP-05 |
| Factura sin cliente | Factura con detalle y sin RUC | `EmisionComprobante.Errores` | «La factura requiere un cliente con RUC…» | CP-09 |
| Boleta > S/ 700 sin DNI | 40 bolsas de cemento | R. 007-99/SUNAT en `EmisionComprobante` | «Las boletas de más de S/ 700.00 deben llevar el DNI del cliente…» | CP-09 |
| Período invertido | 30/11/2026 a 01/11/2026 | Ruta `GET /api/comprobantes` | «La fecha final no puede ser anterior a la inicial.» | CP-11 |
| Período > 366 días | 01/01/2024 a hoy | `ReporteVentas.ValidarPeriodo` | Mensaje de período inválido | CP-12 |
| Compra repetida | Mismo proveedor, tipo, serie y número | `ux` de la base → `CompraDuplicadaException` | «… ya está registrada …» | CP-13 |
| Fecha de compra futura | Hoy + 3 días | `ValidadorCompra` | «La fecha del comprobante no puede ser posterior a hoy.» | CP-13 |

## 4. Efecto sobre la base de demostración

Las ejecuciones dejan sus registros en la base `condor`. Es intencional: así se demuestra que lo registrado persiste. Todos se identifican por «G09» en el nombre. Tras las seis ejecuciones de `04_Reportes` hay, entre otros:

- clientes «Cliente G09 …»;
- proformas PR01-00000027 a PR01-00000034, y algunas siguen vigentes porque su caso se detuvo en el fallo de la ejecución de defectos;
- boletas y facturas de prueba en el historial.

Antes de llevar la base a producción se usa una base limpia (`db/servidor`). La suite no necesita datos previos además del catálogo y los usuarios de demostración.
