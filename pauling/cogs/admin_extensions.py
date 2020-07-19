import discord
from discord.ext import commands
import logging
import traceback

class Admin_Extensions(commands.Cog, name="Extensions"):

    logger = logging.getLogger(__name__)

    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def load(self, ctx, extension):
        try:
            self.client.load_extension(f'pauling.cogs.{extension}')
            self.logger.info(f"Loaded extension {extension}")
            await ctx.send(f'Loaded extension {extension}')
        except Exception as e:
            self.logger.warning(f"Failed to load extension {extension}.")
            self.logger.warning(traceback.format_exc())
            await ctx.send(f'Failed to load extension {extension}')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def unload(self, ctx, extension):
        try:
            self.client.unload_extension(f'pauling.cogs.{extension}')
            self.logger.info(f"Unloaded extension {extension}")
            await ctx.send(f'Unloaded extension {extension}')
        except Exception as e:
            self.logger.warning(f"Failed to unload extension {extension}")
            self.logger.warning(traceback.format_exc())
            await ctx.send(f"Failed to unload extension {extension}")

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def reload(self, ctx, extension):
        try:
            self.client.unload_extension(f'pauling.cogs.{extension}')
            self.client.load_extension(f'pauling.cogs.{extension}')
            self.logger.info(f"Reloaded extension {extension}")
            await ctx.send(f'Reloaded extension {extension}')
        except Exception as e:
            self.logger.warning(f"Reload of {extension} failed")
            self.logger.warning(traceback.format_exc())
            await ctx.send(f"Reload of {extension} failed")

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #
    
    def cog_unload(self):
        self.logger.info("Extension admin_extensions is being unloaded!")
        self.logger.handlers = []

def setup(client):
    client.add_cog(Admin_Extensions(client))