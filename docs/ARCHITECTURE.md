# Supplemental Architecture Notes

This document supplements the canonical architecture in the top-level `ARCHITECTURE.md`.

## Supported Runtime

- Flask API: `api/main.py`
- Canonical ORM: `api/models.py`
- SQLite database: `data/rgvl.db`
- Dashboard: `web/`

## Legacy Components

The following areas remain in the repository for migration support or historical reference and are not the supported runtime contract:

- `src/` — legacy FastAPI prototype
- `data/ARCHITECTURE.md` — archived architecture snapshot
- older ETL helpers that still operate on Portuguese table names

## Compatibility Boundary

The current API normalizes legacy Portuguese database values to English at the response boundary. That allows the application contract to stay English while older ETL and migration scripts continue to work during cleanup.

## Data Flow Rule

The project uses a strict one-way flow:

`INTEL/docs -> ETL -> database -> API/UI`

Reverse sync from the database back into INTEL or other unstructured sources is intentionally unsupported.

## Source of Truth

1. The schema source of truth is `api/models.py`.
2. Runtime behavior should be verified against `tests/`.
3. Architecture updates should be made in the top-level `ARCHITECTURE.md` first.
