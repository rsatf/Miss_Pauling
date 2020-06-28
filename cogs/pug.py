# pylint: disable=no-member
# pylint: disable=E1101
import logging
import os
import random
import sys
import discord
import asyncio
import valve.rcon
import valve.source.a2s
from discord.ext import commands, tasks
from dotenv import load_dotenv

from cogs.bin.pickup import (Game, GameFullError, GameNotOnError, GameOnError,
                             PlayerAddedError, PlayerNotAddedError,
                             TeamFullError)
from cogs.bin.player import Player

class Timer():

    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    logger = logging.getLogger('timer')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    def __init__(self, game, chan):
        self.game = game
        self.chan = chan
        self.loop = asyncio.get_event_loop()

    def __del__(self):
        self.logger.info("Reference to object Timer being deleted!")
        self.logger.handlers = []

    async def start_countdown(self):
        await self.loop.create_task(self.countdown())

    async def countdown(self):
        context = self.game.chaninfo[self.chan]
        count = 10
        while count and context['game_full']:
            self.logger.info(f'{self.chan}: Game is still full. Checks remaining: {count}')
            count -= 1
            await asyncio.sleep(1)

        # Make a copy here so a !remove doesn't cause our for-loop up ahead to fail due to the data structure changing during the loop
        # player_list = [x for x in context['added_players'].values()]

        if not context['game_full']:
            self.logger.info(f'{self.chan}: Game no longer full')

        if context['game_full']:
            self.logger.info(f'Game commencing')
            self.game.reset_password.restart()
            await context['ctx'].send('Game commencing! PM\'ing connection details to all players')
            context['game'].stop()
            valve.rcon.execute(context['game_server'], self.game.rcon_password, f"changelevel {context['game_map']}")
            context['game_password'] = random.choice(self.game.passwords)
            connect_string = f'Your Pick-up Game is ready. Please connect to steam://connect/{context["game_server"][0]}:{context["game_server"][1]}/{context["game_password"]}'
            for player in context['added_players'].values():
                await player.player.send(connect_string)
            await self.game.change_password(address=context['game_server'], password=f'{context["game_password"]}')
            self.game.used_servers.append(context['game_server'])
            # context['game'].stop()
            await context['game_message'].unpin()
            context['added_players'] = {}
            await self.loop.create_task(self.server_readd())

    async def server_readd(self):
        context = self.game.chaninfo[self.chan]
        await asyncio.sleep(10)
        self.logger.info(f'Adding {context["game_server"]} back to to server pool')
        self.game.used_servers.remove(context["game_server"])
        self.game.servers.append(context["game_server"])

