import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# Em producao, defina SECRET_KEY como variavel de ambiente forte e secreta.
# Nunca deixe uma chave fixa em codigo indo para producao real.
SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def _criar_token(data: dict, expires_delta: timedelta, tipo: str) -> str:
    """Monta um JWT com um claim 'type' (access/refresh), para que um refresh
    token roubado não possa ser usado como se fosse um access token e vice-versa."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": tipo})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return _criar_token(
        data, expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), tipo="access"
    )


def criar_refresh_token(data: dict) -> str:
    return _criar_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), tipo="refresh")


def decodificar_token(token: str, tipo_esperado: str = "access") -> Optional[dict]:
    """Decodifica o token e confere se o tipo bate com o esperado.
    Um token de refresh usado numa rota normal (ou vice-versa) é rejeitado aqui,
    mesmo que a assinatura seja válida."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    if payload.get("type") != tipo_esperado:
        return None
    return payload
