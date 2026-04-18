"""
battle_repository.py — Opérations CRUD sur la table `battle`.
"""

import json
import sqlite3
from collections.abc import Callable
from typing import Any
from database.db import get_db
from db_connector.models import Battle
from db_connector.exceptions import NotFoundError


def _row_to_battle(row) -> Battle:
    return Battle(
        id=row["id"],
        battleroom_id=row["battleroom"],
        finished=bool(row["finished"]),
        content=json.loads(row["content"]),
    )


def create_battle(battleroom_id: int, content: dict[str, Any] | None = None, finished: bool = False, db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Crée une nouvelle battle rattachée à une battleroom existante.

    Args:
        battleroom_id: Id de la battleroom parente (clé secondaire).
        content:       Données initiales de la battle (dict sérialisé en JSON).
        finished:      True pour les byes, clôturés dès la création.

    Raises:
        ValueError: Si battleroom_id n'est pas un entier positif.
    """
    if not isinstance(battleroom_id, int) or battleroom_id <= 0:
        raise ValueError("battleroom_id doit être un entier positif.")

    content = content or {}
    db: sqlite3.Connection = db_provider()
    cursor = db.execute(
        "INSERT INTO battle (battleroom, finished, content) VALUES (?, ?, ?)",
        (battleroom_id, int(finished), json.dumps(content)),
    )
    db.commit()

    return Battle(
        id=cursor.lastrowid,
        battleroom_id=battleroom_id,
        finished=finished,
        content=content,
    )


def get_battle_by_id(battle_id: int, db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Retourne une battle par son identifiant.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT id, battleroom, finished, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")
    return _row_to_battle(row)


def get_battles_by_room(battleroom_id: int, db_provider: Callable[[], sqlite3.Connection] = get_db) -> list[Battle]:
    """Retourne toutes les battles d'une battleroom."""
    db: sqlite3.Connection = db_provider()
    rows = db.execute(
        "SELECT id, battleroom, finished, content FROM battle WHERE battleroom = ?", (battleroom_id,)
    ).fetchall()
    return [_row_to_battle(r) for r in rows]


def get_all_battles(db_provider: Callable[[], sqlite3.Connection] = get_db) -> list[Battle]:
    """Retourne toutes les battles."""
    db: sqlite3.Connection = db_provider()
    rows = db.execute("SELECT id, battleroom, finished, content FROM battle").fetchall()
    return [_row_to_battle(r) for r in rows]


def get_battles_by_user(username: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> list[Battle]:
    """Retourne les battles dont le contenu mentionne l'utilisateur."""
    db: sqlite3.Connection = db_provider()
    rows = db.execute(
        "SELECT id, battleroom, finished, content FROM battle WHERE content LIKE ?",
        (f"%{username}%",),
    ).fetchall()
    return [_row_to_battle(r) for r in rows]


def set_champions_room_id(battle_id: int, champions_room_id: int, db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Renseigne le champions_room_id d'une battle.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT id, battleroom, finished, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")

    try:
        content = json.loads(row["content"])
    except json.JSONDecodeError:
        content = {}

    content["champions_room_id"] = champions_room_id
    db.execute(
        "UPDATE battle SET content = ? WHERE id = ?",
        (json.dumps(content), battle_id),
    )
    db.commit()
    return Battle(id=battle_id, battleroom_id=row["battleroom"], finished=bool(row["finished"]), content=content)


def end_battle(battle_id: int, result: dict[str, Any], db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Clôture une battle en fusionnant le résultat dans son contenu JSON.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")
    try:
        existing = json.loads(row["content"])
    except json.JSONDecodeError:
        existing = {}
    existing["result"] = result
    db.execute(
        "UPDATE battle SET finished = 1, content = ? WHERE id = ?",
        (json.dumps(existing), battle_id),
    )
    db.commit()
    return Battle(id=battle_id, battleroom_id=row["battleroom"], finished=True, content=existing)
