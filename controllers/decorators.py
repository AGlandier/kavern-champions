"""
decorators.py — Décorateurs de protection des routes Flask.
"""

from functools import wraps
from flask import g, request, jsonify, current_app
from services.token_service import verify_user_token


def require_admin_key(f):
    """Décorateur — vérifie la clé admin dans le header X-Admin-Key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key", "")
        if key != current_app.config["ADMIN_KEY"]:
            return jsonify({"error": "Unauthorized — invalid admin key"}), 401
        return f(*args, **kwargs)
    return decorated


def require_user_token(f):
    """Décorateur — vérifie le token Bearer dans Authorization. Expose g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou format invalide"}), 401
        name = verify_user_token(auth_header[7:])
        if name is None:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        g.current_user = name
        return f(*args, **kwargs)
    return decorated


def require_admin_or_user_token(f):
    """Décorateur — accepte la clé admin OU un token Bearer valide.

    Expose g.is_admin (bool) et g.current_user (str | None).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-Admin-Key", "") == current_app.config["ADMIN_KEY"]:
            g.is_admin = True
            g.current_user = None
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            name = verify_user_token(auth_header[7:])
            if name is not None:
                g.is_admin = False
                g.current_user = name
                return f(*args, **kwargs)

        return jsonify({"error": "Authentification requise (clé admin ou token Bearer valide)"}), 401
    return decorated
