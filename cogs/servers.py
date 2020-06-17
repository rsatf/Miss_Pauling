import sys
import discord
from discord.ext import commands
import valve.source.a2s

class Servers(commands.Cog, name="Servers"):
    def __init__(self, client):
        self.client = client

    # @commands.Cog.listener()
    # @commands.command()

    def server_query(self, serv_addr):
        d = {}
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
        
    # @bot.group()
    # async def git(ctx):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send('Invalid git command passed...')

    # @git.command()
    # async def push(ctx, remote: str, branch: str):
    #     await ctx.send('Pushing to {} {}'.format(remote, branch))

    @commands.command()
    async def servers(self, ctx):
        
        serv_addr_list = [
            ('cpt.rsa.tf', 27015),
            ('cpt2.rsa.tf', 27015),
            ('jhb1.rsa.tf', 27015),
            ('jhb1.rsa.tf', 27025),
            ('jhb1.rsa.tf', 27035)
        ]
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )
        embed.set_footer(text="rsa.tf")
        embed.set_author(name="Servers", icon_url="https://rsa.tf/img/fist-s.jpg")
        for addr in serv_addr_list:
            serv_info = self.server_query(addr)
            if len(serv_info["players"]) == 0:
                serv_info["players"] = " "
            embed.add_field(
                name=f'({addr[0]}:{addr[1]}) {serv_info["name"]}',
                value=f'({serv_info["player_count"]}/{serv_info["max_players"]}) {serv_info["map"]}\n \
                    Players: ```{", ".join(serv_info["players"])}```',
                inline=False)
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Servers(client))