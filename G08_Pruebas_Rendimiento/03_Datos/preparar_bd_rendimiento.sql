-- G08 Pruebas de rendimiento: conjunto de datos de la base condor_rendimiento.
--
-- La base la crea preparar_entorno.ps1 y su esquema lo crea Condor.Api al
-- arrancar (migraciones V001-V014, que también crean encargado, vendedor1 y
-- vendedor2). Este script deja siempre el mismo conjunto de datos:
--   * 3 000 productos activos (el tamaño de catálogo de RNF-01), ids 1-3000,
--     precios entre S/ 1.00 y S/ 59.99;
--   * 200 clientes con DNI 40000001-40000200;
--   * 10 vendedores de carga, carga01-carga10, con la clave Vendedor2026!
--     (copian el hash PBKDF2 de vendedor1, así que no se guarda la clave);
--   * 0 comprobantes y las series en 0 (lo repite reiniciar_ventas.sql antes
--     de cada escenario).
-- Los nombres son ficticios pero siguen la forma del catálogo real
-- (familia + medida + marca) para que la búsqueda por trigramas trabaje igual.

BEGIN;

TRUNCATE comprobante_sunat, comprobante_detalle, guia_detalle, guia_remision,
         comprobante, compra_detalle, compra, producto, cliente RESTART IDENTITY CASCADE;
UPDATE serie SET ultimo_correlativo = 0;

WITH familia(f, nombre) AS (
    SELECT row_number() OVER (), n FROM unnest(ARRAY[
        'Tornillo autorroscante', 'Clavo de acero', 'Perno hexagonal', 'Tuerca hexagonal', 'Arandela plana',
        'Tubo PVC', 'Codo PVC', 'Tee PVC', 'Cable THW', 'Cinta aislante',
        'Interruptor simple', 'Tomacorriente doble', 'Foco LED', 'Pintura látex', 'Esmalte sintético',
        'Brocha', 'Rodillo', 'Lija al agua', 'Disco de corte', 'Broca para concreto',
        'Llave de paso', 'Grifo', 'Manguera', 'Candado', 'Bisagra',
        'Cerradura', 'Silicona', 'Pegamento PVC', 'Alambre galvanizado', 'Malla metálica']) AS n
), medida(m, nombre) AS (
    SELECT row_number() OVER (), n FROM unnest(ARRAY[
        '1/4 in', '3/8 in', '1/2 in', '3/4 in', '1 in', '2 mm', '5 mm', '10 mm', '1 m', '3 m']) AS n
), marca(k, nombre) AS (
    SELECT row_number() OVER (), n FROM unnest(ARRAY[
        'Cóndor', 'Majes', 'Andino', 'Pacífico', 'Volcán', 'Misti', 'Colca', 'Chachani', 'Sabandía', 'Yura']) AS n
), combinacion AS (
    SELECT (f.f - 1) * 100 + (m.m - 1) * 10 + k.k AS i,
           f.nombre || ' ' || m.nombre || ' ' || k.nombre AS nombre
    FROM familia f CROSS JOIN medida m CROSS JOIN marca k
)
INSERT INTO producto (nombre, precio, unidad, codigo_barras)
SELECT nombre,
       round(1 + ((i * 37) % 5899) / 100.0, 2),
       CASE WHEN nombre LIKE '% m %' OR nombre LIKE '% m' THEN 'MT' ELSE 'UND' END,
       '775' || lpad(i::text, 10, '0')
FROM combinacion
ORDER BY i;

INSERT INTO cliente (tipo_documento, numero_documento, nombre, direccion)
SELECT '1', (40000000 + g)::text, 'Cliente de prueba ' || lpad(g::text, 3, '0'), 'Majes, Arequipa'
FROM generate_series(1, 200) AS g;

DELETE FROM usuario WHERE nombre_usuario LIKE 'carga__';
INSERT INTO usuario (nombre_usuario, nombre_completo, rol, hash_clave)
SELECT 'carga' || lpad(g::text, 2, '0'), 'Vendedor de carga ' || g, 'VENDEDOR',
       (SELECT hash_clave FROM usuario WHERE nombre_usuario = 'vendedor1')
FROM generate_series(1, 10) AS g;

UPDATE usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL;
TRUNCATE acceso_usuario;

COMMIT;

VACUUM ANALYZE;

SELECT (SELECT count(*) FROM producto) AS productos,
       (SELECT count(*) FROM cliente) AS clientes,
       (SELECT count(*) FROM usuario WHERE activo) AS usuarios,
       (SELECT count(*) FROM comprobante) AS comprobantes;
