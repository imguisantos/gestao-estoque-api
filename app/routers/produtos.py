from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_usuario_atual, get_usuario_admin
from app.pagination import Paginado

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _validar_categoria_e_fornecedor(db: Session, categoria_id: Optional[int], fornecedor_id: Optional[int]):
    """Garante que referencias estrangeiras informadas realmente existem antes
    de gravar o produto. Sem isso, o banco aceitaria um categoria_id/fornecedor_id
    inexistente (SQLite nem sempre reforça FK) e o erro só apareceria depois,
    de forma confusa, ao tentar listar/exibir o produto."""
    if categoria_id is not None:
        if not db.query(models.Categoria.id).filter(models.Categoria.id == categoria_id).first():
            raise HTTPException(status_code=404, detail=f"Categoria {categoria_id} não encontrada")
    if fornecedor_id is not None:
        if not db.query(models.Fornecedor.id).filter(models.Fornecedor.id == fornecedor_id).first():
            raise HTTPException(status_code=404, detail=f"Fornecedor {fornecedor_id} não encontrado")


@router.post("/", response_model=schemas.ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto_in: schemas.ProdutoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    _validar_categoria_e_fornecedor(db, produto_in.categoria_id, produto_in.fornecedor_id)

    produto = models.Produto(**produto_in.model_dump())
    try:
        db.add(produto)
        db.commit()
    except Exception:
        # Garante que a sessao nao fique "suja" com uma transacao pendente
        # em caso de erro (ex: violacao de constraint no banco). Sem o
        # rollback explicito, a proxima query nesta mesma sessao falharia
        # tambem, mesmo sendo uma operacao nao relacionada.
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar o produto")
    db.refresh(produto)
    return produto


@router.get("/", response_model=Paginado[schemas.ProdutoOut])
def listar_produtos(
    categoria_id: Optional[int] = None,
    fornecedor_id: Optional[int] = None,
    nome: Optional[str] = Query(None, description="Busca parcial por nome"),
    apenas_ativos: bool = True,
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros por página"),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    query = db.query(models.Produto)
    if categoria_id:
        query = query.filter(models.Produto.categoria_id == categoria_id)
    if fornecedor_id:
        query = query.filter(models.Produto.fornecedor_id == fornecedor_id)
    if nome:
        query = query.filter(models.Produto.nome.ilike(f"%{nome}%"))
    if apenas_ativos:
        query = query.filter(models.Produto.ativo == True)  # noqa: E712

    total = query.count()
    itens = query.order_by(models.Produto.id).offset(skip).limit(limit).all()
    return Paginado(total=total, skip=skip, limit=limit, itens=itens)


@router.get("/{produto_id}", response_model=schemas.ProdutoOut)
def obter_produto(produto_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    produto = db.query(models.Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.put("/{produto_id}", response_model=schemas.ProdutoOut)
def atualizar_produto(
    produto_id: int,
    produto_in: schemas.ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    produto = db.query(models.Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    dados = produto_in.model_dump(exclude_unset=True)
    _validar_categoria_e_fornecedor(db, dados.get("categoria_id"), dados.get("fornecedor_id"))

    for campo, valor in dados.items():
        setattr(produto, campo, valor)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível atualizar o produto")
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(produto_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_admin)):
    """Exclusao logica: o produto some das listagens padrao mas o historico
    de movimentacoes continua integro (nunca apagamos linha de produto com
    movimentacoes associadas, por integridade do relatorio)."""
    produto = db.query(models.Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.ativo = False
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível excluir o produto")
