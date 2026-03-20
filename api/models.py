"""
RGVL - SQLAlchemy Models

Canonical data model for the Lanna family research platform.
All tables are part of the canonical schema (single source of truth).
Old tables (persons, companies, etc.) have been migrated into these models.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# FAMILY
# =============================================================================

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

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    pai = relationship('Pessoa', foreign_keys=[pai_id], remote_side=[id])
    mae = relationship('Pessoa', foreign_keys=[mae_id], remote_side=[id])
    conjuge = relationship('Pessoa', foreign_keys=[conjuge_id], remote_side=[id])
    empresas = relationship('Empresa', back_populates='responsavel')

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

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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


# =============================================================================
# ASSETS — COMPANIES & PROPERTIES
# =============================================================================

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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    responsavel = relationship('Pessoa', back_populates='empresas')

    __table_args__ = (
        Index('idx_empresas_cnpj', 'cnpj'),
        Index('idx_empresas_pessoa', 'pessoa_id'),
    )


class Imovel(Base):
    """Real estate property (apartments, houses, land)."""
    __tablename__ = 'imoveis'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Property type and location
    property_type = Column(String(50))           # e.g. "Apartamento"
    address = Column(String(500))                # Full street address
    city = Column(String(100))                   # e.g. "Belo Horizonte"
    state = Column(String(2))                    # e.g. "MG"
    neighborhood = Column(String(100))            # e.g. "Savassi"
    registration = Column(String(50))             # Matrícula do cartório
    cartorio = Column(String(255))                # Nome do cartório
    cnm = Column(String(50))                      # Código Nacional da Matrícula

    # Building details
    building_name = Column(String(255))          # Nome do edifício
    floor = Column(String(20))                   # Andar / apartamento

    # Areas (in square meters)
    area_sqm = Column(Float)                      # Área privativa
    area_common = Column(Float)                  # Área comum
    area_total = Column(Float)                   # Área total

    # Rooms
    bedrooms = Column(Integer)                   # Número de quartos
    parking_spaces = Column(Integer)             # Número de vagas
    parking_boxes = Column(String(100))           # Identificação das vagas

    # Ownership (JSON list of owner names)
    owners = Column(Text)

    # Financial
    purchase_date = Column(String(20))            # Date of purchase
    purchase_value = Column(Float)               # Valor de compra
    financing_value = Column(Float)               # Valor do financiamento (SFH)
    itbi = Column(Float)                         # Valor do ITBI
    fiscal_value = Column(Float)                  # Valor fiscal (IPTU base)
    current_value = Column(Float)                # Valor estimado de mercado

    # Status
    status = Column(String(50))                  # e.g. "paid_off", "mortgaged"
    description = Column(Text)                   # Additional notes

    # Provenance
    fonte = Column(String(255))
    annotations = Column(Text)                   # JSON metadata
    raw_data = Column(Text)                      # JSON original data
    collected_at = Column(DateTime)              # When data was collected

    __table_args__ = (
        Index('idx_imoveis_endereco', 'address'),
        Index('idx_imoveis_cidade', 'city'),
        Index('idx_imoveis_matricula', 'registration'),
    )


# =============================================================================
# LEGAL
# =============================================================================

class ProcessoJudicial(Base):
    """Judicial process involving a family member."""
    __tablename__ = 'processos_judiciais'

    id = Column(Integer, primary_key=True, autoincrement=True)

    process_number = Column(String(50))          # Número do processo
    court = Column(String(50))                   # Tribunal (TJMG, TRT3, etc.)
    subject = Column(Text)                       # Tema (Trabalhista, Paternidade, etc.)
    parties = Column(Text)                       # JSON — {autores: [], reus: [], papel_rgvl: ''}
    status = Column(String(100))                # Concluído, Em andamento, etc.
    value = Column(Float)                        # Valor da causa

    # Filings / andamentos
    filings = Column(Text)                        # JSON array of {date, description}

    # Provenance
    fonte = Column(String(255))
    raw_data = Column(Text)                       # JSON original
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_processos_numero', 'process_number'),
        Index('idx_processos_court', 'court'),
    )


# =============================================================================
# DOCUMENTS & CONTACTS
# =============================================================================

class Documento(Base):
    """Document related to a family member (RG, CPF, certidões, etc.)."""
    __tablename__ = 'documentos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    doc_type = Column(String(50))               # rg, cpf, birth_certificate, escritura, etc.
    title = Column(String(255))                 # Title/label
    description = Column(Text)                   # Description
    file_path = Column(String(500))              # Local file path
    issue_date = Column(DateTime)                # Data de emissão
    expiry_date = Column(DateTime)               # Data de expiração (se aplicável)

    # Provenance
    fonte = Column(String(50))                   # Source (father_drive, cartorio, etc.)
    raw_data = Column(Text)                      # JSON original
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_documentos_tipo', 'doc_type'),
    )


class Contato(Base):
    """Contact (lawyers, relatives, institutions)."""
    __tablename__ = 'contatos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String(255))                  # Nome completo
    role = Column(String(100))                   # Papel (Advogado, Cartório, etc.)
    empresa = Column(String(255))                # Empresa/Instituição

    # Contact info
    telefone = Column(String(30))
    email = Column(String(255))

    # Metadata
    is_primary = Column(Boolean, default=False)
    notes = Column(Text)
    fonte = Column(String(50))                   # Source (father_drive, INTEL, etc.)

    # Provenance
    raw_data = Column(Text)                      # JSON original
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_contatos_nome', 'nome'),
        Index('idx_contatos_role', 'role'),
    )


# =============================================================================
# OFFICIAL GAZETTES & PROFILES
# =============================================================================

class DiarioOficial(Base):
    """Publication in an official gazette (Diário Oficial)."""
    __tablename__ = 'diarios_oficiais'

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = Column(String(20))                 # Diário Oficial da União, Estado de MG, etc.
    publication_date = Column(DateTime)         # Data de publicação
    edition = Column(String(20))                 # Edição/número
    section = Column(String(50))                # Seção (Economia, Pessoal, etc.)
    page = Column(String(20))                   # Página
    title = Column(String(500))                 # Título da publicação
    content = Column(Text)                      # Conteúdo resumido
    url = Column(String(500))                   # Link para publicação

    # Tags
    tags = Column(Text)                          # JSON array of strings

    # Provenance
    fonte = Column(String(50))
    raw_data = Column(Text)                      # JSON original
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_diarios_data', 'publication_date'),
        Index('idx_diarios_source', 'source'),
    )


class Perfil(Base):
    """Online profile found during research (LinkedIn, FamilySearch, etc.)."""
    __tablename__ = 'perfis'

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = Column(String(50))                  # Source platform (father_drive, LinkedIn, FamilySearch, etc.)
    external_id = Column(String(100))            # External ID on that platform
    name = Column(String(255))                  # Full name on the platform
    bio = Column(Text)                          # Bio/description
    location = Column(String(255))              # Location
    empresa = Column(String(255))               # Current company
    email = Column(String(255))                 # Email (if public)
    avatar_url = Column(String(500))            # Profile picture URL
    profile_url = Column(String(500))           # Direct URL to profile

    # Provenance
    raw_data = Column(Text)                      # JSON original
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_perfis_source', 'source'),
        Index('idx_perfis_name', 'name'),
    )


# =============================================================================
# EVENTS
# =============================================================================

class Evento(Base):
    """Life event (birth, death, marriage, career milestone)."""
    __tablename__ = 'eventos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    person_id = Column(Integer, ForeignKey('pessoas.id'), nullable=True)
    event_type = Column(String(50))                         # birth, death, marriage, company, etc.
    event_date = Column(String(20))                         # YYYY-MM-DD or YYYY
    description = Column(Text)                               # Human-readable description

    # Provenance
    reference_table = Column(String(50))                     # Source table (pessoas, empresas, etc.)
    reference_id = Column(Integer)                          # Source row ID
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_eventos_pessoa', 'person_id'),
        Index('idx_eventos_tipo', 'event_type'),
    )


# =============================================================================
# RESEARCH TRACKING
# =============================================================================

class BuscaRealizada(Base):
    """Record of a search performed against a data source."""
    __tablename__ = 'buscas_realizadas'

    id = Column(Integer, primary_key=True, autoincrement=True)

    fonte = Column(String(100), nullable=False)  # FamilySearch, JUCEMG, Receita Federal, etc.
    query_usada = Column(Text)
    resultado = Column(Text)                     # JSON
    status = Column(String(20), default='pendente')
    data_busca = Column(DateTime, default=lambda: datetime.now(timezone.utc))
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

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
