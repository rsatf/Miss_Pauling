import discord
from discord.ext import commands, tasks

class PUG(commands.Cog, name="Pick-up Game"):
    def __init__(self, client):
        self.client = client
        self.empty_slot = "(?)"
        self.game_on = False
        self.game_full = False
        self.player_count = 0
        self.max_players = 12
        self.start_delay = 10
        self.players = []
        self.game_message = ""
        self.servers = [('jhb1.rsa.tf', 27035), ('jhb1.rsa.tf', 27025)]
        self.passwords = ['games', 'apples']

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

    @commands.command()
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def start(self, ctx, size=12):
        if not self.game_on:
            self.game_on = True
            self.max_players = size
            ret = await self.game_reset(size)
            if ret:
                await ctx.send(f'Game started!')
                self.game_message = await ctx.send(await self.game_status())
                await self.game_message.pin()
        else:
            await ctx.send(f'Game already on')

    @commands.command()
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def stop(self, ctx):
        if self.game_on:
            ret = await self.game_stop()
            if ret:
                await ctx.send(f'Game stopped')
        else:
            await ctx.send(f'No game active')

    @commands.command()
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def restart(self, ctx, size=0):
        if self.game_on:
            ret = await self.game_reset(size)
            if ret:
                await ctx.send(f'Game restarted!')
                self.game_message = await ctx.send(await self.game_status())
                await self.game_message.pin()
        else:
            await ctx.send(f'No game active')

    @commands.command()
    async def status(self, ctx):
        if self.game_on:
            await ctx.send(await self.game_status())
        else:
            await ctx.send(f'No game on')

    @commands.command()
    @commands.has_any_role('player')
    async def add(self, ctx):
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

    @commands.command()
    async def remove(self, ctx):
        if self.game_on:
            ret = await self.player_remove(ctx.message.author)
            if ret:
                await self.game_update_pin()
                await self.status(ctx)
            else:
                await ctx.send(f'Not added')
        else:
            await ctx.send(f'No game on')

    @commands.command()
    @commands.has_any_role('admin', 'pug-admin', 'captain')
    async def kickplayer(self, ctx, member : discord.Member):
        if self.game_on:
            ret = await self.player_remove(member.mention)
            if ret:
                await self.game_update_pin()
                await self.status(ctx)
            else:
                await ctx.send(f'Player not added')
        else:
            await ctx.send(f'No game on')

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
        return f'Players [{self.player_count}/{self.max_players}]: {", ".join(lineup + empty)}'

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
            await self.game_message.unpin()
            return True
        else:
            return False

    async def game_start(self, ctx):
        if self.player_count == self.max_players:
            self.game_full = True
            await ctx.send(f'Game is full! PM\'ing connection details to all players')
            for player in self.players:
                await player.send(f'Your Pick-up Game is ready. Please connect to steam://connect/{self.servers[0][0]}:{self.servers[0][1]}/{self.passwords[0]}')
                lineup = await self.game_status()
                await player.send(f'{lineup}')
            await self.game_stop()
    
    # @tasks.loop(seconds=1, count=10)
    # async def game_countdown(self):
    #     if not self.game_full:
    #         print("not full")
    #         self.game_countdown.cancel()
    #         return False
    #     else:
    #         print("game full")

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

def setup(client):
    client.add_cog(PUG(client))