"""
battleroom_controller — Blueprint Flask
Préfixe : /battleroom
"""

from flask import Blueprint, jsonify, request, Response

import db_connector
from database.db import get_db
from controllers.auth import require_admin_key
from db_connector.models import Battleroom

battleroom_bp = Blueprint("battleroom", __name__)


# ------------------------------------------------------------------
# POST /battleroom/create  (admin)
# Crée une nouvelle battleroom
# ------------------------------------------------------------------
@battleroom_bp.route("/create", methods=["POST"])
@require_admin_key
def create():
    print(request.get_json())
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400

    battleroom : Battleroom = db_connector.create_battleroom(name)

    return jsonify(battleroom), 201

@battleroom_bp.route("/<room_id>", methods=["GET"])
def get_room(room_id) :
    try :
        battleroom : Battleroom = db_connector.get_battleroom_by_id(room_id)
        return jsonify(battleroom), 200
    except db_connector.NotFoundError:
        return jsonify("Battleroom not found"), 404


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

    db = get_db()
    row = db.execute(
        "SELECT id, round FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Battleroom introuvable"}), 404

    new_round = row["round"] + 1
    db.execute(
        "UPDATE battlerooms SET round = ? WHERE id = ?", (new_round, battleroom_id)
    )
    db.commit()
    return jsonify({"battleroom_id": battleroom_id, "round": new_round}), 200


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

    db = get_db()
    # Vérifie que la battleroom existe
    room = db.execute(
        "SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if room is None:
        return jsonify({"error": "Battleroom introuvable"}), 404

    # Crée l'utilisateur s'il n'existe pas encore
    db.execute(
        "INSERT OR IGNORE INTO user (name) VALUES (?)", (username,)
    )
    db.commit()
    return jsonify({"message": f"{username} a rejoint la battleroom {battleroom_id}"}), 200


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

    db = get_db()
    row = db.execute(
        "SELECT id FROM battlerooms WHERE id = ?", (battleroom_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Battleroom introuvable"}), 404

    db.execute("DELETE FROM battlerooms WHERE id = ?", (battleroom_id,))
    db.commit()
    return jsonify({"message": f"Battleroom {battleroom_id} terminée et supprimée"}), 200


# ------------------------------------------------------------------
# GET /battleroom/battle
# Retourne la liste de toutes les battles
# ------------------------------------------------------------------
@battleroom_bp.route("/battle", methods=["GET"])
def get_all_battles():
    db = get_db()
    rows = db.execute(
        "SELECT id, battleroom, content FROM battle"
    ).fetchall()
    battles = [{"id": r["id"], "battleroom": r["battleroom"], "content": r["content"]} for r in rows]
    return jsonify(battles), 200


# ------------------------------------------------------------------
# GET /battleroom/battle/<user>
# Retourne les battles associées à un utilisateur
# ------------------------------------------------------------------
@battleroom_bp.route("/battle/<string:user>", methods=["GET"])
def get_battle_by_user(user: str):
    db = get_db()
    # Vérifie que l'utilisateur existe
    u = db.execute("SELECT name FROM user WHERE name = ?", (user,)).fetchone()
    if u is None:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # Le contenu JSON de chaque battle peut contenir les participants —
    # à adapter selon la logique métier réelle.
    rows = db.execute(
        "SELECT id, battleroom, content FROM battle WHERE content LIKE ?",
        (f"%{user}%",),
    ).fetchall()
    battles = [{"id": r["id"], "battleroom": r["battleroom"], "content": r["content"]} for r in rows]
    return jsonify({"user": user, "battles": battles}), 200


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

    import json as _json

    db = get_db()
    row = db.execute(
        "SELECT id, content FROM battle WHERE id = ?", (battle_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Battle introuvable"}), 404

    # Fusionne le contenu existant avec les données de fin de battle
    try:
        existing = _json.loads(row["content"])
    except _json.JSONDecodeError:
        existing = {}

    existing.update({"status": "ended", "result": data.get("result", {})})
    db.execute(
        "UPDATE battle SET content = ? WHERE id = ?",
        (_json.dumps(existing), battle_id),
    )
    db.commit()
    return jsonify({"battle_id": battle_id, "content": existing}), 200
