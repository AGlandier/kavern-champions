# Guide de déploiement — KavernChampions

## 1. Recommandation d'hébergement

### Contexte
- Stack : Flask (backend) + Vite/React (frontend) + Nginx + bot Python
- Volume attendu : quelques dizaines d'utilisateurs simultanés
- Architecture : 3 conteneurs Docker (nginx+frontend, backend, bot)

### Recommandation : VPS Hetzner (CX22)

**Pourquoi Hetzner ?**
- Prix : ~4,50 €/mois (2 vCPU, 4 Go RAM, 40 Go SSD)
- Datacenter en Europe (Allemagne ou Finlande, latence faible depuis la France)
- Interface simple, support sérieux
- Amplement suffisant pour ce volume : le backend Flask + le bot Python ensemble consomment < 300 Mo RAM
- Contrôle total sur Docker et docker-compose

**Alternatives si Hetzner n'est pas disponible :**
| Hébergeur | Prix | Notes |
|---|---|---|
| OVH VPS Starter | ~4 €/mois | Datacenter français, support FR |
| DigitalOcean Droplet Basic | ~6 $/mois | Interface très soignée, bonne doc |
| Fly.io | Gratuit (limites) | Bon pour test, moins prévisible en prod |
| Render.com | 7 $/mois | Se met en veille sur le free tier — à éviter |

> **À éviter pour ce projet** : les plateformes PaaS comme Heroku, Railway ou Render en free tier. Elles font "dormir" le service après inactivité, ce qui est incompatible avec un bot Twitch qui doit rester connecté en permanence.

---

## 2. Recommandation nom de domaine

### Stratégie recommandée : un domaine principal + sous-domaine

Plutôt qu'acheter `kavernchampions.gg`, acheter un domaine à ton nom (`monpseudo.com`) et utiliser un **sous-domaine** pour cette application :

| URL | Destination |
|---|---|
| `monpseudo.com` | Ton CV / portfolio |
| `kavernchampions.monpseudo.com` | Cette application |
| `autreprojet.monpseudo.com` | Un futur projet, etc. |

**Avantages :**
- Un seul domaine à payer (~9 $/an), autant de sous-domaines que voulu (gratuits)
- Cohérence de marque personnelle
- Facile à étendre si tu héberges d'autres projets sur le même VPS

### Recommandation registrar : Cloudflare Registrar

**Pourquoi Cloudflare ?**
- Prix au coût (sans marge) : ~9 $/an pour un `.com`
- DNS gratuit inclus, avec proxy (cache + protection DDoS basique)
- Certificats SSL/TLS gérés automatiquement via leur proxy
- Interface simple pour créer des sous-domaines

**Alternatives :**
| Registrar | Prix .com | Notes |
|---|---|---|
| Namecheap | ~9 $/an | Fiable, interface claire |
| OVH | ~9 €/an | Support en français |
| Gandi | ~15 €/an | Premium, éthique, mais plus cher |

> **Extension recommandée** : `.com` (~9 $/an) pour un domaine personnel polyvalent. Le `.gg` reste une option si tu veux un domaine dédié gaming, mais il coûte ~20 $/an et ne peut pas accueillir un CV sans paraître décalé.

---

## 3. Architecture Docker cible

```
                        Internet
                            │
                        Nginx (port 443/80)
                       /           \
              Frontend (static)   /api/*  → Backend Flask (port 5000)
                                               │
                                           SQLite DB (volume)
                                  
              Bot Python (conteneur séparé, se connecte au backend via HTTP interne)
```

**docker-compose.yml final :**
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
      - frontend_build:/usr/share/nginx/html:ro
    depends_on:
      - backend

  backend:
    build: ./backend
    expose:
      - "5000"
    volumes:
      - db_data:/app/data
    env_file:
      - .env.prod
    restart: unless-stopped

  bot:
    build: ./twitch-bot
    env_file:
      - .env.prod
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  db_data:
  frontend_build:
```

---

## 4. Marche à suivre détaillée

### Étape 1 — Acheter le nom de domaine

1. Aller sur [cloudflare.com/products/registrar](https://www.cloudflare.com/products/registrar/)
2. Créer un compte Cloudflare (gratuit)
3. Dans le dashboard → **Domain Registration** → **Register Domains**
4. Chercher ton domaine personnel (ex: `monpseudo.com`)
5. Payer (~9 $/an)
6. Le domaine apparaît dans ton dashboard Cloudflare — ne pas encore configurer le DNS, ce sera fait après.

---

### Étape 2 — Créer le VPS Hetzner

1. Aller sur [hetzner.com/cloud](https://www.hetzner.com/cloud)
2. Créer un compte (carte bancaire requise)
3. **New Project** → nommer le projet `KavernChampions`
4. **Add Server** :
   - Location : **Nuremberg** ou **Helsinki**
   - Image : **Ubuntu 24.04**
   - Type : **CX22** (2 vCPU, 4 Go RAM) — 4,50 €/mois
   - SSH Key : ajouter ta clé publique (recommandé, voir note ci-dessous)
   - Name : `kavern-prod`
5. Cliquer **Create & Buy**

> **Créer une clé SSH si tu n'en as pas :**
> ```bash
> ssh-keygen -t ed25519 -C "kavern-deploy"
> # Copier le contenu de ~/.ssh/id_ed25519.pub dans Hetzner
> ```

6. Noter l'**IP publique** du serveur (ex: `65.21.x.x`)

---

### Étape 3 — Configurer le DNS

Dans Cloudflare Dashboard → ton domaine → **DNS** → **Add record** :

| Type | Name | Value | Proxy | Destination |
|---|---|---|---|---|
| A | `@` | IP de l'hébergeur de ton CV | Proxied | `monpseudo.com` → CV |
| A | `www` | IP de l'hébergeur de ton CV | Proxied | `www.monpseudo.com` → CV |
| A | `kavernchampions` | `65.21.x.x` (ton VPS Hetzner) | Proxied | `kavernchampions.monpseudo.com` → cette app |

> Si ton CV est sur une plateforme tierce (GitHub Pages, Vercel, etc.), elle t'indiquera quelle IP ou valeur CNAME utiliser. Si ton CV est aussi sur le même VPS, les deux `A` pointent vers la même IP.

> Le proxy Cloudflare cache la vraie IP et gère le SSL automatiquement. La propagation DNS prend quelques minutes.

---

### Étape 4 — Configurer le serveur

Se connecter en SSH :
```bash
ssh root@65.21.x.x
```

Mise à jour et installation de Docker :
```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose-v2 git
systemctl enable docker
systemctl start docker
```

Créer un utilisateur dédié (bonne pratique) :
```bash
adduser kavern
usermod -aG docker kavern
# Copier la clé SSH autorisée pour cet utilisateur
cp -r /root/.ssh /home/kavern/.ssh
chown -R kavern:kavern /home/kavern/.ssh
```

---

### Étape 5 — Préparer les fichiers Docker

#### 5.1 — Dockerfile backend (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

> Modifier `app.py` pour écouter sur `0.0.0.0` :
> ```python
> if __name__ == "__main__":
>     app.run(host="0.0.0.0", port=5000)
> ```

#### 5.2 — Dockerfile bot (`twitch-bot/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

