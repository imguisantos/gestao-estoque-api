from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.security import decodificar_token

# auto_error=False: por padrão o HTTPBearer responde 403 quando nenhum token
# é enviado, o que não é semanticamente correto (403 é "autenticado mas sem
# permissão"; a ausência de credenciais é 401 "não autenticado"). Desligamos
# o comportamento automático e levantamos o 401 nós mesmos logo abaixo.
security_scheme = HTTPBearer(auto_error=False)


def get_usuario_atual(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> models.Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciais is None:
        raise credenciais_invalidas

    token = credenciais.credentials
    payload = decodificar_token(token, tipo_esperado="access")
    if payload is None:
        raise credenciais_invalidas

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise credenciais_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas

    return usuario


def get_usuario_admin(usuario: models.Usuario = Depends(get_usuario_atual)) -> models.Usuario:
    if not usuario.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar esta ação",
        )
    return usuario