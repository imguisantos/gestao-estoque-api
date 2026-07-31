import pytest


@pytest.fixture()
def produto_id(client, auth_headers):
    resposta = client.post(
        "/produtos/",
        json={"nome": "Produto Teste", "preco": "50.00", "estoque_minimo": 5, "quantidade_estoque": 20},
        headers=auth_headers,
    )
    return resposta.json()["id"]


def test_entrada_soma_ao_estoque(client, auth_headers, produto_id):
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "ENTRADA", "quantidade": 10, "motivo": "Compra"},
        headers=auth_headers,
    )
    assert resposta.status_code == 201

    produto = client.get(f"/produtos/{produto_id}", headers=auth_headers).json()
    assert produto["quantidade_estoque"] == 30  # 20 iniciais + 10


def test_saida_subtrai_do_estoque(client, auth_headers, produto_id):
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "SAIDA", "quantidade": 8, "motivo": "Venda"},
        headers=auth_headers,
    )
    assert resposta.status_code == 201

    produto = client.get(f"/produtos/{produto_id}", headers=auth_headers).json()
    assert produto["quantidade_estoque"] == 12  # 20 iniciais - 8


def test_saida_maior_que_estoque_e_rejeitada(client, auth_headers, produto_id):
    """A regra mais importante do sistema: nunca permitir estoque negativo."""
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "SAIDA", "quantidade": 999, "motivo": "Venda impossível"},
        headers=auth_headers,
    )
    assert resposta.status_code == 400

    # o estoque não deve ter sido alterado pela tentativa rejeitada
    produto = client.get(f"/produtos/{produto_id}", headers=auth_headers).json()
    assert produto["quantidade_estoque"] == 20


def test_saida_exata_ao_saldo_disponivel_e_permitida(client, auth_headers, produto_id):
    """Caso de borda: zerar o estoque exatamente deve funcionar (só não pode ficar negativo)."""
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "SAIDA", "quantidade": 20, "motivo": "Liquidação total"},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    produto = client.get(f"/produtos/{produto_id}", headers=auth_headers).json()
    assert produto["quantidade_estoque"] == 0


def test_movimentacao_produto_inexistente_retorna_404(client, auth_headers):
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": 999, "tipo": "ENTRADA", "quantidade": 1},
        headers=auth_headers,
    )
    assert resposta.status_code == 404


def test_movimentacao_de_produto_inativo_e_rejeitada(client, auth_headers, produto_id):
    client.delete(f"/produtos/{produto_id}", headers=auth_headers)  # exclusão lógica
    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "ENTRADA", "quantidade": 1},
        headers=auth_headers,
    )
    assert resposta.status_code == 404


def test_listar_movimentacoes_filtra_por_tipo(client, auth_headers, produto_id):
    client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "ENTRADA", "quantidade": 5},
        headers=auth_headers,
    )
    client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "SAIDA", "quantidade": 3},
        headers=auth_headers,
    )

    resposta = client.get("/movimentacoes/?tipo=SAIDA", headers=auth_headers)
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["itens"][0]["tipo"] == "SAIDA"


def test_relatorio_resumo_estoque_reflete_movimentacoes(client, auth_headers, produto_id):
    client.post(
        "/movimentacoes/",
        json={"produto_id": produto_id, "tipo": "SAIDA", "quantidade": 15},
        headers=auth_headers,
    )
    # sobrou 5 unidades, e estoque_minimo do fixture é 5 -> deve aparecer como estoque baixo
    resposta = client.get("/relatorios/resumo-estoque", headers=auth_headers)
    corpo = resposta.json()
    assert corpo["total_produtos"] == 1
    assert len(corpo["produtos_estoque_baixo"]) == 1
    assert corpo["produtos_estoque_baixo"][0]["quantidade_estoque"] == 5
