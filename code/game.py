import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from time import sleep
from random import randint, choice

from .lista_de_perguntas import perguntas
               

def check_partida():
    # Verifica o conteudo do arquivo "partidas" e retorna o valor (se for 1 o jogo já foi iniciado por alguem, se for 0 não tem nenhum jogo acontecendo)
    f = open("partida", "r")
    content = f.read()
    return int(content)

def end_game():
    # Finaliza o game, altera o valor no arquivo "partidas" para 0
    f = open("partida", "w")
    f.write("0")
    f.close()

def start_game():
    # Inicia um game, altera o valor no arquivo "partidas" para 1
    f = open("partida", "w")
    f.write("1")
    f.close()

class Game(commands.Cog):

    def __init__(self, bot, game=False):
        self.bot = bot
    

    @commands.command(name="start", aliases=["estudar"])
    async def start(self, ctx, *, arg="geral"):
        try:
            # n é usado como contador, para saber o numero de perguntas já feitas na partida
            n = 0

            # checando se já tem alguma partida acontecendo, se tiver ele avisa que o jogo já começou, se não, ele inicia um
            partida_iniciada = check_partida()
            if partida_iniciada > 0:
                await ctx.send("A partida já começou")
            else:

                # iniciando um novo jogo
                start_game()

                # lista vazia que vai conter as perguntas do tema escolhido
                lista = []

                # se não houver um arg(argumento) na hora de iniciar ele pega todas as perguntas sem filtrar
                if arg.lower() == "geral":
                    lista = list(perguntas.keys())
                
                # possivel filtro de perguntas "matematica" entao ele verifica e so adiciona as perguntas desse tema
                elif arg.lower() == "matematica":
                    # passa por TODAS as perguntas da lista de perguntas, se a materia dela for a do filtro ele adiciona na nova lista
                    for i in perguntas:
                        if perguntas[i]["materia"] == "matematica":
                            lista.append(i)
                elif arg.lower() == "emprendedorismo":
                    for i in perguntas:
                        if perguntas[i]["materia"] == "emprendedorismo":
                            lista.append(i)
                else:
                    # se a pessoa passar um tema que não existe ele avisa, e finaliza o jogo
                    await ctx.send("Tema não encontrado.")
                    end_game()
                    return

                # Se a quantidade de itens na lista for menor q 1. Ele avisa que esse tema nao possui perguntas ainda e finaliza.
                if len(lista) < 1:
                    await ctx.send("Esse tema ainda não possui perguntas...")
                    end_game()
                    return

                # loop infinito, para sempre gerar novas perguntas, a medida que elas forem sendo respondidas
                while True:
                    
                    # aumentando o número do contador de perguntas feitas, sempre vai somando de 1 em 1
                    n +=1

                    # pega na lista de perguntas uma pergunta aleatoria
                    pergunta = lista[randint(0, len(lista)-1)]

                    # cria a msg que vai ser enviada, com o numero da pergunta, a pergunta, e o tempo para responder
                    embed_pergunta = discord.Embed(title=f'Pergunta #{n}', description=" ")
                    embed_pergunta.set_image(url=perguntas[pergunta]["pergunta"])
                    tempo = perguntas[pergunta]["tempo"]
                    embed_pergunta.set_footer(text=f"Você tem {tempo}s")
                    await ctx.send(embed=embed_pergunta)

                    # função que verifica se a resposta esta correta e retorna o conteudo, caso contrario nao faz nada
                    def check(msg):
                        response = msg.content
                        try:
                            response = response.lower()
                        except:
                            pass
                        if response in perguntas[pergunta]["resposta"]:
                            return msg.content

                    # loop infinito para pegar todas as respostas que forem enviadas
                    while True:

                        # pega TODAS msg enviadas por TODOS usuarios no periodo de tempo referente a pergunta, e usa a funcao check
                        response = await self.bot.wait_for("message", check=check, timeout=perguntas[pergunta]["tempo"])

                        # Se for a resposta correta vai ter um retorno do check, e envia a msg avisando que acertou
                        # também avisa que a proxima pergunta esta por vir, quebrando o loop inifinto(break) pois a pergunta foi acertada
                        if response.content in perguntas[pergunta]["resposta"]:
                            embed_acerto = discord.Embed(title="Acertou :tada: :tada: :tada:", description=f"A resposta era {response.content}\n", colour=0x00FF00)
                            embed_acerto.set_footer(text="Próxima pergunta em 5s...")
                            await ctx.send(embed=embed_acerto)
                            sleep(5)
                            break
        
        # ao exceder o tempo de resposta, entra aqui, finaliza o game, e envia a resposta da tal pergunta
        except asyncio.TimeoutError:
            resposta = perguntas[pergunta]["resposta"][0]
            embed_fim = discord.Embed(title="Game Over.", description=f"A resposta era: {resposta}\nFim de jogo.", colour=0xFF0000)
            await ctx.send(embed=embed_fim)
            end_game()
            return 




def setup(bot):
    """Load Game Cog."""
    bot.add_cog(Game(bot))
