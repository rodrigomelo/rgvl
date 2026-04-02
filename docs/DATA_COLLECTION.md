# RGVL - Data Collection Sources & Pipeline

> Historical source inventory. Collector details here may describe older paths and names. For the supported pipeline, use `docs/ETL_FLOW.md` and the root `ARCHITECTURE.md` first.

> **Last updated:** 2026-03-23
> **Author:** Poseidon - Data Architect

---

## 1. Data Sources & Collectors

All collectors live in `data/collectors/`. Each is a standalone Python script that can be run independently or triggered via cron.

**Collector location:** `~/.openclaw/workspace-shared/projects/rgvl/data/collectors/`

---

### 1.1 `email.py` — Gmail Contact Discovery

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Email addresses and sender names found in Gmail threads matching target names |
| **Source** | Gmail (Google Workspace) |
| **Access method** | `gog` CLI (`gog gmail search <query> --max N --json`) |
| **Output format** | Database → `contacts` table |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | `gog` must be authenticated (`gog auth list` must not show "Secret not found") |
| **Target names searched** | `"Rodrigo Gorgulho"`, `"Rodrigo Lanna"`, `"Rodrigo Gorgulho Lanna"` |

**How it works:**
1. Checks `gog auth list` for valid credentials
2. For each target name, runs `gog gmail search` with the name as query
3. Extracts sender/recipient email addresses from results
4. Deduplicates and upserts into `contacts` table (`source = 'gmail_search'`)

**Output table:** `contacts`
```python
Contact(
    source='gmail_search',     # distinguishes from other contact sources
    contact_type='email',
    value='addr@domain.com',
    raw_data={'name': 'Display Name'},
    is_verified=False,
    is_primary=False
)
```

---

### 1.2 `father_drive.py` — Father Profile & Drive Data (Static Import)

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Profile, contacts, documents, family tree, companies, real estate for Rodrigo Gorgulho de Vasconcellos Lanna |
| **Source** | Hardcoded Python constants (originally sourced from Google Drive spreadsheets) |
| **Access method** | Direct Python module import — no external API calls |
| **Output format** | Database → `profiles`, `contacts`, `documents`, `notes` tables |
| **Update frequency** | Every 12h via `rgvl-data-collector` (safe to re-run — uses upsert logic) |
| **Auth required** | None |

**Data imported (all hardcoded in script):**

**Profile:**
```python
{
    'source': 'father_drive',
    'external_id': 'rgvl_father',
    'name': 'Rodrigo Gorgulho de Vasconcellos Lanna',
    'bio': 'Engenheiro Civil',
    'location': 'Belo Horizonte, MG, Brasil',
    'company': 'Construtora Barbosa Mello S/A',
    'email': 'rlanna@cbmsa.com.br',
}
```

**Contacts (3 records):**
- Phone: `+55(31)3417-6319` (primary)
- Phone: `+55(31)3213-6476`
- Email: `rlanna@cbmsa.com.br` (primary)

**Documents (3 records):**
- CPF: `314.516.326-49`
- RG: `MG-594.589`
- CREA/MG: `24920/D`

**Family data** (saved as JSON note, category=`family`):
- Spouse: Rosália Fagundes Ladeira (Arquiteta, CPF `359.959.806-10`)
- Siblings: Júnia, Marcelo, Henrique (3 Gorgulho de Vasconcellos Lanna)
- Parents: Nice (Vó Nice)
- Nephews/nieces: 17 entries (Luiza, Fernanda, Marcela, Andre, Andrea, Paula Lanna Silva, etc.)

**Companies (3 records), saved as JSON note, category=`business`:**
- CNPJ `17.185.786/0001-61` — Construtora Barbosa Mello S/A (ativa, capital R$290M)
- CNPJ `22.676.938/0001-69` — Rvl Engenharia (Rodrigo Gorgulho de Vasconcellos Lanna - EPP, ativa)
- CNPJ `02.835.659/0001-93` — Erh Lanna Engenharia Ltda (Henrique, ativa, baixada Jun/2024 per INTEL.md)

**Properties (2 records), saved as JSON note, category=`real_estate`:**
- Rua Gonçalves Dias 865, Apto 1201, Savassi, BH — matrícula 121.974, 3 bed, 5 parking, 373m², purchased R$3.93M (2017-12-21)
- Rua Oliveira 259, Apto 303, Cruzeiro, BH — matrícula 15.902, 3 bed, 2 parking, 245m², purchased 1982

---

