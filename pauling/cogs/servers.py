import sys
import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import aiohttp
import aioquery


class Servers(commands.Cog, name="Servers"):

    logger = logging.getLogger(__name__)

    def __init__(self, client):
        load_dotenv()
        self.client = client

    @commands.group(invoke_without_command=True)
    async def servers(self, ctx):
        await self.comp(ctx)
        await self.pub(ctx)

    @servers.command()
    async def comp(self, ctx):
        serv_addr_list = eval(os.getenv('PUG_SERVERS'))
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )
        embed.set_footer(text="rsa.tf")
        embed.set_author(name="rsa.tf servers", icon_url="https://rsa.tf/img/fist-s.jpg")
        servers_with_players = 0
        for addr in serv_addr_list:
            serv_info = await self.comp_query(addr)
            if not serv_info:
                continue

            if len(serv_info["players"]) == 0:
                continue
                
            servers_with_players += 1
            embed.add_field(
                name=f'{serv_info["name"]}\n \
                    Server: {addr[0]}:{addr[1]}\n \
                    SourceTV: {addr[0]}:{addr[1] + 5}',
                value=f'({serv_info["player_count"]}/{serv_info["max_players"]}) {serv_info["map"]}\n \
                    Players: ```{", ".join(serv_info["players"])}```',
                inline=False)
        if servers_with_players !=  0:
            await ctx.send(embed=embed)
        else:
            await ctx.send("No activity on rsa.tf servers")

    @servers.command()
    async def pub(self, ctx):
        res = await self.pub_query('https://api.battlemetrics.com/servers?sort=rank&fields[server]=name,players,maxPlayers,details&relations[server]=player,game,serverGroup&filter[game]=tf2&filter[countries][0]=ZA&filter[status]=online&filter[players][min]=1')
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )
        embed.set_footer(text="rsa.tf")
        embed.set_author(name="pub servers", icon_url="https://rsa.tf/img/fist-s.jpg")
        for server in res['data']:
            if 'rsa.tf' in server['attributes']['name']:
                continue
            embed.add_field(
                name=f"{server['attributes']['name']}",
                value=f'({server["attributes"]["players"]}/{server["attributes"]["maxPlayers"]}) {server["attributes"]["details"]["map"]}',
                inline=False
            )
        await ctx.send(embed=embed)

    async def comp_query(self, addr):
        query = aioquery.client(addr[0], addr[1], timeout=1)
        info = await query.info()
        players = await query.players()
        all_players = []
        if info and players:
            for player in players:
                all_players.append(player['name'])
            d = {}
            d['name'] = info['hostname']
            d['map'] = info['map']
            d['player_count'] = info['players']
            d['max_players'] = info['max_players']
            d['players'] = all_players
            return d

    # async def comp_query(self, serv_addr):
    #     d = {}
    #     try:
    #         with valve.source.a2s.ServerQuerier(serv_addr) as server:
    #             d['name'] = server.info()["server_name"]
    #             d['map'] = server.info()["map"]
    #             d['player_count'] = server.info()["player_count"]
    #             d['max_players'] = server.info()["max_players"]

    #             players = []
    #             for player in server.players()['players']:
    #                 players.append(player['name'])
    #             d['players'] = players
    #         return d
    #     except valve.source.NoResponseError as e:
    #         raise e

    async def pub_query(self, url) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return data

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #
    
    def cog_unload(self):
        self.logger.info("Extension servers is being unloaded!")
        self.logger.handlers = []

def setup(client):
    client.add_cog(Servers(client))