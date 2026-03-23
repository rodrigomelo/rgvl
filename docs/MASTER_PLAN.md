# RGVL — Research & Collection Master Plan

> **Goal:** Build the richest possible repository of information about Rodrigo Gorgulho de Vasconcellos Lanna — father of Rodrigo Melo Lanna.
>
> **Principle:** Collect first (any format), structure later, display last.
>
> **Priority order:** Research Architecture → Collection → Monitoring → Consistency → Web Display
>
> **Language:** All technical documentation, code, tables, and schemas are in English. Portuguese is used only in user-facing content (web portal labels, etc.).

---

## Phase Order

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1 — Research Architecture                               │
│  Define WHAT we want to know, WHAT sources exist, HOW to      │
│  access them. No code. Just strategy and source inventory.   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2 — Raw Collection                                    │
│  Collect ANY information, ANY format. Into a staging area.  │
│  Unstructured is fine. Just get the data.                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3 — Structured Storage                                │
│  Move cleaned data into canonical DB schema.                │
│  This is when we worry about tables, relations, schemas.    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4 — Monitoring                                        │
│  Detect changes in existing data sources.                   │
│  Alert when new information appears.                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5 — Consistency                                      │
│  Deduplicate, resolve conflicts, validate, rank accuracy.  │
│  Ensure single source of truth.                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6 — Web Display (LAST)                               │
│  Only now do we build the portal sections, charts, maps.     │
│  The web is a view on top of clean data — not the goal.    │
└─────────────────────────────────────────────────────────────┘
```

---

## Current State

### What We Have

**Database** (`data/rgvl.db`) — 13 tables:

| Table | Rows | Purpose |
|-------|------|---------|
| `pessoas` | 26 | Family members |
| `relacionamentos` | 30 | Relationships between people |
| `empresas_familia` | 10 | Family businesses |
| `imoveis` | 3 | Real estate |
| `processos_judiciais` | 9 | Court cases |
| `documentos` | 5 | Documents (RG, CPF, certidões) |
| `contatos` | 3 | Contacts (lawyers, cartório) |
| `perfis` | 1 | Online profiles |
| `eventos` / `events` | 9 | Life events (births, deaths) |
| `buscas_realizadas` | 0 | Search history (empty) |
| `tarefas_pesquisa` | 5 | Research tasks (existing) |
| `diarios_oficiais` | 0 | Official gazettes |

**Existing Collectors** (`data/collectors/`):

| Collector | Status | Source |
|----------|--------|--------|
| `email.py` | Active | Gmail |
| `father_drive.py` | Active | Hardcoded Drive data |
| `jucemg.py` | Active | Junta Comercial MG |
| `jucesp.py` | Active | Junta Comercial SP |
| `tjmg.py` | Active | Tribunal de Justiça MG |
| `tjsp.py` | Active | Tribunal de Justiça SP |
| `twitter.py` | Active | X/Twitter |
| `web_search.py` | Active | Brave Search |
| `local.py` | Active | Workspace files |
| `import_structured.py` | Active | ETL from hardcoded sources |

**Services:**

- Web portal: `localhost:5002`
- API: `localhost:5003`
- DB: `data/rgvl.db` (SQLite)
- Launchd: `com.rgvl.api` (port 5003), `com.rgvl.web` (port 5002)
- Health check: every 1 hour
- Data collection: every 12 hours (via cron)

---

## Phase 1 — Research Architecture

### 1.1 Define Information Categories

For RGVL, we track 5 domains:

```
RESEARCH DOMAIN 1: Identity
  - Full name, aliases, nickname
  - Birth date/place
  - CPF, RG, CREA, CNH
  - Death date (if applicable)
  - Physical description

RESEARCH DOMAIN 2: Family Network
  - Parents (avós — paternal grandparents)
  - Siblings (full + half)
  - Children (confirmed + potential unknown)
  - Spouse(s)
  - Extended family ( aunts, uncles, cousins)
  - Godparents / close family friends

RESEARCH DOMAIN 3: Professional Life
  - Education (school, university, courses)
  - Career history (companies, positions, dates)
  - Professional licenses (CREA, CAU, OAB, etc.)
  - Business ownership (companies he founded/managed)

