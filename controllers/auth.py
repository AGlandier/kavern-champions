from functools import wraps
from flask import g, request, jsonify, current_app
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
