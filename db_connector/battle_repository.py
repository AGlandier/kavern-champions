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


def get_battles_by_room(battleroom_id: int) -> list[Battle]:
    """Retourne toutes les battles d'une battleroom."""
    db: sqlite3.Connection = get_db()
    rows = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE battleroom = ?", (battleroom_id,)
    ).fetchall()
    return [
        Battle(id=r["id"], battleroom_id=r["battleroom"], content=json.loads(r["content"]))
        for r in rows
    ]


def get_all_battles() -> list[Battle]:
    """Retourne toutes les battles."""
    db: sqlite3.Connection = get_db()
    rows = db.execute("SELECT id, battleroom, content FROM battle").fetchall()
    return [
        Battle(id=r["id"], battleroom_id=r["battleroom"], content=json.loads(r["content"]))
        for r in rows
    ]


def get_battles_by_user(username: str) -> list[Battle]:
    """
    Retourne les battles dont le contenu mentionne l'utilisateur.

    Raises:
        NotFoundError: Si l'utilisateur n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    if db.execute("SELECT name FROM user WHERE name = ?", (username,)).fetchone() is None:
        raise NotFoundError(f"Utilisateur '{username}' introuvable.")
    rows = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE content LIKE ?",
        (f"%{username}%",),
    ).fetchall()
    return [
        Battle(id=r["id"], battleroom_id=r["battleroom"], content=json.loads(r["content"]))
        for r in rows
    ]


def set_champions_room_id(battle_id: int, champions_room_id: int, username: str) -> Battle:
    """
    Renseigne le champions_room_id d'une battle.

    Seul un des deux participants (player1 ou player2) peut effectuer cette action.

    Raises:
        NotFoundError:  Si la battle n'existe pas.
        PermissionError: Si l'utilisateur n'est pas participant de la battle.
    """
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")

    try:
        content = json.loads(row["content"])
    except json.JSONDecodeError:
        content = {}

    if username not in (content.get("player1"), content.get("player2")):
        raise PermissionError(f"'{username}' n'est pas participant de cette battle.")

    content["champions_room_id"] = champions_room_id
    db.execute(
        "UPDATE battle SET content = ? WHERE id = ?",
        (json.dumps(content), battle_id),
    )
    db.commit()
    return Battle(id=battle_id, battleroom_id=row["battleroom"], content=content)


def end_battle(battle_id: int, result: dict[str, Any]) -> Battle:
    """
    Clôture une battle en fusionnant le résultat dans son contenu JSON.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")
    try:
        existing = json.loads(row["content"])
    except json.JSONDecodeError:
        existing = {}
    existing.update({"status": "ended", "result": result})
    db.execute(
        "UPDATE battle SET content = ? WHERE id = ?",
        (json.dumps(existing), battle_id),
    )
    db.commit()
    return Battle(id=battle_id, battleroom_id=row["battleroom"], content=existing)
