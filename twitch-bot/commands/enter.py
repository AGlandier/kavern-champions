import time
import config
from api.client import get_latest_battleroom, battleroom_enter

_cooldowns: dict[str, float] = {}


async def enter_command(ctx) -> None:
    username = ctx.author.name
    now = time.monotonic()
    if now - _cooldowns.get(username, 0) < config.COOLDOWN_SECONDS:
        return

    room = await get_latest_battleroom()
    if room is None:
        await ctx.reply("Aucune battleroom n'est ouverte pour le moment.")
        return

    result = await battleroom_enter(room["id"], username)
    status = result["status"]

    if status == 200:
        await ctx.reply(f"@{(ctx.author.name)} est prêt à se battre !")

    _cooldowns[username] = now
