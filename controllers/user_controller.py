"""
user_controller — Blueprint Flask
Préfixe : /user
"""

from flask import Blueprint, jsonify, request
from db_connector import get_user, update_user_teamlist, NotFoundError

user_bp = Blueprint("user", __name__)


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
# POST /user/teamlist
# Met à jour la teamlist d'un utilisateur
# ------------------------------------------------------------------
@user_bp.route("/teamlist", methods=["POST"])
def update_teamlist():
    data = request.get_json(silent=True) or {}
    username = data.get("name", "").strip()
    teamlist = data.get("teamlist", "").strip()

    if not username:
        return jsonify({"error": "Le champ 'name' est requis"}), 400

    try:
        user = update_user_teamlist(username, teamlist)
        return jsonify({"name": user.name, "teamlist": user.teamlist}), 200
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404
