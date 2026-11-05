-- V014: usuarios con contraseña y roles (CC-01; reemplaza el perfil único
-- MAESTRO sin credenciales de HU-14).

-- Cada persona entra con su usuario y contraseña. La contraseña nunca se
-- guarda: solo su hash PBKDF2-SHA256 (Condor.Dominio.Seguridad.HashClave).
-- Tras 5 intentos fallidos la cuenta queda bloqueada 15 minutos.
CREATE TABLE usuario (
    id                 bigserial     PRIMARY KEY,
    nombre_usuario     varchar(20)   NOT NULL UNIQUE CHECK (nombre_usuario = lower(btrim(nombre_usuario)) AND nombre_usuario <> ''),
    nombre_completo    varchar(100)  NOT NULL CHECK (btrim(nombre_completo) <> ''),
    rol                varchar(20)   NOT NULL CHECK (rol IN ('VENDEDOR', 'ENCARGADO')),
    hash_clave         varchar(200)  NOT NULL,
    activo             boolean       NOT NULL DEFAULT true,
    intentos_fallidos  int           NOT NULL DEFAULT 0 CHECK (intentos_fallidos >= 0),
    bloqueado_hasta    timestamptz,
    ultimo_acceso      timestamptz,
    creado_en          timestamptz   NOT NULL DEFAULT now()
);

-- Bitácora de accesos, correctos y fallidos, desde la app de escritorio y
-- desde la API (control de G6: trazabilidad de quién entró, cuándo y desde dónde).
CREATE TABLE acceso_usuario (
    id              bigserial     PRIMARY KEY,
    nombre_usuario  varchar(20)   NOT NULL,
    terminal        varchar(60),
    exitoso         boolean       NOT NULL,
    detalle         varchar(200)  NOT NULL,
    fecha           timestamptz   NOT NULL DEFAULT now()
);

CREATE INDEX ix_acceso_usuario_fecha ON acceso_usuario (fecha DESC);

-- Usuarios de demostración (docs/seguridad.md). Cambiar las contraseñas antes
-- de usar el sistema en el local.
--   encargado / Encargado2026!   (Encargado general)
--   vendedor1 / Vendedor2026!    (Vendedor)
--   vendedor2 / Vendedor2026!    (Vendedor)
INSERT INTO usuario (nombre_usuario, nombre_completo, rol, hash_clave) VALUES
    ('encargado', 'Encargado General', 'ENCARGADO',
     'pbkdf2-sha256$100000$0TRZJn3Ul+iMWgcGr6XQoA==$5KDIMhegEwPmiYtCA5OToHwTAYET1xsetgpidMyIqsA='),
    ('vendedor1', 'Vendedor de mostrador 1', 'VENDEDOR',
     'pbkdf2-sha256$100000$N/BPELQmJ38jeaPZLqmtfw==$iCBQsdTRm8ezfk+OobwN30Y4idywuFlXU/Y5/ZrREKM='),
    ('vendedor2', 'Vendedor de mostrador 2', 'VENDEDOR',
     'pbkdf2-sha256$100000$w7f0RGPTQ0REjkAx2Q+8Tw==$f7TJSHPNVpTAxq/h8szLPhJnbRyIvVAA+1RXIq3+aNE=');

-- Desde ahora comprobante.usuario guarda el nombre de usuario de quien emitió
-- (antes siempre MAESTRO). Los comprobantes anteriores conservan MAESTRO.
