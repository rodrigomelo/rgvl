# Engineering — Hefesto

**Last Updated:** 2026-03-31

## Platform Status

### API
- Running at `http://localhost:5003` ✅
- Database: `data/rgvl.db` (581KB, 76 tables) ✅
- Requires authorization header for API access

### Collectors

#### Working Collectors
- `collectors/social_profiles.py` — Instagram + Facebook profile finder ✅
  - Found: 8 Instagram profiles for RGVL family
  - Run: `python3 collectors/social_profiles.py --no-db`
  - Note: `--no-db` avoids import conflicts; use `PYTHONPATH=. python3 data/collectors/social_profiles.py` for DB writes

#### Blocked/Issue Collectors
- `collectors/receita_federal.py`, `arisp.py`, etc. — fail with `ModuleNotFoundError: No module named 'data'`
  - Fix: Run with `PYTHONPATH=. python3 data/collectors/<name>.py`
  - The `data/` prefix imports require PYTHONPATH set to project root

#### New Collectors Created
- `collectors/linkedin_search.py` — LinkedIn public profile finder 🆕
  - Status: BLOCKED — LinkedIn returns HTTP 999 (anti-bot)
  - Need: Browser automation (Playwright) or LinkedIn API credentials
  - Run: `python3 collectors/linkedin_search.py --no-db`

- `collectors/detran_mg_vehicles.py` — DETRAN-MG vehicle lookup 🆕
  - Status: Portal accessible but `portalservicos.detran.mg.gov.br` unreachable from this machine
  - **BLOCKER:** Needs birth dates for both targets:
    - Rodrigo Gorgulho: 1955-12-17 ✅ (known)
    - Rosália: birth date unknown ❌
  - DETRAN-MG vehicle consultation URL: `https://portalservicos.detran.mg.gov.br/veiculos/consulta-veiculo`

### Critical Bugs Fixed

1. **`data/collectors/email.py` shadowing stdlib `email` module** 🔴
   - File `data/collectors/email.py` shadows Python's stdlib `email` module
   - This breaks all collectors that use `httpx` (which imports `urllib.request` which imports `email`)
   - **FIX APPLIED:** Renamed `data/collectors/email.py` → `data/collectors/email_collector.py`
   - httpx now works correctly after fix

### Scheduling

#### Crontab Issue ⚠️
- Current crontab points to **WRONG PATH**: `~/.openclaw/workspace/projects/rgvl` (doesn't exist)
- Should be: `~/.openclaw/workspace-shared/projects/rgvl`
- Crontab command is blocked/hanging on this system

#### Launchd Agent ✅ (FIXED)
- Created: `~/Library/LaunchAgents/com.rodrigomelo.rgvl-collectors.plist`
- Runs: `run_all.py` at 06:00 and 18:00 daily
- Loaded successfully: `launchctl load ~/Library/LaunchAgents/com.rodrigomelo.rgvl-collectors.plist`

### Database Status
- `vehicles` table: **EMPTY** (0 records) — needs DETRAN-MG query with birth dates
- `profiles` table: 51 records (Instagram + GitHub)
- `collection_runs` table: **EMPTY** — no collection run history recorded
- `empresas_familia`: 7 companies with CNPJs (some active, some baixada)

### TODO
- [ ] Get Rosália's birth date for DETRAN-MG vehicle search
- [ ] Fix crontab path (or verify launchd is working)
- [ ] Get LinkedIn API credentials or set up Playwright browser automation
- [ ] Fix remaining collectors that need PYTHONPATH
- [ ] Add birth date for Rodrigo (1955-12-17) to pessoas table
