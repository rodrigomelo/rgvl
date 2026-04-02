# Legacy Status

## Purpose

This document records which repository artifacts are historical only and should not be used as part of the supported runtime.

## Active Runtime

The supported runtime is the Flask application under `api/` backed by the English canonical schema defined in `api/models.py`.

The supported ETL path is driven by `etl/seed.py`.

## Legacy Runtime Artifacts

### `src/api/`

Status: legacy prototype

Reason:

- it is not the supported production runtime
- it duplicates backend responsibilities already implemented in `api/`
- the repository documentation now points to Flask under `api/` as the canonical backend

### `data/ARCHITECTURE.md`

Status: historical snapshot

Reason:

- it documents an earlier architecture state
- it is useful only for archaeology and comparison

## Removed ETL and Migration Scripts

### `etl/sync_to_intel.py`

Status: removed

Reason:

- it violates the required one-way architecture by attempting structured to unstructured flow

### `etl/migrate_to_canonical.py`

Status: removed

Reason:

- it targets an obsolete Portuguese and mixed-schema migration path
- it is not part of the supported runtime lifecycle

### `etl/003_add_coletas_veiculos_eleitorais_fts.py`

Status: removed

Reason:

- it creates and alters legacy Portuguese-schema tables
- it does not match the current English canonical schema

## Historical Planning Documents

The following files may contain useful context, but they are not the source of truth for the current system state:

- `docs/MASTER_PLAN.md`
- `docs/DATA_COLLECTION.md`
- `docs/MASTER_PLAN_PRE_CLEANUP.md`

Use `README.md`, `ARCHITECTURE.md`, and `docs/ETL_FLOW.md` first.

## Rule for Future Changes

If a file contradicts the active architecture, treat it as legacy until it is rewritten. Do not expand legacy paths or restore reverse synchronization.
