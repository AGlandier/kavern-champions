"""
auth_controller — Blueprint Flask
Préfixe : /auth
"""

from flask import Blueprint, jsonify, request
from db_connector import (
    create_user,
    user_has_password,
    set_user_password,
    check_user_password,
    NotFoundError,
    DuplicateError,
)

from controllers.auth import make_user_token, verify_user_token

auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------
# POST /auth/register
# Crée un utilisateur avec son nom uniquement (sans mot de passe)
# ------------------------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    password = data.get("password", "")

    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400

    try:
        user = create_user(name)
        if password:
            set_user_password(name, password)
        return jsonify({"name": user.name, "secured": bool(password)}), 201
    except DuplicateError:
        return jsonify({"error": f"L'utilisateur '{name}' existe déjà"}), 409


# ------------------------------------------------------------------
# POST /auth/set-password
# Définit ou change le mot de passe d'un utilisateur
# Si un mot de passe existe déjà, current_password est obligatoire
# ------------------------------------------------------------------
@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    new_password = data.get("password", "")
    current_password = data.get("current_password", "")

    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400
    if not new_password:
        return jsonify({"error": "Le champ 'password' est requis"}), 400

    try:
        if user_has_password(name):
            if not current_password:
                return jsonify({"error": "Le champ 'current_password' est requis pour modifier le mot de passe"}), 400
            if not check_user_password(name, current_password):
                return jsonify({"error": "Mot de passe actuel incorrect"}), 401
        set_user_password(name, new_password)
        return jsonify({"message": "Mot de passe défini avec succès"}), 200
    except NotFoundError:
        return jsonify({"error": f"Utilisateur '{name}' introuvable"}), 404


# ------------------------------------------------------------------
# POST /auth/login
# Authentifie un utilisateur et retourne un token Bearer (24 h)
# ------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    password = data.get("password", "")

    if not name or not password:
        return jsonify({"error": "Les champs 'name' et 'password' sont requis"}), 400

    if not check_user_password(name, password):
        return jsonify({"error": "Identifiants invalides"}), 401

    return jsonify({"token": make_user_token(name), "name": name}), 200


# ------------------------------------------------------------------
# GET /auth/me
# Vérifie un token et retourne le nom d'utilisateur associé
# Header : Authorization: Bearer <token>
# ------------------------------------------------------------------
@auth_bp.route("/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token manquant ou format invalide"}), 401
    name = verify_user_token(auth_header[7:])
    if name is None:
        return jsonify({"error": "Token invalide ou expiré"}), 401
    return jsonify({"name": name}), 200
