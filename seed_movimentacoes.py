"""
Script para gerar movimentacoes de estoque (entradas e saidas) para os
produtos ja cadastrados, com datas e responsaveis variados, simulando um
historico realista ao longo do tempo.

Pre-requisito: rode primeiro seed_fornecedores_e_produtos.py

Como usar:
   python seed_movimentacoes.py
"""
import random
from datetime import datetime, timedelta

import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "user@teste.com"
SENHA = "123456"

RESPONSAVEIS = [
    "Carlos Henrique",
    "Mariana Costa",
    "Ana Paula Ferreira",
    "Bruno Oliveira",
    "Juliana Santos",
]

MOTIVOS_ENTRADA = [
    "Compra inicial de estoque",
    "Reposição de estoque",
    "Devolução de cliente",
    "Recebimento de fornecedor",
]

MOTIVOS_SAIDA = [
    "Venda ao cliente",
    "Transferência para outra filial",
    "Uso interno",
    "Produto danificado",
]

# Janela de datas simuladas para o histórico
DATA_INICIO = datetime(2026, 1, 1)
DATA_FIM = datetime(2026, 7, 31)


def login() -> str:
    resposta = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
    resposta.raise_for_status()
    return resposta.json()["access_token"]


def listar_produtos(headers) -> list:
    produtos = []
    skip, limit = 0, 100
    while True:
        resposta = requests.get(f"{BASE_URL}/produtos/", params={"skip": skip, "limit": limit}, headers=headers)
        resposta.raise_for_status()
        corpo = resposta.json()
        produtos.extend(corpo["itens"])
        if len(corpo["itens"]) < limit:
            break
        skip += limit
    return produtos


def data_aleatoria() -> str:
    delta = DATA_FIM - DATA_INICIO
    dias_aleatorios = random.randint(0, delta.days)
    horas_aleatorias = random.randint(8, 18)
    data = DATA_INICIO + timedelta(days=dias_aleatorios, hours=horas_aleatorias)
    return data.isoformat()


def registrar_movimentacao(headers, produto_id: int, tipo: str, quantidade: int, motivo: str) -> bool:
    payload = {
        "produto_id": produto_id,
        "tipo": tipo,
        "quantidade": quantidade,
        "motivo": motivo,
        "data": data_aleatoria(),
        "responsavel_nome": random.choice(RESPONSAVEIS),
    }
    resposta = requests.post(f"{BASE_URL}/movimentacoes/", json=payload, headers=headers)
    return resposta.status_code == 201


def gerar_movimentacoes_para_produto(headers, produto: dict):
    nome = produto["nome"]
    produto_id = produto["id"]
    saldo_atual = produto["quantidade_estoque"]

    # 1) Entrada inicial: leva o estoque de 0 até um valor "cheio" plausível.
    # Como os produtos foram criados com quantidade_estoque=0 pelo script anterior,
    # esta entrada estabelece o estoque de partida do histórico.
    entrada_inicial = random.randint(20, 60)
    if registrar_movimentacao(headers, produto_id, "ENTRADA", entrada_inicial, random.choice(MOTIVOS_ENTRADA)):
        saldo_atual += entrada_inicial

    # 2) Algumas saídas ao longo do tempo, sempre respeitando o saldo disponível
    num_saidas = random.randint(2, 5)
    for _ in range(num_saidas):
        if saldo_atual <= 1:
            break
        quantidade = random.randint(1, max(1, saldo_atual // 3))
        if registrar_movimentacao(headers, produto_id, "SAIDA", quantidade, random.choice(MOTIVOS_SAIDA)):
            saldo_atual -= quantidade

    # 3) Uma reposição extra, simulando um novo pedido ao fornecedor
    if random.random() < 0.6:
        reposicao = random.randint(10, 30)
        if registrar_movimentacao(headers, produto_id, "ENTRADA", reposicao, random.choice(MOTIVOS_ENTRADA)):
            saldo_atual += reposicao

    print(f"  OK - {nome}: saldo final ~{saldo_atual} unidades")


if __name__ == "__main__":
    print("Fazendo login...")
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    print("Login ok.\n")

    produtos = listar_produtos(headers)
    if not produtos:
        print("Nenhum produto encontrado. Rode seed_fornecedores_e_produtos.py primeiro.")
    else:
        print(f"Gerando movimentações para {len(produtos)} produtos...\n")
        for produto in produtos:
            gerar_movimentacoes_para_produto(headers, produto)
        print("\nConcluído. Confira /relatorios/resumo-estoque e /relatorios/mais-movimentados no Swagger.")
