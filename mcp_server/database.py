"""Acceso de solo lectura a la base de datos PostgreSQL del proyecto."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator, Sequence

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_SCHEMA = os.getenv("DB_SCHEMA", "geren2") or "geren2"


class DatabaseError(RuntimeError):
    """Error controlado para no exponer detalles sensibles al agente."""


def _database_config() -> dict[str, Any]:
    """Obtiene y valida la configuración necesaria para PostgreSQL."""
    required = {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise DatabaseError(
            "Faltan variables de configuración de la base de datos en el archivo .env."
        )

    try:
        port = int(os.getenv("DB_PORT", "5432"))
    except ValueError as exc:
        raise DatabaseError("DB_PORT debe ser un número entero.") from exc

    try:
        connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    except ValueError as exc:
        raise DatabaseError("DB_CONNECT_TIMEOUT debe ser un número entero.") from exc

    return {
        **required,
        "port": port,
        "sslmode": os.getenv("DB_SSLMODE") or "prefer",
        "connect_timeout": connect_timeout,
    }


def get_connection() -> psycopg2.extensions.connection:
    """Abre una conexión PostgreSQL usando las variables del archivo .env."""
    try:
        return psycopg2.connect(**_database_config())
    except DatabaseError:
        raise
    except psycopg2.Error as exc:
        LOGGER.error("No se pudo conectar a PostgreSQL.", exc_info=True)
        raise DatabaseError("No fue posible conectar con la base de datos.") from exc


@contextmanager
def connection() -> Iterator[psycopg2.extensions.connection]:
    """Entrega una conexión y garantiza su cierre."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def qualified_table(table_name: str) -> sql.Composed:
    """Construye un identificador seguro para una tabla del esquema del proyecto."""
    return sql.SQL("{}.{}").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table_name),
    )


def _json_value(value: Any) -> Any:
    """Convierte tipos propios de PostgreSQL a valores serializables como JSON."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def fetch_all(
    query: sql.Composed | sql.SQL | str,
    params: Sequence[Any] | None = None,
) -> list[dict[str, Any]]:
    """Ejecuta una consulta de lectura y devuelve una lista de diccionarios."""
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params if params is not None else ())
                return [_json_value(dict(row)) for row in cursor.fetchall()]
    except DatabaseError:
        raise
    except psycopg2.Error as exc:
        LOGGER.error("Error ejecutando una consulta de análisis.", exc_info=True)
        raise DatabaseError("No fue posible consultar la base de datos.") from exc


def fetch_one(
    query: sql.Composed | sql.SQL | str,
    params: Sequence[Any] | None = None,
) -> dict[str, Any] | None:
    """Ejecuta una consulta de lectura y devuelve una fila o None."""
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params if params is not None else ())
                row = cursor.fetchone()
                return _json_value(dict(row)) if row is not None else None
    except DatabaseError:
        raise
    except psycopg2.Error as exc:
        LOGGER.error("Error ejecutando una consulta de análisis.", exc_info=True)
        raise DatabaseError("No fue posible consultar la base de datos.") from exc

