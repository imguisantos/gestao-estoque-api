"""
Fixtures compartilhadas por todos os testes.

Estratégia: cada teste roda contra um banco SQLite em memória, criado do
zero e destruído no final. Isso mantém os testes rápidos e completamente
isolados do MySQL "de verdade" usado em desenvolvimento/produção — rodar
`pytest` nunca deve tocar nos seus dados reais.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # mantém a MESMA conexão em memória entre chamadas
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    """Cliente de teste com banco limpo a cada teste."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def usuario_dados():
    return {"nome": "Usuário Teste", "email": "teste@exemplo.com", "senha": "senha123"}


@pytest.fixture()
def auth_headers(client, usuario_dados):
    """Registra um usuário, faz login e devolve o header Authorization pronto
    para ser usado em qualquer rota protegida."""
    client.post("/auth/registrar", json=usuario_dados)
    resposta = client.post(
        "/auth/login",
        json={"email": usuario_dados["email"], "senha": usuario_dados["senha"]},
    )
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
