"""
user_controller — Blueprint Flask
Préfixe : /user
"""

from flask import Blueprint, jsonify, request, g
from db_connector import (
    get_user,
    get_battleroom_teamlist,
    upsert_battleroom_teamlist,
    user_has_password,
    get_active_battle_for_user,
    NotFoundError,
)
from db_connector.battleroom_repository import get_battleroom_for_user
from controllers.decorators import require_user_token

user_bp = Blueprint("user", __name__)


# ------------------------------------------------------------------
# GET /user/secured
# Indique si un utilisateur a un mot de passe défini
# ------------------------------------------------------------------
@user_bp.route("/secured", methods=["GET"])
def is_secured():
    username = request.args.get("name", "").strip().lower()
    if not username:
        return jsonify({"error": "Le paramètre de requête 'name' est requis"}), 400

    try:
        get_user(username)
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"name": username, "secured": user_has_password(username)}), 200


# ------------------------------------------------------------------
# GET /user/stats
# Retourne les statistiques d'un utilisateur
# Accepte un paramètre optionnel battleroom_id pour inclure la teamlist
# ------------------------------------------------------------------
@user_bp.route("/stats", methods=["GET"])
def get_stats():
    username = request.args.get("name", "").strip().lower()
    if not username:
        return jsonify({"error": "Le paramètre de requête 'name' est requis"}), 400

    raw_room = request.args.get("battleroom_id")
    battleroom_id = None
    if raw_room is not None:
        try:
            battleroom_id = int(raw_room)
        except ValueError:
            return jsonify({"error": "Le paramètre 'battleroom_id' doit être un entier"}), 400

    try:
        user = get_user(username)
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    teamlist = get_battleroom_teamlist(username, battleroom_id) if battleroom_id is not None else ""

    return jsonify({
        "name": user.name,
        "teamlist": teamlist,
        "number_battle": user.number_battle,
    }), 200


# ------------------------------------------------------------------
# GET /user/battleroom
# Retourne la battleroom courante de l'utilisateur authentifié
# ------------------------------------------------------------------
@user_bp.route("/battleroom", methods=["GET"])
@require_user_token
def get_user_battleroom():
    battleroom_id = get_battleroom_for_user(g.current_user)
    return jsonify({"battleroom_id": battleroom_id}), 200


# ------------------------------------------------------------------
# GET /user/active-battle
# Retourne la battle active d'un utilisateur (player1 ou player2)
# ------------------------------------------------------------------
@user_bp.route("/active-battle", methods=["GET"])
def get_active_battle():
    username = request.args.get("name", "").strip().lower()
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
# Met à jour la teamlist d'un utilisateur pour une battleroom
# ------------------------------------------------------------------
_TEAMLIST_ALLOWED_PREFIXES = ("https://pokepast.es/", "https://www.vrpastes.com/")


def _is_valid_teamlist_url(url: str) -> bool:
    return any(url.startswith(p) for p in _TEAMLIST_ALLOWED_PREFIXES)


@user_bp.route("/teamlist", methods=["POST"])
@require_user_token
def update_teamlist():
    data = request.get_json(silent=True) or {}
    teamlist = data.get("teamlist", "").strip()

    if not _is_valid_teamlist_url(teamlist):
        return jsonify({"error": "La teamlist doit être une URL pokepast.es ou vrpastes.com"}), 400

    battleroom_id = data.get("battleroom_id")
    if battleroom_id is None:
        return jsonify({"error": "Le champ 'battleroom_id' est requis"}), 400
    try:
        battleroom_id = int(battleroom_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Le champ 'battleroom_id' doit être un entier"}), 400

    try:
        saved = upsert_battleroom_teamlist(g.current_user, battleroom_id, teamlist)
        return jsonify({
            "name": g.current_user,
            "battleroom_id": battleroom_id,
            "teamlist": saved,
        }), 200
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404
