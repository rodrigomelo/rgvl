# Migration Plan

## Status

The migration from the older Portuguese and mixed-schema repository state into the current English canonical runtime is complete for the supported application path.

Completed areas:

- Canonical ORM schema in `api/models.py`
- Active Flask API routes and contracts
- Schema reference in `database/schema.sql`
- Seeder and seed-related tests
- Reverse-sync removal and one-way ETL enforcement
- Primary architecture and README documentation

## Canonical Mapping

| Legacy Name | Canonical Name |
|-------------|----------------|
| `pessoas` | `people` |
| `relacionamentos` | `relationships` |
| `empresas_familia` | `companies` |
| `imoveis` | `properties` |
| `processos_judiciais` / `legal_processes` | `legal_cases` |
| `documentos` | `documents` |
| `contatos` | `contacts` |
| `perfis` / `profiles` | `social_profiles` |
| `eventos` / `events` | `timeline_events` |
| `diarios_oficiais` | `official_gazettes` |
| `buscas_realizadas` | `search_history` |
| `tarefas_pesquisa` | `research_tasks` |
| `coletas` | `collection_runs` |

## Architecture Rule

The repository now follows a strict one-way flow:

`INTEL/docs -> ETL -> database -> API/UI`

The database must not write back into INTEL or any other unstructured source.

## Removed Artifacts

The following scripts were removed from the supported runtime because they targeted the obsolete Portuguese-schema or reverse-sync architecture:

- `etl/migrate_to_canonical.py`
- `etl/003_add_coletas_veiculos_eleitorais_fts.py`
- `etl/sync_to_intel.py`

See `LEGACY_STATUS.md` for details.

## Remaining Work

The remaining work is documentation and eventual archival removal of historical files that are no longer needed. The supported runtime path itself is already aligned.
