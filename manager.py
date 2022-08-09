import discord
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument, CommandOnCooldown, BadArgument, MissingPermissions
from discord.ext import commands


class Manager(commands.Cog):
    """Manage the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game(name='| Digite .info', type=3)
        # VERDE Status.online / AMARELO Status.idle/ VERMELHO Status.dnd
        await self.bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"{self.bot.user} is alive")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            pass
        elif isinstance(error, CommandNotFound):
            pass
        elif isinstance(error, CommandOnCooldown):
            pass
        elif isinstance(error, BadArgument):
            pass
        else:
            raise error




def setup(bot):
    bot.add_cog(Manager(bot))