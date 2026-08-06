import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime,
    ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    movimentacoes = relationship("Movimentacao", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)

    produtos = relationship("Produto", back_populates="categoria")


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    produtos = relationship("Produto", back_populates="fornecedor")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    # Numeric em vez de Float: Float usa ponto flutuante binário, que não
    # representa exatamente valores decimais (ex: 0.1 + 0.2 != 0.3 em Python).
    # Numeric(10, 2) guarda o valor exato, essencial para dinheiro.
    preco = Column(Numeric(10, 2), nullable=False, default=0)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)

    categoria = relationship("Categoria", back_populates="produtos")
    fornecedor = relationship("Fornecedor", back_populates="produtos")
    movimentacoes = relationship("Movimentacao", back_populates="produto")


class Movimentacao(Base):
    """Toda entrada ou saída de estoque gera um registro aqui.
    A quantidade em Produto.quantidade_estoque é sempre recalculada
    a partir dessas movimentações, nunca editada diretamente por outra rota.
    """
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    data = Column(DateTime, default=datetime.utcnow)
    # Nome livre de quem executou a movimentação no mundo real (ex: "Carlos Henrique"),
    # distinto do usuario_id (que é sempre quem estava logado na API). Útil para
    # registrar operações feitas por alguém que não tem conta no sistema, ou para
    # popular dados de exemplo com responsáveis variados.
    responsavel_nome = Column(String(150), nullable=True)

    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    produto = relationship("Produto", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")
