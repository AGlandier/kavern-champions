# Spec Technique — Bot Twitch KavernChampions

## Vue d'ensemble

Un bot Twitch Python qui écoute le chat d'un channel et permet aux viewers de s'inscrire à une battleroom en tapant une commande. Il appelle `/battleroom/enter` via l'API existante en s'authentifiant avec l'`X-Admin-Key`.

---

## Architecture

```
twitch-bot/
├── bot.py                 # Point d'entrée, boucle principale
├── commands/
│   └── enter.py           # Logique de la commande !enter
├── api/
│   └── client.py          # Wrapper HTTP vers le backend Flask
├── config.py              # Chargement des variables d'env
├── requirements.txt
├── .env.example
├── Dockerfile             # Pour déploiement conteneurisé
└── README.md
```

Le bot est un **troisième processus indépendant** — il se connecte au backend Flask existant via HTTP, sans accès direct à la base de données.

---

## Stack technique

| Composant | Choix | Raison |
|---|---|---|
| Bibliothèque Twitch | `twitchio` 2.x | Library Python native IRC/EventSub, active, bien documentée |
| HTTP client | `httpx` | Async-first, plus moderne que `requests` |
| Config | `python-dotenv` | Cohérent avec le backend Flask existant |
| Python | 3.11+ | Compatible `.venv` du projet |

---

## Commandes Twitch

### `!enter`

**Déclencheur** : n'importe quel viewer du chat  
**Comportement** :
1. Appelle `GET /battleroom/latest` pour récupérer la dernière room créée
2. Utilise le **login Twitch** du viewer comme `username`
3. Appelle `POST /battleroom/enter` avec `{ battleroom_id, username }`
4. Répond dans le chat avec le résultat

> **Prérequis backend** : l'endpoint `GET /battleroom/latest` n'existe pas encore — il doit être ajouté au backend Flask. Il retourne simplement la battleroom avec l'`id` le plus élevé (dernière créée).

**Réponses bot** :

| Cas | Réponse |
|---|---|
| Succès | `@pseudo ✅ Tu as rejoint la battleroom !` |
| Déjà inscrit (409) | `@pseudo Tu es déjà inscrit dans cette battleroom.` |
| Aucune room active (404) | `@pseudo Aucune battleroom n'est ouverte pour le moment.` |
| Erreur API | `@pseudo Une erreur est survenue, réessaie.` |

### Commandes modérateur (optionnel — phase 2)

- `!battleroom create <nom>` → `POST /battleroom/create`
- `!battleroom next` → `POST /battleroom/next`

---

## Variables d'environnement

```env
# Twitch
TWITCH_BOT_TOKEN=oauth:xxxxxxxxxxxx   # Token OAuth du compte bot (pas du streamer)
TWITCH_BOT_NICK=KavernBot             # Nom d'utilisateur du compte bot Twitch
TWITCH_CHANNEL=nomdustreamer          # Channel à écouter

# Backend API
API_BASE_URL=http://localhost:5000
ADMIN_KEY=your_admin_key_here

# Optionnel
COOLDOWN_SECONDS=10                   # Anti-spam par utilisateur
```

---

## Obtenir le token Twitch

