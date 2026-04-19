"""
exceptions.py — Exceptions métier du connecteur.
Permet aux controllers de distinguer les erreurs sans dépendre de sqlite3.
"""


class NotFoundError(Exception):
    """Levée quand un enregistrement est introuvable en base."""


class DuplicateError(Exception):
    """Levée quand une contrainte d'unicité est violée (ex: user déjà existant)."""
