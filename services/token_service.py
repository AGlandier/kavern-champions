"""
token_service.py — Génération et vérification des tokens utilisateur.
"""

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

_TOKEN_MAX_AGE = 86_400  # 24 heures


def make_user_token(username: str) -> str:
    """Génère un token signé pour l'utilisateur (valable 24 h)."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(username, salt="user-auth")


def verify_user_token(token: str) -> str | None:
    """Valide le token et retourne le nom d'utilisateur, ou None si invalide/expiré."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="user-auth", max_age=_TOKEN_MAX_AGE)
    except (SignatureExpired, BadSignature):
        return None
