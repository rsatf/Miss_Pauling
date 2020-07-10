import discord
from discord.ext import commands
import logging

class Admin_Users(commands.Cog, name="Users"):

    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    logger = logging.getLogger('admin_users')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.logger.info(f'{member} has joined the server')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.logger.info(f'{member} has left the server')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        self.logger.info(f"{ctx.channel.name}: {ctx.message.author} triggered kick()")
        await member.kick(reason=reason)
        await ctx.send(f'Kicked user {member.mention}')
        self.logger.info(f'Kicked user {member.mention}')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        self.logger.info(f"{ctx.channel.name}: {ctx.message.author} triggered ban()")
        await member.ban(reason=reason)
        await ctx.send(f'Banned user {member.mention}')
        self.logger.info(f'Banned user {member.mention}')

    @commands.command(hidden=True)
    @commands.has_any_role('admin')
    async def unban(self, ctx, *, member: discord.Member):
        self.logger.info(f"{ctx.channel.name}: {ctx.message.author} triggered unban()")
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.descriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned user {member.mention}')
                self.logger.info(f'Unbanned user {member.mention}')
                return

    ## # # # # # # # # # # # #
    # Cleanup when unloading #
    ## # # # # # # # # # # # #
    
    def cog_unload(self):
        self.logger.info("Extension admin_users is being unloaded!")
        self.logger.handlers = []

def setup(client):
    client.add_cog(Admin_Users(client))