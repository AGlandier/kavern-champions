"""
battleroom_controller — Blueprint Flask
Préfixe : /battleroom
"""

from flask import Blueprint, g, jsonify, request

from controllers.decorators import require_admin_key, require_user_token, require_admin_or_user_token
from db_connector import battleroom_repository, battle_repository, user_repository
from db_connector.exceptions import NotFoundError
from db_connector.models import Battleroom
from kchampions_core import make_pairings

battleroom_bp = Blueprint("battleroom", __name__)

_ALLOWED_ORDER_BY = {"date", "name"}


def _parse_pagination():
    """Lit et valide limit, offset, query depuis les query params."""
    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return None, None, None, (jsonify({"error": "Les paramètres 'limit' et 'offset' doivent être des entiers"}), 400)
    if limit < 1:
        return None, None, None, (jsonify({"error": "'limit' doit être >= 1"}), 400)
    if offset < 0:
        return None, None, None, (jsonify({"error": "'offset' doit être >= 0"}), 400)
    query = request.args.get("query", "").strip() or None
    return limit, offset, query, None


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

    battleroom: Battleroom = battleroom_repository.create_battleroom(name)
    return jsonify(battleroom), 201


# ------------------------------------------------------------------
# GET /battleroom/
# Retourne la liste de toutes les battlerooms
# ------------------------------------------------------------------
@battleroom_bp.route("/", methods=["GET"])
def get_all_rooms():
    limit, offset, query, err = _parse_pagination()
    if err:
        return err

    order_by = request.args.get("order-by", "date")
    if order_by not in _ALLOWED_ORDER_BY:
        return jsonify({"error": f"'order-by' doit être l'une des valeurs : {', '.join(_ALLOWED_ORDER_BY)}"}), 400

    rooms = battleroom_repository.get_all_battlerooms(limit=limit, offset=offset, query=query, order_by=order_by)
    total = battleroom_repository.count_battlerooms(query=query)
    return jsonify({
        "battlerooms": [{"id": r.id, "name": r.name, "date": r.date, "round": r.round} for r in rooms],
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200


# ------------------------------------------------------------------
# GET /battleroom/<room_id>/players
# Retourne la liste des joueurs inscrits dans une battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/<int:room_id>/players", methods=["GET"])
def get_players(room_id: int):
    limit, offset, query, err = _parse_pagination()
    if err:
        return err
    try:
        players = battleroom_repository.get_room_players(room_id, limit=limit, offset=offset, query=query)
        total = battleroom_repository.count_room_players(room_id, query=query)
        return jsonify({
            "battleroom_id": room_id,
            "players": players,
            "total": total,
            "limit": limit,
            "offset": offset,
        }), 200
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# GET /battleroom/<room_id>/players/<username>
# Vérifie si un joueur est inscrit dans une battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/<int:room_id>/players/<string:username>", methods=["GET"])
def is_player_in_room(room_id: int, username: str):
    try:
        players = battleroom_repository.get_room_players(room_id)
        return jsonify({"battleroom_id": room_id, "username": username, "in_room": username in players}), 200
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


@battleroom_bp.route("/<int:room_id>/stats", methods=["GET"])
def get_room_stats(room_id: int):
    try:
        room = battleroom_repository.get_battleroom_by_id(room_id)
        players = battleroom_repository.get_room_players(room_id)
        return jsonify({
            "id": room.id,
            "name": room.name,
            "players_count": len(players),
            "round": room.round,
        }), 200
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


@battleroom_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id):
    try:
        battleroom: Battleroom = battleroom_repository.get_battleroom_by_id(room_id)
        return jsonify(battleroom), 200
    except NotFoundError:
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
        players = battleroom_repository.get_room_players(battleroom_id)
        past_battles = battle_repository.get_battles_by_room(battleroom_id)
        past_pairings = [
            (b.content["player1"], b.content.get("player2"))
            for b in past_battles
            if "player1" in b.content
        ]

        # 2. Génère les appariements via le core (aucun I/O)
        pairings = make_pairings(players, past_pairings)

        # 3. Clôture les battles encore ouvertes du round précédent
        battle_repository.finish_unfinished_battles(battleroom_id)

        # 4. Incrémente le round
        battleroom = battleroom_repository.next_battleroom_round(battleroom_id)

        # 5. Persiste les combats en base (byes clôturés automatiquement via finished=True)
        battles = [
            battle_repository.create_battle(
                battleroom_id,
                battleroom.round,
                {"player1": p.player1, "player2": p.player2, "champions_room_id": None},
                finished=p.player2 is None,
            )
            for p in pairings
        ]

        return jsonify({
            "battleroom_id": battleroom.id,
            "round": battleroom.round,
            "battles": [
                {
                    "id": b.id,
                    "round": b.round,
                    "finished": b.finished,
                    "player1": b.content["player1"],
                    "player2": b.content.get("player2"),
                    "champions_room_id": b.content.get("champions_room_id"),
                    "bye": b.content.get("player2") is None,
                }
                for b in battles
            ],
        }), 200

    except NotFoundError:
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
        battleroom_repository.enter_battleroom(battleroom_id, username)
        return jsonify({"message": f"{username} a rejoint la battleroom {battleroom_id}"}), 200
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# POST /battleroom/drop  (user ou admin)
# Retire un joueur d'une battleroom ; termine sa battle en cours si elle existe
# ------------------------------------------------------------------
@battleroom_bp.route("/drop", methods=["POST"])
@require_admin_or_user_token
def drop():
    data = request.get_json(silent=True) or {}
    battleroom_id = data.get("battleroom_id")
    if battleroom_id is None:
        return jsonify({"error": "Le champ 'battleroom_id' est requis"}), 400

    if g.is_admin:
        username = data.get("username", "").strip()
        if not username:
            return jsonify({"error": "Le champ 'username' est requis pour un admin"}), 400
    else:
        username = g.current_user

    try:
        active = battle_repository.get_active_battle_for_player(battleroom_id, username)
        if active is not None:
            battle_repository.end_battle(active.id, {"forfeit": True})
        battleroom_repository.leave_battleroom(battleroom_id, username)
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404

    return jsonify({
        "message": f"{username} a quitté la battleroom {battleroom_id}",
        "forfeited_battle_id": active.id if active is not None else None,
    }), 200


# ------------------------------------------------------------------
# GET /battleroom/<room_id>/battles
# Retourne les battles d'une battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/<int:room_id>/battles", methods=["GET"])
def get_battles_by_room(room_id: int):
    try:
        battleroom_repository.get_battleroom_by_id(room_id)
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404

    try:
        round_filter = int(request.args.get("round", -1))
    except ValueError:
        return jsonify({"error": "Le paramètre 'round' doit être un entier"}), 400

    limit, offset, _, err = _parse_pagination()
    if err:
        return err

    battles = battle_repository.get_battles_by_room(room_id, round=round_filter, limit=limit, offset=offset)
    total = battle_repository.count_battles_by_room(room_id, round=round_filter)
    return jsonify({
        "battleroom_id": room_id,
        "battles": [
            {"id": b.id, "round": b.round, "finished": b.finished, "content": b.content}
            for b in battles
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200


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
        battleroom_repository.delete_battleroom(battleroom_id)
        return jsonify({"message": f"Battleroom {battleroom_id} terminée et supprimée"}), 200
    except NotFoundError:
        return jsonify({"error": "Battleroom introuvable"}), 404


# ------------------------------------------------------------------
# GET /battleroom/battle
# Retourne la liste de toutes les battles
# ------------------------------------------------------------------
@battleroom_bp.route("/battle", methods=["GET"])
def get_all_battles():
    limit, offset, _, err = _parse_pagination()
    if err:
        return err
    battles = battle_repository.get_all_battles(limit=limit, offset=offset)
    total = battle_repository.count_all_battles()
    return jsonify({
        "battles": [
            {"id": b.id, "battleroom": b.battleroom_id, "round": b.round, "finished": b.finished, "content": b.content}
            for b in battles
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200


# ------------------------------------------------------------------
# GET /battleroom/battle/<id>
# Retourne une battle par son identifiant
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/<int:battle_id>", methods=["GET"])
def get_battle(battle_id: int):
    try:
        battle = battle_repository.get_battle_by_id(battle_id)
        return jsonify({"id": battle.id, "battleroom": battle.battleroom_id, "round": battle.round, "finished": battle.finished, "content": battle.content}), 200
    except NotFoundError:
        return jsonify({"error": "Battle introuvable"}), 404


# ------------------------------------------------------------------
# GET /battleroom/battle/<user>
# Retourne les battles associées à un utilisateur
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/<string:user>", methods=["GET"])
def get_battle_by_user(user: str):
    try:
        user_repository.get_user(user)
    except NotFoundError:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    limit, offset, _, err = _parse_pagination()
    if err:
        return err
    battles = battle_repository.get_battles_by_user(user, limit=limit, offset=offset)
    total = battle_repository.count_battles_by_user(user)
    return jsonify({
        "user": user,
        "battles": [
            {"id": b.id, "battleroom": b.battleroom_id, "round": b.round, "finished": b.finished, "content": b.content}
            for b in battles
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200


# ------------------------------------------------------------------
# POST /battleroom/battle/set-room
# Renseigne le champions_room_id d'une battle (participant authentifié)
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/set-room", methods=["POST"])
@require_user_token
def set_battle_room():
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
        battle = battle_repository.get_battle_by_id(battle_id)
    except NotFoundError:
        return jsonify({"error": "Battle introuvable"}), 404

    content = battle.content
    if g.current_user not in (content.get("player1"), content.get("player2")):
        return jsonify({"error": f"'{g.current_user}' n'est pas participant de cette battle."}), 403

    battle = battle_repository.set_champions_room_id(battle_id, code)
    return jsonify({
        "battle_id": battle.id,
        "champions_room_id": battle.content["champions_room_id"],
    }), 200


# ------------------------------------------------------------------
# POST /battleroom/battle/end
# Clôture une battle (enregistre le résultat)
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/end", methods=["POST"])
@require_admin_or_user_token
def end_battle():
    data = request.get_json(silent=True) or {}
    battle_id = data.get("battle_id")
    if battle_id is None:
        return jsonify({"error": "Le champ 'battle_id' est requis"}), 400

    try:
        battle = battle_repository.get_battle_by_id(battle_id)
    except NotFoundError:
        return jsonify({"error": "Battle introuvable"}), 404

    if not g.is_admin:
        content = battle.content
        if g.current_user not in (content.get("player1"), content.get("player2")):
            return jsonify({"error": f"'{g.current_user}' n'est pas participant de cette battle."}), 403

    battle = battle_repository.end_battle(battle_id, data.get("result", {}))

    # Incrémente number_battle pour chaque participant réel (pas les byes)
    for player in (battle.content.get("player1"), battle.content.get("player2")):
        if player is not None:
            user_repository.increment_number_battle(player)

    return jsonify({"battle_id": battle.id, "round": battle.round, "finished": battle.finished, "content": battle.content}), 200
