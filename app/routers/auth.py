from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(usuario_in: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(models.Usuario).filter(models.Usuario.email == usuario_in.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # Bootstrap: como toda rota de escrita de dados mestres exige admin,
    # e não existe outra forma de promover alguém a admin nesta API,
    # o primeiro usuário cadastrado no sistema recebe is_admin automaticamente.
    # Cadastros seguintes entram como usuário comum (is_admin=False, default).
    primeiro_usuario = db.query(models.Usuario).count() == 0

    usuario = models.Usuario(
        nome=usuario_in.nome,
        email=usuario_in.email,
        senha_hash=security.hash_senha(usuario_in.senha),
        is_admin=primeiro_usuario,
    )
    try:
        db.add(usuario)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar o usuário")
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=schemas.Token)
def login(dados: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == dados.email).first()

    if not usuario or not security.verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    access_token = security.criar_access_token(data={"sub": str(usuario.id)})
    refresh_token = security.criar_refresh_token(data={"sub": str(usuario.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
def refresh(dados: schemas.RefreshRequest, db: Session = Depends(get_db)):
    """Troca um refresh token válido por um novo par de tokens, sem exigir
    login/senha de novo. É assim que um app consegue manter a sessão viva
    por dias sem guardar a senha do usuário nem usar um access token de
    vida longa (que seria mais perigoso se vazasse)."""
    payload = security.decodificar_token(dados.refresh_token, tipo_esperado="refresh")
    if payload is None:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    usuario_id = payload.get("sub")
    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")

    novo_access_token = security.criar_access_token(data={"sub": str(usuario.id)})
    novo_refresh_token = security.criar_refresh_token(data={"sub": str(usuario.id)})
    return {"access_token": novo_access_token, "refresh_token": novo_refresh_token, "token_type": "bearer"}
