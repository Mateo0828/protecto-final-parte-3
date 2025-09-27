"""Consultas de acceso a datos para la gestión de miembros."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from psycopg2 import sql

from . import database

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS country (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS department (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    country_id INTEGER NOT NULL REFERENCES country(id) ON DELETE RESTRICT,
    UNIQUE (name, country_id)
);

CREATE TABLE IF NOT EXISTS municipality (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES department(id) ON DELETE RESTRICT,
    UNIQUE (name, department_id)
);

CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    municipality_id INTEGER NOT NULL REFERENCES municipality(id) ON DELETE RESTRICT,
    UNIQUE (name, municipality_id)
);

CREATE TABLE IF NOT EXISTS document_type (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    description VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS pastor (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS member (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    birth_date DATE,
    civil_status VARCHAR(20),
    address TEXT,
    phone VARCHAR(30),
    email VARCHAR(120),
    document_number VARCHAR(30) UNIQUE NOT NULL,
    baptized_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVO',
    city_id INTEGER REFERENCES city(id) ON DELETE SET NULL,
    pastor_id INTEGER REFERENCES pastor(id) ON DELETE SET NULL,
    document_type_id INTEGER REFERENCES document_type(id) ON DELETE RESTRICT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS membership_log (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES member(id) ON DELETE CASCADE,
    action VARCHAR(40) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION trg_member_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS member_set_updated_at ON member;
CREATE TRIGGER member_set_updated_at
    BEFORE UPDATE ON member
    FOR EACH ROW
    EXECUTE FUNCTION trg_member_updated_at();
"""


def bootstrap_schema() -> None:
    """Crea las tablas necesarias en la base de datos."""

    with database.get_cursor(dict_cursor=False) as cursor:
        cursor.execute(SCHEMA_SQL)


def seed_catalogs() -> None:
    """Inserta valores base para catálogos."""

    document_types = [
        ("CC", "Cédula de ciudadanía"),
        ("TI", "Tarjeta de identidad"),
        ("CE", "Cédula de extranjería"),
    ]

    with database.get_cursor() as cursor:
        cursor.executemany(
            "INSERT INTO document_type (code, description) VALUES (%s, %s)"
            " ON CONFLICT (code) DO NOTHING",
            document_types,
        )

        # Ubicaciones de ejemplo
        cursor.execute(
            "INSERT INTO country (name) VALUES (%s)"
            " ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name"
            " RETURNING id",
            ("Colombia",),
        )
        country_id = cursor.fetchone()["id"]

        cursor.execute(
            "INSERT INTO department (name, country_id) VALUES (%s, %s)"
            " ON CONFLICT (name, country_id) DO UPDATE SET name = EXCLUDED.name"
            " RETURNING id",
            ("Cauca", country_id),
        )
        department_id = cursor.fetchone()["id"]

        cursor.execute(
            "INSERT INTO municipality (name, department_id) VALUES (%s, %s)"
            " ON CONFLICT (name, department_id) DO UPDATE SET name = EXCLUDED.name"
            " RETURNING id",
            ("Santander de Quilichao", department_id),
        )
        municipality_id = cursor.fetchone()["id"]

        cursor.execute(
            "INSERT INTO city (name, municipality_id) VALUES (%s, %s)"
            " ON CONFLICT (name, municipality_id) DO UPDATE SET name = EXCLUDED.name"
            " RETURNING id",
            ("Caunces", municipality_id),
        )
        cursor.fetchone()

        cursor.execute(
            "INSERT INTO pastor (first_name, last_name, phone, email)"
            " VALUES (%s, %s, %s, %s)"
            " ON CONFLICT DO NOTHING",
            ("Juan", "Pérez", "+57 300 123 4567", "juan.perez@ipuco.org"),
        )


def list_pastors() -> List[Dict[str, Any]]:
    with database.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, first_name, last_name, phone, email FROM pastor ORDER BY last_name"
        )
        return list(cursor.fetchall())


