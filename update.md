# Mise à jour de l'application en production

## Workflow

```
Local → git push origin master → SSH serveur → git pull → docker compose up -d --build
```

---

## Étapes

### 1 — Merger et pousser sur master (depuis ton poste local)

```bash
git checkout master
git merge develop
git push origin master
```

---

### 2 — Se connecter au serveur

```bash
ssh kavern@77.42.93.189
cd KavernChampions
```

---

### 3 — Récupérer les changements

```bash
git pull origin master
```

---

### 4 — Reconstruire et redémarrer les conteneurs

```bash
docker compose up -d --build
```

Docker reconstruit uniquement les images modifiées, puis redémarre les conteneurs.

---

### 5 — Vérifier

```bash
docker compose ps          # les 3 services doivent être "running"
docker compose logs -f     # surveiller les logs au démarrage
```

---

## La base de données est-elle conservée ?

**Oui.** La base SQLite est stockée dans un volume Docker nommé (`db_data`), indépendant des conteneurs. `docker compose up -d --build` ne touche jamais les volumes.

> ⚠️ La seule commande qui supprime les volumes est `docker compose down -v` — ne jamais l'utiliser en production.

---

## Si le .env.prod a changé

Les variables d'environnement sont lues au démarrage des conteneurs. Si tu modifies `.env.prod` sur le serveur, un simple restart suffit (pas besoin de rebuild) :

```bash
docker compose down
docker compose up -d
```

---

## Sauvegarder la base avant une mise à jour importante

```bash
# Sur le serveur
docker compose exec backend cp /app/data/battleapp.db /app/data/battleapp.db.bak
```

La copie reste dans le volume et peut être restaurée si nécessaire :

```bash
docker compose exec backend cp /app/data/battleapp.db.bak /app/data/battleapp.db
docker compose restart backend
```
