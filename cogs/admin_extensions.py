import discord
from discord.ext import commands

class Admin_Extensions(commands.Cog, name="Extensions"):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Extension {extension} loaded')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Extension {extension} loaded')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def reload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Extension {extension} reloaded')

def setup(client):
    client.add_cog(Admin_Extensions(client))