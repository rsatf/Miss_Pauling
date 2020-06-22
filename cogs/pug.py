import discord
from discord.ext import commands, tasks
import valve.source.a2s
import valve.rcon
import random
import logging
import os
from dotenv import load_dotenv

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
        self.client.ctx = None
        self.game_guild = int(os.getenv('PRIMARY_GUILD'))
        self.game_channel = int(os.getenv('PRIMARY_CHANNEL'))
        self.empty_slot = "(?)"
        self.game_on = False
        self.game_full = False
        self.player_count = 0
        self.max_players = 12
        self.start_delay = 10
        self.players = []
        self.game_message = None
        self.servers = eval(os.getenv('PUG_SERVERS'))
        self.passwords = eval(os.getenv('PUG_PASSWORDS'))
        self.game_server = None
        self.game_password = None
        self.rcon_password = os.getenv('RCON_PASSWORD')
        self.map_pool = eval(os.getenv('MAP_POOL'))
        self.game_map = None
        self.used_servers = []

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     channel = reaction.message.channel
    #     await channel.send(f'{user.name} added {reaction.emoji} to "{reaction.message.content}"')

    ## # # # # # # # # ##
    # Helper Decorators #
    ## # # # # # # # # ##

    ## # # # # # # #
    # Bot commands #
    ## # # # # # # #

    @commands.command(help="- Starts a pick-up game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def start(self, ctx, size=12):
        self.logger.info(f"{ctx.message.author} triggered start()")

        if ctx.message.guild.id != self.game_guild:
            await ctx.send(f'Got message from unknown guild')
            return
        
        if ctx.message.channel != self.game_channel:
            await ctx.send(f'Got message from unknown channel')
            return
        
        if self.game_on:
            await ctx.send(f'Game already on')
            return
        
        self.game_server = await self.find_server()
        if self.game_server is None:
            await ctx.send("No open servers to use, not starting")
            return
        
        if self.game_server in self.used_servers:
            self.used_servers.remove(self.game_server)
        
        self.game_on = True
        self.max_players = size
        self.game_map = random.choice(self.map_pool)
        ret = await self.game_reset(size)
        
        if ret:
            await ctx.send(f'Game started! This game will be played on map {self.game_map} and server {self.game_server[0]}:{self.game_server[1]}')
            self.game_message = await ctx.send(await self.game_status())
            await self.game_message.pin()
            await self.change_password(address=self.game_server, password="temppassword")

    @commands.command(help="- Stops an active pick-up game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def stop(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered stop()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                ret = await self.game_stop()
                if ret:
                    await ctx.send(f'Game stopped.')
            else:
                await ctx.send(f'No game active.')

    @commands.command(aliases=['re'], help="- Restarts an active pick-up game. Can take an integer argument for the size of the new pug")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def restart(self, ctx, size=0):
        self.logger.info(f"{ctx.message.author} triggered restart()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                ret = await self.game_reset(size)
                if ret:
                    await ctx.send(f'Game restarted!')
                    self.game_message = await ctx.send(await self.game_status())
                    await self.game_message.pin()
        else:
            await ctx.send(f'No game active')

    @commands.command(help="- Checks the status of an active pick-up game")
    async def status(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered status()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                await ctx.send(await self.game_status())
            else:
                await ctx.send(f'No game on')

    @commands.command(help="- Adds yourself to an active pick-up game")
    @commands.has_any_role('player')
    async def add(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered add()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                if not self.game_full:
                    ret = await self.player_add(ctx.message.author)
                    if ret:
                        await self.game_update_pin()
                        await self.status(ctx)
                        await self.game_start(ctx)
                    else:
                        await ctx.send(f'Already added')
                else:
                    await ctx.send(f'Game is full')
            else:
                await ctx.send(f'No game on')

    @commands.command(aliases=['rem'], help="- Removes yourself from an active pick-up game")
    async def remove(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered remove()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                ret = await self.player_remove(ctx.message.author)
                if ret:
                    await self.game_update_pin()
                    await self.status(ctx)
                else:
                    await ctx.send(f'Not added')
            else:
                await ctx.send(f'No game on')

    @commands.command(aliases=['kp'], hidden=True)
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def kickplayer(self, ctx, member : discord.Member):
        self.logger.info(f"{ctx.message.author} triggered kickplayer()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if self.game_on:
                ret = await self.player_remove(member.mention)
                if ret:
                    await self.game_update_pin()
                    await self.status(ctx)
                else:
                    await ctx.send(f'Player not added')
            else:
                await ctx.send(f'No game on')

    @commands.command(help="- Changes the map of the active game")
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def map(self, ctx, map):
        self.logger.info(f"{ctx.message.author} triggered map()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            if map in self.map_pool:
                self.game_map = map
                await ctx.send(f"Map changed to {self.game_map}")
                await ctx.send(await self.game_status())
            else:
                await ctx.send(f"Invalid map name, !maps to see valid maps.")

    @commands.command(help="- Lists the maps in the map pool")
    @commands.has_any_role('player')
    async def maps(self, ctx):
        self.logger.info(f"{ctx.message.author} triggered maps()")
        if ctx.message.guild.id == self.game_guild and ctx.message.channel.id == self.game_channel:
            await ctx.send(f"Map pool: {', '.join(self.map_pool)}")

    ## # # # # # # # #
    # Game functions #
    ## # # # # # # # #

    async def game_status(self):
        lineup = []
        empty = []
        for player in self.players:
            if player != self.empty_slot:
                lineup.append(player.name)
            else:
                empty.append(player)
        return f'({self.game_map}) Players [{self.player_count}/{self.max_players}]: {", ".join(lineup + empty)}'

    async def game_reset(self, size=0):
        if self.game_on:
            if self.game_message:
                await self.game_message.unpin()
            if size:
                self.max_players = size
            self.game_full = False
            self.player_count = 0
            self.players = [self.empty_slot for x in range(self.max_players)]
            return True
        else:
            return False
    
    async def game_stop(self):
        if self.game_on:
            self.game_on = False
            self.player_count = 0
            self.max_players = 12
            self.players = []
            self.game_server = None
            await self.game_message.unpin()
            return True
        else:
            return False

    async def game_start(self, ctx):
        if self.player_count == self.max_players:
            self.game_full = True
            await ctx.send('Game is full. Waiting 60 seconds before game starts.')
            self.client.ctx = ctx
            self.game_countdown.start()

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

    async def change_password(self, address, password=None):
        if password is None:
            self.game_password = random.choice(self.passwords)
            command = f"sv_password {self.game_password}"
            valve.rcon.execute(address, self.rcon_password, command)
        else:
            command = f"sv_password {password}"
            valve.rcon.execute(address, self.rcon_password, command)

    async def game_update_pin(self):
        await self.game_message.edit(content=(await self.game_status()))

    ## # # # # # # # # #
    # Player functions #
    ## # # # # # # # # #

    async def player_add(self, player):
        if player not in self.players:
            for index, slot in enumerate(self.players):
                if slot == self.empty_slot:
                    self.players[index] = player
                    self.player_count += 1
                    break
            if self.player_count == self.max_players:
                self.game_full = True
            return True
        else:
            return False

    async def player_remove(self, player):
        if player in self.players:
            self.players.remove(player)
            new_list = []
            for slot in self.players:
                if slot != self.empty_slot:
                    new_list.append(slot)
            while len(new_list) < self.max_players:
                new_list.append(self.empty_slot)
            self.players = new_list
            self.player_count -= 1
            if self.player_count < self.max_players:
                self.game_full = False
            return True
        else:
            return False

    ## # # # # # # # #
    # Loop functions #
    ## # # # # # # # #

    @tasks.loop(seconds=1, count=60)
    async def game_countdown(self):
        if not self.game_full:
            self.logger.info("Game is no longer full, cancelling.")
            self.game_countdown.cancel()
        else:
            self.logger.info("Game is still full, continuing countdown")

    @game_countdown.after_loop
    async def game_countdown_decision(self):
        self.logger.info("Reached game_countdown_decision")
        if self.game_countdown.is_being_cancelled():
            await self.client.ctx.send('No longer full, cancelling countdown')
        else:
            await self.client.ctx.send(f'Game commencing! PM\'ing connection details to all players')
            valve.rcon.execute(self.game_server, self.rcon_password, f"changelevel {self.game_map}")
            await self.change_password(address=self.game_server)
            for player in self.players:
                await player.send(f'Your Pick-up Game is ready. Please connect to steam://connect/{self.game_server[0]}:{self.game_server[1]}/{self.game_password}')
                lineup = await self.game_status()
                await player.send(f'{lineup}')
                self.used_servers.append(self.game_server)
                self.reset_password.restart()
            await self.game_stop()
            
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
                        else:
                            self.logger.info(f"Server {server} still in use, not changing password")
                except valve.source.NoResponseError:
                    self.logger.warn(f"Could not connect to {address}")
                    pass

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #

    def cog_unload(self):
        self.logger.info("Extension pug is being unloaded!")
        self.logger.handlers = []
        self.reset_password.cancel()

def setup(client):
    client.add_cog(PUG(client))