RESEARCH DOMAIN 4: Assets & Wealth
  - Real estate (owned, co-owned, inherited)
  - Vehicles (cars, motorcycles)
  - Bank accounts (if discoverable)
  - Investments (if discoverable)
  - Companies he owns or co-owns

RESEARCH DOMAIN 5: Legal & Public Records
  - Court cases (labor, civil, consumer, family)
  - Protests (tabelionatos de protesto)
  - Credit/serasa records
  - Electoral registration
  - Criminal antecedents
  - Immigration/travel records
```

### 1.2 Source Inventory

List every public/private source relevant to each domain:

#### Public Sources (no auth needed)

| Source | What it gives | URL | Domain |
|--------|-------------|-----|--------|
| Receita Federal | CNPJ, company partners | receitasreceita.gov.br | Assets |
| JUCEMG | Company registrations MG | jucemg.mg.gov.br | Assets |
| JUCESP | Company registrations SP | jucesponline.sp.gov.br | Assets |
| TJMG | Court cases MG | tjmg.jus.br | Legal |
| TJSP | Court cases SP | esaj.tjsp.jus.br | Legal |
| TRT3 | Labor court cases MG | trt3.jus.br | Legal |
| Detran MG | Vehicles | detran.mg.gov.br | Assets |
| TSE | Electoral data | tse.jus.br | Identity |
| FamilySearch | Genealogical records | familysearch.org | Family |
| JusBrasil | Case summaries | jusbrasil.com.br | Legal |
| Escavador | Aggregated court data | escavador.com | Legal |
| Google News | Press mentions | news.google.com | Reputation |
| Google Search | General presence | google.com | All |

#### Authenticated Sources (need login/API)

| Source | What it gives | Auth method |
|--------|-------------|-------------|
| Gmail | All email threads | `gog` CLI |
| Google Drive | Documents, spreadsheets | `gog` CLI |
| X/Twitter | Social mentions | `xurl` CLI |
| Serasa | Credit report | Direct request |
| Receita Federal (CPF) | CPF situation | API or site |

### 1.3 Research Tasks Already Defined

From `tarefas_pesquisa` table:

| Priority | Task | Status |
|---------|------|--------|
| ALTA | Find RGVL's 2 unknown siblings | pending |
| ALTA | Confirm if RGVL has other children besides Rodrigo Melo | pending |
| MEDIA | Investigate Marcelo's court cases | pending |
| MEDIA | Map Henrique's 6 children | pending |
| BAIXA | Research Consórcio Sossego details | pending |

### 1.4 Architecture Decision: Raw vs Structured

**Current problem:** The DB schema is somewhat structured, but raw data (PDFs, screenshots, email threads) has no staging area.

**Proposed:** Add a `raw_intelligence` staging layer:

```
raw_intelligence/
├── rgvl/
│   ├── emails/          # Raw email files (txt, eml)
│   ├── documents/        # PDFs, scans (certidões, contratos)
│   ├── screenshots/     # Web scrapes, court portal captures
│   ├── web_pages/      # Saved HTML from scraping
│   └── research_notes/  # Free-form markdown notes per topic
```

Each raw item gets a metadata file:
```
emails/2026-03-19_paternity_investigation.yaml
  source: gmail
  date_collected: 2026-03-19
  topic: paternity
  person_mentioned: [Rodrigo Gorgulho]
  contains_pii: true
  cleaned: false
  imported_to_db: false
