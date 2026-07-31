import pytest


@pytest.fixture()
def usuario_comum_headers(client, auth_headers):
    """auth_headers já criou o PRIMEIRO usuário (que vira admin automaticamente).
    Aqui criamos um SEGUNDO usuário, que deve entrar como usuário comum."""
    dados = {"nome": "Usuário Comum", "email": "comum@exemplo.com", "senha": "senha123"}
    client.post("/auth/registrar", json=dados)
    resposta = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_primeiro_usuario_e_admin(client, usuario_dados):
    resposta = client.post("/auth/registrar", json=usuario_dados)
    # não expomos is_admin no UsuarioOut? -> checa via tentativa de ação de admin
    login = client.post("/auth/login", json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resposta = client.post("/categorias/", json={"nome": "Categoria Admin"}, headers=headers)
    assert resposta.status_code == 201


def test_segundo_usuario_nao_e_admin_e_nao_pode_criar_categoria(client, usuario_comum_headers):
    resposta = client.post("/categorias/", json={"nome": "Categoria Proibida"}, headers=usuario_comum_headers)
    assert resposta.status_code == 403


def test_usuario_comum_pode_listar_categorias(client, auth_headers, usuario_comum_headers):
    client.post("/categorias/", json={"nome": "Visível a todos"}, headers=auth_headers)
    resposta = client.get("/categorias/", headers=usuario_comum_headers)
    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1


def test_usuario_comum_nao_pode_criar_produto(client, usuario_comum_headers):
    resposta = client.post(
        "/produtos/",
        json={"nome": "Produto Proibido", "preco": "10.00", "estoque_minimo": 0},
        headers=usuario_comum_headers,
    )
    assert resposta.status_code == 403


def test_usuario_comum_pode_registrar_movimentacao(client, auth_headers, usuario_comum_headers):
    """Movimentação de estoque é operação do dia a dia — não deve exigir admin,
    só um usuário autenticado."""
    produto = client.post(
        "/produtos/",
        json={"nome": "Produto", "preco": "10.00", "estoque_minimo": 0, "quantidade_estoque": 5},
        headers=auth_headers,
    ).json()

    resposta = client.post(
        "/movimentacoes/",
        json={"produto_id": produto["id"], "tipo": "ENTRADA", "quantidade": 5},
        headers=usuario_comum_headers,
    )
    assert resposta.status_code == 201


def test_login_retorna_access_e_refresh_token(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    resposta = client.post(
        "/auth/login", json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]}
    )
    corpo = resposta.json()
    assert "access_token" in corpo
    assert "refresh_token" in corpo


def test_refresh_token_gera_novo_access_token(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    login = client.post(
        "/auth/login", json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]}
    )
    refresh_token = login.json()["refresh_token"]

    resposta = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resposta.status_code == 200
    novo_corpo = resposta.json()
    assert "access_token" in novo_corpo
    assert "refresh_token" in novo_corpo


def test_access_token_nao_pode_ser_usado_como_refresh_token(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    login = client.post(
        "/auth/login", json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]}
    )
    access_token = login.json()["access_token"]

    resposta = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert resposta.status_code == 401


def test_refresh_token_nao_pode_ser_usado_em_rota_protegida(client, usuario_dados):
    """Um refresh token não deve funcionar como credencial de acesso normal —
    só serve para trocar por um novo access token na rota /auth/refresh."""
    client.post("/auth/registrar", json=usuario_dados)
    login = client.post(
        "/auth/login", json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]}
    )
    refresh_token = login.json()["refresh_token"]

    resposta = client.get("/categorias/", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resposta.status_code == 401
