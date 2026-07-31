from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_usuario_atual
from app.pagination import Paginado

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


@router.post("/", response_model=schemas.MovimentacaoOut, status_code=status.HTTP_201_CREATED)
def registrar_movimentacao(
    mov_in: schemas.MovimentacaoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    """Regra de negocio central da API:
    - ENTRADA soma ao estoque do produto.
    - SAIDA subtrai, mas nunca pode deixar o estoque negativo.
    Tudo dentro de uma unica transacao: se algo falhar, nada e persistido
    (rollback explicito garante que a sessao volte ao estado anterior).
    """
    produto = db.query(models.Produto).get(mov_in.produto_id)
    if not produto or not produto.ativo:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou inativo")

    if mov_in.tipo == models.TipoMovimentacao.SAIDA:
        if produto.quantidade_estoque < mov_in.quantidade:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Estoque insuficiente. Disponível: {produto.quantidade_estoque}, "
                    f"solicitado: {mov_in.quantidade}"
                ),
            )
        produto.quantidade_estoque -= mov_in.quantidade
    else:
        produto.quantidade_estoque += mov_in.quantidade

    movimentacao = models.Movimentacao(
        produto_id=mov_in.produto_id,
        tipo=mov_in.tipo,
        quantidade=mov_in.quantidade,
        motivo=mov_in.motivo,
        usuario_id=usuario.id,
    )

    try:
        db.add(movimentacao)
        db.add(produto)
        db.commit()
    except Exception:
        # Se o commit falhar (ex: erro de conexao, violacao de constraint),
        # desfaz a alteracao de quantidade_estoque feita em memoria e devolve
        # a sessao a um estado limpo, para nao deixar o produto com saldo
        # "fantasma" que nunca foi de fato salvo no banco.
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível registrar a movimentação")

    db.refresh(movimentacao)
    return movimentacao


@router.get("/", response_model=Paginado[schemas.MovimentacaoOut])
def listar_movimentacoes(
    produto_id: Optional[int] = None,
    tipo: Optional[models.TipoMovimentacao] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    query = db.query(models.Movimentacao)
    if produto_id:
        query = query.filter(models.Movimentacao.produto_id == produto_id)
    if tipo:
        query = query.filter(models.Movimentacao.tipo == tipo)

    total = query.count()
    itens = query.order_by(models.Movimentacao.data.desc()).offset(skip).limit(limit).all()
    return Paginado(total=total, skip=skip, limit=limit, itens=itens)


@router.get("/{movimentacao_id}", response_model=schemas.MovimentacaoOut)
def obter_movimentacao(movimentacao_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    mov = db.query(models.Movimentacao).get(movimentacao_id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    return mov