class PUG(commands.Cog, name="Pick-up Game"):

    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    logger = logging.getLogger('pug')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    def __init__(self, client):
        load_dotenv()
        self.reset_password.start()
        self.client = client
        self.game_guild = int(os.getenv('PRIMARY_GUILD'))
        self.servers = eval(os.getenv('PUG_SERVERS'))
        self.passwords = eval(os.getenv('PUG_PASSWORDS'))
        self.rcon_password = os.getenv('RCON_PASSWORD')
        self.map_pool = eval(os.getenv('MAP_POOL'))
        self.used_servers = []
        self.channels = eval(os.getenv('PUG_CHANNELS'))
        self.chaninfo = {}
        self.pug_init()

    def __del__(self):
        self.logger.info("Reference to object Pug being deleted!")
        self.logger.handlers = []

    def pug_init(self):
        for channel in self.channels:
            self.chaninfo[channel] = {}
            self.chaninfo[channel]['ctx'] = None
            self.chaninfo[channel]['game_full'] = False
            self.chaninfo[channel]['game_message'] = None
            self.chaninfo[channel]['game_server'] = None
            self.chaninfo[channel]['game_password'] = None
            self.chaninfo[channel]['game_map'] = None
            self.chaninfo[channel]['player_count'] = 0
            self.chaninfo[channel]['added_players'] = {}
            game = Game(2, 6)
            self.chaninfo[channel]['game'] = game
            timer = Timer(self, channel)
            self.chaninfo[channel]['timer'] = timer

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     channel = reaction.message.channel
    #     await channel.send(f'{user.name} added {reaction.emoji} to "{reaction.message.content}"')

    @commands.command(help="- Starts a pick-up game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def start(self, ctx, teams=1, mode=12):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered start()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if context['game'].game_on:
            await ctx.send(f'Game already on')
            return

        if not context['game'].game_on:
            context['game_server'] = await self.find_server()

            if context['game_server'] is None:
                await ctx.send("No open servers to use, not starting.")
                return

            if context['game_server'] in self.used_servers:
                self.used_servers.remove(context['game_server'])

            if context['game_server'] is not None:
                self.servers.remove(context['game_server'])

            context['game_map'] = random.choice(self.map_pool)
            try:
                context['game'].start(teams, mode)
            except GameOnError as e:
                await ctx.send(f'{e}')
                return

            await ctx.send(f'Game started! This game will be played on {context["game_server"][0]}:{context["game_server"][1]}')
            context['game_message'] = await ctx.send(f'```({context["game_map"]}) {context["game"].status()}```')
            await context['game_message'].pin()
            await self.change_password(address=context['game_server'], password="temppassword")
        return

    @commands.command(help="- Stops an active pick-up game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def stop(self, ctx):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered stop()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if not context['game'].game_on:
            await ctx.send(f'No game on.')
            return

        if context['game'].game_on:
            try:
                context['game'].stop()
            except (GameOnError, GameNotOnError) as e:
                await ctx.send(f'{e}')
                return
            await context['game_message'].unpin()
            await ctx.send("Game stopped.")
            self.servers.append(context['game_server'])
            context['game_server'] = None
            context['added_players'] = {}
            context['game_full'] = False
            context['player_count'] = 0
            await context['game_message'].edit(content=f'```Game cancelled.```')
        return

    @commands.command(help="- Checks the status of an active pick-up game")
    async def status(self, ctx):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered status()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if not context['game'].game_on:
            await ctx.send(f'No game on.')
            return

        if context['game'].game_on:
            status = f'```({context["game_map"]}) {context["game"].status()}```'
            await ctx.send(status)
        return

    @commands.command(help="- Adds yourself to an active pick-up game")
    @commands.has_any_role('player')
    async def add(self, ctx):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered add()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if not context['game'].game_on:
            await ctx.send(f'No game on.')
            return

        if ctx.message.author.id in context['added_players'].keys():
            await ctx.send(f'Already added.')
            return

        for _, value in self.chaninfo.items():
            if ctx.message.author.id in value['added_players'].keys():
                await ctx.send(f'Already added elsewhere.')
                return

        player = Player(ctx.message.author, 0)

        try:
            context['added_players'][ctx.message.author.id] = player
            context['game'].add(context['added_players'][ctx.message.author.id])
        except (PlayerAddedError, GameFullError, TeamFullError) as e:
            del context['added_players'][ctx.message.author.id]
            await ctx.send(f'{e}')
            return
        
        await self.game_update_pin(ctx.channel.id)
        context['player_count'] += 1
        await self.status(ctx)
        await self.game_start(ctx, context)
        return

    @commands.command(aliases=['rem'], help="- Removes yourself from an active pick-up game")
    async def remove(self, ctx):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered remove()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if not context['game'].game_on:
            await ctx.send(f'No game on')

        if ctx.message.author.id not in context['added_players'].keys():
            await ctx.send(f'Not added.')
            return    

        if context['game'].game_on:
            try:
                context['game'].remove(context['added_players'][ctx.message.author.id])
                del context['added_players'][ctx.message.author.id]
            except (GameNotOnError, PlayerNotAddedError) as e:
                await ctx.send(f'{e}')
                return

        if context['game_full']:
            context['game_full'] = False

        context['player_count'] -= 1
        await self.game_update_pin(ctx.channel.id)
        await self.status(ctx)
        return

    @commands.command(aliases=['pk'], hidden=True)
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def playerkick(self, ctx, member : discord.Member):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered playerkick()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if not context['game'].game_on:
            await ctx.send(f'No game on')
        
        if member.id not in context['added_players'].keys():
            await ctx.send(f'Player not added.')
            return  

        if context['game'].game_on:
            try:
                context['game'].remove(context['added_players'][member.id])
                del context['added_players'][member.id]
                await self.game_update_pin(ctx.channel.id)
                await self.status(ctx)
            except (GameNotOnError, PlayerNotAddedError) as e:
                await ctx.send(f'{e}')
                return

    @commands.command(help="- Changes the map of the active game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def map(self, ctx, map):
        context = self.chaninfo[ctx.channel.id]
        self.logger.info(f"{ctx.message.author} triggered map()")

        if ctx.message.guild.id != self.game_guild:
            return
            
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        if map in self.map_pool:
            context['game_map'] = map
            await ctx.send(f"Map changed to {context['game_map']}")
            await self.status(ctx)
        else:
            await ctx.send(f"Invalid map name, !maps to see valid maps.")

    @commands.command(help="- Lists the maps in the map pool")
    @commands.has_any_role('player')
    async def maps(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered maps()")

        if ctx.message.guild.id != self.game_guild:
            return
        
        if ctx.message.channel.id not in self.chaninfo.keys():
            return

        await ctx.send(f"Map pool: {', '.join(self.map_pool)}")
        return

    async def game_start(self, ctx, context):
        if context['player_count'] >= context['game'].max_players:
            context['game_full'] = True
            await ctx.send('Game is full. Waiting 60 seconds before game starts.')
            context['ctx'] = ctx
            await context['timer'].start_countdown()

    async def find_server(self):
        self.logger.info("Looking for an open server")
        for address in self.servers:
            try:
                with valve.source.a2s.ServerQuerier(address) as server:
                    server_name = server.info()["server_name"]
                    player_count = server.info()["player_count"]
                    self.logger.info(f"Server {server_name} has {player_count} players")
                    if player_count < 1:
                        return (server.host, server.port)
            except valve.source.NoResponseError:
                self.logger.warning(f"Could not query server {address} to see if it is open")
                pass

    async def change_password(self, address, password):
        command = f"sv_password {password}"
        valve.rcon.execute(address, self.rcon_password, command)

    async def game_update_pin(self, chan):
        context = self.chaninfo[chan]
        await context['game_message'].edit(content=(f'```({context["game_map"]}) {context["game"].status()}```'))

    @tasks.loop(seconds=600)
    async def reset_password(self):
        self.logger.info("Checking for a server password to reset")
        if self.used_servers:
            for address in self.used_servers:
                self.logger.info(f"Trying to reset password for server {address}")
                try:
                    with valve.source.a2s.ServerQuerier(address) as server:
                        player_count = server.info()["player_count"]
                        server_name = server.info()["server_name"]
                        if player_count < 1:
                            self.logger.info(f"Changing sv_password of server {server_name}")
                            valve.rcon.execute(address, self.rcon_password, "sv_password wedontreallycare")
                            self.used_servers.remove(address)
                            self.servers.append(address)
                        else:
                            self.logger.info(f"Server {server} still in use, not changing password")
                except valve.source.NoResponseError:
                    self.logger.warn(f"Could not connect to {address}")
                    pass

    def cog_unload(self):
        self.logger.info("Extension pug is being unloaded!")
        self.logger.handlers = []
        self.reset_password.cancel()
        del self.chaninfo

def setup(client):
    client.add_cog(PUG(client))