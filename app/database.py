"""Utilidades para la conexión con PostgreSQL."""
from __future__ import annotations

import contextlib
from typing import Iterator

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings


@contextlib.contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    """Retorna una conexión nueva a la base de datos."""

    connection = psycopg2.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
    )
    try:
        yield connection
    finally:
        connection.close()


@contextlib.contextmanager
def get_cursor(dict_cursor: bool = True) -> Iterator[psycopg2.extensions.cursor]:
    """Genera un cursor gestionando la transacción automáticamente."""

    with get_connection() as connection:
        cursor_factory = RealDictCursor if dict_cursor else None
        with connection.cursor(cursor_factory=cursor_factory) as cursor:
            try:
                yield cursor
                connection.commit()
            except Exception:  # pragma: no cover - repropaga el error
                connection.rollback()
                raise
