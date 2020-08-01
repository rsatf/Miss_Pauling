import logging
import sys
from discord.ext import commands

logger = logging.getLogger(__name__)

class Bot(commands.Bot):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logon_str = f"Logged in as {self.user}"
        logger.info(logon_str)

    def add_cog(self, cog):
        super().add_cog(cog)
        logger.info(f"Added cog {cog.qualified_name}")

    def run(self, token):
        if token is None:
            raise ValueError("Bot cannot start without a token")
        super().run(token)

    async def close(self):
        await super().close()
        logger.info("Bot instance closing.")

    async def on_error(self, event_method, *args, **kwargs):
        _, exception, _ = sys.exc_info()
        logger.error(exception)