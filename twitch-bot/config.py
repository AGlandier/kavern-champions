import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_BOT_TOKEN: str = os.environ["TWITCH_BOT_TOKEN"]
TWITCH_BOT_NICK: str = os.environ["TWITCH_BOT_NICK"]
TWITCH_CHANNEL: str = os.environ["TWITCH_CHANNEL"]
API_BASE_URL: str = os.environ.get("API_BASE_URL", "http://localhost:5000")
ADMIN_KEY: str = os.environ["ADMIN_KEY"]
COOLDOWN_SECONDS: int = int(os.environ.get("COOLDOWN_SECONDS", 10))
