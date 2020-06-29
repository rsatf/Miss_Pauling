import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import logging
import traceback

log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('!help'))
    logger.info("Bot is online.")

@client.command(help="- Just checks the bot is still alive")
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
                logger.info(f"Loaded extension {filename}")
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logger.warning(f"Failed to load file {filename} as extension\n{exc}")
            logger.warning(traceback.format_exc())
            logger.warning(f'{e}')

    client.run(TOKEN)