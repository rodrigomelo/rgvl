# RGVL - Architecture

## Overview

RGVL is a personal data platform for family history research. It tracks people, companies, properties, legal processes, documents, contacts, and research tasks across 5+ generations of the Lanna family.

## Stack

| Layer | Technology | Port |
|-------|-----------|-------|
| **Web Dashboard** | Flask (static HTML/JS) | 5002 |
| **API** | Flask + SQLAlchemy | 5003 |
| **Database** | SQLite (`data/rgvl.db`) | file |
| **Container** | Docker Compose | - |

## Data Flow

```
docs/
├── INTEL.md         → Base de conhecimento (fonte primária de narrativa)
├── FAMILY_TREE.md   → Resumo genealogia (referência)
└── BUSCAS.md        → Queries pendentes de pesquisa

etl/
├── seed.py                   → Popula DB: pessoas, empresas, relacionamentos, tarefas
└── migrate_to_canonical.py   → Migra dados legados → schema canônico

data/rgvl.db (SQLite — schema canônico único, 12 tabelas)
  └── API (Flask, porta 5003) → Web Dashboard (porta 5002)
```

## Canonical Schema (13 tables)

```
pessoas                  26 rows  — family members
relacionamentos          30 rows  — relationships between people
empresas_familia         10 rows  — family businesses
imoveis                  3 rows  — real estate
legal_processes          9 rows  — court cases (renamed 2026-03-23)
documentos               5 rows  — documents (RG, CPF, certidões)
contatos                 3 rows  — contacts (lawyers, cartório)
events                   9 rows  — life events (RGVL, Henrique — person_id unverified)
eventos                  9 rows  — life events (Rodrigo Melo, Edmundo)
diarios_oficiais          0 rows  — official gazettes
profiles                 1 rows  — online profiles (no API endpoint yet)
buscas_realizadas         0 rows  — search history (empty)
tarefas_pesquisa          5 rows  — research tasks
```

> **Schema note (2026-03-23):** `processos_judiciais` renamed → `legal_processes`. `perfis` renamed → `profiles`. `events` and `eventos` are separate tables — do not confuse them.

## Project Structure

```
rgvl/
├── api/
│   ├── main.py              # App entry, port 5003
│   ├── db.py                # SQLAlchemy engine + session
│   ├── models.py            # 11 entity models (canonical)
│   ├── utils.py             # Serialization helpers
│   └── routes/
│       ├── family.py         # /api/family/*
│       ├── assets.py         # /api/assets/* (companies, properties)
│       ├── legal.py          # /api/legal/*
│       └── research.py       # /api/research/* (tasks, documents, contacts)
├── web/
│   └── index.html            # Single-page dashboard (port 5002)
├── etl/
│   ├── seed.py               # Populate from INTEL.md
│   └── migrate_to_canonical.py # Migrate legacy → canonical
├── docs/
│   ├── INTEL.md              # Knowledge base (canonical narrative source)
│   ├── FAMILY_TREE.md         # Genealogy summary
│   └── BUSCAS.md             # Pending search queries
└── data/
    ├── rgvl.db               # SQLite canonical database
    └── collectors/            # Data source collectors
```

## API Endpoints

### Family (`/api/family`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/family/person/<id>` | Get person by ID |
| GET | `/api/family/person/<id>/relatives` | All relatives of a person |
| GET | `/api/family/person/<id>/tree` | Family tree branch (5 gen) |
| GET | `/api/family/generation/<n>` | List by generation (1-5) |
| GET | `/api/family/summary` | Family statistics |
| GET | `/api/family/events` | Life events (births, deaths, marriages) |

### Assets (`/api/assets`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets/companies` | List companies |
| GET | `/api/assets/companies/<id>` | Company detail |
| GET | `/api/assets/properties` | List properties |
| GET | `/api/assets/properties/<id>` | Property detail |

### Legal (`/api/legal`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/processes` | List judicial processes |
| GET | `/api/legal/processes/<id>` | Process detail |
| GET | `/api/legal/summary` | Process summary by court |

### Research (`/api/research`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/research/tasks` | Research tasks |
| GET | `/api/research/searches` | Search history |
| GET | `/api/research/documents` | Documents (RG, CPF, certidões) |
| GET | `/api/research/contacts` | Contacts (lawyers, relatives) |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Database statistics (11 counters) |
| GET | `/api/search?q=` | Cross-table full-text search |

## Data Model (Canonical)

```sql
pessoas             id, nome_completo, cpf, cnpj, rg, data_nascimento,
                    local_nascimento, data_falecimento,
                    profissao, cargo, empresa,
                    pai_id, mae_id, conjuge_id, data_casamento,
                    geracao (1-5), status, fonte, observacoes

relacionamentos     pessoa_de, pessoa_para, tipo, confirmado (0/1), fonte

empresas_familia    cnpj (unique), nome_fantasia, razao_social,
                    socios (JSON), status_jucemg,
                    capital, data_abertura, data_baixa,
                    pessoa_id → pessoas, fonte

imoveis             address, city, neighborhood, building_name,
                    bedrooms, parking_spaces, area_sqm,
                    owners (JSON), purchase_date, purchase_value,
                    financing_value, itbi, current_value,
                    registration, cartorio, status

processos_judiciais process_number, court, subject,
                    parties (JSON), status, value, filings (JSON)

documentos          doc_type, title, description, file_path,
                    issue_date, expiry_date, fonte

contatos            nome, role, empresa, telefone, email,
                    is_primary, notes, fonte

eventos             person_id, event_type, event_date, description

perfis              source, external_id, name, bio, location,
                    empresa, email, avatar_url, profile_url

buscas_realizadas   fonte, query_usada, resultado (JSON),
                    status, data_busca, proxima_tentativa

tarefas_pesquisa    tarefa, prioridade, pessoa_alvo,
                    fontes_sugeridas, status, resultado
```

## Rules for Agents

1. **Schema canonical**: 12 tabelas em `data/rgvl.db`. Uma única fonte de verdade estruturada.
2. **INTEL.md é a fonte narrativa primária** — dados estruturados vão para o DB via ETL.
3. **DB nunca é editado manualmente** — todas as alterações passam pelo ETL.
4. **API serve na porta 5003** — web na 5002 faz proxy. O dashboard não acessa DB direto.
5. **LGPD**: Apenas dados públicos. Sem saúde, finanças pessoais, ou comunicações privadas.
6. **Não mascarar dados** — CPFs, CNPJs e outros identificadores são mostrados completos.
