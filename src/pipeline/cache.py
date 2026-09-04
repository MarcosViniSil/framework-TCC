from dataclasses import asdict
import json
import sqlite3
from pathlib import Path

from domain.csv_model import CSVModel


CACHE_FILE = Path("cache/cache.db")


def _get_connection() -> sqlite3.Connection:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(CACHE_FILE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    return connection


def _key_to_string(key: tuple) -> str:
    return str(key)


def key_exists_on_cache(key: tuple) -> bool:
    key_string = _key_to_string(key)

    with _get_connection() as connection:
        result = connection.execute(
            """
            SELECT 1
            FROM cache
            WHERE key = ?
            LIMIT 1
            """,
            (key_string,)
        ).fetchone()

    return result is not None


def append_to_cache(key: tuple, data: CSVModel) -> bool:
    key_string = _key_to_string(key)

    value = json.dumps(
    asdict(data),
    ensure_ascii=False,
    default=str
    )

    with _get_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO cache (key, value)
            VALUES (?, ?)
            """,
            (key_string, value)
        )

    return True


def get_value_cached(key: tuple) -> CSVModel:
    key_string = _key_to_string(key)

    with _get_connection() as connection:
        result = connection.execute(
            """
            SELECT value
            FROM cache
            WHERE key = ?
            """,
            (key_string,)
        ).fetchone()

    if result is None:
        raise KeyError(f"Key {key} não encontrada no cache")

    value = json.loads(result[0])

    return CSVModel(**value)
