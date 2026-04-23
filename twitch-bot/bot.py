import logging
from twitchio.ext import commands
import config
from commands.enter import enter_command

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class KavernBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=config.TWITCH_BOT_TOKEN,
            nick=config.TWITCH_BOT_NICK,
            prefix="!",
            initial_channels=[config.TWITCH_CHANNEL],
        )

    async def event_ready(self):
        logging.info(f"Bot connecté : {self.nick}")

    async def event_error(self, error: Exception, data=None):
        logging.error("Erreur non gérée : %s", error, exc_info=error)

    async def event_command_error(self, ctx: commands.Context, error: Exception):
        logging.error("Erreur commande '%s' par %s : %s", ctx.command, ctx.author.name, error, exc_info=error)

    @commands.command(name="enter")
    async def enter(self, ctx: commands.Context):
        await enter_command(ctx)


if __name__ == "__main__":
    KavernBot().run()
