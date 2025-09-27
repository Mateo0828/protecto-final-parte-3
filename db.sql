-- ====== Esquema alineado al diagrama provisto (IDs serial/integer) ======

-- Crear rol y BD manualmente si lo prefieres desde pgAdmin.
-- Luego conéctate a la BD y ejecuta este script.

-- Limpieza opcional para rehacer (ejecuta en orden inverso si hay dependencias):
-- DROP TABLE IF EXISTS miembros CASCADE;
-- DROP TABLE IF EXISTS pastores CASCADE;
-- DROP TABLE IF EXISTS congregaciones CASCADE;
-- DROP TABLE IF EXISTS barrios CASCADE;
-- DROP TABLE IF EXISTS ciudades CASCADE;
-- DROP TABLE IF EXISTS departamentos CASCADE;
-- DROP TABLE IF EXISTS paises CASCADE;

CREATE TABLE IF NOT EXISTS paises (
    id_pais SERIAL PRIMARY KEY,
    nombre_pais VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS departamentos (
    id_departamento SERIAL PRIMARY KEY,
    nombre_departamento VARCHAR(50) NOT NULL,
    id_pais INTEGER NOT NULL REFERENCES paises(id_pais) ON DELETE RESTRICT,
    UNIQUE (id_pais, nombre_departamento)
);

CREATE TABLE IF NOT EXISTS ciudades (
    id_ciudad SERIAL PRIMARY KEY,
    nombre_ciudad VARCHAR(50) NOT NULL,
    id_departamento INTEGER NOT NULL REFERENCES departamentos(id_departamento) ON DELETE RESTRICT,
    UNIQUE (id_departamento, nombre_ciudad)
);

CREATE TABLE IF NOT EXISTS barrios (
    id_barrio SERIAL PRIMARY KEY,
    nombre_barrio VARCHAR(50) NOT NULL,
    id_ciudad INTEGER NOT NULL REFERENCES ciudades(id_ciudad) ON DELETE RESTRICT,
    UNIQUE (id_ciudad, nombre_barrio)
);

CREATE TABLE IF NOT EXISTS congregaciones (
    id_congregacion SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(100),
    telefono VARCHAR(20),
    id_ciudad INTEGER NOT NULL REFERENCES ciudades(id_ciudad) ON DELETE RESTRICT,
    UNIQUE (nombre, id_ciudad)
);

CREATE TABLE IF NOT EXISTS pastores (
    id_pastor SERIAL PRIMARY KEY,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    id_congregacion INTEGER REFERENCES congregaciones(id_congregacion) ON DELETE SET NULL
);

-- Nota: el diagrama no muestra tipo/numero de documento; puedes añadirlos si el profe los pide.
CREATE TABLE IF NOT EXISTS miembros (
    id_miembro SERIAL PRIMARY KEY,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE,
    direccion VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    fecha_bautismo DATE,
    id_congregacion INTEGER NOT NULL REFERENCES congregaciones(id_congregacion) ON DELETE RESTRICT,
    id_pastor INTEGER REFERENCES pastores(id_pastor) ON DELETE SET NULL,
    id_barrio INTEGER REFERENCES barrios(id_barrio) ON DELETE SET NULL,
    estado_civil VARCHAR(30),
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_miembro_congregacion ON miembros(id_congregacion);
CREATE INDEX IF NOT EXISTS idx_miembro_barrio ON miembros(id_barrio);
CREATE INDEX IF NOT EXISTS idx_congregacion_ciudad ON congregaciones(id_ciudad);

-- ====== Vistas para consultas ======
CREATE OR REPLACE VIEW vw_miembros_detalle AS
SELECT  m.id_miembro, m.nombres, m.apellidos, m.estado_civil, m.fecha_bautismo,
        b.nombre_barrio, c.nombre_ciudad, d.nombre_departamento, p.nombre_pais,
        cg.nombre AS congregacion, cg.telefono AS tel_congregacion
FROM miembros m
LEFT JOIN barrios b ON b.id_barrio = m.id_barrio
LEFT JOIN ciudades c ON c.id_ciudad = b.id_ciudad
LEFT JOIN departamentos d ON d.id_departamento = c.id_departamento
LEFT JOIN paises p ON p.id_pais = d.id_pais
JOIN congregaciones cg ON cg.id_congregacion = m.id_congregacion;

CREATE OR REPLACE VIEW vw_estadistica_congregacion AS
SELECT
    cg.id_congregacion,
    cg.nombre AS congregacion,
    COUNT(*) AS total_miembros,
    COUNT(*) FILTER (WHERE estado_civil ILIKE 'Soltero%') AS solteros,
    COUNT(*) FILTER (WHERE estado_civil ILIKE 'Casado%') AS casados
FROM miembros m
JOIN congregaciones cg ON cg.id_congregacion = m.id_congregacion
GROUP BY cg.id_congregacion, cg.nombre
ORDER BY cg.nombre;

-- ====== Datos de ejemplo mínimos ======
INSERT INTO paises (nombre_pais) VALUES ('Colombia')
ON CONFLICT (nombre_pais) DO NOTHING;

WITH pa AS (SELECT id_pais FROM paises WHERE nombre_pais='Colombia')
INSERT INTO departamentos (nombre_departamento, id_pais)
SELECT x.nombre, pa.id_pais
FROM pa, (VALUES ('Cundinamarca')) AS x(nombre)
ON CONFLICT DO NOTHING;

WITH de AS (SELECT id_departamento FROM departamentos WHERE nombre_departamento='Cundinamarca')
INSERT INTO ciudades (nombre_ciudad, id_departamento)
SELECT x.nombre, de.id_departamento
FROM de, (VALUES ('Mosquera'), ('Bogotá')) AS x(nombre)
ON CONFLICT DO NOTHING;

WITH ci AS (SELECT id_ciudad FROM ciudades WHERE nombre_ciudad='Mosquera')
INSERT INTO barrios (nombre_barrio, id_ciudad)
SELECT x.nombre, ci.id_ciudad
FROM ci, (VALUES ('Centro'), ('El Porvenir')) AS x(nombre)
ON CONFLICT DO NOTHING;

WITH ci AS (SELECT id_ciudad FROM ciudades WHERE nombre_ciudad='Mosquera')
INSERT INTO congregaciones (nombre, direccion, telefono, id_ciudad)
SELECT 'PUC - Sede Caunces', 'Cra 1 # 2-34', '6011234567', ci.id_ciudad
FROM ci
ON CONFLICT DO NOTHING;

WITH cg AS (SELECT id_congregacion FROM congregaciones WHERE nombre='PUC - Sede Caunces'),
     b  AS (SELECT id_barrio FROM barrios WHERE nombre_barrio='Centro' LIMIT 1)
INSERT INTO pastores (nombres, apellidos, telefono, correo, id_congregacion)
SELECT 'Juan', 'Pérez', '3001234567', 'juan.perez@example.org', cg.id_congregacion
FROM cg
ON CONFLICT DO NOTHING;

WITH cg AS (SELECT id_congregacion FROM congregaciones WHERE nombre='PUC - Sede Caunces'),
     pa AS (SELECT id_pastor FROM pastores ORDER BY id_pastor LIMIT 1),
     b  AS (SELECT id_barrio FROM barrios WHERE nombre_barrio='Centro' LIMIT 1)
INSERT INTO miembros (nombres, apellidos, fecha_nacimiento, direccion, telefono, correo, fecha_bautismo,
                      id_congregacion, id_pastor, id_barrio, estado_civil)
SELECT 'María', 'Gómez', '1990-05-12', 'Calle 1 #2-34', '3109998877', 'maria.gomez@example.org', '2010-08-20',
       cg.id_congregacion, pa.id_pastor, b.id_barrio, 'Soltero'
FROM cg, pa, b
ON CONFLICT DO NOTHING;
