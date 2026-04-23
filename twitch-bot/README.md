# KavernBot — Twitch Bot

Bot Twitch qui permet aux viewers de s'inscrire dans une battleroom KavernChampions via `!enter`.

## Setup

```bash
cd twitch-bot
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Remplir `.env` avec les valeurs réelles (voir section Variables).

```bash
python bot.py
```

## Variables d'environnement

| Variable | Description |
|---|---|
| `TWITCH_BOT_TOKEN` | Token OAuth du compte bot (`oauth:xxxx`) — générer sur [twitchapps.com/tmi](https://twitchapps.com/tmi/) |
| `TWITCH_BOT_NICK` | Nom d'utilisateur Twitch du compte bot |
| `TWITCH_CHANNEL` | Channel à écouter (sans `#`) |
| `API_BASE_URL` | URL du backend Flask (défaut : `http://localhost:5000`) |
| `ADMIN_KEY` | Clé admin partagée avec le backend |
| `COOLDOWN_SECONDS` | Anti-spam par utilisateur en secondes (défaut : `10`) |

## Commandes

| Commande | Qui | Effet |
|---|---|---|
| `!enter` | Tout viewer | Inscrit le viewer dans la battleroom active |

Le bot répond uniquement sur succès ou absence de battleroom active. Les erreurs (déjà inscrit, problème réseau) sont loguées côté serveur sans message dans le chat.
