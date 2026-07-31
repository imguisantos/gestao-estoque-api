def test_criar_fornecedor(client, auth_headers):
    resposta = client.post(
        "/fornecedores/",
        json={"nome": "Fornecedor XPTO", "cnpj": "12.345.678/0001-99"},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Fornecedor XPTO"


def test_listar_fornecedores_paginado(client, auth_headers):
    for i in range(3):
        client.post("/fornecedores/", json={"nome": f"Fornecedor {i}"}, headers=auth_headers)

    resposta = client.get("/fornecedores/", headers=auth_headers)
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert len(corpo["itens"]) == 3


def test_atualizar_fornecedor(client, auth_headers):
    criado = client.post("/fornecedores/", json={"nome": "Nome Antigo"}, headers=auth_headers).json()
    resposta = client.put(
        f"/fornecedores/{criado['id']}",
        json={"nome": "Nome Novo"},
        headers=auth_headers,
    )
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Nome Novo"


def test_atualizar_fornecedor_inexistente_retorna_404(client, auth_headers):
    resposta = client.put("/fornecedores/999", json={"nome": "Qualquer"}, headers=auth_headers)
    assert resposta.status_code == 404


def test_excluir_fornecedor(client, auth_headers):
    criado = client.post("/fornecedores/", json={"nome": "Temporário"}, headers=auth_headers).json()
    resposta = client.delete(f"/fornecedores/{criado['id']}", headers=auth_headers)
    assert resposta.status_code == 204
