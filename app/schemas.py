from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import TipoMovimentacao


# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_admin: bool
    ativo: bool
    criado_em: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


# ---------- Categoria ----------
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaOut(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Fornecedor ----------
class FornecedorBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorOut(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Produto ----------
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    descricao: Optional[str] = None
    preco: Decimal = Field(..., ge=0, decimal_places=2, max_digits=10)
    estoque_minimo: int = Field(0, ge=0)
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None


class ProdutoCreate(ProdutoBase):
    quantidade_estoque: int = Field(0, ge=0)


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = Field(None, ge=0, decimal_places=2, max_digits=10)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    ativo: Optional[bool] = None


class ProdutoOut(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantidade_estoque: int
    ativo: bool
    criado_em: datetime
    categoria: Optional[CategoriaOut] = None
    fornecedor: Optional[FornecedorOut] = None


# ---------- Movimentacao ----------
class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(..., gt=0)
    motivo: Optional[str] = None
    # Opcional: se não informado, a API usa a data/hora real da requisição.
    # Útil para registrar movimentações retroativas (ex: migração de dados históricos).
    data: Optional[datetime] = None
    # Opcional: nome livre de quem executou a movimentação no mundo real.
    # O responsável "oficial" continua sendo o usuário autenticado (usuario_id).
    responsavel_nome: Optional[str] = None


class MovimentacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: TipoMovimentacao
    quantidade: int
    motivo: Optional[str]
    data: datetime
    responsavel_nome: Optional[str] = None
    produto_id: int
    usuario_id: int


# ---------- Relatorios ----------
class ProdutoEstoqueBaixo(BaseModel):
    id: int
    nome: str
    quantidade_estoque: int
    estoque_minimo: int


class ResumoEstoque(BaseModel):
    total_produtos: int
    valor_total_estoque: Decimal
    produtos_estoque_baixo: List[ProdutoEstoqueBaixo]
