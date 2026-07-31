from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Paginado(BaseModel, Generic[T]):
    """Envelope padrao de resposta paginada.
    total: quantidade total de registros que batem com o filtro (sem paginacao)
    skip / limit: os parametros usados na consulta, ecoados de volta por conveniencia
    itens: a pagina atual de resultados
    """
    total: int
    skip: int
    limit: int
    itens: List[T]
