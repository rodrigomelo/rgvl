# ETL Flow

## Supported Direction

The only supported data flow in this repository is:

`INTEL/docs -> ETL -> database -> API/UI`

This rule is mandatory.

The database is the structured runtime store. INTEL and documentation files are the unstructured source material. The project does not support reverse synchronization from the database back into INTEL or any other narrative document.

## Source of Truth by Layer

- Unstructured research: `intel/` and selected `docs/`
- ETL implementation: `etl/seed.py`
- Canonical structured schema: `api/models.py`
- SQL reference schema: `database/schema.sql`
- Runtime API: `api/`
- Frontend and dashboard: `web/`

## Supported ETL Entry Point

Use only the active seeder:

```bash
python -m etl.seed
```

What it does:

- parses unstructured narrative sources
- maps entities into the English canonical schema
- upserts structured records into the SQLite database
- preserves source attribution for downstream inspection

## Canonical Entity Set

The active ETL writes into the English canonical schema, including these main entities:

- `people`
- `relationships`
- `companies`
- `properties`
- `legal_cases`
- `documents`
- `contacts`
- `official_gazettes`
- `social_profiles`
- `timeline_events`
- `research_insights`
- `search_history`
- `research_tasks`

## Compatibility Boundary

The repository still contains historical Portuguese values in some stored records and historical documents. Compatibility is handled only at the API normalization boundary.

That means:

- the supported schema and code names are English
- public API responses are normalized to English
- internal compatibility may still map legacy Portuguese stored values to English outputs
- new code must not introduce new Portuguese schema or API contracts

## Operational Sequence

1. Update or review source material in `intel/` or documented source inputs.
2. Run `python -m etl.seed`.
3. Start the API application.
4. Query the API or use the web UI.
5. Validate behavior with the test suite.

## Unsupported Operations

The following operations are not supported in the current architecture:

- database to INTEL synchronization
- replaying historical Portuguese-schema migrations against the active database
- treating `src/api/` as the production runtime
- adding new Portuguese table names, column names, or API fields

## Validation

After ETL or schema-related changes, validate with:

```bash
pytest
```

For seed-path changes, at minimum run the seed-focused tests.
