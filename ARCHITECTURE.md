# RGVL - Architecture

## Overview

RGVL is a personal data platform for family history research. It tracks people, companies, properties, legal processes, and research tasks across 5+ generations of the Lanna family.

## Stack

| Layer | Technology | Port |
|-------|-----------|------|
| **Web Dashboard** | Flask (static HTML/JS) | 5002 |
| **API** | Flask + SQLAlchemy | 5003 |
| **Database** | SQLite (`data/rgvl.db`) | file |
| **Container** | Docker Compose | - |

## Project Structure

```
rgvl/
├── api/                    # REST API (Flask)
│   ├── main.py             # App entry, port 5003
│   ├── db.py               # SQLAlchemy engine + session
│   ├── models.py           # All entity models
│   ├── utils.py            # Serialization helpers
│   └── routes/             # Endpoint blueprints
│       ├── family.py       # /api/family/* — people, tree
│       ├── assets.py       # /api/assets/* — companies, properties
│       ├── legal.py        # /api/legal/* — processes
│       └── research.py     # /api/research/* — searches, tasks
├── web/                    # Dashboard (Flask serving HTML)
│   ├── server.py           # Port 5002, proxies to API
│   └── index.html          # Single-page dashboard
├── etl/                    # Data ingestion
│   └── seed.py             # Populate DB from INTEL.md + sources
├── database/
│   └── schema.sql          # Canonical DDL (reference)
├── docs/
│   ├── INTEL.md            # Knowledge base (research data)
│   ├── FAMILY_TREE.md      # Genealogy reference
│   └── BUSCAS.md           # Search history
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── ARCHITECTURE.md         # This file
```

## Data Model

### Core Entities

```
pessoas (people)
├── id, nome_completo, cpf, cnpj
├── data_nascimento, local_nascimento, data_falecimento
├── profissao, cargo, empresa
├── pai_id → pessoas(id), mae_id → pessoas(id)
├── conjuge_id → pessoas(id)
├── geracao (1-6), Status (ativo/falecido/desconhecido)
├── fonte, observacoes
└── timestamps

relacionamentos (relationships)
├── pessoa_de → pessoas(id)
├── pessoa_para → pessoas(id)
├── tipo (pai/mae/irmao/conjuge/tio/sobrinho/primo/...)
├── confirmado (0=speculative, 1=confirmed)
└── fonte

empresas_familia (family companies)
├── cnpj, nome_fantasia, razao_social
├── socios (JSON), status_jucemg
├── pessoa_id → pessoas(id)
└── fonte

buscas_realizadas (search history)
├── fonte, query_usada, resultado (JSON)
├── status, data_busca
└── proxima_tentativa

tarefas_pesquisa (research tasks)
├── tarefa, prioridade, pessoa_alvo
├── fontes_sugeridas, status, resultado
└── timestamps
```

## API Endpoints

### Family (`/api/family`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/family/person/:id` | Get person by ID |
| GET | `/api/family/person/:id/relatives` | Get all relatives |
| GET | `/api/family/person/:id/tree` | Get family tree branch |
| GET | `/api/family/generation/:gen` | List people by generation |
| GET | `/api/family/summary` | Family stats |

### Assets (`/api/assets`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets/companies` | List companies |
| GET | `/api/assets/companies/:id` | Company detail |
| GET | `/api/assets/companies?person_id=X` | Companies by person |
| GET | `/api/assets/properties` | List properties |
| GET | `/api/assets/properties/:id` | Property detail |

### Legal (`/api/legal`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/processes` | List processes |
| GET | `/api/legal/processes/:id` | Process detail |

### Research (`/api/research`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/research/searches` | Search history |
| GET | `/api/research/tasks` | Pending research tasks |
| GET | `/api/research/tasks?status=pendente` | Tasks by status |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Database statistics |
| GET | `/api/search?q=` | Global full-text search |

## Rules for Agents

1. **API runs on port 5003.** Web proxies on 5002.
2. **Database is SQLite** at `data/rgvl.db`. Use SQLAlchemy, never raw SQL in routes.
3. **INTEL.md is the knowledge base.** Structured data goes in DB, narrative stays in docs.
4. **All data changes go through ETL** (`etl/seed.py`). Don't manually edit the DB.
5. **Don't modify `web/`** without explicit approval.
6. **LGPD compliance:** Only public data. No health, financial details, or private communications.