#### 5.3 — Build frontend et intégration Nginx

Le frontend Vite doit être buildé **localement** (ou dans un multi-stage Docker) :

Option recommandée — multi-stage dans `frontend/Dockerfile` :
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

#### 5.4 — Configuration Nginx (`nginx/nginx.conf`)
```nginx
server {
    listen 80;
    server_name kavernchampions.monpseudo.com;

    # Frontend (fichiers statiques)
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;  # SPA routing
    }

    # Reverse proxy vers le backend Flask
    location /api/ {
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

> **Note SSL** : Cloudflare en mode proxy gère le SSL entre le visiteur et Cloudflare. Entre Cloudflare et ton serveur, le trafic passe en HTTP (port 80). C'est suffisant pour débuter. Pour du SSL end-to-end, utiliser Certbot (voir section optionnelle).

---

### Étape 6 — Fichier de configuration production

Créer `.env.prod` à la racine du projet (ne jamais committer ce fichier) :
```env
# Backend
ADMIN_KEY=un_secret_fort_generé_aléatoirement_ici
DATABASE_PATH=/app/data/battleapp.db
FLASK_ENV=production

# Bot Twitch
TWITCH_BOT_TOKEN=oauth:xxxxxxxxxxxx
TWITCH_BOT_NICK=KavernBot
TWITCH_CHANNEL=nomdustreamer
API_BASE_URL=http://backend:5000
COOLDOWN_SECONDS=10
```

> Générer un ADMIN_KEY solide : `python -c "import secrets; print(secrets.token_hex(32))"`

Ajouter `.env.prod` au `.gitignore` :
```bash
echo ".env.prod" >> .gitignore
```

---

### Étape 7 — Déployer sur le serveur

#### 7.1 — Pousser le code sur le serveur

Option A — via Git (recommandé) :
```bash
# Sur le serveur
su - kavern
git clone https://github.com/TON_COMPTE/KavernChampions.git
cd KavernChampions
```

Option B — via rsync depuis ton poste local :
```bash
rsync -avz --exclude node_modules --exclude __pycache__ --exclude .env* \
  ./ kavern@65.21.x.x:~/KavernChampions/
```

#### 7.2 — Copier le fichier d'environnement
```bash
# Depuis ton poste local
scp .env.prod kavern@65.21.x.x:~/KavernChampions/.env.prod
```

#### 7.3 — Lancer les conteneurs
```bash
# Sur le serveur, dans ~/KavernChampions/
docker compose up -d --build
```

Vérifier que tout tourne :
```bash
docker compose ps
docker compose logs -f
```

---

### Étape 8 — Vérification finale

1. Ouvrir `https://kavernchampions.monpseudo.com` dans un navigateur → le frontend doit s'afficher
2. Tester `https://kavernchampions.monpseudo.com/api/battleroom/latest` → réponse JSON du backend
3. Vérifier les logs du bot : `docker compose logs bot -f`
4. Dans le chat Twitch, taper `!enter` → vérifier la réponse du bot

---

### Étape 9 — Mises à jour futures

Workflow de mise à jour :
```bash
# Depuis ton poste local
git push origin main

# Sur le serveur
cd ~/KavernChampions
git pull
docker compose up -d --build
```

---

## 5. Optionnel — SSL end-to-end avec Certbot

Si tu veux que Cloudflare soit en mode "Full (strict)" (SSL entre Cloudflare et ton serveur) :

```bash
# Sur le serveur
apt install -y certbot python3-certbot-nginx
certbot --nginx -d kavernchampions.monpseudo.com
```

Mettre à jour `nginx.conf` pour écouter sur le port 443, puis ouvrir le port dans Hetzner :
- Hetzner Dashboard → ton serveur → **Firewalls** → autoriser les ports 80 et 443

---

## 6. Résumé des coûts

| Poste | Coût |
|---|---|
| VPS Hetzner CX22 | ~4,50 €/mois (~54 €/an) |
| Domaine `monpseudo.com` (Cloudflare) | ~9 $/an |
| Sous-domaines supplémentaires | Gratuit |
| SSL (Cloudflare proxy) | Gratuit |
| **Total** | **~63 €/an** |

> Le même domaine couvre cette app, ton CV, et tous tes futurs projets sans coût additionnel.
