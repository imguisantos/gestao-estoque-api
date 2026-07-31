def test_criar_categoria(client, auth_headers):
    resposta = client.post(
        "/categorias/",
        json={"nome": "Eletrônicos", "descricao": "Produtos eletrônicos"},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Eletrônicos"


def test_criar_categoria_duplicada_retorna_400(client, auth_headers):
    dados = {"nome": "Papelaria", "descricao": None}
    client.post("/categorias/", json=dados, headers=auth_headers)
    resposta = client.post("/categorias/", json=dados, headers=auth_headers)
    assert resposta.status_code == 400


def test_listar_categorias_retorna_formato_paginado(client, auth_headers):
    client.post("/categorias/", json={"nome": "Categoria A"}, headers=auth_headers)
    client.post("/categorias/", json={"nome": "Categoria B"}, headers=auth_headers)

    resposta = client.get("/categorias/", headers=auth_headers)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 2
    assert len(corpo["itens"]) == 2
    assert corpo["skip"] == 0
    assert corpo["limit"] == 20


def test_paginacao_respeita_limit(client, auth_headers):
    for i in range(5):
        client.post("/categorias/", json={"nome": f"Categoria {i}"}, headers=auth_headers)

    resposta = client.get("/categorias/?limit=2", headers=auth_headers)
    corpo = resposta.json()
    assert corpo["total"] == 5
    assert len(corpo["itens"]) == 2


def test_obter_categoria_inexistente_retorna_404(client, auth_headers):
    resposta = client.get("/categorias/999", headers=auth_headers)
    assert resposta.status_code == 404


def test_excluir_categoria(client, auth_headers):
    criada = client.post("/categorias/", json={"nome": "Temporária"}, headers=auth_headers).json()
    resposta = client.delete(f"/categorias/{criada['id']}", headers=auth_headers)
    assert resposta.status_code == 204
    assert client.get(f"/categorias/{criada['id']}", headers=auth_headers).status_code == 404
