import discord
import asyncio
import json
from discord.ext import commands
from time import sleep, strftime, gmtime
from random import shuffle, randint

from .lista_de_perguntas import perguntas
               
def check_partida(channel_id):
    # Verifica o conteudo do arquivo "partidas" e retorna o valor (se for 1 o jogo já foi iniciado por alguem, se for 0 não tem nenhum jogo acontecendo)
    f = open('partida.json')
    data = json.load(f)
    for i in data:
        if i == channel_id:
            return data[i]


def end_game(channel_id):
    # Finaliza o game, altera o valor no arquivo "partidas" para 0
    f = open("partida.json", "r")
    data = json.load(f)
    for i in data:
        if i == channel_id:
            data[i] = 0

    with open("partida.json", "w") as outfile:
        json.dump(data, outfile)


def start_game(channel_id):
    # Inicia um game, altera o valor no arquivo "partidas" para 1
    f = open("partida.json", "r")
    data = json.load(f)
    for i in data:
        if i == channel_id:
            data[i] = 1

    with open("partida.json", "w") as outfile:
        json.dump(data, outfile)


def pass_to_min(seconds):
    # convertendo segundos para minutos
	return strftime("%M:%S", gmtime(seconds))


def remove_space(msg):
    # Remove alguns espaços a mais, ex: {1,    2,  3,  4} se torna {1, 2, 3, 4}
    msg = msg.split()
    msg = " ".join(msg)
    return msg

