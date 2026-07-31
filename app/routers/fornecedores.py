from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_usuario_atual, get_usuario_admin
from app.pagination import Paginado

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.post("/", response_model=schemas.FornecedorOut, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
    fornecedor_in: schemas.FornecedorCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    fornecedor = models.Fornecedor(**fornecedor_in.model_dump())
    try:
        db.add(fornecedor)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar o fornecedor")
    db.refresh(fornecedor)
    return fornecedor


@router.get("/", response_model=Paginado[schemas.FornecedorOut])
def listar_fornecedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    query = db.query(models.Fornecedor).order_by(models.Fornecedor.id)
    total = query.count()
    itens = query.offset(skip).limit(limit).all()
    return Paginado(total=total, skip=skip, limit=limit, itens=itens)


@router.get("/{fornecedor_id}", response_model=schemas.FornecedorOut)
def obter_fornecedor(fornecedor_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    fornecedor = db.query(models.Fornecedor).get(fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor


@router.put("/{fornecedor_id}", response_model=schemas.FornecedorOut)
def atualizar_fornecedor(
    fornecedor_id: int,
    fornecedor_in: schemas.FornecedorCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_admin),
):
    fornecedor = db.query(models.Fornecedor).get(fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    for campo, valor in fornecedor_in.model_dump().items():
        setattr(fornecedor, campo, valor)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível atualizar o fornecedor")
    db.refresh(fornecedor)
    return fornecedor


@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_admin)):
    fornecedor = db.query(models.Fornecedor).get(fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    try:
        db.delete(fornecedor)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Não foi possível excluir o fornecedor (verifique se há produtos vinculados)",
        )
