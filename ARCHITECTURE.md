# RGVL Architecture

## Overview

RGVL is a family-research platform with one supported runtime stack:

- Flask API in `api/`
- SQLite database at `data/rgvl.db`
- Static web dashboard in `web/`

The repository still contains older prototypes and migration helpers, but the canonical application contract is the English ORM and Flask API under `api/`.

## Runtime Stack

| Layer | Technology | Port |
|-------|------------|------|
| Web Dashboard | Flask static server + HTML/JS | 5002 |
| API | Flask + SQLAlchemy | 5003 |
| Database | SQLite (`data/rgvl.db`) | file |
| Packaging | Docker Compose | - |

## Canonical Data Flow

```
intel/*.md or docs/*.md
        ↓
    etl/seed.py
        ↓
  data/rgvl.db (SQLite)
        ↓
 api/main.py (Flask)
        ↓
 web/index.html
```

This flow is strictly one-way. Structured database records must not be synced back into INTEL or other narrative sources.

## Canonical Schema

The schema source of truth is `api/models.py`. The canonical table set is:

| Table | Purpose |
|-------|---------|
| `people` | Family members and core person records |
| `relationships` | Person-to-person relationships |
| `companies` | Company and ownership records |
| `properties` | Real-estate records |
| `legal_cases` | Judicial case records |
| `documents` | Personal and legal documents |
| `contacts` | People and institutions of interest |
| `social_profiles` | Online profiles |
| `timeline_events` | Chronological events |
| `official_gazettes` | Official publication records |
| `collection_runs` | Collector execution history |
| `search_history` | External search history |
| `research_tasks` | Open research tasks |
| `research_notes` | Research notes |
| `research_insights` | Derived insights |

## Project Structure

```
rgvl/
├── api/                # Supported Flask API and canonical ORM
├── web/                # Supported dashboard
├── etl/                # ETL and migration scripts
├── data/               # SQLite DB and data assets
├── docs/               # Supplemental project documentation
├── intel/              # Research narratives and summaries
├── tests/              # Active Flask API and ETL tests
└── src/                # Legacy FastAPI prototype, not part of the runtime
```

## Design Rules

1. `api/models.py` is the schema source of truth.
2. Public API contracts are English, including route descriptions, response keys, and normalized enum values.
3. Legacy Portuguese database values may still exist internally, but the API layer normalizes them to English.
4. The supported application stack is the top-level Flask app, not the prototype in `src/`.
5. Documentation should describe only the active canonical architecture unless a file is explicitly marked as legacy.
6. The architecture is strictly `unstructured -> structured`; reverse sync from the database back into INTEL/docs is not allowed.
