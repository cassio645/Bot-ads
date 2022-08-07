import os
from decouple import config
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents, strip_after_prefix=True)
bot.remove_command('help')

bot.load_extension("manager")
bot.load_extension("code.game")


TOKEN = config("TOKEN")

bot.run(TOKEN)