def list_cities() -> List[Dict[str, Any]]:
    with database.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT city.id, city.name AS city, municipality.name AS municipality,
                   department.name AS department, country.name AS country
            FROM city
            JOIN municipality ON city.municipality_id = municipality.id
            JOIN department ON municipality.department_id = department.id
            JOIN country ON department.country_id = country.id
            ORDER BY country, department, municipality, city.name
            """
        )
        return list(cursor.fetchall())


def create_member(data: Dict[str, Any]) -> int:
    """Crea un nuevo miembro y retorna su identificador."""

    columns = data.keys()
    values = [data[column] for column in columns]
    insert = sql.SQL("""
        INSERT INTO member ({fields})
        VALUES ({placeholders})
        RETURNING id
    """).format(
        fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
    )
    with database.get_cursor() as cursor:
        cursor.execute(insert, values)
        member_id = cursor.fetchone()["id"]
        cursor.execute(
            "INSERT INTO membership_log (member_id, action, notes) VALUES (%s, %s, %s)",
            (member_id, "ALTA", "Registro inicial en el sistema"),
        )
        return member_id


def get_member(member_id: int) -> Optional[Dict[str, Any]]:
    with database.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT m.*, dt.code AS document_code, dt.description AS document_type,
                   p.first_name || ' ' || p.last_name AS pastor_name,
                   c.name AS city_name
            FROM member m
            LEFT JOIN document_type dt ON m.document_type_id = dt.id
            LEFT JOIN pastor p ON m.pastor_id = p.id
            LEFT JOIN city c ON m.city_id = c.id
            WHERE m.id = %s
            """,
            (member_id,),
        )
        return cursor.fetchone()


def list_members() -> List[Dict[str, Any]]:
    with database.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT m.id, m.first_name, m.last_name, m.gender, m.status,
                   dt.code AS document_type, m.document_number, c.name AS city,
                   m.created_at
            FROM member m
            LEFT JOIN document_type dt ON m.document_type_id = dt.id
            LEFT JOIN city c ON m.city_id = c.id
            ORDER BY m.created_at DESC
            """
        )
        return list(cursor.fetchall())


def update_member(member_id: int, fields: Dict[str, Any]) -> None:
    if not fields:
        return
    assignments = [sql.SQL("{} = %s").format(sql.Identifier(field)) for field in fields]
    query = sql.SQL("""
        UPDATE member
        SET {assignments}
        WHERE id = %s
        RETURNING id
    """).format(assignments=sql.SQL(", ").join(assignments))
    values = list(fields.values()) + [member_id]
    with database.get_cursor() as cursor:
        cursor.execute(query, values)
        if cursor.fetchone() is None:
            raise ValueError(f"No existe un miembro con id {member_id}")
        cursor.execute(
            "INSERT INTO membership_log (member_id, action, notes) VALUES (%s, %s, %s)",
            (member_id, "ACTUALIZACIÓN", str(fields)),
        )


def record_transfer(member_id: int, notes: str) -> None:
    with database.get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO membership_log (member_id, action, notes) VALUES (%s, %s, %s)",
            (member_id, "TRASLADO", notes),
        )
        cursor.execute(
            "UPDATE member SET status = %s WHERE id = %s",
            ("TRASLADADO", member_id),
        )


def membership_history(member_id: int) -> List[Dict[str, Any]]:
    with database.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT action, notes, created_at
            FROM membership_log
            WHERE member_id = %s
            ORDER BY created_at
            """,
            (member_id,),
        )
        return list(cursor.fetchall())


def demographic_summary() -> Dict[str, Any]:
    with database.get_cursor() as cursor:
        cursor.execute(
            "SELECT gender, COUNT(*) AS total FROM member GROUP BY gender"
        )
        by_gender = cursor.fetchall()

        cursor.execute(
            "SELECT status, COUNT(*) AS total FROM member GROUP BY status"
        )
        by_status = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM member")
        total = cursor.fetchone()["total"]

        return {
            "total_members": total,
            "by_gender": by_gender,
            "by_status": by_status,
        }


def certificate_payload(member_id: int) -> Dict[str, Any]:
    member = get_member(member_id)
    if not member:
        raise ValueError("Miembro no encontrado")

    history = membership_history(member_id)
    return {
        "member": member,
        "history": history,
    }
