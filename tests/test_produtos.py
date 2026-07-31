import pytest


@pytest.fixture()
def categoria_id(client, auth_headers):
    resposta = client.post("/categorias/", json={"nome": "Informática"}, headers=auth_headers)
    return resposta.json()["id"]


def test_criar_produto(client, auth_headers, categoria_id):
    resposta = client.post(
        "/produtos/",
        json={
            "nome": "Teclado Mecânico",
            "preco": "199.90",
            "estoque_minimo": 3,
            "categoria_id": categoria_id,
            "quantidade_estoque": 10,
        },
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == "Teclado Mecânico"
    assert corpo["quantidade_estoque"] == 10


def test_preco_mantem_precisao_decimal(client, auth_headers):
    """Regressão para o bug de arredondamento de Float: 19.99 deve continuar
    sendo exatamente 19.99 depois de ida e volta pelo banco."""
    resposta = client.post(
        "/produtos/",
        json={"nome": "Produto Preciso", "preco": "19.99", "estoque_minimo": 0, "quantidade_estoque": 1},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    assert resposta.json()["preco"] == "19.99"


def test_criar_produto_com_categoria_inexistente_retorna_404(client, auth_headers):
    resposta = client.post(
        "/produtos/",
        json={"nome": "Produto Órfão", "preco": "10.00", "estoque_minimo": 0, "categoria_id": 999},
        headers=auth_headers,
    )
    assert resposta.status_code == 404
    assert "Categoria" in resposta.json()["detail"]


def test_criar_produto_com_fornecedor_inexistente_retorna_404(client, auth_headers):
    resposta = client.post(
        "/produtos/",
        json={"nome": "Produto Órfão", "preco": "10.00", "estoque_minimo": 0, "fornecedor_id": 999},
        headers=auth_headers,
    )
    assert resposta.status_code == 404
    assert "Fornecedor" in resposta.json()["detail"]


def test_listar_produtos_paginado(client, auth_headers):
    for i in range(4):
        client.post(
            "/produtos/",
            json={"nome": f"Produto {i}", "preco": "10.00", "estoque_minimo": 0},
            headers=auth_headers,
        )
    resposta = client.get("/produtos/?limit=2&skip=1", headers=auth_headers)
    corpo = resposta.json()
    assert corpo["total"] == 4
    assert len(corpo["itens"]) == 2
    assert corpo["skip"] == 1


def test_atualizar_produto_com_categoria_inexistente_retorna_404(client, auth_headers):
    produto = client.post(
        "/produtos/",
        json={"nome": "Produto", "preco": "10.00", "estoque_minimo": 0},
        headers=auth_headers,
    ).json()

    resposta = client.put(
        f"/produtos/{produto['id']}",
        json={"categoria_id": 999},
        headers=auth_headers,
    )
    assert resposta.status_code == 404


def test_excluir_produto_e_exclusao_logica(client, auth_headers):
    """Produto excluído deve sumir da listagem padrão mas continuar existindo
    no banco (exclusão lógica, não física)."""
    produto = client.post(
        "/produtos/",
        json={"nome": "Produto Descontinuado", "preco": "5.00", "estoque_minimo": 0},
        headers=auth_headers,
    ).json()

    resposta = client.delete(f"/produtos/{produto['id']}", headers=auth_headers)
    assert resposta.status_code == 204

    listagem = client.get("/produtos/", headers=auth_headers).json()
    ids_listados = [p["id"] for p in listagem["itens"]]
    assert produto["id"] not in ids_listados

    # a rota de detalhe ainda enxerga o produto, só marcado como inativo
    detalhe = client.get(f"/produtos/{produto['id']}", headers=auth_headers)
    assert detalhe.status_code == 200
    assert detalhe.json()["ativo"] is False
