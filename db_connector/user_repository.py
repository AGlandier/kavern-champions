"""
user_repository.py — Opérations CRUD sur la table `user`.
"""

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from db_connector.models import User
from db_connector.exceptions import NotFoundError, DuplicateError


def create_user(name: str, teamlist: str = "") -> User:
    """
    Crée un nouvel utilisateur en base.

    Args:
        name:     Identifiant unique de l'utilisateur (clé primaire).
        teamlist: Liste d'équipe initiale (chaîne libre, vide par défaut).

    Returns:
        User créé.

    Raises:
        ValueError:     Si le nom est vide.
        DuplicateError: Si un utilisateur avec ce nom existe déjà.
    """
    name = name.strip()
    if not name:
        raise ValueError("Le nom de l'utilisateur ne peut pas être vide.")

    db: sqlite3.Connection = get_db()

    # Vérifie l'unicité avant insertion pour lever une erreur explicite
    existing = db.execute(
        "SELECT name FROM user WHERE name = ?", (name,)
    ).fetchone()
    if existing is not None:
        raise DuplicateError(f"L'utilisateur '{name}' existe déjà.")

    db.execute(
        "INSERT INTO user (name, teamlist) VALUES (?, ?)",
        (name, teamlist),
    )
    db.commit()

    return User(name=name, teamlist=teamlist, number_battle=0)


def get_user(name: str) -> User:
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
    db: sqlite3.Connection = get_db()

    row = db.execute(
        "SELECT name, teamlist, number_battle FROM user WHERE name = ?",
        (name,),
    ).fetchone()

    if row is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")

    return User(
        name=row["name"],
        teamlist=row["teamlist"],
        number_battle=row["number_battle"],
    )


def update_user_teamlist(name: str, teamlist: str) -> User:
    """
    Met à jour la teamlist d'un utilisateur.

    Returns:
        User mis à jour.

    Raises:
        NotFoundError: Si l'utilisateur n'existe pas.
    """
    name = name.strip()
    db: sqlite3.Connection = get_db()
    row = db.execute("SELECT name FROM user WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")
    db.execute("UPDATE user SET teamlist = ? WHERE name = ?", (teamlist, name))
    db.commit()
    return get_user(name)


def user_has_password(name: str) -> bool:
    """Retourne True si l'utilisateur a un mot de passe défini."""
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT password_hash FROM user WHERE name = ?", (name.strip(),)
    ).fetchone()
    return row is not None and row["password_hash"] is not None


def set_user_password(name: str, password: str) -> None:
    """
    Hash et enregistre le mot de passe de l'utilisateur.

    Raises:
        NotFoundError: Si l'utilisateur n'existe pas.
    """
    name = name.strip()
    db: sqlite3.Connection = get_db()
    row = db.execute("SELECT name FROM user WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise NotFoundError(f"Utilisateur '{name}' introuvable.")
    db.execute(
        "UPDATE user SET password_hash = ? WHERE name = ?",
        (generate_password_hash(password), name),
    )
    db.commit()


def check_user_password(name: str, password: str) -> bool:
    """Retourne True si le mot de passe correspond au hash stocké."""
    db: sqlite3.Connection = get_db()
    row = db.execute(
        "SELECT password_hash FROM user WHERE name = ?", (name.strip(),)
    ).fetchone()
    if row is None or row["password_hash"] is None:
        return False
    return check_password_hash(row["password_hash"], password)
