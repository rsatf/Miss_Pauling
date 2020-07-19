import sys
import discord
from discord.ext import commands
import valve.source.a2s
import logging
import os
from dotenv import load_dotenv

class Servers(commands.Cog, name="Servers"):

    logger = logging.getLogger(__name__)

    def __init__(self, client):
        load_dotenv()
        self.client = client

    # @commands.Cog.listener()
    # @commands.command()

    async def server_query(self, serv_addr):
        d = {}
        try:
            with valve.source.a2s.ServerQuerier(serv_addr) as server:
                d['name'] = server.info()["server_name"]
                d['map'] = server.info()["map"]
                d['player_count'] = server.info()["player_count"]
                d['max_players'] = server.info()["max_players"]

                players = []
                for player in server.players()['players']:
                    players.append(player['name'])
                d['players'] = players
            return d
        except valve.source.NoResponseError as e:
            raise e

        
    # @bot.group()
    # async def git(ctx):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send('Invalid git command passed...')

    # @git.command()
    # async def push(ctx, remote: str, branch: str):
    #     await ctx.send('Pushing to {} {}'.format(remote, branch))

    @commands.command(help="- Lists rsa.tf servers that have players on them")
    async def servers(self, ctx):
        self.logger.info(f"{ctx.channel.name}: {ctx.message.author} triggered servers()")
        
        serv_addr_list = eval(os.getenv('PUG_SERVERS'))
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )
        embed.set_footer(text="rsa.tf")
        embed.set_author(name="Servers", icon_url="https://rsa.tf/img/fist-s.jpg")
        servers_with_players = 0
        for addr in serv_addr_list:
            try:
                serv_info = await self.server_query(addr)
                if len(serv_info["players"]) == 0:
                    break
                servers_with_players += 1
                embed.add_field(
                    name=f'({addr[0]}:{addr[1]}) {serv_info["name"]}',
                    value=f'({serv_info["player_count"]}/{serv_info["max_players"]}) {serv_info["map"]}\n \
                        Players: ```{", ".join(serv_info["players"])}```',
                    inline=False)
            except valve.source.NoResponseError:
                pass
        if servers_with_players !=  0:
            await ctx.send(embed=embed)
        else:
            await ctx.send("No activity on rsa.tf servers")

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #
    
    def cog_unload(self):
        self.logger.info("Extension servers is being unloaded!")
        self.logger.handlers = []

def setup(client):
    client.add_cog(Servers(client))