"""
user_repository.py — Opérations CRUD sur la table `user` et `battleroom_teamlist`.
"""

import sqlite3
from collections.abc import Callable
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from db_connector.models import User
from db_connector.exceptions import NotFoundError, DuplicateError


def create_user(name: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> User:
    """
    Crée un nouvel utilisateur en base.

    Args:
        name: Identifiant unique de l'utilisateur (clé primaire).

    Returns:
        User créé.

    Raises:
        ValueError:     Si le nom est vide.
        DuplicateError: Si un utilisateur avec ce nom existe déjà.
    """
    name = name.strip()
    if not name:
        raise ValueError("Le nom de l'utilisateur ne peut pas être vide.")

    db: sqlite3.Connection = db_provider()

    existing = db.execute(
        "SELECT name FROM user WHERE name = ?", (name,)
    ).fetchone()
    if existing is not None:
        raise DuplicateError(f"L'utilisateur '{name}' existe déjà.")

    db.execute("INSERT INTO user (name) VALUES (?)", (name,))
    db.commit()

    return User(name=name, number_battle=0)


def get_user(name: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> User:
    """
    Récupère un utilisateur par son nom (clé primaire).

    Args:
        name: Nom de l'utilisateur.

    Returns:
        User correspondant.

    Raises:
        NotFoundError: Si aucun utilisateur ne correspond à ce nom.
    """
    name = name.strip()
    db: sqlite3.Connection = db_provider()

    row = db.execute(
        "SELECT name, number_battle FROM user WHERE name = ?",
        (name,),
    ).fetchone()

    if row is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")

    return User(
        name=row["name"],
        number_battle=row["number_battle"],
    )


def get_battleroom_teamlist(
    name: str,
    battleroom_id: int,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> str:
    """
    Retourne la teamlist d'un utilisateur pour une battleroom donnée.
    Retourne une chaîne vide si aucune entrée n'existe.
    """
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT teamlist FROM battleroom_teamlist WHERE username = ? AND battleroom_id = ?",
        (name.strip(), battleroom_id),
    ).fetchone()
    return row["teamlist"] if row else ""


def upsert_battleroom_teamlist(
    name: str,
    battleroom_id: int,
    teamlist: str,
    db_provider: Callable[[], sqlite3.Connection] = get_db,
) -> str:
    """
    Crée ou met à jour la teamlist d'un utilisateur pour une battleroom.

    Returns:
        La teamlist enregistrée.

    Raises:
        NotFoundError: Si l'utilisateur n'existe pas.
    """
    name = name.strip()
    db: sqlite3.Connection = db_provider()

    if db.execute("SELECT name FROM user WHERE name = ?", (name,)).fetchone() is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")

    db.execute(
        """
        INSERT INTO battleroom_teamlist (battleroom_id, username, teamlist)
        VALUES (?, ?, ?)
        ON CONFLICT(battleroom_id, username) DO UPDATE SET teamlist = excluded.teamlist
        """,
        (battleroom_id, name, teamlist),
    )
    db.commit()
    return teamlist


def increment_number_battle(name: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> None:
    """Incrémente le compteur de battles d'un utilisateur. Silencieux si l'utilisateur n'existe pas."""
    db: sqlite3.Connection = db_provider()
    db.execute(
        "UPDATE user SET number_battle = number_battle + 1 WHERE name = ?", (name,)
    )
    db.commit()


def user_has_password(name: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> bool:
    """Retourne True si l'utilisateur a un mot de passe défini."""
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT password_hash FROM user WHERE name = ?", (name.strip(),)
    ).fetchone()
    return row is not None and row["password_hash"] is not None


def set_user_password(name: str, password: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> None:
    """
    Hash et enregistre le mot de passe de l'utilisateur.

    Raises:
        NotFoundError: Si l'utilisateur n'existe pas.
    """
    name = name.strip()
    db: sqlite3.Connection = db_provider()
    row = db.execute("SELECT name FROM user WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")
    db.execute(
        "UPDATE user SET password_hash = ? WHERE name = ?",
        (generate_password_hash(password), name),
    )
    db.commit()


def check_user_password(name: str, password: str, db_provider: Callable[[], sqlite3.Connection] = get_db) -> bool:
    """Retourne True si le mot de passe correspond au hash stocké."""
    db: sqlite3.Connection = db_provider()
    row = db.execute(
        "SELECT password_hash FROM user WHERE name = ?", (name.strip(),)
    ).fetchone()
    if row is None or row["password_hash"] is None:
        return False
    return check_password_hash(row["password_hash"], password)
