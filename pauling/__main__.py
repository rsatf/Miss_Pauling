import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

from pauling.bot import Bot

pauling = Bot(
    command_prefix="!",
    activity=discord.Game('!help'),
    case_insensitive=True
)

pauling.load_extension("pauling.cogs.pug")
pauling.load_extension("pauling.cogs.servers")
pauling.load_extension("pauling.cogs.admin_extensions")
pauling.load_extension("pauling.cogs.admin_users")

pauling.run(TOKEN)