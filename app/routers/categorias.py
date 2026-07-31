from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_usuario_atual, get_usuario_admin
from app.pagination import Paginado

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=schemas.CategoriaOut, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    categoria_in: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    if db.query(models.Categoria).filter(models.Categoria.nome == categoria_in.nome).first():
        raise HTTPException(status_code=400, detail="Categoria já existe")
    categoria = models.Categoria(**categoria_in.model_dump())
    try:
        db.add(categoria)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar a categoria")
    db.refresh(categoria)
    return categoria


@router.get("/", response_model=Paginado[schemas.CategoriaOut])
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    query = db.query(models.Categoria).order_by(models.Categoria.id)
    total = query.count()
    itens = query.offset(skip).limit(limit).all()
    return Paginado(total=total, skip=skip, limit=limit, itens=itens)


@router.get("/{categoria_id}", response_model=schemas.CategoriaOut)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    categoria = db.query(models.Categoria).get(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.put("/{categoria_id}", response_model=schemas.CategoriaOut)
def atualizar_categoria(
    categoria_id: int,
    categoria_in: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    categoria = db.query(models.Categoria).get(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for campo, valor in categoria_in.model_dump().items():
        setattr(categoria, campo, valor)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível atualizar a categoria")
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_admin)):
    categoria = db.query(models.Categoria).get(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    try:
        db.delete(categoria)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Não foi possível excluir a categoria (verifique se há produtos vinculados)",
        )
