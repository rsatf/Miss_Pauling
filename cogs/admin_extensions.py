import discord
from discord.ext import commands
import logging

class Admin_Extensions(commands.Cog, name="Extensions"):

    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    logger = logging.getLogger('admin_extensions')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def load(self, ctx, extension):
        try:
            self.client.load_extension(f'cogs.{extension}')
            self.logger.info(f"Loaded extension {extension}")
            await ctx.send(f'Loaded extension {extension}')
        except:
            self.logger.warning(f"Failed to load extension {extension}.")
            await ctx.send(f'Failed to load extension {extension}')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def unload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            self.logger.info(f"Unloaded extension {extension}")
            await ctx.send(f'Unloaded extension {extension}')
        except:
            self.logger.warning(f"Failed to unload extension {extension}")
            await ctx.send(f"Failed to unload extension {extension}")

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def reload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            self.logger.info(f"Reloaded extension {extension}")
            await ctx.send(f'Reloaded extension {extension}')
        except:
            self.logger.warning(f"Reload of {extension} failed")
            await ctx.send(f"Reload of {extension} failed")

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #
    
    def cog_unload(self):
        self.logger.info("Extension admin_extensions is being unloaded!")
        self.logger.handlers = []

def setup(client):
    client.add_cog(Admin_Extensions(client))