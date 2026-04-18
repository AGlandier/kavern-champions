# BattleApp — API REST Flask + SQLite

## Structure du projet

```
battleapp/
├── app.py                        # Point d'entrée Flask (create_app)
├── init_db.py                    # Script autonome d'initialisation BDD
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py               # Config (clé admin, chemin BDD, etc.)
├── database/
│   ├── __init__.py
│   ├── db.py                     # Connexion SQLite + init_db()
│   └── schema.sql                # Définition des tables
└── controllers/
    ├── __init__.py
    ├── auth.py                   # Décorateur @require_admin_key
    ├── battleroom_controller.py  # Blueprint /battleroom
    └── user_controller.py        # Blueprint /user
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Initialisation de la base de données

```bash
python init_db.py
```

## Lancement

```bash
# Variables d'environnement (optionnel)
export ADMIN_KEY="ma-cle-secrete"
export DATABASE_PATH="./battleapp.db"

python app.py
```

## Routes

### battleroom_controller — préfixe `/battleroom`

| Méthode | Route                    | Auth admin | Description                         |
|---------|--------------------------|------------|-------------------------------------|
| POST    | `/battleroom/create`     | ✅          | Crée une battleroom                 |
| POST    | `/battleroom/next`       | ✅          | Passe au round suivant              |
| POST    | `/battleroom/enter`      | ✅          | Fait entrer un user dans la room    |
| POST    | `/battleroom/end`        | ✅          | Supprime / termine une battleroom   |
| GET     | `/battleroom/battle`     | ❌          | Liste toutes les battles            |
| GET     | `/battleroom/battle/<user>` | ❌       | Battles d'un utilisateur            |
| POST    | `/battleroom/battle/end` | ❌          | Clôture une battle                  |

### user_controller — préfixe `/user`

| Méthode | Route            | Auth admin | Description                          |
|---------|------------------|------------|--------------------------------------|
| GET     | `/user/stats`    | ❌          | Stats d'un user (`?name=xxx`)         |
| POST    | `/user/teamlist` | ❌          | Met à jour la teamlist d'un user      |

## Authentification admin

Passer le header HTTP suivant pour les routes protégées :

```
X-Admin-Key: ma-cle-secrete
```

## Tables SQLite

### `battlerooms`
| Colonne | Type    | Description                     |
|---------|---------|---------------------------------|
| id      | INTEGER | Clé primaire autoincrément      |
| name    | TEXT    | Nom de la room                  |
| date    | TEXT    | Date de création (auto)         |
| round   | INTEGER | Numéro du round en cours (≥ 0)  |

### `battle`
| Colonne    | Type    | Description                          |
|------------|---------|--------------------------------------|
| id         | INTEGER | Clé primaire autoincrément           |
| battleroom | INTEGER | Clé étrangère → battlerooms(id)      |
| content    | TEXT    | Données JSON (chaîne sérialisée)     |

### `user`
| Colonne       | Type    | Description                  |
|---------------|---------|------------------------------|
| name          | TEXT    | Clé primaire unique          |
| teamlist      | TEXT    | Chaîne de caractères         |
| number_battle | INTEGER | Nombre de battles jouées     |