class Game(commands.Cog):

    def __init__(self, bot, game=False):
        self.bot = bot
        self.channels = [1005542693528678447, 998717439258923162]
    

    @commands.command(name="start", aliases=["estudar"])
    async def start(self, ctx, *, arg="geral"):
        if ctx.channel.id in self.channels:
            # n é usado como contador, para saber o numero de perguntas já feitas na partida
            n = 0

            # checando se já tem alguma partida acontecendo, se tiver ele avisa que o jogo já começou, se não, ele inicia um
            partida_iniciada = check_partida(str(ctx.channel.id))
            if partida_iniciada > 0:
                await ctx.send("A partida já começou")
            else:

                # iniciando um novo jogo
                start_game(str(ctx.channel.id))

                # lista vazia que vai conter as perguntas do tema escolhido
                lista = []

                # se não houver um arg(argumento) na hora de iniciar ele pega todas as perguntas sem filtrar
                if arg.lower() == "geral":
                    lista = list(perguntas.keys())
                
                # possivel filtro de perguntas "matematica" entao ele verifica e so adiciona as perguntas desse tema
                elif arg.lower() in ["matematica", "matemática"]:
                    # passa por TODAS as perguntas da lista de perguntas, se a materia dela for a do filtro ele adiciona na nova lista
                    for i in perguntas:
                        if perguntas[i]["materia"] == "matematica":
                            lista.append(i)
                elif arg.lower() == "empreendedorismo":
                    for i in perguntas:
                        if perguntas[i]["materia"] == "empreendedorismo":
                            lista.append(i)
                else:
                    # se a pessoa passar um tema que não existe ele avisa, e finaliza o jogo
                    await ctx.send("Tema não encontrado.")
                    end_game(str(ctx.channel.id))
                    return

                # Se a quantidade de itens na lista for menor q 1. Ele avisa que esse tema nao possui perguntas ainda e finaliza.
                if len(lista) < 1:
                    await ctx.send("Esse tema ainda não possui perguntas...")
                    end_game(str(ctx.channel.id))
                    return

                # mistura as perguntas da lista
                shuffle(lista)

                # loop infinito, para sempre gerar novas perguntas, a medida que elas forem sendo respondidas
                while True:
                    try:
                        # TENTA pegar na lista de perguntas a pergunta na posição n
                        pergunta = lista[n]
                    except IndexError:
                        # caso a pessoa já tenha respondido todas as perguntas da lista
                        # ele passa a pegar repetidas, de modo aleatorio
                        pergunta = lista[randint(0, len(lista)-1)]

                    # aumentando o número do contador, sempre vai somando de 1 em 1
                    n +=1

                    # cria a msg que vai ser enviada, com o numero da pergunta, a pergunta, e o tempo para responder
                    cor = (perguntas[pergunta]["cor"])
                    embed_pergunta = discord.Embed(title=f'Pergunta #{n}', description=" ", colour=cor)
                    embed_pergunta.set_image(url=perguntas[pergunta]["pergunta"])

                    # formatando tempo
                    tempo = pass_to_min(perguntas[pergunta]["tempo"])
                    if int(tempo[3:]) > 0:
                        embed_pergunta.set_footer(text=f"🕔 Tempo para responder {tempo}s")
                    else:
                        embed_pergunta.set_footer(text=f"🕔 Tempo para responder {tempo[:2]}min")
                    await ctx.send(embed=embed_pergunta)

                    # função que verifica se a resposta esta correta e retorna o conteudo, caso contrario nao faz nada
                    def check(msg):
                        response = msg.content
                        try:
                            response = response.lower()
                        except:
                            pass
                        # verifica se a resposta foi enviada no mesmo chat da pergunta
                        if(msg.channel.id == ctx.channel.id):
                            response = remove_space(response)
                            if response in perguntas[pergunta]["resposta"] or response in [".fim", ". fim"]:
                                return response

                    # loop infinito para pegar todas as respostas que forem enviadas
                    while True:
                        try:
                            # pega TODAS msg enviadas por TODOS usuarios no periodo de tempo referente a pergunta, e usa a funcao check
                            # timeout=(perguntas[pergunta]["tempo"])-30) pega o tempo definido e diminui 30s que será o tempo de alerta
                            response = await self.bot.wait_for("message", check=check, timeout=(perguntas[pergunta]["tempo"])-30)
                            response = remove_space(response.content)

                            # Se for a resposta correta vai ter um retorno do check, e envia a msg avisando que acertou
                            # também avisa que a proxima pergunta esta por vir, quebrando o loop inifinto(break) pois a pergunta foi acertada
                            if response in perguntas[pergunta]["resposta"]:
                                embed_acerto = discord.Embed(title="Acertou :tada: :tada: :tada:", description=f"A resposta era {response}\n", colour=0x00FF00)
                                embed_acerto.set_footer(text="Próxima pergunta em 5s...")
                                await ctx.send(embed=embed_acerto)
                                sleep(5)
                                break
                            elif response in [".fim", ". fim"]:
                                # se a pessoa digitar  .fim  finaliza o jogo e envia a resposta
                                resposta = perguntas[pergunta]["resposta"][0]
                                embed_fim = discord.Embed(title="Jogo finalizado", description=f"A resposta era: {resposta}\n", colour=0x4682B4)
                                await ctx.send(embed=embed_fim)
                                end_game(str(ctx.channel.id))
                                return
            
                        # ao exceder o tempo de resposta, entra aqui, e envia o alerta avisando que faltam 30s
                        except asyncio.TimeoutError:
                            embed_alerta = discord.Embed(title="Faltam 30s", colour=0x4682B4)
                            await ctx.send(embed=embed_alerta)
                            try:
                                # Faz o mesmo que nas linhas acima, mas com timeout de 30s
                                response = await self.bot.wait_for("message", check=check, timeout=30)
                                response = remove_space(response.content)
                                
                                if response in perguntas[pergunta]["resposta"]:
                                    embed_acerto = discord.Embed(title="Acertou :tada: :tada: :tada:", description=f"A resposta era {response}\n", colour=0x00FF00)
                                    embed_acerto.set_footer(text="Próxima pergunta em 5s...")
                                    await ctx.send(embed=embed_acerto)
                                    sleep(5)
                                    break
                                elif response == ".fim":
                                    resposta = perguntas[pergunta]["resposta"][0]
                                    embed_fim = discord.Embed(title="Jogo finalizado", description=f"A resposta era: {resposta}\n", colour=0x4682B4)
                                    await ctx.send(embed=embed_fim)
                                    end_game(str(ctx.channel.id))
                                    return
                            except asyncio.TimeoutError:
                                # Ao entrar no timeouterror pela segunda vez ele finaliza o jogo
                                resposta = perguntas[pergunta]["resposta"][0]
                                embed_fim = discord.Embed(title="Game Over.", description=f"A resposta era: {resposta}", colour=0xFF0000)
                                await ctx.send(embed=embed_fim)
                                end_game(str(ctx.channel.id))
                                return 
        else:
            if ctx.message.guild.id == 1004124654392332490:
                await ctx.send("Por favor use este comando em <#>")
            elif ctx.message.guild.id == 1005542693063118858:
                await ctx.send("Por favor use este comando em <#1005542693528678447>")



def setup(bot):
    """Load Game Cog."""
    bot.add_cog(Game(bot))