```

**Rule:** Raw data NEVER touches the canonical DB directly. A collector or manual process must clean and import.

---

## Phase 2 — Raw Collection

### 2.1 Immediate Collection Priorities

Based on RGVL context, ranked by value:

| # | What to collect | Source | Format | Priority |
|---|----------------|--------|--------|---------|
| 1 | RGVL birth certificate | Cartório Itaituba or archived records | PDF | 🔴 |
| 2 | Nice (mãe) death certificate | Cartório São Paulo | PDF | 🔴 |
| 3 | Paternity recognition deed (escritura) | 3º Ofício Notas BH | PDF | 🔴 |
| 4 | All RGVL court cases full text | TJMG/TJSP/Escavador | HTML/PDF | 🔴 |
| 5 | All company registrations (full partner lists) | JUCEMG/JUCESP | HTML | 🔴 |
| 6 | RGVL's 6 labor case details | TRT3 | HTML | 🔴 |
| 7 | Family network (siblings, children) | FamilySearch | Screenshots | 🔴 |
| 8 | Marcelo's court cases (22+ cases) | TJMG | HTML | 🟡 |
| 9 | Henrique's 16+ court cases | TJMG | HTML | 🟡 |
| 10 | Júnia's AVOSC presidency docs | JUCEMG | HTML | 🟡 |
| 11 | Vehicle records | Detran MG | HTML | 🟡 |
| 12 | Property registrations (matrículas) | Cartório BH | PDF | 🟡 |
| 13 | Newspaper archives | Estado de Minas digital | PDF | 🟢 |
| 14 | LinkedIn professional history | LinkedIn | Screenshots | 🟢 |

### 2.2 Collection Methods

**Method A — Web Scraping (automated)**
- Write scrapers for each public portal
- Run on schedule or on-demand
- Output: raw HTML → saved to `raw_intelligence/`

**Method B — Manual Research (human + agent)**
- For sources requiring CAPTCHA (court portals)
- For sources requiring physical documents (cartórios)
- Agent documents findings in markdown → saved to `raw_intelligence/research_notes/`

**Method C — Direct Data Requests**
- Certidões via sites de cartórios
- Serasa via formal request
- Receita Federal via API

**Method D — Social/Press Monitoring**
- Google Alerts for name variations
- News monitoring
- Social media checks

### 2.3 Raw Intelligence Storage Schema

Create a simple metadata DB (`raw_intelligence.db`) to track all raw items:

```sql
CREATE TABLE raw_items (
    id INTEGER PRIMARY KEY,
    collected_at DATETIME,
    source_type TEXT,        -- 'email', 'web_scrape', 'document', 'manual', 'api'
    source_name TEXT,        -- 'tjmg', 'jucemg', 'gmail', etc.
    topic TEXT,             -- 'court_case', 'company', 'family', 'property', etc.
    person_mentioned TEXT,  -- 'RGVL', 'Marcelo', 'Henrique', etc.
    file_path TEXT,          -- path to raw file
    file_hash TEXT,          -- SHA256 for deduplication
    cleaned BOOLEAN DEFAULT 0,
    imported_to_db BOOLEAN DEFAULT 0,
    import_target_table TEXT,  -- 'processos_judiciais', 'empresas_familia', etc.
    notes TEXT
);

CREATE TABLE search_queries (
    id INTEGER PRIMARY KEY,
    source TEXT,
    query_text TEXT,
    executed_at DATETIME,
    results_count INTEGER,
    status TEXT  -- 'success', 'blocked_captcha', 'no_results', 'error'
);

CREATE TABLE research_notes (
    id INTEGER PRIMARY KEY,
    topic TEXT,
    person TEXT,
    note_content TEXT,
    written_by TEXT,  -- 'Hermes', 'Poseidon', 'Rodrigo', etc.
    written_at DATETIME,
    tags TEXT
);
```

---

## Phase 3 — Structured Storage

### 3.1 When to Structure

Data moves from raw → canonical DB only when:
1. It has been reviewed (at least spot-checked)
2. It maps cleanly to an existing table, OR
3. A new table has been created for it

### 3.2 Schema Extensions Needed

Current canonical schema is good but needs additions:

#### New Tables to Add

**`research_notes`** — free-form intelligence (migrate from `tarefas_pesquisa` concept)
```sql
CREATE TABLE research_notes (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,         -- 'siblings', 'properties', 'legal', etc.
    person_target TEXT,          -- 'RGVL', 'Marcelo', 'Nice', etc.
    note TEXT NOT NULL,          -- The actual intelligence
    confidence TEXT,              -- 'confirmed', 'probable', 'speculative', 'debunked'
    source TEXT,                 -- Where this came from
    collected_by TEXT,           -- Agent or human
    collected_at DATETIME,
    reviewed_by TEXT,
    reviewed_at DATETIME,
    raw_item_id INTEGER,         -- FK to raw_items if applicable
    tags TEXT                    -- JSON array
);
```

**`alternative_names`** — AKA/mistaken identity tracking
```sql
CREATE TABLE alternative_names (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,           -- FK to pessoas
    alias TEXT NOT NULL,          -- The alternative name
    source TEXT,                  -- Where found
    is_mistaken BOOLEAN,         -- True if this name refers to a DIFFERENT person
    verified BOOLEAN DEFAULT 0,
    collected_at DATETIME
);
```

**`wealth_indicators`** — asset and wealth signals (not definitive records, just signals)
```sql
CREATE TABLE wealth_indicators (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,           -- FK to pessoas
    indicator_type TEXT,          -- 'property', 'vehicle', 'company', 'court_judgment'
    description TEXT,
    source TEXT,
    value_estimate BRL,          -- Estimated value if known
    date_found DATE,
    date_expires DATE,
    status TEXT,                 -- 'active', 'sold', 'transferred', 'unknown'
    raw_item_id INTEGER,
    confidence TEXT,             -- 'high', 'medium', 'low'
    notes TEXT
);
```

#### Tables to Extend

**`pessoas`** — add fields:
- `data_nascimento_confirmed BOOLEAN`
- `cpf_verified BOOLEAN`
- `death_date DATE`
- `death_certificate_id INTEGER` (FK to documentos)

**`empresas_familia`** — add fields:
- `quadro_societario_pdf_path TEXT`
- `recibo_abertura DATE`

**`processos_judiciais`** — already good, but needs:
- `rgvl_party_role TEXT` — 'author', 'defendant', 'co-plaintiff', 'witness', 'third_party'
- `case_outcome TEXT`

**`imoveis`** — already good

### 3.3 Import Workflow

```
raw_item (verified)
    ↓
