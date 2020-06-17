import discord
from discord.ext import commands

class Admin_Users(commands.Cog, name="Users"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined the server')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'{member} has left the server')

    @commands.command()
    # async def kick(self, ctx, member : Discord.Member, *, reason=None):
    async def kick(self, ctx, member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'Kicked user {member.mention}')

    @commands.command()
    # async def ban(self, ctx, member : Discord.Member, *, reason=None):
    async def ban(self, ctx, member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned user {member.mention}')

    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.descriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned user {member.mention}')
                return

def setup(client):
    client.add_cog(Admin_Users(client))