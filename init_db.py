# init_db.py
from pathlib import Path
from db import DB_PATH, get_connection

SCHEMA_PATH = Path("schema.sql")

def init_db():
      if not SCHEMA_PATH.exists():
                raise FileNotFoundError(f"Schema file {SCHEMA_PATH} not found")

      with SCHEMA_PATH.open("r", encoding="utf-8") as f:
                schema_sql = f.read()

      with get_connection(DB_PATH) as conn:
                conn.executescript(schema_sql)

      print(f"Initialized database at {DB_PATH}")

if __name__ == "__main__":
      init_db()
