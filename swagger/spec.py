"""
spec.py — Spécification OpenAPI (Swagger 2.0) de l'API Champions Kaverne.
Chargée uniquement en mode développement.
"""

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Champions Kaverne API",
        "description": "API de gestion des battlerooms et tournois Pokémon.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "AdminKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Admin-Key",
            "description": "Clé d'administration (variable d'environnement ADMIN_KEY)",
        },
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Token utilisateur au format `Bearer <token>`",
        },
    },
    "tags": [
        {"name": "Authentification", "description": "Inscription, mot de passe, login"},
        {"name": "Utilisateur", "description": "Stats et teamlist"},
        {"name": "Battleroom", "description": "Gestion des salles de combat"},
        {"name": "Battle", "description": "Gestion des combats"},
    ],
    "paths": {

        # ── AUTH ─────────────────────────────────────────────────────────────

        "/auth/register": {
            "post": {
                "tags": ["Authentification"],
                "summary": "Inscrire un nouvel utilisateur",
                "description": (
                    "Crée un compte avec un nom d'utilisateur uniquement. "
                    "Aucun mot de passe n'est requis à l'inscription."
                ),
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "example": "Sacha"},
                        },
                    },
                }],
                "responses": {
                    "201": {
                        "description": "Utilisateur créé",
                        "schema": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}},
                        },
                    },
                    "400": {"description": "Champ 'name' manquant"},
                    "409": {"description": "Nom d'utilisateur déjà pris"},
                },
            },
        },

        "/auth/set-password": {
            "post": {
                "tags": ["Authentification"],
                "summary": "Définir ou modifier le mot de passe",
                "description": (
                    "Si l'utilisateur n'a pas encore de mot de passe, le définit librement. "
                    "Si un mot de passe existe déjà, `current_password` est obligatoire."
                ),
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["name", "password"],
                        "properties": {
                            "name": {"type": "string", "example": "Sacha"},
                            "password": {"type": "string", "example": "nouveauMDP"},
                            "current_password": {
                                "type": "string",
                                "example": "ancienMDP",
                                "description": "Requis uniquement si un mot de passe est déjà défini",
                            },
                        },
                    },
                }],
                "responses": {
                    "200": {"description": "Mot de passe défini avec succès"},
                    "400": {"description": "Champs requis manquants"},
                    "401": {"description": "Mot de passe actuel incorrect"},
                    "404": {"description": "Utilisateur introuvable"},
                },
            },
        },

        "/auth/login": {
            "post": {
                "tags": ["Authentification"],
                "summary": "Se connecter",
                "description": "Retourne un token Bearer valable 24 heures.",
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["name", "password"],
                        "properties": {
                            "name": {"type": "string", "example": "Sacha"},
                            "password": {"type": "string", "example": "monMDP"},
                        },
                    },
                }],
                "responses": {
                    "200": {
                        "description": "Authentification réussie",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "token": {"type": "string"},
                                "name": {"type": "string"},
                            },
                        },
                    },
                    "400": {"description": "Champs 'name' ou 'password' manquants"},
                    "401": {"description": "Identifiants invalides"},
                },
            },
        },

        "/auth/me": {
            "get": {
                "tags": ["Authentification"],
                "summary": "Vérifier son token",
                "description": "Retourne le nom d'utilisateur associé au token.",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Token valide",
                        "schema": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Token manquant, invalide ou expiré"},
                },
            },
        },

        # ── USER ─────────────────────────────────────────────────────────────

        "/user/stats": {
            "get": {
                "tags": ["Utilisateur"],
                "summary": "Statistiques d'un utilisateur",
                "parameters": [{
                    "in": "query", "name": "name", "required": True,
                    "type": "string", "description": "Nom de l'utilisateur",
                }],
                "responses": {
                    "200": {
                        "description": "Statistiques de l'utilisateur",
                        "schema": {"$ref": "#/definitions/User"},
                    },
                    "400": {"description": "Paramètre 'name' manquant"},
                    "404": {"description": "Utilisateur introuvable"},
                },
            },
        },

        "/user/teamlist": {
            "post": {
                "tags": ["Utilisateur"],
                "summary": "Mettre à jour la teamlist",
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "example": "Sacha"},
                            "teamlist": {"type": "string", "example": "Pikachu, Évoli"},
                        },
                    },
                }],
                "responses": {
                    "200": {
                        "description": "Teamlist mise à jour",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "teamlist": {"type": "string"},
                            },
                        },
                    },
                    "400": {"description": "Champ 'name' manquant"},
                    "404": {"description": "Utilisateur introuvable"},
                },
            },
        },

        # ── BATTLEROOM ────────────────────────────────────────────────────────

        "/battleroom/create": {
            "post": {
                "tags": ["Battleroom"],
                "summary": "Créer une battleroom (admin)",
                "security": [{"AdminKey": []}],
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "example": "Room principale"},
                        },
                    },
                }],
                "responses": {
                    "201": {
                        "description": "Battleroom créée",
                        "schema": {"$ref": "#/definitions/Battleroom"},
                    },
                    "400": {"description": "Champ 'name' manquant"},
                    "401": {"description": "Clé admin invalide"},
                },
            },
        },

        "/battleroom/{room_id}": {
            "get": {
                "tags": ["Battleroom"],
                "summary": "Récupérer une battleroom",
                "parameters": [{
                    "in": "path", "name": "room_id", "required": True,
                    "type": "integer", "description": "Identifiant de la battleroom",
                }],
                "responses": {
                    "200": {
                        "description": "Battleroom trouvée",
                        "schema": {"$ref": "#/definitions/Battleroom"},
                    },
                    "404": {"description": "Battleroom introuvable"},
                },
            },
        },

        "/battleroom/next": {
            "post": {
                "tags": ["Battleroom"],
                "summary": "Passer au round suivant (admin)",
                "security": [{"AdminKey": []}],
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["battleroom_id"],
                        "properties": {
                            "battleroom_id": {"type": "integer", "example": 1},
                        },
                    },
                }],
                "responses": {
                    "200": {
                        "description": "Round incrémenté",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "battleroom_id": {"type": "integer"},
                                "round": {"type": "integer"},
                            },
                        },
                    },
                    "400": {"description": "Champ 'battleroom_id' manquant"},
                    "401": {"description": "Clé admin invalide"},
                    "404": {"description": "Battleroom introuvable"},
                },
            },
        },

        "/battleroom/enter": {
            "post": {
                "tags": ["Battleroom"],
                "summary": "Faire entrer un utilisateur (admin)",
                "security": [{"AdminKey": []}],
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["battleroom_id", "username"],
                        "properties": {
                            "battleroom_id": {"type": "integer", "example": 1},
                            "username": {"type": "string", "example": "Sacha"},
                        },
                    },
                }],
                "responses": {
                    "200": {"description": "Utilisateur ajouté à la battleroom"},
                    "400": {"description": "Champs requis manquants"},
                    "401": {"description": "Clé admin invalide"},
                    "404": {"description": "Battleroom introuvable"},
                },
            },
        },

        "/battleroom/end": {
            "post": {
                "tags": ["Battleroom"],
                "summary": "Terminer une battleroom (admin)",
                "security": [{"AdminKey": []}],
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["battleroom_id"],
                        "properties": {
                            "battleroom_id": {"type": "integer", "example": 1},
                        },
                    },
                }],
                "responses": {
                    "200": {"description": "Battleroom supprimée"},
                    "400": {"description": "Champ 'battleroom_id' manquant"},
                    "401": {"description": "Clé admin invalide"},
                    "404": {"description": "Battleroom introuvable"},
                },
            },
        },

        # ── BATTLE ────────────────────────────────────────────────────────────

        "/battleroom/battle": {
            "get": {
                "tags": ["Battle"],
                "summary": "Lister toutes les battles",
                "responses": {
                    "200": {
                        "description": "Liste des battles",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/Battle"},
                        },
                    },
                },
            },
        },

        "/battleroom/battle/{user}": {
            "get": {
                "tags": ["Battle"],
                "summary": "Battles d'un utilisateur",
                "parameters": [{
                    "in": "path", "name": "user", "required": True,
                    "type": "string", "description": "Nom de l'utilisateur",
                }],
                "responses": {
                    "200": {
                        "description": "Battles de l'utilisateur",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "user": {"type": "string"},
                                "battles": {
                                    "type": "array",
                                    "items": {"$ref": "#/definitions/Battle"},
                                },
                            },
                        },
                    },
                    "404": {"description": "Utilisateur introuvable"},
                },
            },
        },

        "/battleroom/battle/end": {
            "post": {
                "tags": ["Battle"],
                "summary": "Clôturer une battle",
                "parameters": [{
                    "in": "body", "name": "body", "required": True,
                    "schema": {
                        "type": "object",
                        "required": ["battle_id"],
                        "properties": {
                            "battle_id": {"type": "integer", "example": 1},
                            "result": {
                                "type": "object",
                                "description": "Données de résultat libres",
                            },
                        },
                    },
                }],
                "responses": {
                    "200": {
                        "description": "Battle clôturée",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "battle_id": {"type": "integer"},
                                "content": {"type": "object"},
                            },
                        },
                    },
                    "400": {"description": "Champ 'battle_id' manquant"},
                    "404": {"description": "Battle introuvable"},
                },
            },
        },
    },

    "definitions": {
        "Battleroom": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "date": {"type": "string", "format": "date-time"},
                "round": {"type": "integer"},
            },
        },
        "Battle": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "battleroom": {"type": "integer"},
                "content": {"type": "object"},
            },
        },
        "User": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "teamlist": {"type": "string"},
                "number_battle": {"type": "integer"},
            },
        },
    },
}
