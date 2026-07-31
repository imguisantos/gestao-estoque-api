import logging
import sys

def configurar_logging() -> None:
    """Configura um logger simples que escreve no stdout, no formato
    esperado por qualquer plataforma de deploy (Railway, Render, Docker) —
    elas capturam stdout/stderr automaticamente e centralizam os logs,
    então não é preciso escrever em arquivo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # bibliotecas de terceiros tendem a ser muito verbosas em INFO;
    # deixamos elas em WARNING para não afogar os logs da própria aplicação
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


logger = logging.getLogger("estoque_api")
