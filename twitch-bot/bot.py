import logging
import httpx
from twitchio.ext import commands
import config
from commands.enter import enter_command
from commands.kchampions import kchampions_command

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

    async def event_token_expired(self):
        async with httpx.AsyncClient() as client:
            r = await client.post("https://id.twitch.tv/oauth2/token", data={
                "grant_type": "refresh_token",
                "refresh_token": config.TWITCH_REFRESH_TOKEN,
                "client_id": config.TWITCH_CLIENT_ID,
                "client_secret": config.TWITCH_CLIENT_SECRET,
            })
        data = r.json()
        config.TWITCH_REFRESH_TOKEN = data["refresh_token"]
        config.save_tokens(data["access_token"], data["refresh_token"])
        logging.info("Token Twitch rafraîchi")
        return data["access_token"]

    async def event_error(self, error: Exception, data=None):
        logging.error("Erreur non gérée : %s", error, exc_info=error)

    async def event_command_error(self, ctx: commands.Context, error: Exception):
        logging.error("Erreur commande '%s' par %s : %s", ctx.command, ctx.author.name, error, exc_info=error)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        await ctx.reply("pong !")

    @commands.command(name="enter")
    async def enter(self, ctx: commands.Context):
        await enter_command(ctx)

    @commands.command(name="kchampions")
    async def kchampions(self, ctx: commands.Context):
        await kchampions_command(ctx)


if __name__ == "__main__":
    KavernBot().run()
