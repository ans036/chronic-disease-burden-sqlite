# db.py
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("chronic_disease.db")

@contextmanager
def get_connection(path: Path = DB_PATH):
      conn = sqlite3.connect(path)
      conn.row_factory = sqlite3.Row  # access columns by name
    try:
              conn.execute("PRAGMA foreign_keys = ON;")
              yield conn
              conn.commit()
finally:
          conn.close()
