-- ====== CONSULTAS ALINEADAS AL DIAGRAMA (serial/int) ======

-- 1) Listar miembros con detalle de ubicación y congregación
SELECT * FROM vw_miembros_detalle
ORDER BY apellidos, nombres;

-- 2) Miembros por ciudad (filtro parcial)
-- :ciudad
SELECT m.id_miembro, m.nombres, m.apellidos, c.nombre_ciudad
FROM miembros m
JOIN barrios b ON b.id_barrio = m.id_barrio
JOIN ciudades c ON c.id_ciudad = b.id_ciudad
WHERE c.nombre_ciudad ILIKE %(ciudad)s || '%%'
ORDER BY m.apellidos, m.nombres;

-- 3) Miembros por congregación
-- :id_congregacion
SELECT id_miembro, nombres, apellidos
FROM miembros
WHERE id_congregacion = %(id_congregacion)s
ORDER BY apellidos, nombres;

-- 4) Estadística por congregación (vista)
SELECT * FROM vw_estadistica_congregacion;

-- 5) Crear miembro (campos básicos)
INSERT INTO miembros (nombres, apellidos, fecha_nacimiento, direccion, telefono, correo, fecha_bautismo,
                      id_congregacion, id_pastor, id_barrio, estado_civil)
VALUES (%(nombres)s, %(apellidos)s, %(fecha_nacimiento)s, %(direccion)s, %(telefono)s, %(correo)s, %(fecha_bautismo)s,
        %(id_congregacion)s, %(id_pastor)s, %(id_barrio)s, %(estado_civil)s)
RETURNING id_miembro;

-- 6) Editar contacto de miembro
UPDATE miembros
SET telefono = COALESCE(%(telefono)s, telefono),
    correo   = COALESCE(%(correo)s, correo),
    direccion= COALESCE(%(direccion)s, direccion)
WHERE id_miembro = %(id_miembro)s
RETURNING id_miembro, telefono, correo, direccion;
