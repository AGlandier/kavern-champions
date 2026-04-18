#!/usr/bin/env python3
"""
init_db.py — Script autonome pour initialiser la base de données SQLite.
Usage :
    python init_db.py
    DATABASE_PATH=./custom.db python init_db.py
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "battleapp.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def init_database(db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH) -> None:
    print(f"[init_db] Base de données : {db_path}")
    print(f"[init_db] Schéma          : {schema_path}")

    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None

    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[init_db] Tables créées avec succès ✓")


if __name__ == "__main__":
    init_database()
