"""
battleroom_controller — Blueprint Flask
Préfixe : /battleroom
"""

from flask import Blueprint, jsonify, request

import db_connector
from controllers.auth import require_admin_key, require_user_token
from db_connector.models import Battleroom
from kchampions_core import make_pairings

battleroom_bp = Blueprint("battleroom", __name__)


# ------------------------------------------------------------------
# POST /battleroom/create  (admin)
# Crée une nouvelle battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/create", methods=["POST"])
@require_admin_key
def create():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400

    battleroom: Battleroom = db_connector.create_battleroom(name)
    return jsonify(battleroom), 201


@battleroom_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id):
    try:
        battleroom: Battleroom = db_connector.get_battleroom_by_id(room_id)
        return jsonify(battleroom), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# POST /battleroom/next  (admin)
# Passe au round suivant de la battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/next", methods=["POST"])
@require_admin_key
def next_round():
    data = request.get_json(silent=True) or {}
    battleroom_id = data.get("battleroom_id")
    if battleroom_id is None:
        return jsonify({"error": "Le champ 'battleroom_id' est requis"}), 400

    try:
        # 1. Récupère les joueurs et l'historique complet (matchs + byes)
        players = db_connector.get_room_players(battleroom_id)
        past_battles = db_connector.get_battles_by_room(battleroom_id)
        past_pairings = [
            (b.content["player1"], b.content.get("player2"))
            for b in past_battles
            if "player1" in b.content
        ]

        # 2. Génère les appariements via le core (aucun I/O)
        pairings = make_pairings(players, past_pairings)

        # 3. Incrémente le round
        battleroom = db_connector.next_battleroom_round(battleroom_id)

        # 4. Persiste les combats en base (player2=None pour les byes)
        battles = [
            db_connector.create_battle(battleroom_id, {
                "player1": p.player1,
                "player2": p.player2,
                "champions_room_id": None,
            })
            for p in pairings
        ]

        return jsonify({
            "battleroom_id": battleroom.id,
            "round": battleroom.round,
            "battles": [
                {
                    "id": b.id,
                    "player1": b.content["player1"],
                    "player2": b.content.get("player2"),
                    "champions_room_id": b.content.get("champions_room_id"),
                    "bye": b.content.get("player2") is None,
                }
                for b in battles
            ],
        }), 200

    except db_connector.NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# POST /battleroom/enter  (admin)
# Fait entrer un utilisateur dans une battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/enter", methods=["POST"])
@require_admin_key
def enter():
    data = request.get_json(silent=True) or {}
    battleroom_id = data.get("battleroom_id")
    username = data.get("username", "").strip()
    if not battleroom_id or not username:
        return jsonify({"error": "Les champs 'battleroom_id' et 'username' sont requis"}), 400

    try:
        db_connector.enter_battleroom(battleroom_id, username)
        return jsonify({"message": f"{username} a rejoint la battleroom {battleroom_id}"}), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# POST /battleroom/end  (admin)
# Termine une battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/end", methods=["POST"])
@require_admin_key
def end_room():
    data = request.get_json(silent=True) or {}
    battleroom_id = data.get("battleroom_id")
    if battleroom_id is None:
        return jsonify({"error": "Le champ 'battleroom_id' est requis"}), 400

    try:
        db_connector.delete_battleroom(battleroom_id)
        return jsonify({"message": f"Battleroom {battleroom_id} terminée et supprimée"}), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# GET /battleroom/battle
# Retourne la liste de toutes les battles
# ------------------------------------------------------------------
@battleroom_bp.route("/battle", methods=["GET"])
def get_all_battles():
    battles = db_connector.get_all_battles()
    return jsonify([
        {"id": b.id, "battleroom": b.battleroom_id, "content": b.content}
        for b in battles
    ]), 200


# ------------------------------------------------------------------
# GET /battleroom/battle/<user>
# Retourne les battles associées à un utilisateur
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/<string:user>", methods=["GET"])
def get_battle_by_user(user: str):
    try:
        battles = db_connector.get_battles_by_user(user)
        return jsonify({
            "user": user,
            "battles": [
                {"id": b.id, "battleroom": b.battleroom_id, "content": b.content}
                for b in battles
            ],
        }), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404


# ------------------------------------------------------------------
# POST /battleroom/battle/set-room
# Renseigne le champions_room_id d'une battle (participant authentifié)
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/set-room", methods=["POST"])
@require_user_token
def set_battle_room():
    from flask import g
    data = request.get_json(silent=True) or {}
    battle_id = data.get("battle_id")
    code = data.get("champions_room_id")

    if battle_id is None or code is None:
        return jsonify({"error": "Les champs 'battle_id' et 'champions_room_id' sont requis"}), 400

    try:
        code = int(code)
    except (TypeError, ValueError):
        return jsonify({"error": "'champions_room_id' doit être un entier"}), 400

    if not (10_000_000 <= code <= 99_999_999):
        return jsonify({"error": "'champions_room_id' doit être un code à 8 chiffres"}), 400

    try:
        battle = db_connector.set_champions_room_id(battle_id, code, g.current_user)
        return jsonify({
            "battle_id": battle.id,
            "champions_room_id": battle.content["champions_room_id"],
        }), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Battle introuvable"}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# ------------------------------------------------------------------
# POST /battleroom/battle/end
# Clôture une battle (enregistre le résultat)
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/end", methods=["POST"])
def end_battle():
    data = request.get_json(silent=True) or {}
    battle_id = data.get("battle_id")
    if battle_id is None:
        return jsonify({"error": "Le champ 'battle_id' est requis"}), 400

    try:
        battle = db_connector.end_battle(battle_id, data.get("result", {}))
        return jsonify({"battle_id": battle.id, "content": battle.content}), 200
    except db_connector.NotFoundError:
        return jsonify({"error": "Battle introuvable"}), 404
