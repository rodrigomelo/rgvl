# RGVL Platform Documentation

## Recommended Reading Order

1. `../README.md` for quick start
2. `../ARCHITECTURE.md` for the canonical runtime and schema
3. `ETL_FLOW.md` for the one-way data pipeline
4. `LEGACY_STATUS.md` for retired scripts and historical artifacts
5. `MIGRATION_PLAN.md` for the final migration state and what is still archival

## Document Map

- `ARCHITECTURE.md` - supplemental architecture notes
- `DATA_COLLECTION.md` - historical source inventory and collector notes
- `ETL_FLOW.md` - supported ETL responsibilities and one-way flow
- `LEGACY_STATUS.md` - deprecated files and why they are retired
- `MIGRATION_PLAN.md` - migration status from legacy Portuguese schema to English canonical schema
- `MASTER_PLAN.md` - historical planning material
- `SPEC_AUTH.md` - authentication details
- `SPEC_SOURCES.md` - source-specific API behavior

## Operating Rule

The supported architecture is strictly:

`INTEL/docs -> ETL -> database -> API/UI`

Reverse sync from the database back into narrative sources is not supported.
