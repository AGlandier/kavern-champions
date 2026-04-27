import sqlite3
import os
from flask import g, current_app


def get_db() -> sqlite3.Connection:
    """Retourne la connexion SQLite liée au contexte de la requête Flask."""
    if "db" not in g:
        db_path = os.path.abspath(current_app.config["DATABASE_PATH"])
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row  # accès par nom de colonne
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None) -> None:
    """Ferme la connexion en fin de requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    db = sqlite3.connect(
        os.path.abspath(current_app.config["DATABASE_PATH"]),
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    try:
        db.execute("ALTER TABLE battlerooms ADD COLUMN closed INTEGER NOT NULL DEFAULT 0")
        db.commit()
    except Exception:
        pass  # colonne déjà présente
    db.close()
    # Enregistre le teardown pour les requêtes Flask
    current_app.teardown_appcontext(close_db)
