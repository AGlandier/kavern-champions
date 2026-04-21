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
        round=row["round"],
        finished=bool(row["finished"]),
        content=json.loads(row["content"]),
    )


def create_battle(battleroom_id: int, round: int, content: dict[str, Any] | None = None, finished: bool = False, db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Crée une nouvelle battle rattachée à une battleroom existante.

    Args:
        battleroom_id: Id de la battleroom parente (clé secondaire).
        round:         Numéro du round auquel appartient cette battle.
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
        "INSERT INTO battle (battleroom, round, finished, content) VALUES (?, ?, ?, ?)",
        (battleroom_id, round, int(finished), json.dumps(content)),
    )
    db.commit()

    return Battle(
        id=cursor.lastrowid,
        battleroom_id=battleroom_id,
        round=round,
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
        "SELECT id, battleroom, round, finished, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battle introuvable (id={battle_id}).")
    return _row_to_battle(row)


def get_battles_by_room(
    battleroom_id: int,
    round: int = -1,
    limit: int | None = None,
    offset: int = 0,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> list[Battle]:
    """
    Retourne les battles d'une battleroom.

    Args:
        round: Si != -1, filtre par numéro de round.
    """
    db: sqlite3.Connection = db_provider()
    params: list = [battleroom_id]
    where = "WHERE battleroom = ?"
    if round != -1:
        where += " AND round = ?"
        params.append(round)
    sql = f"SELECT id, battleroom, round, finished, content FROM battle {where} ORDER BY id ASC"
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [_row_to_battle(r) for r in rows]


def count_battles_by_room(
    battleroom_id: int,
    round: int = -1,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> int:
    """Retourne le nombre de battles d'une battleroom."""
    db: sqlite3.Connection = db_provider()
    if round == -1:
        return db.execute(
            "SELECT COUNT(*) FROM battle WHERE battleroom = ?", (battleroom_id,)
        ).fetchone()[0]
    return db.execute(
        "SELECT COUNT(*) FROM battle WHERE battleroom = ? AND round = ?", (battleroom_id, round)
    ).fetchone()[0]


def get_all_battles(
    limit: int | None = None,
    offset: int = 0,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> list[Battle]:
    """Retourne toutes les battles."""
    db: sqlite3.Connection = db_provider()
    sql = "SELECT id, battleroom, round, finished, content FROM battle ORDER BY id ASC"
    params: list = []
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [_row_to_battle(r) for r in rows]


def count_all_battles(db_provider: Callable[[], sqlite3.Connection] = get_db) -> int:
    """Retourne le nombre total de battles."""
    return get_db().execute("SELECT COUNT(*) FROM battle").fetchone()[0]


def get_battles_by_user(
    username: str,
    limit: int | None = None,
    offset: int = 0,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> list[Battle]:
    """Retourne les battles dont le contenu mentionne l'utilisateur."""
    db: sqlite3.Connection = db_provider()
    params: list = [f"%{username}%"]
    sql = (
        "SELECT id, battleroom, round, finished, content FROM battle "
        "WHERE content LIKE ? ORDER BY id ASC"
    )
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [_row_to_battle(r) for r in rows]


def count_battles_by_user(username: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> int:
    """Retourne le nombre de battles d'un utilisateur."""
    return get_db().execute(
        "SELECT COUNT(*) FROM battle WHERE content LIKE ?", (f"%{username}%",)
    ).fetchone()[0]


def set_champions_room_id(battle_id: int, champions_room_id: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Renseigne le champions_room_id d'une battle.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT id, battleroom, round, finished, content FROM battle WHERE id = ?", (battle_id,)
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
    return _row_to_battle(db.execute(
        "SELECT id, battleroom, round, finished, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone())


def get_active_battle_for_player(battleroom_id: int, username: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> "Battle | None":
    """
    Retourne la battle non-terminée du joueur dans la battleroom, ou None s'il n'en a pas.

    Un joueur ne peut avoir qu'une seule battle active à la fois dans une room.
    """
    db: sqlite3.Connection = db_provider()
    rows = db.execute(
        "SELECT id, battleroom, round, finished, content FROM battle"
        " WHERE battleroom = ? AND finished = 0 AND content LIKE ?",
        (battleroom_id, f"%{username}%"),
    ).fetchall()
    for row in rows:
        try:
            content = json.loads(row["content"])
        except json.JSONDecodeError:
            content = {}
        if content.get("player1") == username or content.get("player2") == username:
            return _row_to_battle(row)
    return None


def get_active_battle_for_user(username: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> "Battle | None":
    """
    Retourne la battle active (non-terminée) du joueur toutes rooms confondues, ou None.

    Un joueur ne peut appartenir qu'à une seule battle active à la fois.
    """
    db: sqlite3.Connection = db_provider()
    rows = db.execute(
        "SELECT id, battleroom, round, finished, content FROM battle"
        " WHERE finished = 0 AND content LIKE ?",
        (f"%{username}%",),
    ).fetchall()
    for row in rows:
        try:
            content = json.loads(row["content"])
        except json.JSONDecodeError:
            content = {}
        if content.get("player1") == username or content.get("player2") == username:
            return _row_to_battle(row)
    return None


def has_unfinished_battles(battleroom_id: int, round: int, db_provider: Callable[[], sqlite3.Connection] = get_db) -> bool:
    """Retourne True s'il reste des battles non terminées pour le round donné."""
    db: sqlite3.Connection = db_provider()
    count = db.execute(
        "SELECT COUNT(*) FROM battle WHERE battleroom = ? AND round = ? AND finished = 0",
        (battleroom_id, round),
    ).fetchone()[0]
    return count > 0


def end_battle(battle_id: int, result: dict[str, Any], db_provider: Callable[[], sqlite3.Connection] = get_db) -> Battle:
    """
    Clôture une battle en fusionnant le résultat dans son contenu JSON.

    Raises:
        NotFoundError: Si la battle n'existe pas.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT id, battleroom, round, finished, content FROM battle WHERE id = ?", (battle_id,)
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
    return Battle(id=battle_id, battleroom_id=row["battleroom"], round=row["round"], finished=True, content=existing)