collector or manual review
    ↓
clean & parse
    ↓
map to schema
    ↓
upsert into canonical DB (with FK validation)
    ↓
mark raw_item.imported_to_db = TRUE
    ↓
record in busca_realizadas
```

---

## Phase 4 — Monitoring

### 4.1 What to Monitor

| Source | What changes | How to detect | Frequency |
|--------|-------------|---------------|-----------|
| TJMG | New court case | Escavador alert / CNJ search | Daily |
| TJSP | New court case | Escavador alert / CNJ search | Daily |
| TRT3 | New labor case | Escavador alert / CNJ search | Daily |
| JUCEMG | Company status change (ativa→baixada) | Periodic scrape of company detail | Weekly |
| JUCESP | Same | Same | Weekly |
| Receita Federal | CNPJ situation change | API check | Weekly |
| Gmail | New threads mentioning RGVL | gog polling | 12h |
| Google Alerts | News mentions | Email alert | Real-time |
| Escavador | Any RGVL + family name | Alert subscription | Real-time |

### 4.2 Alert Thresholds

Trigger an alert (not just a log) when:
- New court case found
- Company goes from ativa → baixada
- Death record found for RGVL or family member
- New child/spouse discovered
- Property transfer discovered
- Any search query returns ZERO results (source might be down)

### 4.3 Monitoring Cron

Current: health check every 1h, data collection every 12h.

Proposed addition:
- `rgvl-monitor` — every 6h: check for new court cases, company status changes, alert if new data found.

---

## Phase 5 — Consistency

### 5.1 Deduplication

When the same fact appears in multiple sources:
- Mark all sources
- Use confidence hierarchy: `documento_original > cartorio > 政府 > escavador > google > rumor`
- If conflicting: keep both with confidence scores, flag for human review

### 5.2 Confidence Taxonomy

Every piece of intelligence gets a confidence tag:

| Level | Meaning | Example |
|-------|---------|---------|
| `confirmed` | Official document, no doubt | Birth certificate from cartório |
| `corroborated` | Multiple independent sources agree | 3 different court portals show same case |
| `probable` | One reliable source, plausible | Escavador shows case, details unclear |
| `speculative` | Fragment found, may be wrong | Name appears in old newspaper |
| `debunked` | Proven false | Name confusion with another person |

### 5.3 Conflict Resolution Rules

Priority (highest to lowest):
1. Official government document (cartório, Receita Federal, TJ)
2. Notary deed (escritura pública)
3. Lawyer correspondence (with letterhead)
4. Email from verified contact
5. Web scraping result
6. User input (Rodrigo)

### 5.4 Annual Review

Once per year: full audit of all `probable` and `speculative` entries.

---

## Phase 6 — Web Display (Last)

Only after Phases 1-5 are mature.

### 6.1 What the Portal Should Show

The portal is a **viewer**, not a collector. It shows clean data.

Sections to build when data is ready:
- Family tree (already exists, needs completion)
- Timeline of RGVL's life
- Asset map (properties, companies)
- Legal timeline (cases by year)
- Source attribution on every data point

### 6.2 What NOT to Build Yet

- Charts / graphs / visualizations
- Export features
- Public portal
- Mobile responsive redesign
- Any UI work until data is comprehensive

---

## Implementation Order

### Immediately (this week)
1. Create `raw_intelligence/` directory structure
2. Create `raw_intelligence.db` metadata database
3. Add new tables to canonical DB: `research_notes`, `alternative_names`, `wealth_indicators`
4. Write collector for Escavador (key for new case alerts)
5. Set up Google Alerts for RGVL name variations
6. Document Phase 1 (source inventory) fully

### Short term (this month)
7. Build raw collection for: FamilySearch (screenshot archive), JUCEMG full scrape, newspaper archives
8. Add `rgvl_party_role` to `processos_judiciais`
9. Set up `rgvl-monitor` cron (6h interval)
10. Add confidence tags to existing data
11. Write research notes for all existing `tarefas_pesquisa`

### Medium term (this quarter)
12. Complete family network (siblings, children, parents)
13. Property registration archive
14. Credit/Serasa record (if feasible)
15. Vehicle records from Detran MG
16. Consistency audit

### Long term
17. Historical newspaper archive search
18. Immigration records
19. Full genealogical research (FamilySearch depth)
20. Web portal redesign with all clean data

---

## Poseidon Review — Architecture Improvements

### 1. Current DB vs MASTER_PLAN Mismatch

**Issue:** MASTER_PLAN references tables that don't exist in current schema:

| MASTER_PLAN says | Actual table | Status |
|-----------------|---------------|--------|
| `pessoas` | `persons` | ✅ exists |
| `eventos` / `events` | ❌ MISSING | 🔴 |
| `empresas_familia` | `companies` | ✅ exists |
| `imoveis` | `properties` | ✅ exists |
| `processos_judiciais` | `legal_processes` | ✅ exists |
| `relacionamentos` | ❌ MISSING | 🔴 |
| `perfis` | ❌ MISSING | 🔴 |
| `tarefas_pesquisa` | ❌ MISSING | 🔴 |
| `buscas_realizadas` | ❌ MISSING | 🔴 |

**Fix:** Update MASTER_PLAN to reflect actual schema. Use English naming throughout.

### 2. Raw Intelligence Layer — Refined Proposal

**Problem:** The proposed `raw_intelligence/` with YAML metadata is too complex for initial implementation.

**Simpler approach:**

```
data/
├── raw/                    # Unstructured data (PDFs, screenshots, emails)
│   ├── court_cases/       # HTML/PDF from TJMG, TJSP
│   ├── company_records/    # JUCEMG/JUCESP prints
│   ├── documents/         # Certidões, contratos (scanned)
│   └── research/          # Markdown notes per topic
└── rgvl.db               # Canonical DB (current)
```

**Raw items tracked via simple manifest file:**
```json
// data/raw/manifest.json
[
  {
    "id": "rc_001",
    "type": "court_case",
    "source": "tjmg",
    "person": "RGVL",
    "file": "court_cases/1044263_2026.html",
    "collected": "2026-03-23",
    "processed": false
  }
]
```

**Why not `raw_intelligence.db`?** SQLite is overkill for metadata. JSON manifest is simpler, versionable via git, and sufficient.

### 3. Event Tracking — New Table Needed

**Issue:** We have life events (birth, death, marriage) but no dedicated table.

**Proposed:**
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,
    event_type TEXT,      -- 'birth', 'death', 'marriage', 'divorce', 'property_acquired'
    event_date DATE,
    location TEXT,
    source TEXT,
    document_id INTEGER,  -- FK to documents
    confidence TEXT,       -- 'confirmed', 'probable', 'speculative'
    notes TEXT
);
```

