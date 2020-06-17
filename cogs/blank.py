import discord
from discord.ext import commands

class Blank(commands.Cog, name="Blank Cog"):
    def __init__(self, client):
        self.client = client

    # @commands.Cog.listener()
    # @commands.command()

def setup(client):
    client.add_cog(Blank(client))