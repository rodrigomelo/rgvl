# RGVL Architecture

## Overview

RGVL (Rodrigo Gorgulho de Vasconcellos Lanna) is a research platform for genealogical and legal investigation of a family tree. The platform consists of a REST API, a web dashboard, and automated data collectors.

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     intel/ (modular)                        │
│  master.md | timeline.md | companies.md | legal.md | etc.   │
└─────────────────────────┬───────────────────────────────────┘
                          │ etl/seed.py (ETL)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Database (presentation cache)            │
│   persons | events | companies | legal_processes | etc.     │
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

1. **intel/*.md** = source of truth for structured knowledge (manual research)
2. **Database** = presentation cache only (NOT a repository)
3. **etl/seed.py** = ETL layer: intel/*.md → DB (one-way, manual)
4. **NEVER** insert data directly into DB without passing through ETL

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
│   └── seed.py          # ETL: intel/*.md → DB
├── intel/               # Modular intelligence files
│   ├── master.md        # Index
│   ├── timeline.md      # Events (birth, death, marriage, etc.)
│   ├── companies.md     # Companies and participations
│   ├── legal.md         # Legal processes
│   ├── properties.md    # Properties and addresses
│   ├── family.md        # Family network
│   └── contacts.md      # Contacts
├── data/
│   └── rgvl.db         # SQLite database (presentation cache)
└── docs/
    ├── INTEL.md         # Legacy knowledge base
    ├── ARCHITECTURE.md  # This file
    └── MASTER_PLAN.md   # Project master plan
```

---

## 📋 DECISIONS LOG (Last updated: 2026-03-24)

### Data Architecture (SSOT - Single Source of Truth)
| Decision | Date | Notes |
|----------|------|-------|
| INTEL.md = ONLY non-structured source | 2026-03-24 | Golden source, git-versioned |
| DB = presentation cache only | 2026-03-24 | NOT a repository |
| Manual research → INTEL only | 2026-03-24 | NEVER directly to DB |
| ETL: etl/intel_parser.py | 2026-03-24 | INTEL → structured data |
| No reverse sync (DB → INTEL) | 2026-03-24 | REMOVED |

### Database Rules
| Decision | Date | Notes |
|----------|------|-------|
| Single DB: `data/rgvl.db` | 2026-03-24 | ONLY this path exists. Never create another DB. |
| Table names: English only | 2026-03-24 | English: persons, children, companies, etc. Portuguese tables (eventos, etc.) do NOT exist. |
| DB Schema | 2026-03-24 | 11 tables: persons, children, siblings, nephews, companies, properties, contacts, documents, legal_processes, official_gazettes, research_tasks |

### Modular INTEL Structure (2026-03-24)
| Decision | Notes |
|----------|-------|
| intel/*.md modular | Separated by domain: timeline, companies, legal, properties, family, contacts |
| intel/master.md | Index linking all modular files |
| ETL: seed.py | Reads from intel/*.md, outputs to DB |
| Data flow | intel/*.md → seed.py → DB → API → Web |

### Data Quality Fixes (2026-03-24)
| Decision | Notes |
|----------|-------|
| person_id linking | Parser now correctly links events to persons by name |
| ~ prefix for year-only dates | Shows as "aproximado" in UI |
| Rodrigo Melo vs RGVL separation | Son (ID=11) and father (ID=6) events kept separate |
| Rodrigo Melo's personal events | Removed from RGVL timeline (privacy) |

### Team Rules (2026-03-24)
| Decision | Notes |
|----------|-------|
| Channel #rgvl | RGVL project ONLY — never Palmeiras or other projects |
| Approval flow | Agent → Hermes → Rodrigo (never directly to Rodrigo) |
| INTEL = source of truth | All data must go through INTEL before DB |

### Project Conventions
| Decision | Date | Notes |
|----------|------|-------|
| Auth: Auth0 SPA | 2026-03-24 | Domain: dev-4mhbzq6x4yvyckmt.us.auth0.com |
| Portal: port 5002 | 2026-03-24 | Web dashboard |
| API: port 5003 | 2026-03-24 | REST API |
| Language: PT for labels, EN for code | 2026-03-24 | User-facing labels in Portuguese, code/docs in English |
| No commits without approval | 2026-03-23 | Two-layer: Rodrigo → Hermes → Agent |

### Agents
| Agent | Role |
|-------|------|
| Hermes | Orchestrator (you) |
| Hefesto | Engineering |
| Athena | UX/UI Design |
| Apollo | QA/Testing |
| Artemis | Research |
| Poseidon | Data Architecture |

---

_This log is updated whenever a significant architectural decision is made._