### 4. Relationships Table — Needed

**Issue:** `relacionamentos` is missing. Currently relationships are implicit via tables (siblings, spouses, children).

**Proposed:**
```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    person_a_id INTEGER,
    person_b_id INTEGER,
    relationship_type TEXT,  -- 'sibling', 'spouse', 'parent_child', 'cousin'
    source TEXT,
    confidence TEXT,
    verified BOOLEAN DEFAULT 0,
    notes TEXT
);
```

**Note:** This doesn't replace sibling/spouse tables — it provides a graph view for complex family relationships.

### 5. Research Tasks — New Table

**Issue:** `tarefas_pesquisa` is referenced but doesn't exist.

**Proposed:**
```sql
CREATE TABLE research_tasks (
    id INTEGER PRIMARY KEY,
    task TEXT NOT NULL,
    priority TEXT,          -- 'HIGH', 'MEDIUM', 'LOW'
    status TEXT,           -- 'pending', 'in_progress', 'completed'
    assigned_to TEXT,      -- 'Artemis', 'Poseidon', etc.
    created_at DATETIME,
    completed_at DATETIME,
    result TEXT
);
```

### 6. Duplicate `events`/`eventos` Reference — Fix

Remove all Portuguese table name references. Use English consistently:
- `persons` ✅ (already English)
- `children` ✅ (already English)
- `legal_processes` ✅ (already English)
- `companies` ✅ (already English)
- `properties` ✅ (already English)

