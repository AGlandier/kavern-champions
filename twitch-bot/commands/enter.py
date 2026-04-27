import time
import logging
import config
from api.client import get_latest_battleroom, battleroom_enter

CLOSED_MESSAGE = (
    "La Kaverne des Champions est fermée pour l'instant ! "
    "Suis-moi sur twitter : https://x.com/g_rathur "
    "ou rejoins le Discord : https://discord.gg/VushHVeU4A "
    "pour te tenir au courant des prochaines éditions !"
)

_cooldowns: dict[str, float] = {}


async def enter_command(ctx) -> None:
    username = ctx.author.name
    now = time.monotonic()
    if now - _cooldowns.get(username, 0) < config.COOLDOWN_SECONDS:
        return

    _cooldowns[username] = now

    room = await get_latest_battleroom()
    if room is None or room.get("closed"):
        await ctx.reply(CLOSED_MESSAGE)
        return

    result = await battleroom_enter(room["id"], username)
    if result is None:
        logging.warning("battleroom_enter returned None for user %s", username)
        return

    status = result["status"]

    if status == 200:
        await ctx.reply(f"@{username} est prêt pour la bagarre !")
    elif status == 409:
        logging.info("User %s already registered in battleroom %s", username, room["id"])
    else:
        logging.warning("Unexpected status %s for user %s", status, username)
