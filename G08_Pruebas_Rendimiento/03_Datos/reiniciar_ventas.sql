-- G08: se ejecuta antes de cada escenario para que todos partan del mismo
-- estado (3 000 productos, 200 clientes, 0 comprobantes, series en 0).
-- No toca el catálogo, los clientes ni los usuarios.
BEGIN;
TRUNCATE comprobante_sunat, comprobante_detalle, guia_detalle, guia_remision, comprobante RESTART IDENTITY CASCADE;
UPDATE serie SET ultimo_correlativo = 0;
UPDATE usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL;
TRUNCATE acceso_usuario;
COMMIT;
VACUUM ANALYZE comprobante;
VACUUM ANALYZE comprobante_detalle;
