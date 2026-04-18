"""
battleroom_repository.py — Opérations CRUD sur la table `battlerooms`.
"""

import sqlite3
from database.db import get_db
from db_connector.models import Battleroom
from db_connector.exceptions import NotFoundError


def create_battleroom(name: str) -> Battleroom:
    """
    Insère une nouvelle battleroom en base.

    Args:
        name: Nom de la battleroom (non vide).

    Returns:
        Battleroom créée avec son id généré et round initialisé à 0.

    Raises:
        ValueError: Si le nom est vide.
    """
    name = name.strip()
    if not name:
        raise ValueError("Le nom de la battleroom ne peut pas être vide.")

    db: sqlite3.Connection = get_db()
    cursor = db.execute(
        "INSERT INTO battlerooms (name) VALUES (?)",
        (name,),
    )
    db.commit()

    row = db.execute(
        "SELECT id, name, date, round FROM battlerooms WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()

    return Battleroom(
        id=row["id"],
        name=row["name"],
        date=row["date"],
        round=row["round"],
    )


def get_battleroom_by_id(battleroom_id: int) -> Battleroom:
    """
    Récupère une battleroom par son identifiant.

    Args:
        battleroom_id: Identifiant entier de la battleroom.

    Returns:
        Battleroom correspondante.

    Raises:
        NotFoundError: Si aucune battleroom ne correspond à cet id.
    """
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT id, name, date, round FROM battlerooms WHERE id = ?",
        (battleroom_id,),
    ).fetchone()

    if row is None:
        raise NotFoundError(f"Battleroom introuvable (id={battleroom_id}).")

    return Battleroom(
        id=row["id"],
        name=row["name"],
        date=row["date"],
        round=row["round"],
    )


def next_battleroom_round(battleroom_id: int) -> Battleroom:
    """
    Incrémente le round de la battleroom et retourne l'objet mis à jour.

    Raises:
        NotFoundError: Si la battleroom n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT round FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battleroom introuvable (id={battleroom_id}).")
    db.execute(
        "UPDATE battlerooms SET round = ? WHERE id = ?",
        (row["round"] + 1, battleroom_id),
    )
    db.commit()
    return get_battleroom_by_id(battleroom_id)


def enter_battleroom(battleroom_id: int, username: str) -> None:
    """
    Fait entrer un utilisateur dans une battleroom.
    Crée l'utilisateur en base s'il n'existe pas encore.

    Raises:
        NotFoundError: Si la battleroom n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    room = db.execute(
        "SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if room is None:
        raise NotFoundError(f"Battleroom introuvable (id={battleroom_id}).")
    db.execute("INSERT OR IGNORE INTO user (name) VALUES (?)", (username,))
    db.execute(
        "INSERT OR IGNORE INTO battleroom_players (battleroom_id, username) VALUES (?, ?)",
        (battleroom_id, username),
    )
    db.commit()


def get_room_players(battleroom_id: int) -> list[str]:
    """
    Retourne la liste des noms de joueurs inscrits dans la battleroom.

    Raises:
        NotFoundError: Si la battleroom n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    if db.execute("SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)).fetchone() is None:
        raise NotFoundError(f"Battleroom introuvable (id={battleroom_id}).")
    rows = db.execute(
        "SELECT username FROM battleroom_players WHERE battleroom_id = ?", (battleroom_id,)
    ).fetchall()
    return [r["username"] for r in rows]


def delete_battleroom(battleroom_id: int) -> None:
    """
    Supprime une battleroom (et ses battles en cascade).

    Raises:
        NotFoundError: Si la battleroom n'existe pas.
    """
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Battleroom introuvable (id={battleroom_id}).")
    db.execute("DELETE FROM battlerooms WHERE id = ?", (battleroom_id,))
    db.commit()
