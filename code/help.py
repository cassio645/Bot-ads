import discord
from discord.ext import commands
from discord.ext.commands import cooldown,BucketType

class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["info", "ajuda"])
    @cooldown(1, 3, BucketType.channel)
    async def help(self, ctx):
        comandos_embed = discord.Embed(title="Bot de estudos", description="Bot criado com a finalidade de ajudar nos seus estudos.", colour=0x4682B4)
        comandos_embed.add_field(name="Como usar", value="Basta utilizar o comando `.estudar` ou\n`.estudar matematica`\n`.estudar empreendedorismo`\n\nQue o bot começa a enviar perguntas\n\n**Dicas**\n• Pegue papel e caneta para resolver possíveis contas.\n• Para representar frações utilize 2/3 como ⅔\n• Para representar potências utilize 5^2 como 5²\n\n")
        comandos_embed.add_field(name="Código do bot", value="https://github.com/cassio645/Bot-ads/blob/main/code/game.py", inline=False)
        comandos_embed.set_footer(text="Criado por @CASSIO645#3477")
        await ctx.send(embed=comandos_embed)


def setup(bot):
	bot.add_cog(HelpCog(bot))