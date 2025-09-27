"""Configuración de la aplicación."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Parámetros de conexión a la base de datos."""

    host: str = os.getenv("PENTA_DB_HOST", "localhost")
    port: int = int(os.getenv("PENTA_DB_PORT", "5432"))
    database: str = os.getenv("PENTA_DB_NAME", "penta_db")
    user: str = os.getenv("PENTA_DB_USER", "postgres")
    password: str = os.getenv("PENTA_DB_PASSWORD", "postgres")


settings = Settings()
