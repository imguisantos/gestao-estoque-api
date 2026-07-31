import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega variáveis do arquivo .env (se existir) para o ambiente do processo.
# Dentro do Docker isso não tem efeito (as variáveis já vêm do docker-compose.yml),
# mas é o que permite rodar `uvicorn` direto no VSCode sem Docker.
load_dotenv()

# String de conexão vem do ambiente (definida no .env / docker-compose)
# Formato MySQL: mysql+pymysql://usuario:senha@host:porta/nome_banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://estoque_user:estoque_pass@db:3306/estoque_db",
)

# pool_pre_ping evita erros de "conexão perdida" quando o MySQL fica
# ocioso por muito tempo (comum em containers Docker)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão por requisição e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
