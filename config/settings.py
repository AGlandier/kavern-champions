import os
from pathlib import Path
from dotenv import load_dotenv

# Remonte jusqu'à la racine du projet (dossier parent de config/)
# et charge le fichier .env s'il existe.
_ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT_DIR / ".env")


class Config:
    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")

    # SQLite
    DATABASE_PATH: str = os.environ.get(
        "DATABASE_PATH",
        str(_ROOT_DIR / "battleapp.db"),
    )

    # Clé admin — header X-Admin-Key attendu sur les routes protégées
    ADMIN_KEY: str = os.environ.get("ADMIN_KEY", "super-secret-admin-key")


class DevelopmentConfig(Config):
    DEBUG: bool = True


class ProductionConfig(Config):
    DEBUG: bool = False

    def __init__(self) -> None:
        if self.SECRET_KEY == "change-me-in-production":
            raise RuntimeError(
                "SECRET_KEY non définie — ajoutez-la dans les variables d'environnement."
            )
        if self.ADMIN_KEY == "super-secret-admin-key":
            raise RuntimeError(
                "ADMIN_KEY non définie — ajoutez-la dans les variables d'environnement."
            )
