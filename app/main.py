import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from app.logging_config import configurar_logging, logger
from app.routers import auth, categorias, fornecedores, produtos, movimentacoes, relatorios

configurar_logging()

app = FastAPI(
    title="API de Gestão de Estoque",
    description=(
        "API REST para controle de estoque: produtos, categorias, fornecedores, "
        "movimentações (entrada/saída) e relatórios gerenciais. "
        "Autenticação via JWT (access + refresh token)."
    ),
    version="1.1.0",
)

app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(fornecedores.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(relatorios.router)


# ---------------------------------------------------------------------------
# Middleware de logging de requisições
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requisicoes(request: Request, call_next):
    """Loga toda requisição com um ID único (útil para rastrear um erro
    específico nos logs de produção) e o tempo de resposta."""
    request_id = str(uuid.uuid4())[:8]
    inicio = time.time()

    response = await call_next(request)

    duracao_ms = round((time.time() - inicio) * 1000, 2)
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"-> {response.status_code} ({duracao_ms}ms)"
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Tratamento global de exceções
# ---------------------------------------------------------------------------
# A ideia central aqui: nenhuma rota deve vazar um traceback bruto do Python
# (ou detalhes internos do banco) para quem está chamando a API. Toda exceção
# não tratada cai em algum destes handlers e vira uma resposta JSON
# consistente, no mesmo formato que o restante da API já usa ({"detail": ...}).

@app.exception_handler(RequestValidationError)
async def validacao_invalida_handler(request: Request, exc: RequestValidationError):
    """Erro de validação do Pydantic (campo faltando, tipo errado, etc.).
    Reformatamos para ficar mais legível do que a estrutura padrão do FastAPI."""
    erros = [
        {"campo": " -> ".join(str(p) for p in erro["loc"]), "mensagem": erro["msg"]}
        for erro in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dados inválidos", "erros": erros},
    )


@app.exception_handler(IntegrityError)
async def integridade_handler(request: Request, exc: IntegrityError):
    """Violação de constraint do banco (chave duplicada, FK inexistente etc.)
    que escapou das validações da rota. Loga o erro real internamente, mas
    devolve uma mensagem genérica e segura para quem chamou a API."""
    logger.error(f"Erro de integridade no banco: {exc}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflito de dados: verifique se os valores enviados já existem ou são válidos"},
    )


@app.exception_handler(OperationalError)
async def banco_indisponivel_handler(request: Request, exc: OperationalError):
    """O banco caiu, a conexão foi recusada, timeout, etc. Isso é erro de
    infraestrutura, não do cliente da API — por isso 503, não 500."""
    logger.error(f"Banco de dados indisponível: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Serviço temporariamente indisponível. Tente novamente em instantes."},
    )


@app.exception_handler(Exception)
async def erro_inesperado_handler(request: Request, exc: Exception):
    """Rede de segurança final: qualquer exceção que não foi prevista pelos
    handlers acima cai aqui. Loga o traceback completo no servidor (para
    debug), mas nunca expõe esse detalhe para o cliente."""
    logger.exception(f"Erro não tratado em {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"},
    )


@app.get("/", tags=["Status"])
def status_api():
    return {"status": "online", "mensagem": "API de Gestão de Estoque no ar 🚀"}


@app.get("/health", tags=["Status"])
def health_check():
    """Endpoint simples para checagem de saúde por load balancers e
    plataformas de deploy (Railway, Render, etc. costumam pingar isso)."""
    return {"status": "healthy"}
