\
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "congregacion_db")
PGUSER = os.getenv("PGUSER", "congregacion_user")
PGPASSWORD = os.getenv("PGPASSWORD", "congregacion_pass")

DSN = f"host={PGHOST} port={PGPORT} dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD}"

def get_conn():
    return psycopg2.connect(DSN)

app = FastAPI(title="Congregación API (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/miembros/detalle")
def miembros_detalle():
    sql = "SELECT * FROM vw_miembros_detalle ORDER BY apellidos, nombres"
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        return cur.fetchall()

@app.get("/miembros/ciudad/{ciudad}")
def miembros_por_ciudad(ciudad: str):
    sql = """
    SELECT m.id_miembro, m.nombres, m.apellidos, c.nombre_ciudad
    FROM miembros m
    JOIN barrios b ON b.id_barrio = m.id_barrio
    JOIN ciudades c ON c.id_ciudad = b.id_ciudad
    WHERE c.nombre_ciudad ILIKE %(ciudad)s || '%%'
    ORDER BY m.apellidos, m.nombres
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, {"ciudad": ciudad})
        return cur.fetchall()

@app.get("/miembros/congregacion/{id_congregacion}")
def miembros_por_congregacion(id_congregacion: int):
    sql = """
    SELECT id_miembro, nombres, apellidos
    FROM miembros
    WHERE id_congregacion = %(id)s
    ORDER BY apellidos, nombres
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, {"id": id_congregacion})
        return cur.fetchall()

@app.post("/miembros")
def crear_miembro(payload: dict):
    oblig = ["nombres", "apellidos", "id_congregacion"]
    for k in oblig:
        if not payload.get(k):
            raise HTTPException(status_code=400, detail=f"Falta campo obligatorio: {k}")
    sql = """
    INSERT INTO miembros (nombres, apellidos, fecha_nacimiento, direccion, telefono, correo, fecha_bautismo,
                          id_congregacion, id_pastor, id_barrio, estado_civil)
    VALUES (%(nombres)s, %(apellidos)s, %(fecha_nacimiento)s, %(direccion)s, %(telefono)s, %(correo)s, %(fecha_bautismo)s,
            %(id_congregacion)s, %(id_pastor)s, %(id_barrio)s, %(estado_civil)s)
    RETURNING id_miembro
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, payload)
        row = cur.fetchone()
        return row

@app.patch("/miembros/{id_miembro}")
def editar_contacto(id_miembro: int, payload: dict):
    sql = """
    UPDATE miembros
    SET telefono = COALESCE(%(telefono)s, telefono),
        correo   = COALESCE(%(correo)s, correo),
        direccion= COALESCE(%(direccion)s, direccion)
    WHERE id_miembro = %(id)s
    RETURNING id_miembro, telefono, correo, direccion
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, {"id": id_miembro, **payload})
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")
        return row

@app.get("/estadistica")
def estadistica():
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM vw_estadistica_congregacion")
        return cur.fetchall()
