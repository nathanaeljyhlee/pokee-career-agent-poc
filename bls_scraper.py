import sqlite3
from pathlib import Path
from contextlib import contextmanager

from config import DB_PATH

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text())


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query(sql: str, params: tuple = ()):
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def query_one(sql: str, params: tuple = ()):
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple = ()):
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid


def execute_many(sql: str, params_list: list):
    with get_connection() as conn:
        conn.executemany(sql, params_list)
