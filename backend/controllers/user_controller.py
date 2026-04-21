"""
user_controller — Blueprint Flask
Préfixe : /user
"""

from flask import Blueprint, jsonify, request, g
from db_connector import get_user, update_user_teamlist, user_has_password, get_active_battle_for_user, NotFoundError, DuplicateError
from controllers.decorators import require_user_token

user_bp = Blueprint("user", __name__)


# ------------------------------------------------------------------
# GET /user/secured
# Indique si un utilisateur a un mot de passe défini
# ------------------------------------------------------------------
@user_bp.route("/secured", methods=["GET"])
def is_secured():
    username = request.args.get("name", "").strip()
    if not username:
        return jsonify({"error": "Le paramètre de requête 'name' est requis"}), 400

    try:
        get_user(username)  # vérifie l'existence
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"name": username, "secured": user_has_password(username)}), 200


# ------------------------------------------------------------------
# GET /user/stats
# Retourne les statistiques d'un utilisateur
# ------------------------------------------------------------------
@user_bp.route("/stats", methods=["GET"])
def get_stats():
    username = request.args.get("name", "").strip()
    if not username:
        return jsonify({"error": "Le paramètre de requête 'name' est requis"}), 400

    try:
        user = get_user(username)
        return jsonify({
            "name": user.name,
            "teamlist": user.teamlist,
            "number_battle": user.number_battle,
        }), 200
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404


# ------------------------------------------------------------------
# GET /user/active-battle
# Retourne la battle active d'un utilisateur (player1 ou player2)
# ------------------------------------------------------------------
@user_bp.route("/active-battle", methods=["GET"])
def get_active_battle():
    username = request.args.get("name", "").strip()
    if not username:
        return jsonify({"error": "Le paramètre de requête 'name' est requis"}), 400

    try:
        get_user(username)
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    battle = get_active_battle_for_user(username)
    if battle is None:
        return jsonify({"battle": None}), 200

    return jsonify({
        "battle": {
            "id": battle.id,
            "battleroom_id": battle.battleroom_id,
            "round": battle.round,
            "finished": battle.finished,
            "content": battle.content,
        }
    }), 200


# ------------------------------------------------------------------
# POST /user/teamlist
# Met à jour la teamlist d'un utilisateur
# ------------------------------------------------------------------
@user_bp.route("/teamlist", methods=["POST"])
@require_user_token
def update_teamlist():
    data = request.get_json(silent=True) or {}
    teamlist = data.get("teamlist", "").strip()

    try:
        user = update_user_teamlist(g.current_user, teamlist)
        return jsonify({"name": user.name, "teamlist": user.teamlist}), 200
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404
