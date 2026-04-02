# RGVL English Migration — 2026-04-02

## Summary

Complete audit and migration of the RGVL system from Portuguese to English for all non-display code, schemas, and data values. Presentation layer (HTML UI labels) remains in Portuguese per design decision.

## What Was Done

### 1. Relationship Types (Portuguese → English)

**File:** `api/utils.py`, `api/routes/family.py`, `data/rgvl.db`

| Before (PT) | After (EN) |
|-------------|-----------|
| `irmao` | `brother` |
| `irma` | `sister` |
| `conjuge` | `spouse` |
| `filho` | `son` |
| `filha` | `daughter` |
| `mae` | `mother` |
| `nora` | `daughter_in_law` |

**Verification:**
```bash
sqlite3 data/rgvl.db "SELECT DISTINCT relationship_type FROM relationships;"
# Result: brother, daughter, daughter_in_law, mother, sister, son, spouse
```

### 2. Event Types (Portuguese → English)

**File:** `data/rgvl.db`, `web/index.html`

| Before (PT) | After (EN) |
|-------------|-----------|
| `DADOS_PESSOAIS` | `personal_data` |
| `PROCESSO_JUDICIAL` | `legal_case` |
| `ESCRITURA` | `deed` |
| `IMOVEL` | `property` |
| `NOME` | `name_change` |
| `EMPRESARIAL` | `business` |

**Already English:** `birth`, `death`, `marriage`, `company`, `career`, `paternity`, `legal`, `family_contact`

**Verification:**
```bash
sqlite3 data/rgvl.db "SELECT DISTINCT event_type FROM timeline_events ORDER BY event_type;"
# Result: birth, business, career, company, death, deed, legal, legal_case, marriage, name_change, paternity, personal_data, property
```

### 3. API Code Fixes

**`api/routes/family.py`** — lines 75 & 81:
```python
# Before (hardcoded Portuguese):
Relationship.relationship_type.in_(['irmao', 'irma'])

# After (English canonical forms):
Relationship.relationship_type.in_(['brother', 'sister'])
```

**`api/utils.py`** — Added bidirectional `RELATIONSHIP_TYPE_ALIASES`:
- Portuguese → English mappings
- English → English (identity for queries)

### 4. Frontend Updates

**`web/index.html`:**
- `typeLabels` mapping updated to include all 11 event types in English
- CSS classes added for: `personal_data`, `legal_case`, `deed`, `property`, `business`
- Removed Portuguese `falecimento` CSS alias (unified to `death`)
- `TL_EMOJI` mapping updated with all event types
- `SOURCE_LABELS` already English ✅

## What Stays in Portuguese

These are intentional and correct:

| Item | Portuguese | Reason |
|------|------------|--------|
| UI labels (display) | `Profissão`, `Email`, `Endereço`, `Telefone`, `CPF`, `RG`, `CNPJ` | User requested PT display |
| `people.status` | `vivo`, `falecido`, `ativo`, `nao_verificado`, `ex-parceira` | Data values |
| `companies.registration_status` | `ativa`, `baixa` | Data values |
| `legal_cases.status` | `Em andamento`, `Concluído`, `Trânsito em julgado` | Data values |
| Timeline event descriptions | Portuguese narrative | Raw source data |

## Current System State

### Database Schema (English)
All 34 tables with English names:
- `people` — family members
- `companies` — family businesses
- `properties` — real estate
- `relationships` — family links
- `timeline_events` — life events
- `legal_cases`, `documents`, `contacts`, `vehicles`, etc.

### API Endpoints (English)
All routes in English:
- `/api/family/person/:id/tree`
- `/api/assets/companies`
- `/api/legal/processes`
- `/api/research/tasks`

### API Response Keys (English)
All JSON keys in English:
- `father_id`, `mother_id`, `spouse_id`
- `full_name`, `birth_date`, `death_date`
- `generation`, `confidence`, `source`

## Git Commits

| Commit | Description |
|--------|-------------|
| `d52a821` | refactor(api): use English canonical forms for relationship types |
| `4d44c93` | fix(timeline): migrate event_types from Portuguese to English |

## Conventions Going Forward

1. **All code, schemas, APIs, parameters, filters** — English only
2. **Database data values** — English (relationship_type, event_type, status aliases)
3. **Presentation/UI labels** — Portuguese (per design decision)
4. **Raw source data** — preserve original language from source

## Files Modified

- `api/utils.py` — bidirectional RELATIONSHIP_TYPE_ALIASES
- `api/routes/family.py` — hardcoded Portuguese → English
- `data/rgvl.db` — relationship_type and event_type values migrated
- `web/index.html` — typeLabels, CSS classes, TL_EMOJI updated

## Services

| Service | Port | Status |
|---------|------|--------|
| Web Dashboard | 5002 | ✅ Running |
| Flask API | 5003 | ✅ Running |

## Access

- **Dashboard:** http://localhost:5002
- **API:** http://localhost:5003
