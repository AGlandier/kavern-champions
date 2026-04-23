import time
import logging
import config
from api.client import get_latest_battleroom, battleroom_enter

_cooldowns: dict[str, float] = {}


async def enter_command(ctx) -> None:
    username = ctx.author.name
    now = time.monotonic()
    if now - _cooldowns.get(username, 0) < config.COOLDOWN_SECONDS:
        return

    _cooldowns[username] = now

    room = await get_latest_battleroom()
    if room is None:
        await ctx.reply("Aucune battleroom n'est ouverte pour le moment.")
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
