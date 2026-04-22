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

    @commands.command(name="enter")
    async def enter(self, ctx: commands.Context):
        await enter_command(ctx)


if __name__ == "__main__":
    KavernBot().run()