### 7. Clean Import Workflow

```
raw/ (unstructured files)
    ↓
Collector reviews raw/
    ↓
If data is clean and fits existing table → import directly
If data is new type → create new table via migration
    ↓
Update manifest.json (processed: true)
    ↓
Commit to git (small delta)
```

### 8. Schema Addition Priority

| Priority | Table | Reason |
|----------|-------|--------|
| 🔴 HIGH | `events` | Life events (birth, death, marriage) currently scattered |
| 🔴 HIGH | `relationships` | Complex family graph beyond siblings/spouses |
| 🟡 MEDIUM | `research_tasks` | Track pending research |
| 🟢 LOW | `raw_intelligence.db` | Only if JSON manifest becomes insufficient |

---

## Technical Decisions

### Language
- All code, schemas, table names, column names, documentation: **English**
- User-facing content (portal labels, alerts): **Portuguese**

### DB Naming
- Canonical DB: `data/rgvl.db` (keep)
- Raw intelligence DB: `data/raw_intelligence.db` (new)
- All table names: snake_case English (`research_notes`, not `notas_pesquisa`)

### Commit Convention
```
feat(raw): description — new raw collector or source
feat(schema): description — DB table or column addition
feat(monitor): description — monitoring rule or alert
feat(collection): description — collection result or finding
fix(schema): description — schema correction
docs: description — documentation update
```

### Rules for All Agents
1. **Report only** — document findings, don't implement
2. **Two-layer approval** — Rodrigo → Hermes → Agent
3. **Raw first** — collect unstructured, then structure
4. **No direct commits** — all changes go through Hermes + Rodrigo approval
5. **Confidence tags** — every fact needs a confidence level

---

*Plan version: 1.0 — 2026-03-23*
*Author: Hermes (Orchestrated with Poseidon, Athena, Hefesto inputs)*

---

## Hefesto Technical Review

**Agent:** Hefesto 🔨 — Engineering
**Focus:** Technical integration, API, cron jobs, backup, infrastructure

---

### A. Current Technical Stack (Verified)

| Component | Current State | Location |
|-----------|--------------|----------|
| Web Dashboard | ✅ Running | `localhost:5002` |
| REST API | ✅ Running | `localhost:5003` |
| Database | ✅ SQLite | `data/rgvl.db` |
| Backup script | ✅ Working | `data/backup.py` |
| Launchd (API) | ✅ Active | `com.rgvl.api` |
| Launchd (Web) | ✅ Active | `com.rgvl.web` |
| Monitor script | ✅ Fixed | `scripts/monitor.sh` |

**Critical path verified:**
```
Web (:5002) → API (:5003) → SQLite DB (data/rgvl.db)
```

---

### B. Integration Issues Found

#### B.1 Database Schema Duplication

Current DB has mixed naming conventions:
- Some tables: Portuguese (`pessoas`, `empresas_familia`, `imoveis`, `eventos`)
- Some tables: English (`events`, `processos_judiciais`)
- Column names: mixed

**Proposed fix:** Phase 3 should include a schema normalization step:
- Rename Portuguese tables to English (e.g., `pessoas` → `persons`)
- Create a view layer for backward compatibility
- Keep legacy column names if web depends on them

#### B.2 Raw Intelligence DB Location

