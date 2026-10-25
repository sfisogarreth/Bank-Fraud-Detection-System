import os
import sqlite3
from contextlib import contextmanager
from config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = getattr(Config, 'DATABASE', os.path.join(BASE_DIR, 'mazi.db'))

def get_db_connection():
    """Returns a SQLite connection with dict-like row access, WAL mode, and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")  # Prevents 'database is locked' errors during concurrent scans
    return conn

@contextmanager
def db_session():
    """Context manager for safe database transactions with auto-commit and rollback."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()