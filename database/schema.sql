-- ================================================
-- RGVL - ÁRVORE GENEALÓGICA - ESTRUTURA DO BANCO
-- Created: 2026-03-19
-- Agent: Poseidon (Data Architect)
-- ================================================

-- ================================================
-- TABELA: pessoas
-- ================================================
CREATE TABLE IF NOT EXISTS pessoas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificação
    nome_completo   TEXT NOT NULL,
    nome_anterior   TEXT,              -- Nome de solteiro,caso mudanca
    
    -- Datas e Local
    data_nascimento TEXT,               -- formato: YYYY-MM-DD
    local_nascimento TEXT,             -- Cidade/UF
    data_falecimento TEXT,             -- formato: YYYY-MM-DD (se falecido)
    
    -- Documentos
    cpf             TEXT UNIQUE,
    cnpj            TEXT,               -- Se tiver empresa propia
    
    -- Contato
    email           TEXT,
    telefone        TEXT,
    endereco        TEXT,
    
    -- Profissão
    profissao       TEXT,
    cargo           TEXT,
    empresa         TEXT,
    
    -- Genealogia
    pai_id          INTEGER REFERENCES pessoas(id),
    mae_id          INTEGER REFERENCES pessoas(id),
    
    -- Relacionamento
    conjuge_id      INTEGER REFERENCES pessoas(id),
    data_casamento  TEXT,
    
    -- Metadados
    Status          TEXT DEFAULT 'ativo' CHECK(Status IN ('ativo','falecido','desconhecido','nao_encontrado')),
    geracao         INTEGER,           -- 1=Avós, 2=Pais, 3=Irmãos, 4=RGVL, 5=Filhos, 6=Netos
    
    -- Fontes
    fonte           TEXT,               -- Receita Federal, JUCEMG, FamilySearch, TJMG, etc
    observacoes     TEXT,
    
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: relacionamentos
-- ================================================
CREATE TABLE IF NOT EXISTS relacionamentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_de       INTEGER REFERENCES pessoas(id),
    pessoa_para     INTEGER REFERENCES pessoas(id),
    tipo            TEXT NOT NULL CHECK(tipo IN (
                        'pai','mae',
                        'filho','filha',
                        'irmao','irma',
                        'conjuge',
                        'tio','tia',
                        'sobrinho','sobrinha',
                        'avô','avó',
                        'neto','neta',
                        'primo','prima'
                    )),
    confirmado      INTEGER DEFAULT 0,   -- 0=Speculativo, 1=Confirmado
    fonte           TEXT,
    observacao      TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: empresas_familia
-- ================================================
CREATE TABLE IF NOT EXISTS empresas_familia (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj            TEXT UNIQUE NOT NULL,
    nome_fantasia   TEXT,
    razao_social    TEXT,
    natureza_juridica TEXT,
    
    -- Endereço
    endereco        TEXT,
    cidade          TEXT,
    uf              TEXT DEFAULT 'MG',
    
    -- Sócios
    socios          TEXT,               -- JSON: [{"nome": "...", "participacao": "50%"}]
    
    -- Status
    status_jucemg   TEXT CHECK(status_jucemg IN ('ativa','baixa','inapta','extinta')),
    data_abertura   TEXT,
    data_baixa      TEXT,
    
    -- Ligação familiar
    pessoa_id       INTEGER REFERENCES pessoas(id),
    
    fonte           TEXT,
    observacoes     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- TABELA: buscas_realizadas
-- ================================================
CREATE TABLE IF NOT EXISTS buscas_realizadas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte           TEXT NOT NULL,      -- Receita Federal, JUCEMG, FamilySearch, etc
    query_usada     TEXT,               -- O que foi buscado
    resultado       TEXT,               -- JSON com resultados
    status          TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','sucesso','sem_resultado','erro')),
    data_busca      TEXT DEFAULT CURRENT_TIMESTAMP,
    proxima_tentativa TEXT             -- Para retries
);

-- ================================================
-- TABELA: tarefas_pesquisa
-- ================================================
CREATE TABLE IF NOT EXISTS tarefas_pesquisa (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa          TEXT NOT NULL,
    prioridade      TEXT CHECK(prioridade IN ('ALTA','MEDIA','BAIXA')),
    pessoa_alvo     TEXT,               -- Nome da pessoa a pesquisar
    fontes_sugeridas TEXT,             -- Quais fontes usar
    status          TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','em_andamento','concluido','bloqueado')),
    resultado        TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- ÍNDICES para performance
-- ================================================
CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome_completo);
CREATE INDEX IF NOT EXISTS idx_pessoas_cpf ON pessoas(cpf);
CREATE INDEX IF NOT EXISTS idx_pessoas_pai ON pessoas(pai_id);
CREATE INDEX IF NOT EXISTS idx_pessoas_mae ON pessoas(mae_id);
CREATE INDEX IF NOT EXISTS idx_empresas_cnpj ON empresas_familia(cnpj);
CREATE INDEX IF NOT EXISTS idx_buscas_fonte ON buscas_realizadas(fonte);
