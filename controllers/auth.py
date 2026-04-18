from functools import wraps
from flask import request, jsonify, current_app


def require_admin_key(f):
    """Décorateur — vérifie la clé admin dans le header X-Admin-Key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key", "")
        if key != current_app.config["ADMIN_KEY"]:
            return jsonify({"error": "Unauthorized — invalid admin key"}), 401
        return f(*args, **kwargs)
    return decorated
