"""
RGVL - SQLAlchemy Models

Canonical data model for the Lanna family research platform.
Based on the family tree spanning 5+ generations.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Pessoa(Base):
    """Person — core entity of the family tree."""
    __tablename__ = 'pessoas'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identity
    nome_completo = Column(String(255), nullable=False)
    nome_anterior = Column(String(255))  # Maiden name or previous name

    # Dates & Location
    data_nascimento = Column(String(10))  # YYYY-MM-DD
    local_nascimento = Column(String(255))
    data_falecimento = Column(String(10))

    # Documents
    cpf = Column(String(14), unique=True)
    cnpj = Column(String(18))
    rg = Column(String(20))

    # Contact
    email = Column(String(255))
    telefone = Column(String(30))
    endereco = Column(Text)

    # Profession
    profissao = Column(String(255))
    cargo = Column(String(255))
    empresa = Column(String(255))

    # Genealogy
    pai_id = Column(Integer, ForeignKey('pessoas.id'))
    mae_id = Column(Integer, ForeignKey('pessoas.id'))
    conjuge_id = Column(Integer, ForeignKey('pessoas.id'))
    data_casamento = Column(String(10))

    # Metadata
    status = Column(String(20), default='ativo')
    geracao = Column(Integer)  # 1=children, 2=RGVL, 3=siblings, 4=parents, 5=grandparents

    # Provenance
    fonte = Column(String(255))
    observacoes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pai = relationship('Pessoa', foreign_keys=[pai_id], remote_side=[id])
    mae = relationship('Pessoa', foreign_keys=[mae_id], remote_side=[id])
    conjuge = relationship('Pessoa', foreign_keys=[conjuge_id], remote_side=[id])
    empresas = relationship('Empresa', back_populates='responsavel')

    # Indexes
    __table_args__ = (
        Index('idx_pessoas_nome', 'nome_completo'),
        Index('idx_pessoas_cpf', 'cpf'),
        Index('idx_pessoas_geracao', 'geracao'),
    )


class Relacionamento(Base):
    """Relationship between two people."""
    __tablename__ = 'relacionamentos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    pessoa_de = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    pessoa_para = Column(Integer, ForeignKey('pessoas.id'), nullable=False)

    tipo = Column(String(20), nullable=False)
    confirmado = Column(Integer, default=0)  # 0=speculative, 1=confirmed
    fonte = Column(String(255))
    observacao = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            tipo.in_([
                'pai', 'mae', 'filho', 'filha',
                'irmao', 'irma', 'conjuge',
                'tio', 'tia', 'sobrinho', 'sobrinha',
                'avo_pai', 'avo_mae', 'neto', 'neta',
                'primo', 'prima', 'genro', 'nora',
                'sogro', 'sogra', 'cunhado', 'cunhada'
            ]),
            name='ck_relacionamento_tipo'
        ),
    )


class Empresa(Base):
    """Company linked to a family member."""
    __tablename__ = 'empresas_familia'

    id = Column(Integer, primary_key=True, autoincrement=True)

    cnpj = Column(String(18), unique=True, nullable=False)
    nome_fantasia = Column(String(255))
    razao_social = Column(String(255))
    natureza_juridica = Column(String(255))

    # Address
    endereco = Column(Text)
    cidade = Column(String(100))
    uf = Column(String(2), default='MG')

    # Partners (JSON string)
    socios = Column(Text)

    # Status
    status_jucemg = Column(String(20))
    data_abertura = Column(String(10))
    data_baixa = Column(String(10))
    capital = Column(Float)

    # Link to family
    pessoa_id = Column(Integer, ForeignKey('pessoas.id'))

    fonte = Column(String(255))
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    responsavel = relationship('Pessoa', back_populates='empresas')

    __table_args__ = (
        Index('idx_empresas_cnpj', 'cnpj'),
        Index('idx_empresas_pessoa', 'pessoa_id'),
    )


class BuscaRealizada(Base):
    """Record of a search performed against a data source."""
    __tablename__ = 'buscas_realizadas'

    id = Column(Integer, primary_key=True, autoincrement=True)

    fonte = Column(String(100), nullable=False)  # FamilySearch, JUCEMG, Receita Federal, etc.
    query_usada = Column(Text)
    resultado = Column(Text)  # JSON
    status = Column(String(20), default='pendente')
    data_busca = Column(DateTime, default=datetime.utcnow)
    proxima_tentativa = Column(DateTime)

    __table_args__ = (
        Index('idx_buscas_fonte', 'fonte'),
    )


class TarefaPesquisa(Base):
    """A pending research task."""
    __tablename__ = 'tarefas_pesquisa'

    id = Column(Integer, primary_key=True, autoincrement=True)

    tarefa = Column(Text, nullable=False)
    prioridade = Column(String(10))
    pessoa_alvo = Column(String(255))
    fontes_sugeridas = Column(Text)
    status = Column(String(20), default='pendente')
    resultado = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