MASTER_PLAN proposes `raw_intelligence.db` but also references `data/raw_intelligence.db`.

**Decision needed:** Should raw DB be:
- Option A: `data/raw_intelligence.db` (same directory as canonical DB)
- Option B: `raw_intelligence/raw_intelligence.db` (separate directory)

**Recommendation:** Option A. Keeps all data in one place, simplifies backup.

#### B.3 API Port Conflict History

Historical issue: services ran on ports 5003/5004/5002 simultaneously, causing confusion. Current state is clean:
- `:5002` = Web
- `:5003` = API

**Recommendation:** Document this as a rule in the plan:
> "Port 5002 = Web (user-facing), Port 5003 = API (internal). No other ports for RGVL services."

#### B.4 Events Table Duplication

`events` AND `eventos` both exist in the DB — likely the same table referenced differently. Need to verify:
```bash
sqlite3 data/rgvl.db "SELECT name FROM sqlite_master WHERE type='table';" | grep -i event
```

If duplicate: merge or deprecate one.

---

### C. Cron Jobs — Proposed Schedule

Current crons:
- `rgvl-health-check` — every 1h ✅
- `rgvl-data-collector` — every 12h ✅

Proposed additions for Phase 4:

```cron
# Court case monitoring (Escavador/TJMG/TJSP) — every 6h
0 */6 * * * cd ~/.openclaw/workspace/projects/rgvl/data && python collectors/escavador.py >> ~/.openclaw/workspace/projects/rgvl/.logs/collector_escavador.log 2>&1

# Company status check (JUCEMG/JUCESP) — weekly
0 3 * * 1 cd ~/.openclaw/workspace/projects/rgvl/data && python collectors/jucemg_status.py >> ~/.openclaw/workspace/projects/rgvl/.logs/collector_jucemg_status.log 2>&1

# Google Alerts email processing — every 12h
0 */12 * * * cd ~/.openclaw/workspace/projects/rgvl/data && python collectors/google_alerts.py >> ~/.openclaw/workspace/projects/rgvl/.logs/collector_google_alerts.log 2>&1

# Backup — daily at 2AM (already documented, confirm active)
0 2 * * * ~/.openclaw/workspace/projects/rgvl/data/backup.sh >> ~/.openclaw/workspace/projects/rgvl/.logs/backup.log 2>&1

# Monitor script — every 5 minutes (for rapid restart)
*/5 * * * * ~/.openclaw/workspace/projects/rgvl/scripts/monitor.sh >> /tmp/rgvl-monitor.log 2>&1
```

**Important:** The monitor script (`/scripts/monitor.sh`) must check `:5002` and `:5003` — verified correct after fix.

---

### D. API Design for Raw Intelligence

For Phase 2-3 to work well, the API needs two new endpoint groups:

#### D.1 Raw Intelligence Endpoints

```python
# GET /api/raw/items
# Returns paginated raw items with filters
# Query params: source, topic, person, cleaned, imported

# GET /api/raw/item/<id>
# Returns single raw item metadata + file path

# POST /api/raw/item
# Register new raw item (called by collectors)

# PATCH /api/raw/item/<id>
# Update cleaned/imported status after processing
```

#### D.2 Research Notes Endpoints

```python
# GET /api/research/notes
# Query params: topic, person, confidence, reviewed

# POST /api/research/notes
# Create new research note

# GET /api/research/tasks
# Current tasks from tarefas_pesquisa (migrate to research_notes)

# PATCH /api/research/task/<id>
# Update task status after completion
```

#### D.3 Confidence Tagging Endpoints

```python
# GET /api/intelligence/summary
# Returns all intelligence grouped by confidence level

# PATCH /api/person/<id>/confidence
# Update person's data confidence score

# PATCH /api/company/<id>/confidence
# Update company's data confidence score
```

---

### E. Backup Strategy — Refined

Current: `data/backup.py` with daily cron at 2AM.

**Enhancements needed for Phase 4:**

1. **Raw intelligence backup** — add `raw_intelligence/` to backup include list
2. **Backup verification** — add `--verify` flag that restores to temp and checks integrity
3. **Offsite backup** — consider adding to iCloud Drive or external disk:
   ```bash
   cp data/backups/rgvl_*.db ~/Library/Mobile\ Documents/com~apple~CloudDocs/rgvl_backups/
   ```
