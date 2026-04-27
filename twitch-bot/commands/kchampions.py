import time
import config
from api.client import get_latest_battleroom
from commands.enter import CLOSED_MESSAGE

_OPEN_MESSAGE = (
    "Pour participer aux Champions de la Kaverne tape !enter dans le chat ! "
    "Puis rends toi sur champions.ksomon.dev, et connecte-toi/crée toi un compte "
    "à partir de ton pseudo Twitch ! Accède ensuite à ton Dashboard, "
    "ton prochain match apparaîtra quand il sera prêt !"
)

_cooldowns: dict[str, float] = {}


async def kchampions_command(ctx) -> None:
    username = ctx.author.name
    now = time.monotonic()
    if now - _cooldowns.get(username, 0) < config.COOLDOWN_SECONDS:
        return

    _cooldowns[username] = now

    room = await get_latest_battleroom()
    if room is None or room.get("closed"):
        await ctx.reply(CLOSED_MESSAGE)
        return

    await ctx.reply(_OPEN_MESSAGE)
