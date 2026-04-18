"""
battle_repository.py — Opérations CRUD sur la table `battle`.
"""

import json
import sqlite3
from typing import Any
from database.db import get_db
from db_connector.models import Battle
from db_connector.exceptions import NotFoundError


def create_battle(battleroom_id: int, content: dict[str, Any] | None = None) -> Battle:
    """
    Crée une nouvelle battle rattachée à une battleroom existante.

    Args:
        battleroom_id: Id de la battleroom parente (clé secondaire).
        content:       Données initiales de la battle (dict sérialisé en JSON).
                       Si None, un dict vide est utilisé.

    Returns:
        Battle créée avec son id généré.

    Raises:
        NotFoundError: Si la battleroom parente n'existe pas.
        ValueError:    Si battleroom_id n'est pas un entier positif.
    """
    if not isinstance(battleroom_id, int) or battleroom_id <= 0:
        raise ValueError("battleroom_id doit être un entier positif.")

    content = content or {}
    db: sqlite3.Connection = get_db()

    # Vérifie l'existence de la battleroom parente avant insertion
    room = db.execute(
        "SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if room is None:
        raise NotFoundError(
            f"Impossible de créer la battle : battleroom {battleroom_id} introuvable."
        )

    cursor = db.execute(
        "INSERT INTO battle (battleroom, content) VALUES (?, ?)",
        (battleroom_id, json.dumps(content)),
    )
    db.commit()

    return Battle(
        id=cursor.lastrowid,
        battleroom_id=battleroom_id,
        content=content,
    )
