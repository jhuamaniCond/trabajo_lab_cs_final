# Verificación de los controles implantados (G06)

Fecha: 2026-10-31 00:22 · API http://localhost:5080 (producto 1.1.1) · base PostgreSQL `condor` (contenedor Cas_condor)

Generado con `verificar_controles.py`. Cada fila es una comprobación contra el sistema en ejecución.

| Control | Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| S1 | Sin token: GET /api/productos | 401 | 401 | ✔ cumple |
| S1 | GET /api/reportes/ventas: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | GET /api/proveedores: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | GET /api/respaldos: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | POST /api/escritorio/compras/buscar: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | POST /api/escritorio/guias/buscar: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | GET /api/escritorio/respaldos: Vendedor / Encargado | 403 / 200 | 403 / 200 | ✔ cumple |
| S1 | Indicador: rutas del Encargado que rechazan al Vendedor | 100 % | 100 % (6/6) | ✔ cumple |
| S1 | Bloqueo: 5 intentos fallidos de vendedor2 y luego la clave correcta | 423 (bloqueada 15 min) | 423 | ✔ cumple |
| S1 | Contraseñas guardadas como hash PBKDF2 (100 000 iteraciones) | 3 de 3 usuarios | 3 de 3 | ✔ cumple |
| S2 | Nota de venta con precio manipulado S/ 0.10 (catálogo S/ 30.80) | se guarda S/ 30.80 y la descripción del catálogo | HTTP 200; precio S/ 30.8; «Cemento Portland tipo IP x 42.5 kg» (NV01-6) | ✔ cumple |
| S2 | Rechazo de cantidad 100 000 (> 99 999) | 400 y no se emite | 400: La línea 1 debe tener una cantidad mayor que cero, hasta 99 999 y con 3 decimales como máximo. | ✔ cumple |
| S2 | Rechazo de cantidad 1.0005 (más de 3 decimales) | 400 y no se emite | 400: La línea 1 debe tener una cantidad mayor que cero, hasta 99 999 y con 3 decimales como máximo. | ✔ cumple |
| S2 | Rechazo de 101 líneas | 400 y no se emite | 400: Un comprobante no puede tener más de 100 líneas. | ✔ cumple |
| S2 | Rechazo de producto inexistente | 400 y no se emite | 400: El producto 999999 no existe o ya no está en el catálogo. | ✔ cumple |
| S3 | pg_dump -Fc de la base condor (formato de RF-16) | archivo generado | código 0; 79904 bytes | ✔ cumple |
| S3 | pg_restore en una base vacía (condor_restaurada) | sin errores | código 0  | ✔ cumple |
| S3 | Conteo de filas por tabla: original frente a restaurada | idénticos | producto 60/60; cliente 32/32; comprobante 82/82; comprobante_detalle 207/207; proveedor 26/26; compra 28/28; guia_remision 26/26; usuario 3/3 | ✔ cumple |

**Resultado: 18 de 18 comprobaciones cumplen.**

Efectos en la base de demostración: se emitió una nota de venta de prueba (NV01, no va a la SUNAT), se registró la terminal `PC-G06-PRUEBA` y `vendedor2` quedó bloqueado 15 minutos. La base restaurada se eliminó al terminar.
