# RGVL Architecture

## Overview

RGVL (Rodrigo Gorgulho de Vasconcellos Lanna) is a research platform for genealogical and legal investigation of a family tree. The platform consists of a REST API, a web dashboard, and automated data collectors.

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     INTEL.md (narrative)                    │
│              Manual research, long-term knowledge            │
└─────────────────────────┬───────────────────────────────────┘
                          │ seed.py (manual)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Database (operational)                    │
│   pessoas | relacionamentos | empresas | tarefas | buscas    │
└─────────────────────────┬───────────────────────────────────┘
                          │ collectors (automated)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   REST API (port 5003)                       │
│                  Flask + SQLAlchemy                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐     ┌─────────────────────────────┐
│  Web Dashboard      │     │  Sync: DB → INTEL.md        │
│  (port 5002)        │     │  sync_to_intel.py           │
│  Vercel deploy      │     │  (after each collector run)  │
└─────────────────────┘     └─────────────────────────────┘
```

## Key Principles

1. **INTEL.md** = source of truth for narrative/context (manual)
2. **Database** = operational state (automated collectors)
3. **seed.py** = populate DB from INTEL (one-way, manual)
4. **sync_to_intel.py** = append DB changes to INTEL (closes the loop)

## Sync Mechanism

After any collector runs and writes to the DB, run:

```bash
cd rgvl && python -m etl.sync_to_intel
```

This appends a `## 🆕 Descobertas Recentes` section to INTEL.md with all new records since last sync. The sync timestamp is stored in `database/last_sync.txt`.

From a collector:
```python
from etl.sync_to_intel import sync
sync()
```

### Datetime Handling

All `created_at` / `updated_at` columns use naive UTC datetime (`datetime.now(timezone.utc).replace(tzinfo=None)`). SQLite stores and returns all datetimes as naive ISO strings. The sync function uses naive datetime objects as query parameters, ensuring correct comparison regardless of Python timezone awareness.

### Sync Coverage

| Table | Synced | Formatter |
|-------|--------|-----------|
| `pessoas` | ✅ | `_person_summary()` |
| `empresas_familia` | ✅ | `_company_summary()` |
| `relacionamentos` | ✅ | `_relationship_summary()` |
| `tarefas_pesquisa` | ✅ | `_task_summary()` |
| `imoveis` | ❌ | Not implemented |
| `processos_judiciais` | ❌ | Not implemented |
| `documentos` | ❌ | Not implemented |
| `contatos` | ❌ | Not implemented |
| `diarios_oficiais` | ❌ | Not implemented |
| `perfis` | ❌ | Not implemented |
| `events` | ❌ | Not implemented |

## API

- **Port:** 5003
- **Base URL:** `http://localhost:5003`
- **Endpoints:** `/api/pessoas`, `/api/empresas`, `/api/relacionamentos`, `/api/tarefas`

## Database Schema

| Table | Description |
|-------|-------------|
| `pessoas` | People (26 records) |
| `relacionamentos` | Relationships between people (30 records) |
| `empresas_familia` | Family companies (7 records) |
| `tarefas_pesquisa` | Research tasks (5 pending) |
| `buscas_realizadas` | Log of external source queries |

## Project Structure

```
rgvl/
├── api/
│   ├── main.py          # Flask app
│   ├── db.py            # SQLAlchemy setup
│   ├── models.py        # Entity models (canonical)
│   ├── utils.py         # Serialization helpers
│   └── routes/          # API route blueprints
├── web/                 # Web dashboard (port 5002)
├── etl/
│   ├── seed.py          # Populate DB from INTEL.md
│   └── sync_to_intel.py # Sync DB changes → INTEL.md
├── database/
│   ├── schema.sql       # Reference DDL
│   ├── last_sync.txt    # Sync timestamp marker
│   └── rgvl.db         # SQLite database
└── docs/
    ├── INTEL.md         # Knowledge base
    ├── FAMILY_TREE.md   # Tree visualization
    └── BUSCAS.md        # Research log
```
