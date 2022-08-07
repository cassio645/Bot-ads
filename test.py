from code.lista_de_perguntas import perguntas
from random import randint

tema = input("Digite o tema [geral/soma/multiplicacao/divisao/subtracao]: ")

lista = []

if tema == "geral":
    lista = list(perguntas.keys())
elif tema == "soma":
    for i in perguntas:
        if perguntas[i]["materia"] == "soma":
            lista.append(i)
elif tema == "multiplicacao":
    for i in perguntas:
        if perguntas[i]["materia"] == "multiplicacao":
            lista.append(i)
elif tema == "divisao":
    for i in perguntas:
        if perguntas[i]["materia"] == "divisao":
            lista.append(i)


#while True:
pergunta = lista[randint(0, len(lista)-1)]
print(perguntas[pergunta]["pergunta"])
resp = input("Respota: ")

if resp in perguntas[pergunta]["resposta"]:
    print("Acertou")
else:
    resposta = perguntas[pergunta]["resposta"][0]
    print(f"Errou era... {resposta}")