1. Créer un compte Twitch dédié au bot (ex: `KavernBot`)
2. Aller sur [twitchapps.com/tmi](https://twitchapps.com/tmi/) connecté avec ce compte
3. Générer le token OAuth → copier dans `TWITCH_BOT_TOKEN`
4. Pour une prod stable : créer une **Twitch App** sur [dev.twitch.tv](https://dev.twitch.tv) et utiliser le Client Credentials Flow pour renouveler le token automatiquement

---

## Exemple de code clé

**bot.py** — structure principale :
```python
from twitchio.ext import commands
from commands.enter import enter_command

class KavernBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=config.TWITCH_BOT_TOKEN,
            nick=config.TWITCH_BOT_NICK,
            prefix="!",
            initial_channels=[config.TWITCH_CHANNEL],
        )

    async def event_ready(self):
        print(f"Bot connecté : {self.nick}")

    @commands.command(name="enter")
    async def enter(self, ctx: commands.Context):
        await enter_command(ctx)
```

**api/client.py** — appel API :
```python
import httpx

async def get_latest_battleroom() -> dict | None:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{config.API_BASE_URL}/battleroom/latest",
            headers={"X-Admin-Key": config.ADMIN_KEY},
            timeout=5.0,
        )
    if r.status_code == 404:
        return None
    return r.json()

async def battleroom_enter(battleroom_id: int, username: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{config.API_BASE_URL}/battleroom/enter",
            json={"battleroom_id": battleroom_id, "username": username},
            headers={"X-Admin-Key": config.ADMIN_KEY},
            timeout=5.0,
        )
    return {"status": r.status_code, "body": r.json()}
```

---

## Déploiement

### Option A — Sur la même machine que le backend (dev/simple)

```bash
cd twitch-bot
python -m venv .venv
source .venv/bin/activate   # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
cp .env.example .env        # remplir les valeurs
python bot.py
```

Ajouter au `start.bat` existant pour lancer les 3 processus ensemble.

### Option B — Docker (recommandé pour production)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker build -t kavern-bot .
docker run -d --name kavern-bot --env-file .env kavern-bot
```

### Option C — VPS / Serveur dédié

- Héberger sur le même VPS que le backend Flask
- Gérer avec `systemd` ou `supervisor` pour redémarrage automatique
- `API_BASE_URL=http://localhost:5000` (pas d'exposition publique du port nécessaire)

---

## Plan de réalisation

### Phase 1 — MVP fonctionnel (≈ 2-3h)

| Étape | Tâche |
|---|---|
| 1 | Créer le dossier `twitch-bot/`, installer `twitchio` + `httpx` + `python-dotenv` |
| 2 | Écrire `config.py` avec chargement `.env` |
| 3 | Ajouter `GET /battleroom/latest` au backend Flask (retourne la room avec l'id le plus élevé) |
| 4 | Écrire `api/client.py` avec `get_latest_battleroom()` et `battleroom_enter()` |
| 5 | Écrire `commands/enter.py` avec appel séquentiel latest → enter + réponse |
| 6 | Écrire `bot.py` et câbler la commande |
| 7 | Tester en local avec le backend Flask déjà lancé |

### Phase 2 — Robustesse (≈ 1-2h)

| Étape | Tâche |
|---|---|
| 7 | Ajouter un cooldown par utilisateur (dict en mémoire, simple) |
| 8 | Gérer les timeouts et erreurs réseau proprement |
| 9 | Logs structurés (module `logging` Python) |
| 10 | Vérifier que le `username` Twitch existe dans la base avant d'appeler l'API (optionnel) |

### Phase 3 — Déploiement (≈ 1h)

| Étape | Tâche |
|---|---|
| 11 | Écrire le `Dockerfile` |
| 12 | Ajouter `twitch-bot` au `start.bat` ou créer `docker-compose.yml` |
| 13 | Documenter dans un `README.md` dédié |

---

## Points de vigilance

- **Correspondance username Twitch ↔ username app** : le login Twitch (ex: `toto42`) doit correspondre exactement au `username` enregistré dans KavernChampions. Si les joueurs ont des pseudos différents, il faudra soit une table de mapping, soit forcer l'inscription avec le pseudo Twitch.
- **Rate limiting Twitch** : le bot ne peut pas envoyer plus de ~20 messages/30s sur un channel où il n'est pas modérateur. Lui donner le statut modérateur lève cette limite à 100/30s.
- **Token OAuth expiration** : le token TMI expire — prévoir un refresh automatique ou utiliser les Client Credentials en phase 2.
- **L'`ADMIN_KEY` ne doit jamais être exposée** — le bot tourne côté serveur, jamais côté client Twitch.
