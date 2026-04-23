import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TWITCH_BOT_TOKEN: str = os.environ["TWITCH_BOT_TOKEN"]
TWITCH_BOT_NICK: str = os.environ["TWITCH_BOT_NICK"]
TWITCH_CHANNEL: str = os.environ["TWITCH_CHANNEL"]
TWITCH_CLIENT_ID: str = os.environ["TWITCH_CLIENT_ID"]
TWITCH_CLIENT_SECRET: str = os.environ["TWITCH_CLIENT_SECRET"]
TWITCH_REFRESH_TOKEN: str = os.environ["TWITCH_REFRESH_TOKEN"]
API_BASE_URL: str = os.environ.get("API_BASE_URL", "http://localhost:5000")
ADMIN_KEY: str = os.environ["ADMIN_KEY"]
COOLDOWN_SECONDS: int = int(os.environ.get("COOLDOWN_SECONDS", 10))

# Tokens rotatifs persistés après chaque refresh (prioritaires sur .env)
_tokens_file = Path(__file__).parent / "tokens.json"
if _tokens_file.exists():
    _saved = json.loads(_tokens_file.read_text())
    TWITCH_BOT_TOKEN = _saved.get("access_token", TWITCH_BOT_TOKEN)
    TWITCH_REFRESH_TOKEN = _saved.get("refresh_token", TWITCH_REFRESH_TOKEN)


def save_tokens(access_token: str, refresh_token: str) -> None:
    _tokens_file.write_text(json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }))