4. **Backup retention** — keep last 30 backups instead of 7 (RGVL is archival project)

---

### F. Monitoring Improvements

#### F.1 Health Check (current)

Script at `scripts/monitor.sh` checks HTTP on 5002/5003 and restarts via launchd if down.

**Enhancement:** Add DB integrity check to health:
```bash
sqlite3 data/rgvl.db "PRAGMA integrity_check;"
```

#### F.2 New Intelligence Alert

Not in current monitor. For Phase 4, add a lightweight check:
```python
# In monitor.sh or new script
new_items=$(sqlite3 raw_intelligence.db "SELECT COUNT(*) FROM raw_items WHERE collected_at > datetime('now', '-6 hours');")
if [ "$new_items" -gt 0 ]; then
    echo "$(date): NEW DATA COLLECTED: $new_items items" >> ~/.logs/rgvl-intelligence.log
    # Future: send Discord alert via webhook
fi
```

#### F.3 Discord Alert Integration

For Phase 4, consider adding to `scripts/monitor.sh`:
```bash
# If service down > 5 minutes, alert
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "⚠️ RGVL API is DOWN on Mac Mini!"}'
```

---

### G. Collector Integration Pattern

For new collectors (Escavador, Google Alerts, etc.), follow this pattern:

**File location:** `data/collectors/<name>.py`

**Structure:**
```python
#!/usr/bin/env python3
"""
Escavador collector — monitors court cases for RGVL and family.
Run: python collectors/escavador.py
Schedule: 0 */6 * * * (every 6h)
"""

import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from database import SessionLocal
from models.entity import Note  # or Company, etc.
from raw_intelligence import RawItemCollector
import requests

def main():
    db = SessionLocal()
    try:
        # 1. Collect raw data
        raw_collector = RawItemCollector(db)
        
        # 2. Search Escavador for each target name
        for name in ["Rodrigo Gorgulho de Vasconcellos Lanna", "Marcelo Gorgulho"]:
            results = search_escavador(name)
            for result in results:
                raw_collector.save_raw_item(
                    source_type="web_scrape",
                    source_name="escavador",
                    topic="court_case",
                    person_mentioned=name,
                    file_path=result["url"],
                    content=result["summary"]
                )
        
        # 3. Log search
        raw_collector.log_search("escavador", query, len(results))
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

---

### H. Git / Deployment Workflow

**Current issue:** The data collectors and web app are in the same repo, but data itself (`.db`, `backups/`, `raw_intelligence/`) should NOT be committed.

**Current `.gitignore`** should already cover:
```
*.db
backups/
raw_intelligence/
logs/
.env
```

**Verify** this is correct:
```bash
cat data/.gitignore  # or project root .gitignore
```

---

### I. Testing Strategy

For Phase 3+ (structured storage), add unit tests:

```
rgvl/
├── tests/
│   ├── test_collectors/
│   │   ├── test_jucemg.py
│   │   ├── test_escavador.py
│   │   └── test_import_structured.py
│   ├── test_api/
│   │   ├── test_raw_endpoints.py
│   │   └── test_research_endpoints.py
│   └── test_db/
│       └── test_schema.py
```

Use `pytest`. Run via GitHub Actions on PRs.

---

### J. Summary of Technical Recommendations

| # | Recommendation | Phase | Priority | Effort |
|---|---------------|-------|----------|--------|
| 1 | Normalize DB schema (Portuguese → English) | 3 | Medium | High |
| 2 | Add raw_intelligence API endpoints | 3 | High | Medium |
| 3 | Add Escavador collector (6h cron) | 4 | High | Medium |
| 4 | Fix events/eventos duplication | 3 | Medium | Low |
| 5 | Add DB integrity check to monitor | 4 | Low | Low |
| 6 | Add Discord alerts for service down | 4 | Low | Low |
| 7 | Expand backup to raw_intelligence | 4 | Medium | Low |
| 8 | Verify .gitignore excludes all data | All | Low | Low |
| 9 | Set up pytest for collectors | 3 | Medium | Medium |
| 10 | Document port standard (5002/5003 only) | 1 | Low | Low |

**Highest value for lowest effort:** #3 (Escavador collector) and #4 (fix events table).

---

*Section version: 1.0 — 2026-03-23*
*Author: Hefesto 🔨 — Engineering*
