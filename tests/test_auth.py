def test_registrar_usuario_com_sucesso(client, usuario_dados):
    resposta = client.post("/auth/registrar", json=usuario_dados)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == usuario_dados["email"]
    assert "senha" not in corpo  # a senha (nem o hash) nunca deve vazar na resposta
    assert "senha_hash" not in corpo


def test_registrar_email_duplicado_retorna_400(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    resposta = client.post("/auth/registrar", json=usuario_dados)
    assert resposta.status_code == 400


def test_login_com_credenciais_corretas(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    resposta = client.post(
        "/auth/login",
        json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "access_token" in corpo
    assert corpo["token_type"] == "bearer"


def test_login_com_senha_errada_retorna_401(client, usuario_dados):
    client.post("/auth/registrar", json=usuario_dados)
    resposta = client.post(
        "/auth/login",
        json={"email": usuario_dados["email"], "senha": "senha_errada"},
    )
    assert resposta.status_code == 401


def test_login_com_email_inexistente_retorna_401(client):
    resposta = client.post(
        "/auth/login",
        json={"email": "ninguem@exemplo.com", "senha": "qualquer"},
    )
    assert resposta.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    resposta = client.get("/produtos/")
    assert resposta.status_code == 401


def test_rota_protegida_com_token_invalido_retorna_401(client):
    resposta = client.get("/produtos/", headers={"Authorization": "Bearer token-invalido"})
    assert resposta.status_code == 401