### 1.3 `jucemg.py` — Junta Comercial de Minas Gerais

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Business registrations (empresas) where target name appears as partner/shareholder in Minas Gerais |
| **Source** | `jucemg.gov.br` / `transparencia.jucemg.gov.br` |
| **Access method** | Web scraping via `requests` + `BeautifulSoup` |
| **Output format** | Database → `companies` table (`source='jucemg'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | None (public site) |
| **Rate limit** | 1 request/second between searches |
| **Target names** | `"Rodrigo Gorgulho de Vasconcellos Lanna"`, `"Rodrigo Gorgulho Lanna"`, `"Rodrigo G. V. Lanna"` |

**How it works:**
1. Session-based scraping of `https://www.jucemg.gov.br/transparencia/juntas/comercial`
2. Attempts multiple search parameter formats (`nome`, `q`, `termo`, `busca`)
3. Parses result tables/lists for company entries
4. Extracts CNPJ, legal name, status from each entry
5. Can optionally fetch detail pages per CNPJ

**Output table:** `companies`
```python
Company(
    cnpj='XX.XXX.XXX/XXXX-XX',
    legal_name='...',
    trade_name='...',
    address='...',
    status='ativa' | 'inativa' | 'baixada',
    activity='...',
    capital=0.0,
    partners=[],
    raw_data={...},
    collected_at=datetime
)
```

**Spec document:** `data/collectors/JUCEMG_SPEC.md`

---

### 1.4 `jucesp.py` — Junta Comercial de São Paulo

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Business registrations where target name appears as partner in São Paulo state |
| **Source** | `jucesponline.sp.gov.br` |
| **Access method** | Web scraping via `requests` + `BeautifulSoup` (3 search methods attempted) |
| **Output format** | Database → `notes` table (`category='business'`, `source='jucesp'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | None (public site) |

**Search methods attempted (in order):**
1. POST to `busca.aspx` / `Pesquisa.aspx` with viewstate and form params
2. GET to `/busca` with query params (`q`, `termo`, `nome`, `pesquisa`)
3. API endpoint: `/api/empresas` or `/WSearch/api`

**Output table:** `notes`
```
Note(
    title=<company_name>,
    content=<multi-line details>,
    category='business',
    source='jucesp',
    tags=['business', 'jucesp', 'company', 'São Paulo', 'registration'],
    importance=3,
    raw_data={...}
)
```

> **Note:** JUCESP results are stored as `notes` (not `companies`) — this is a legacy design choice. Consider migrating to the `companies` table in future iterations.

---

### 1.5 `local.py` — Workspace File Harvester

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Contacts, documents, and file previews from local workspace markdown files |
| **Source** | Local files in `~/.openclaw/workspace-hermes/` |
| **Access method** | Direct file read (`pathlib.Path`) |
| **Output format** | Database → `contacts`, `documents`, `notes` tables |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | None |

**Files scanned:**
| File | Data extracted |
|------|---------------|
| `USER.md` | Email (regex), phone (regex `+55...`), Telegram handle (`@...`), CPF |
| `MEMORY.md` | First 500 chars as preview note |
| `SOUL.md` | First 500 chars as preview note |
| `AGENTS.md` | First 500 chars as preview note |

**Regex patterns used:**
```python
email:   r'[\w.-]+@[\w.-]+\.\w+'
phone:   r'\+55\s*\d{2}\s*\d{4,5}[-\s]*\d{4}'
telegram: r'@[\w]+'
cpf:     r'\d{3}\.\d{3}\.\d{3}-\d{2}'
```

---

### 1.6 `tjmg.py` — Tribunal de Justiça de Minas Gerais

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Court case numbers and URLs for judicial processes where target name appears as party |
| **Source** | `tjmg.jus.br` / `eprocjemg.tjmg.jus.br` |
| **Access method** | Web scraping via `requests` + `BeautifulSoup` |
| **Output format** | Database → `notes` table (`category='court_case'`, `source='tjmg'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | None (public eproc interface) |
| **Target name** | `"Rodrigo Gorgulho de Vasconcellos Lanna"` |

**Search endpoints attempted:**
1. `GET /eprocjemg/publico/buscaProcessoWeb3C.jsp?nomeParte=<name>`
2. `GET /eprocjemg/publico/buscaProcessoWeb2C.jsp`
3. `GET /eproc2g/` (older interface)
4. `GET /proc_web/`

**Output table:** `notes`
```
Note(
    title=<case_number>,
    content=<case details>,
    category='court_case',
    source='tjmg',
    tags=['court', 'tjmg', 'legal', 'Minas Gerais'],
    importance=3,
    raw_data={'case_number': '...', 'url': '...', 'court': 'TJMG'}
)
```

---

### 1.7 `tjsp.py` — Tribunal de Justiça de São Paulo

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Court case numbers and URLs for processes at TJSP where target name appears as party |
| **Source** | `esaj.tjsp.jus.br` |
| **Access method** | Web scraping via `requests` + `BeautifulSoup` (session + JSF form submission) |
| **Output format** | Database → `notes` table (`category='court_case'`, `source='tjsp'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | None (public ESAJ interface) |
| **Target name** | `"Rodrigo Gorgulho de Vasconcellos Lanna"` |

**How it works:**
1. Establishes session with initial GET to `esaj.tjsp.jus.br/cpopg/open.do`
2. Extracts `javax.faces.ViewState` token from page
3. POST to search endpoint with party name (`tipoPesquisa=NMPARTE`)
4. Parses result table or extracts case links

**Search endpoints:**
- `POST /cpopg/open.do` (with JSF partial ajax)
- `GET /cpopg/search.do?paginaConsulta=1&cbPesquisa=NMPARTE&tbNome=<name>`

**Output table:** `notes`
```
Note(
    title=<case_number>,
    content=<case details>,
    category='court_case',
    source='tjsp',
    tags=['court', 'tjsp', 'legal', 'São Paulo'],
    importance=3,
    raw_data={'case_number': '...', 'url': '...', 'court': 'TJSP'}
)
```

---

### 1.8 `twitter.py` — X/Twitter Social Search

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Public tweets mentioning target names |
| **Source** | X (Twitter) API via `xurl` CLI |
| **Access method** | `xurl search <query> -n <max_results>` (JSON output) |
| **Output format** | Database → `notes` table (`category='x_mention'`, `source='x_search'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | `xurl` must be OAuth2-authenticated (`xurl auth status` must pass) |
| **Target names** | `"Rodrigo Gorgulho"`, `"Rodrigo Lanna"`, `"Rodrigo Gorgulho Lanna"` |

**Auth check:**
```python
subprocess.run(['xurl', 'auth', 'status'], ...)
# Fails if output contains "No apps registered" or return code != 0
```

**Output format per tweet (saved as JSON in `raw_data`):**
```python
{
    'id': '<tweet_id>',
    'text': '<tweet_text>',
    'author_id': '<author_id>',
    'created_at': '<ISO8601>',
    'conversation_id': '<conv_id>',
    'source': 'x_search'
}
```

---

### 1.10 `web_search.py` — Brave Search Web Indexing

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Public web mentions (title, URL, description) of target names |
| **Source** | Brave Search API (`api.search.brave.com`) |
| **Access method** | `requests` library with `BRAVE_API_KEY` header |
| **Output format** | Database → `notes` table (`category='web_mention'`, `source='web_search'`) |
| **Update frequency** | Every 12h via `rgvl-data-collector` cron |
| **Auth required** | `BRAVE_API_KEY` env var |
| **Target names** | `"Rodrigo Gorgulho"`, `"Rodrigo Lanna"`, `"Rodrigo Gorgulho Lanna"` |

**Brave API call:**
```python
GET https://api.search.brave.com/res/v1/web/search
Headers: X-Subscription-Token: <BRAVE_API_KEY>
Params: q=<query>, count=<count>
```

**Deduplication:** Checks if URL already exists in DB before saving.

---

### 1.11 `import_structured.py` — ETL: Notes → Structured Tables

| Attribute | Detail |
|-----------|--------|
| **What it collects** | Migrates denormalized JSON blobs from `notes` table into canonical normalized tables |
| **Source** | Existing `notes` rows with `category IN ('family', 'business', 'real_estate')` and `source='father_drive'` |
| **Access method** | SQLAlchemy ORM |
| **Output format** | Database → `family_members`, `companies`, `properties` tables |
| **Update frequency** | Manual / one-time migration (can be re-run safely with upsert logic) |
| **Auth required** | None |

**Three migration functions:**

**`import_family()`** — reads `Note(category='family', source='father_drive')`, parses JSON:
- Spouse → `FamilyMember(relationship='spouse', profession, cpf, notes)`
- Siblings → `FamilyMember(relationship='sibling')`
- Parents → `FamilyMember(relationship='parent')`
- Nephews → `FamilyMember(relationship='nephew', school, notes)`

**`import_companies()`** — reads `Note(category='business', source='father_drive')`, parses JSON array → `Company(cnpj, legal_name, trade_name, opening_date, address, phone, email, capital, status, activity, partners)`

**`import_properties()`** — reads `Note(category='real_estate', source='father_drive')`, parses JSON array → `Property(address, city, state, neighborhood, registration, cartorio, area_sqm, bedrooms, parking, purchase_date, purchase_value, current_value, status, description)`

---

## 2. Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
│  Gmail          Google Drive    JUCEMG         JUCESP    Local Files       │
│  (gog CLI)      (static)       (HTTP)          (HTTP)    (pathlib)        │
│                                                                             │
│  tjmg.jus.br   esaj.tjsp   X API       Brave API                        │
│  (HTTP)        (HTTP)       (xurl)      (requests)                        │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  COLLECTORS     │
                    │  (Python scripts│
                    │  in data/       │
                    │  collectors/)   │
                    └────────┬────────┘
                             │ SQLAlchemy ORM / subprocess
                             ▼
                    ┌─────────────────────┐
                    │   SQLite DB         │
                    │   data/rgvl.db      │
                    │                     │
                    │  profiles           │
                    │  contacts          │
                    │  documents         │
                    │  notes             │
                    │  repositories      │
                    │  activities        │
                    │  family_members    │
                    │  companies         │
                    │  properties        │
                    └────────┬───────────┘
                             │ Flask + SQLAlchemy (port 5003)
                             ▼
                    ┌─────────────────────┐
                    │   Flask API         │
                    │   /api/* endpoints  │
                    │   (port 5003)       │
                    └────────┬───────────┘
                             │ HTTP (port 5002 proxy)
                             ▼
                    ┌─────────────────────┐
                    │   Web Dashboard     │
                    │   (static HTML/JS)  │
                    │   (port 5002)       │
                    └─────────────────────┘
```

### Pipeline Stages

| Stage | Component | Technology | Description |
|-------|-----------|------------|-------------|
| **Source** | Email, Drive, Court sites, X, Web | gog CLI, requests, xurl | Fetch raw data from external sources |
| **Collect** | `data/collectors/*.py` | Python, SQLAlchemy | Extract, transform, deduplicate |
| **Store** | `data/rgvl.db` | SQLite | Canonical structured storage |
| **Serve** | `api/main.py` | Flask + SQLAlchemy | REST API on port 5003 |
| **Present** | `web/index.html` | Static HTML/JS | Dashboard on port 5002 |

### Canonical Schema (12 tables)

| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| `pessoas` | 26 | Family members |
| `relacionamentos` | 30 | Family relationships |
| `empresas_familia` | 10 | Family businesses |
| `imoveis` | 3 | Real estate |
| `processos_judiciais` | 9 | Court cases |
| `documentos` | 5 | IDs, certificates |
| `contatos` | 3 | Lawyer, registry, relatives |
| `eventos` | 9 | Births, marriages, career |
| `diarios_oficiais` | 0 | Official gazette |
| `perfis` | 0 | Online profiles |
| `buscas_realizadas` | 0 | Search history |
| `tarefas_pesquisa` | 5 | Research tasks |

---

## 3. Collection Triggers

### 3.1 Cron Jobs (Automated)

| Cron ID | Name | Schedule | Agent | Status | Purpose |
|---------|------|----------|-------|--------|---------|
| `rgvl-health-check` | Health Check | Every 1 hour | hermes | ✅ ok | Monitor API/health endpoints, DB integrity |
| `rgvl-data-collector` | Data Collector | Every 12 hours | hermes | ✅ ok | Run all collectors in sequence |
| `palmeiras-data-collector` | Palmeiras Collector | Every 12 hours | hermes | ✅ ok | Separate collector for Palmeiras-related data |
| `palmeiras-collector` | Palmeiras Cron | `0 12-23 * * *` | hefesto | ❌ error | Scheduled Palmeiras collection (malfunctioning) |

> **Note:** `palmeiras-collector` is in error state and should be investigated. It does not affect RGVL data collection.

**Health check cron** (`rgvl-health-check`):
- Runs every hour
- Monitors API availability on port 5003
- Checks database integrity
- Alerts if something is wrong

**Data collector cron** (`rgvl-data-collector`):
- Runs every 12 hours
- Executes all collectors in sequence (order defined in `collect.py` or similar orchestrator)
- Collectors run independently — one failure doesn't stop others

### 3.2 Manual Triggers

Any collector can be run manually:

```bash
cd ~/.openclaw/workspace-shared/projects/rgvl

# Run a specific collector
python3 -m data.collectors.email
python3 -m data.collectors.father_drive
python3 -m data.collectors.jucemg
python3 -m data.collectors.jucesp
python3 -m data.collectors.local
python3 -m data.collectors.tjmg
python3 -m data.collectors.tjsp
python3 -m data.collectors.twitter
python3 -m data.collectors.web_search
python3 -m data.collectors.import_structured

# Dry-run (where supported)
python3 -m data.collectors.father_drive --dry-run
```

### 3.3 Event-Based Triggers

Currently **not implemented**. Potential future triggers:

| Trigger | Action | Implementation |
|---------|--------|----------------|
| New email thread from unknown contact | Run `email.py` | OpenClaw email plugin webhook |
| Manual request via Discord command | Run selected collectors | Atlas command handler |

---

## 4. Auth & Credentials

| Service | Credential | Config location |
|---------|-----------|----------------|
| Gmail | `gog` CLI session | `gog auth add` (stores in OS keychain) |
| X/Twitter | `xurl` OAuth2 | `xurl auth oauth2` |
| Brave Search | `BRAVE_API_KEY` | `~/.openclaw/workspace-shared/projects/rgvl/.env` |
| Google Workspace | `gog` session | `gog auth` (keyring) |

---

## 5. Error Handling & Resilience

| Collector | Error strategy |
|-----------|---------------|
| `email.py` | Skips if `gog` not authenticated; logs warning |
| `father_drive.py` | Upsert logic — safe to re-run; commits per-section |
| `jucemg.py` | Try/except per search attempt; logs and continues |
| `jucesp.py` | 3 search methods fallback chain; saves attempt note even on failure |
| `local.py` | Per-file try/except; continues if one file missing |
| `tjmg.py` | Multiple endpoint fallbacks; saves attempt note |
| `tjsp.py` | Session established per attempt; saves attempt note |
| `twitter.py` | Skips if `xurl` not authenticated; logs warning |
| `web_search.py` | Skips if `BRAVE_API_KEY` not set; logs warning |
| `import_structured.py` | Per-table try/except; rollback on failure |

---

## 6. LGPD / Privacy Compliance

All collectors are subject to RGVL's LGPD rules:

- ✅ **Allowed:** Public business registrations (JUCEMG, JUCESP), court records (TJMG, TJSP), professional profiles, property records
- ✅ **Allowed:** Your own Gmail contacts (you control your inbox)
- ❌ **Prohibited:** Health data, financial records of third parties, private communications
- ❌ **Prohibited:** Collecting data about minors without explicit justification
- ❌ **Prohibited:** Using scraped data for commercial purposes beyond family research

> **Internal designation:** RGVL is an internal research project. **Do not use the "RGVL" designation in external searches.** Use the full legal name: **Rodrigo Gorgulho de Vasconcellos Lanna**.

---

## 7. Quick Reference

### Collector Summary Table

| Collector | Source Type | Auth | Output Table | Frequency |
|-----------|-------------|------|-------------|-----------|
| `email.py` | Gmail (gog CLI) | gog session | `contacts` | 12h cron |
| `father_drive.py` | Static/hardcoded | None | `profiles`, `contacts`, `documents`, `notes` | 12h cron |
| `jucemg.py` | jucemg.gov.br | None | `companies` | 12h cron |
| `jucesp.py` | jucesponline.sp.gov.br | None | `notes` (business) | 12h cron |
| `local.py` | Local workspace files | None | `contacts`, `documents`, `notes` | 12h cron |
| `tjmg.py` | tjmg.jus.br | None | `notes` (court_case) | 12h cron |
| `tjsp.py` | esaj.tjsp.jus.br | None | `notes` (court_case) | 12h cron |
| `twitter.py` | X API (xurl CLI) | xurl OAuth2 | `notes` (x_mention) | 12h cron |
| `web_search.py` | Brave Search API | `BRAVE_API_KEY` | `notes` (web_mention) | 12h cron |
| `import_structured.py` | Internal ETL | None | `family_members`, `companies`, `properties` | Manual |

### Files Reference

```
rgvl/
├── data/
│   ├── rgvl.db                    # SQLite canonical database
│   └── collectors/
│       ├── __init__.py
│       ├── email.py               # Gmail contact discovery
│       ├── father_drive.py        # Father profile from Drive
│       ├── jucemg.py              # Junta Comercial MG
│       ├── jucesp.py              # Junta Comercial SP
│       ├── local.py               # Workspace file harvester
│       ├── tjmg.py                # TJ Minas Gerais
│       ├── tjsp.py                # TJ São Paulo
│       ├── twitter.py             # X/Twitter search
│       ├── web_search.py          # Brave Search
│       ├── import_structured.py   # ETL: notes → normalized tables
│       └── JUCEMG_SPEC.md         # JUCEMG technical spec
└── docs/
    ├── DATA_COLLECTION.md         # This file
    ├── INTEL.md                   # Knowledge base (narrative source)
    ├── BUSCAS.md                  # Pending search queries
    └── ARCHITECTURE.md            # System architecture
```

---

# Technical Implementation & Maintenance

**Última atualização:** 2026-03-23
**Autor:** Hefesto (Engineering)

---

## 1. System Architecture (As-Built)

### Services & Ports

| Service | Technology | Port | Launchd Label |
|---------|-----------|------|---------------|
| **Web Dashboard** | Flask | 5004 | `com.rgvl.web` |
| **API** | FastAPI (Uvicorn) | 5003 | `com.rgvl.api` |
| **Database** | SQLite | file | — |

### How They Communicate

```
Browser (port 5004)
  └── Flask web server (proxy)
        └── FastAPI (port 5003)
              └── SQLite database (file-based)
```

The web dashboard proxies API calls to port 5003 via `/api/proxy/<endpoint>`.

> ⚠️ **Note:** The web portal runs on **port 5004**, not 5002. The plist sets `PORT=5004`.

### Launchd Plist Locations

- API: `~/Library/LaunchAgents/com.rgvl.api.plist`
- Web: `~/Library/LaunchAgents/com.rgvl.web.plist`

Both plists use `KeepAlive: true`, meaning launchd auto-restarts the service after crashes and on boot.

### Virtual Environment

Both services share the venv at:
```
~/.openclaw/workspace-shared/projects/rgvl/.venv/bin/python
```

---

## 2. Service Management

### Check Service Status

```bash
# All rgvl services
launchctl list | grep rgvl

# Via HTTP (if running)
curl -s http://localhost:5003/api/health
curl -s http://localhost:5004/
```

### View Logs

```
~/.openclaw/workspace-shared/projects/rgvl/.logs/
```

| File | Contents |
|------|----------|
| `api.log` | FastAPI/uvicorn stdout + stderr |
| `web.log` | Flask stdout + stderr |
| `rgvl-health.log` | Health check script output |
| `health-check.log` | Timestamped health check results |

```bash
tail -f ~/.openclaw/workspace-shared/projects/rgvl/.logs/api.log
tail -50 ~/.openclaw/workspace-shared/projects/rgvl/.logs/web.log
cat ~/.openclaw/workspace-shared/projects/rgvl/.logs/rgvl-health.log
```

### Restart Services Manually

```bash
# Restart API
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist

# Restart Web
launchctl unload ~/Library/LaunchAgents/com.rgvl.web.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.web.plist
```

### Understanding the Launchd Plists

Key fields in each `.plist`:

```xml
<key>Label</key>
<string>com.rgvl.api</string>

<key>ProgramArguments</key>
<array>
    <string>/path/to/.venv/bin/python</string>
    <string>-m</string>
    <string>api.main</string>
</array>

<key>WorkingDirectory</key>
<string>/path/to/rgvl</string>

<key>EnvironmentVariables</key>
<dict>
    <key>PORT</key>
    <string>5003</string>
</dict>

<key>RunAtLoad</key>
<true/>

<key>KeepAlive</key>
<true/>

<key>StandardOutPath</key>
<string>.../.logs/api.log</string>
```

Reload after editing:
```bash
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
```

---

## 3. Health Monitoring

### Health Check Script

```
~/.openclaw/workspace-shared/projects/rgvl/scripts/monitor.sh
```

### How It Works

The script performs HTTP checks on both ports:

```bash
curl -s --max-time 5 http://localhost:5003/
curl -s --max-time 5 http://localhost:5004/
```

If a port fails, it unloads the corresponding launchd service, waits, reloads it, and verifies recovery.

### Verify Health Check Is Working

```bash
~/.openclaw/workspace-shared/projects/rgvl/scripts/monitor.sh
cat ~/.openclaw/workspace-shared/projects/rgvl/.logs/rgvl-health.log
```

Example healthy output:
```
Sun Mar 22 06:54:53 -03 2026: RG VL services health check - RESTARTED services, now healthy
```

### Set Up Periodic Health Checks (Cron)

```cron
*/5 * * * * /Users/rodrigomelo/.openclaw/workspace-shared/projects/rgvl/scripts/monitor.sh >> /Users/rodrigomelo/.openclaw/workspace-shared/projects/rgvl/.logs/health-check.log 2>&1
```

---

## 4. Backup & Recovery

### Backup Scripts

- Python: `~/.openclaw/workspace-shared/projects/rgvl/data/backup.py`
- Shell: `~/.openclaw/workspace-shared/projects/rgvl/data/backup.sh`

### Backup Directory

```
~/.openclaw/workspace-shared/projects/rgvl/data/backups/
```

### Manual Backup

```bash
# Simple (keeps all)
python ~/.openclaw/workspace-shared/projects/rgvl/data/backup.py

# Compress + keep last 7
python ~/.openclaw/workspace-shared/projects/rgvl/data/backup.py --compress --keep 7

# Via shell script
~/.openclaw/workspace-shared/projects/rgvl/data/backup.sh

# List backups
python ~/.openclaw/workspace-shared/projects/rgvl/data/backup.py --list
```

### Automatic Daily Backup (Cron)

```cron
0 2 * * * /Users/rodrigomelo/.openclaw/workspace-shared/projects/rgvl/data/backup.sh >> /Users/rodrigomelo/.openclaw/workspace-shared/projects/rgvl/.logs/backup.log 2>&1
```

Runs daily at 2 AM using SQLite's transaction-safe `.backup` command. Keeps last 7 backups.

### Restore from Backup

```bash
# List then restore
python ~/.openclaw/workspace-shared/projects/rgvl/data/backup.py --list
python ~/.openclaw/workspace-shared/projects/rgvl/data/backup.py --restore rgvl_20260320_020000.db
```

Or manually:
```bash
# Stop services first
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl unload ~/Library/LaunchAgents/com.rgvl.web.plist

# Copy backup over live DB
cp ~/.openclaw/workspace-shared/projects/rgvl/data/backups/rgvl_YYYYMMDD_HHMMSS.db \
   ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db

# Restart
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.web.plist
```

> ⚠️ **Always stop services before manual restore**, or use `backup.py --restore`.

---

## 5. Troubleshooting Guide

### Service Won't Start — "Address Already in Use"

```bash
# Find what's using the port
lsof -i :5003
lsof -i :5004

# Kill and restart
kill -9 <PID>
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
```

### Wrong Port Configured

The web service runs on **5004**, not 5002. If you're seeing unexpected behavior:
1. Check plist: `cat ~/Library/LaunchAgents/com.rgvl.web.plist`
2. Verify: `lsof -i :5004`

### Launchd Not Restarting Service

```bash
launchctl list | grep rgvl
tail -30 ~/.openclaw/workspace-shared/projects/rgvl/.logs/api.log

# Reload the plist
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
```

### API Returning 500 Errors

```bash
# Check API log
tail -50 ~/.openclaw/workspace-shared/projects/rgvl/.logs/api.log

# Test health endpoint
curl http://localhost:5003/api/health

# Verify database integrity
sqlite3 ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db "PRAGMA integrity_check;"

# Check DB file permissions
ls -la ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db
```

### JSON Decode Errors in SQLite Columns

Many columns store JSON strings (e.g., `socios`, `partners`). The API's `to_dict()` helper decodes them:

```python
elif isinstance(value, str) and value.startswith('['):
    try:
        d[column.name] = json.loads(value)
    except:
        d[column.name] = value  # Returns raw string on failure
```

If `JSONDecodeError` appears in logs:
1. Identify the failing column from the stack trace
2. Inspect the raw data:
   ```bash
   sqlite3 ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db \
     "SELECT id, <column> FROM <table> LIMIT 5;"
   ```
3. Fix the value directly:
   ```sql
   UPDATE <table> SET <column> = '[...]' WHERE id = <id>;
   ```

### Database Locked Errors

SQLite allows one writer at a time. If `database is locked`:
```bash
lsof ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db
```
Wait for pending writes, or restart the API service.

---

## 6. Adding a New Collector

### Step 1: Place the Collector

Collectors live in:
```
~/.openclaw/workspace-shared/projects/rgvl/data/collectors/
```

Name the file after the source: `tjsp.py`, `jucesp.py`, `receita.py`, etc.

### Step 2: Use the Correct Imports

The project uses the **data layer** (not the `database/` folder from project root):
```python
# ✅ Correct (from data/collectors/)
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
from database import SessionLocal
from models.entity import Company, Property, Person

# ❌ Wrong (will import the wrong module)
from database import SessionLocal
```

See `data/collectors/jucemg.py` for the canonical pattern.

### Step 3: Register in the Database

```python
from database import SessionLocal
from models.entity import Company

db = SessionLocal()
try:
    company = Company(
        trade_name="...",
        legal_name="...",
        cnpj="...",
        fonte="jucemg"          # Tag the source
    )
    db.add(company)
    db.commit()
finally:
    db.close()
```

### Step 4: Add Cron Scheduling

For periodic collection:
```cron
# Run JUCEMG every 6 hours
0 */6 * * * cd ~/.openclaw/workspace-shared/projects/rgvl/data && python collectors/jucemg.py >> ~/.openclaw/workspace-shared/projects/rgvl/.logs/collector_jucemg.log 2>&1

# Run TJSP every 12 hours
0 */12 * * * cd ~/.openclaw/workspace-shared/projects/rgvl/data && python collectors/tjsp.py >> ~/.openclaw/workspace-shared/projects/rgvl/.logs/collector_tjsp.log 2>&1
```

For ad-hoc collection:
```bash
cd ~/.openclaw/workspace-shared/projects/rgvl/data
python collectors/tjsp.py
```

### Step 5: Integrate with the DB Layer

The `data/` directory has its own Python package structure:
```
data/
├── collectors/
│   ├── __init__.py
│   ├── jucemg.py
│   └── tjsp.py
├── database.py          # SQLAlchemy session/engine
├── models/
│   └── entity.py         # SQLAlchemy models (Company, Property, Person, etc.)
├── rgvl.db              # SQLite database
└── backup.py
```

To add a new entity model, edit `data/models/entity.py`.

---

# Technical Infrastructure, Service Management & Backups

**Última atualização:** 2026-03-23
**Hefesto** 🔨 — Engineering

---

## 1. Infraestrutura como Código

### Estrutura de Diretórios

```
rgvl/
├── data/
│   ├── rgvl.db                 # Banco SQLite (produção)
│   ├── backups/                # Backups automáticos
│   ├── collectors/             # Scripts de coleta (email.py, jucemg.py, etc.)
│   ├── models/
│   │   └── entity.py          # Modelos SQLAlchemy
│   ├── database.py             # Configuração de conexão
│   └── api/
│       └── main.py             # API Flask (porta 5003)
├── web/
│   ├── index.html              # Dashboard web
│   └── server.py               # Servidor Flask (porta 5002)
├── scripts/
│   └── monitor.sh             # Script de monitoramento
└── .logs/                      # Logs de execução
```

### Ambientes

| Ambiente | Local | Descrição |
|----------|-------|-----------|
| **Produção** | Mac Mini de Rodrigo | Serviços rodando 24/7 via launchd |
| **Desenvolvimento** | Workspace local | Testes antes de deploy |

---

## 2. Service Management

### Stack de Serviços

| Serviço | Tecnologia | Porta | launchd | Status |
|---------|-----------|-------|---------|--------|
| **Web** | Flask | 5002 | `com.rgvl.web` | ✅ rodando |
| **API** | Flask (REST) | 5003 | `com.rgvl.api` | ✅ rodando |
| **DB** | SQLite | arquivo | — | ✅ ok |

### Como se Comunicam

```
Browser → Web (5002) → API (5003) → SQLite (arquivo)
                    ↓ (proxy /api/*)
```

### Status dos Serviços

```bash
# Ver todos os serviços rgvl
launchctl list | grep rgvl

# Verificar health da API
curl http://localhost:5003/api/health

# Verificar web
curl http://localhost:5002/
```

### Reiniciar Serviços

```bash
# API
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist

# Web
launchctl unload ~/Library/LaunchAgents/com.rgvl.web.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.web.plist
```

### Configuração launchd

Ambos os serviços têm:
- `KeepAlive: true` — reinicia automaticamente se cair
- `RunAtLoad: true` — inicia no boot do Mac
- `ThrottleInterval: 10` — tenta novamente em 10s se falhar

Arquivos:
- `~/Library/LaunchAgents/com.rgvl.api.plist`
- `~/Library/LaunchAgents/com.rgvl.web.plist`

---

## 3. Monitoramento

### Script de Monitoramento

```
~/.openclaw/workspace-shared/projects/rgvl/scripts/monitor.sh
```

### O que ele faz

1. Testa HTTP em `localhost:5002` e `localhost:5003`
2. Se algum falhar, reinicia o serviço correspondente via launchd
3. Loga resultado em `/tmp/rgvl-monitor.log`

### Verificar Funcionamento

```bash
# Executar manualmente
~/.openclaw/workspace-shared/projects/rgvl/scripts/monitor.sh

# Ver logs
cat /tmp/rgvl-monitor.log
```

### Alertas

O monitor NÃO envia emails/Slack por conta própria. Futuras integrações:
- Enviar notificação via Discord (canal #rgvl)
- Enviar email via `himalaya` ou `gog`
- Webhook para Telegram

---

## 4. Troubleshooting

### Serviço Não Sobe — "Address Already in Use"

```bash
# Ver o que está usando a porta
lsof -i :5002
lsof -i :5003

# Matar e reiniciar
kill -9 <PID>
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
```

### Serviço Caiu Após Atualização

```bash
# Ver logs
cat /tmp/rgvl-api.log
cat /tmp/rgvl-web.log

# Verificar se imports estão funcionando
cd ~/.openclaw/workspace-shared/projects/rgvl/data
python3 -c "from api.main import app; print('API OK')"

cd ~/.openclaw/workspace-shared/projects/rgvl/web
python3 -c "from server import app; print('Web OK')"
```

### API Retornando 500

```bash
# Ver log da API
tail -50 /tmp/rgvl-api.log

# Testar health
curl http://localhost:5003/api/health

# Verificar integridade do banco
sqlite3 ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db "PRAGMA integrity_check;"
```

### Erro "Module Not Found: flask"

Flask não está instalado no Python do sistema. Corrigir:

```bash
/usr/bin/python3 -m pip install flask requests sqlalchemy flask-cors python-dotenv -q
```

Depois reiniciar os serviços.

### Database Locked

```bash
lsof ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db
```

Esperar ou reiniciar a API.

### Erros JSON em Colunas SQLite

Várias colunas armazenam JSON (ex: `socios`, `partners`). O `to_dict()` da API tenta decodificar:

```python
elif isinstance(value, str) and value.startswith('['):
    try:
        d[column.name] = json.loads(value)
    except:
        d[column.name] = value  # Devolve string crua se falhar
```

Se aparecer `JSONDecodeError` nos logs, inspecionar:

```bash
sqlite3 ~/.openclaw/workspace-shared/projects/rgvl/data/rgvl.db \
  "SELECT id, <coluna> FROM <tabela> LIMIT 5;"
```

---

## 5. Backup & Recovery

### Scripts de Backup

- Python: `data/backup.py`
- Shell: `data/backup.sh`

### Diretório de Backups

```
~/.openclaw/workspace-shared/projects/rgvl/data/backups/
```

Formato: `rgvl_YYYYMMDD_HHMMSS.db`

### Backup Manual

```bash
# Simples (mantém todos)
python data/backup.py

# Com compressão e mantém últimos 7
python data/backup.py --compress --keep 7

# Via shell script
data/backup.sh

# Listar backups
python data/backup.py --list
```

### Backup Automático (Cron)

```cron
0 2 * * * ~/.openclaw/workspace-shared/projects/rgvl/data/backup.sh >> ~/.openclaw/workspace-shared/projects/rgvl/.logs/backup.log 2>&1
```

Executa diariamente às 2h usando `.backup` do SQLite. Mantém últimos 7.

### Restaurar de Backup

```bash
# Listar e restaurar
python data/backup.py --list
python data/backup.py --restore rgvl_20260320_020000.db
```

Ou manualmente (PARAR SERVIÇOS PRIMEIRO):

```bash
# Parar
launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl unload ~/Library/LaunchAgents/com.rgvl.web.plist

# Copiar backup
cp data/backups/rgvl_YYYYMMDD_HHMMSS.db data/rgvl.db

# Reiniciar
launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist
launchctl load ~/Library/LaunchAgents/com.rgvl.web.plist
```

> ⚠️ **Sempre parar serviços antes de restaurar manualmente**, ou usar `backup.py --restore`.

---

## 6. Adicionar Novo Collector

### Passo 1: Criar o Script

```
data/collectors/<nome>.py
```

### Passo 2: Imports Corretos

```python
# ✅ Correto (da pasta data/collectors/)
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
from database import SessionLocal
from models.entity import Company, Property, Person

# ❌ Errado (importaria módulo errado)
from database import SessionLocal
```

### Passo 3: Registrar no Banco

```python
from database import SessionLocal
from models.entity import Company

db = SessionLocal()
try:
    company = Company(
        trade_name="...",
        legal_name="...",
        cnpj="...",
        fonte="novo_collector"  # Tag da fonte
    )
    db.add(company)
    db.commit()
finally:
    db.close()
```

### Passo 4: Agendar no Cron

```cron
# A cada 12h
0 */12 * * * cd ~/.openclaw/workspace-shared/projects/rgvl/data && python collectors/novo.py >> ~/.openclaw/workspace-shared/projects/rgvl/.logs/collector_novo.log 2>&1
```

### Passo 5: Testar

```bash
cd ~/.openclaw/workspace-shared/projects/rgvl/data
python collectors/novo.py
```

---

## 7. Acesso Remoto (Tailscale)

### URLs de Acesso Remoto

| Serviço | URL |
|---------|-----|
| **Web** | http://mac-mini-de-rodrigo.tail84bea3.ts.net:5002/ |
| **API** | http://mac-mini-de-rodrigo.tail84bea3.ts.net:5003/ |

### Requisito

O Tailscale deve estar instalado e ativo no Mac Mini. O hostname `mac-mini-de-rodrigo` é o nome da máquina na rede Tailscale.

### Verificar Tailscale

```bash
tailscale status
```

### Se Não Funcionar

1. Verificar se Tailscale está rodando no Mac Mini
2. Verificar se o firewall permite conexões nas portas 5002 e 5003
3. Testar localmente primeiro: `curl http://localhost:5002/`

---

## 8. Git & Versionamento

### Repositório

```
https://github.com/rodrigomelo/rgvl
```

### Commits Recentes (infra)

| Commit | Descrição |
|--------|-----------|
| `9aae091` | feat(services): add monitoring and ensure permanence |
| `7e16304` | fix(network): bind to 0.0.0.0 for Tailscale access |
| `6360bce` | fix(ci): disable auto-run, manual trigger only |
| `35a81b8` | fix(ports): API on 5003, Web on 5002 |
| `a62c541` | feat(services): configure launchd for auto-start |
| `30e1a99` | feat(architecture): migrate to FastAPI + Docker + CI/CD + tests |

### Antes de Commitar

```bash
cd ~/.openclaw/workspace-shared/projects/rgvl

# Pull antes de push
git pull --rebase origin main

# Commitar
git add -A
git commit -m "<type>(<scope>): <description>"

# Push
git push origin main
```

### O Que NÃO Commitar

- `.env` com tokens/API keys
- Arquivos grandes (>5MB)
- Dados sensíveis (CPFs, CNPJs públicos são ok, senhas não)
- Backups (`.db` files)
- Logs

---

## 9. Stack Tecnológica

| Componente | Tecnologia | Versão |
|-----------|-----------|--------|
| **Linguagem** | Python | 3.x (Homebrew) |
| **Web Framework** | Flask | latest |
| **ORM** | SQLAlchemy | latest |
| **Banco** | SQLite | built-in |
| **API REST** | Flask | porta 5003 |
| **Dashboard** | Flask + HTML/JS | porta 5002 |
| **Service Manager** | launchd (macOS) | built-in |
| **Rede** | Tailscale | latest |
| **Versionamento** | Git | latest |

---

## 10. Dependências

### Pacotes Python Instalados (sistema)

```bash
/usr/bin/python3 -m pip install flask requests sqlalchemy flask-cors python-dotenv
```

### Se Falta Algum Pacote

```bash
# Instalar no sistema
/usr/bin/python3 -m pip install <pacote>

# Verificar se está instalado
/usr/bin/python3 -c "import <pacote>; print('<pacote> OK')"
```

### Ambientes Virtuais

O projeto também suporta venv em `.venv/`. Se os serviços pararem de funcionar após mudança no sistema, verificar se o venv tem os pacotes necessários:

```bash
source .venv/bin/activate
pip install flask requests sqlalchemy flask-cors python-dotenv
```
