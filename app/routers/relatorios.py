from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_usuario_atual

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/resumo-estoque", response_model=schemas.ResumoEstoque)
def resumo_estoque(db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    produtos_ativos = db.query(models.Produto).filter(models.Produto.ativo == True).all()  # noqa: E712

    total_produtos = len(produtos_ativos)
    valor_total = sum((p.preco * p.quantidade_estoque for p in produtos_ativos), Decimal("0"))

    estoque_baixo = [
        schemas.ProdutoEstoqueBaixo(
            id=p.id,
            nome=p.nome,
            quantidade_estoque=p.quantidade_estoque,
            estoque_minimo=p.estoque_minimo,
        )
        for p in produtos_ativos
        if p.quantidade_estoque <= p.estoque_minimo
    ]

    return schemas.ResumoEstoque(
        total_produtos=total_produtos,
        valor_total_estoque=valor_total.quantize(Decimal("0.01")),
        produtos_estoque_baixo=estoque_baixo,
    )


@router.get("/mais-movimentados")
def produtos_mais_movimentados(db: Session = Depends(get_db), usuario=Depends(get_usuario_atual), limite: int = 10):
    resultado = (
        db.query(
            models.Produto.id,
            models.Produto.nome,
            func.sum(models.Movimentacao.quantidade).label("total_movimentado"),
        )
        .join(models.Movimentacao, models.Movimentacao.produto_id == models.Produto.id)
        .group_by(models.Produto.id, models.Produto.nome)
        .order_by(func.sum(models.Movimentacao.quantidade).desc())
        .limit(limite)
        .all()
    )
    return [
        {"produto_id": r.id, "nome": r.nome, "total_movimentado": int(r.total_movimentado)}
        for r in resultado
    ]
