-- ================================================
-- RGVL - Canonical Schema (12 tables)
-- Updated: 2026-03-20
-- Reference: api/models.py (source of truth)
-- ================================================

-- ================================================
-- TABELA: pessoas (26 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS pessoas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo   TEXT NOT NULL,
    nome_anterior   TEXT,
    data_nascimento TEXT,
    local_nascimento TEXT,
    data_falecimento TEXT,
    cpf             TEXT UNIQUE,
    cnpj            TEXT,
    rg              TEXT,
    email           TEXT,
    telefone        TEXT,
    endereco        TEXT,
    profissao       TEXT,
    cargo           TEXT,
    empresa         TEXT,
    pai_id          INTEGER REFERENCES pessoas(id),
    mae_id          INTEGER REFERENCES pessoas(id),
    conjuge_id      INTEGER REFERENCES pessoas(id),
    data_casamento  TEXT,
    status          TEXT DEFAULT 'ativo',
    geracao         INTEGER,           -- 1=cousins, 2=RGVL, 3=parents/siblings, 4=grandparents, 5=great-grandparents
    fonte           TEXT,
    observacoes     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: relacionamentos (30 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS relacionamentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_de       INTEGER REFERENCES pessoas(id) NOT NULL,
    pessoa_para     INTEGER REFERENCES pessoas(id) NOT NULL,
    tipo            TEXT NOT NULL CHECK(tipo IN (
                        'pai','mae','filho','filha',
                        'irmao','irma','conjuge',
                        'tio','tia','sobrinho','sobrinha',
                        'avo_pai','avo_mae','neto','neta',
                        'primo','prima','genro','nora',
                        'sogro','sogra','cunhado','cunhada'
                    )),
    confirmado      INTEGER DEFAULT 0,
    fonte           TEXT,
    observacao      TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: empresas_familia (10 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS empresas_familia (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj            TEXT UNIQUE NOT NULL,
    nome_fantasia   TEXT,
    razao_social    TEXT,
    natureza_juridica TEXT,
    endereco        TEXT,
    cidade          TEXT,
    uf              TEXT DEFAULT 'MG',
    socios          TEXT,               -- JSON
    status_jucemg   TEXT,
    data_abertura   TEXT,
    data_baixa      TEXT,
    capital         REAL,
    pessoa_id       INTEGER REFERENCES pessoas(id),
    fonte           TEXT,
    observacoes     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: imoveis (2 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS imoveis (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    property_type   TEXT,
    address         TEXT,
    city            TEXT,
    state           TEXT,
    neighborhood    TEXT,
    registration    TEXT,
    cartorio        TEXT,
    cnm             TEXT,
    building_name   TEXT,
    floor           TEXT,
    area_sqm        REAL,
    area_common     REAL,
    area_total      REAL,
    bedrooms        INTEGER,
    parking_spaces  INTEGER,
    parking_boxes   TEXT,
    owners          TEXT,               -- JSON
    purchase_date   TEXT,
    purchase_value  REAL,
    financing_value REAL,
    itbi            REAL,
    fiscal_value    REAL,
    current_value   REAL,
    status          TEXT,
    description     TEXT,
    fonte           TEXT,
    annotations     TEXT,               -- JSON
    raw_data        TEXT,               -- JSON
    collected_at    TEXT
);

-- ================================================
-- TABELA: processos_judiciais (9 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS processos_judiciais (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    process_number  TEXT,
    court           TEXT,
    subject         TEXT,
    parties         TEXT,               -- JSON
    status          TEXT,
    value           REAL,
    filings         TEXT,               -- JSON
    fonte           TEXT,
    raw_data        TEXT,               -- JSON
    collected_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: documentos (7 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS documentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type        TEXT,
    title           TEXT,
    description     TEXT,
    file_path       TEXT,
    issue_date      TEXT,
    expiry_date     TEXT,
    fonte           TEXT,
    raw_data        TEXT,               -- JSON
    collected_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: contatos (4 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS contatos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT,
    role            TEXT,
    empresa         TEXT,
    telefone        TEXT,
    email           TEXT,
    is_primary      INTEGER DEFAULT 0,
    notes           TEXT,
    fonte           TEXT,
    raw_data        TEXT,               -- JSON
    collected_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: eventos (9 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS eventos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id       INTEGER REFERENCES pessoas(id),
    event_type      TEXT,
    event_date      TEXT,
    description     TEXT,
    reference_table TEXT,
    reference_id    INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: diarios_oficiais (0 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS diarios_oficiais (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT,
    publication_date TEXT,
    edition         TEXT,
    section         TEXT,
    page            TEXT,
    title           TEXT,
    content         TEXT,
    url             TEXT,
    tags            TEXT,               -- JSON
    fonte           TEXT,
    raw_data        TEXT,               -- JSON
    collected_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: perfis (1 row)
-- ================================================
CREATE TABLE IF NOT EXISTS perfis (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT,
    external_id     TEXT,
    name            TEXT,
    bio             TEXT,
    location        TEXT,
    empresa         TEXT,
    email           TEXT,
    avatar_url      TEXT,
    profile_url     TEXT,
    raw_data        TEXT,               -- JSON
    collected_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: buscas_realizadas (0 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS buscas_realizadas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte           TEXT NOT NULL,
    query_usada     TEXT,
    resultado       TEXT,               -- JSON
    status          TEXT DEFAULT 'pendente',
    data_busca      TEXT DEFAULT CURRENT_TIMESTAMP,
    proxima_tentativa TEXT
);

-- ================================================
-- TABELA: tarefas_pesquisa (5 rows)
-- ================================================
CREATE TABLE IF NOT EXISTS tarefas_pesquisa (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa          TEXT NOT NULL,
    prioridade      TEXT,
    pessoa_alvo     TEXT,
    fontes_sugeridas TEXT,
    status          TEXT DEFAULT 'pendente',
    resultado       TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- ÍNDICES
-- ================================================
CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome_completo);
CREATE INDEX IF NOT EXISTS idx_pessoas_cpf ON pessoas(cpf);
CREATE INDEX IF NOT EXISTS idx_pessoas_geracao ON pessoas(geracao);
CREATE INDEX IF NOT EXISTS idx_pessoas_pai ON pessoas(pai_id);
CREATE INDEX IF NOT EXISTS idx_pessoas_mae ON pessoas(mae_id);
CREATE INDEX IF NOT EXISTS idx_empresas_cnpj ON empresas_familia(cnpj);
CREATE INDEX IF NOT EXISTS idx_empresas_pessoa ON empresas_familia(pessoa_id);
CREATE INDEX IF NOT EXISTS idx_imoveis_endereco ON imoveis(address);
CREATE INDEX IF NOT EXISTS idx_imoveis_cidade ON imoveis(city);
CREATE INDEX IF NOT EXISTS idx_imoveis_matricula ON imoveis(registration);
CREATE INDEX IF NOT EXISTS idx_processos_numero ON processos_judiciais(process_number);
CREATE INDEX IF NOT EXISTS idx_processos_court ON processos_judiciais(court);
CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(doc_type);
CREATE INDEX IF NOT EXISTS idx_contatos_nome ON contatos(nome);
CREATE INDEX IF NOT EXISTS idx_contatos_role ON contatos(role);
CREATE INDEX IF NOT EXISTS idx_eventos_pessoa ON eventos(person_id);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(event_type);
CREATE INDEX IF NOT EXISTS idx_diarios_data ON diarios_oficiais(publication_date);
CREATE INDEX IF NOT EXISTS idx_diarios_source ON diarios_oficiais(source);
CREATE INDEX IF NOT EXISTS idx_perfis_source ON perfis(source);
CREATE INDEX IF NOT EXISTS idx_perfis_name ON perfis(name);
CREATE INDEX IF NOT EXISTS idx_buscas_fonte ON buscas_realizadas(fonte);
