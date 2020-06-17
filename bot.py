import discord
from discord.ext import commands, tasks
import os
# from dotenv import load_dotenv
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN')
# GUILD = os.getenv('GUILD_PRIMARY')

TOKEN = "NzE0NzU2NDEwNjQyMDA2MDY3.XuTI7g.uJjlTdzhDSFopMWjKw-Noms_HPg"
GUILD = "##"

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('!help'))
    print("Bot is online.")

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

# @ping.error
# async def ping_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(f'Error in ping command')

if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        try:
            if filename.endswith('.py'):
                client.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load file {} as extension \n{}'.format(filename, exc))

    client.run(TOKEN)