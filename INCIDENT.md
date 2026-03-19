# RGVL - Incident Report

## What Happened (2026-03-18)

### Problem
- Added `Note` model to `models/entity.py`
- Ran `Base.metadata.create_all(engine)` to create table
- This **reset the database** to empty!

### Root Cause
- `create_all()` with a new model definition doesn't just add the new table - it can recreate the database
- The database was pointing to wrong path: `data/data/rgvl.db` instead of `data/rgvl.db`

### Resolution
1. Found backup at `.backups/rgvl_20260318_201324.db` (1 person, 3 companies)
2. Restored backup to `data/rgvl.db`
3. Fixed `database.py` to point to correct path: `PROJECT_ROOT / 'data' / 'rgvl.db'`
4. Restarted API - data restored!

## Current Status (Working)
- ✅ API running on port 5004
- ✅ Web running on port 5003
- ✅ Database: 1 person, 3 companies, 2 properties
- ✅ Data path: `data/rgvl.db`

## Database Structure
```
rgvl/
├── data/
│   └── rgvl.db        ← ACTIVE DATABASE
├── .backups/           ← Backup location
│   └── rgvl_20260318_201324.db
```

## Collectors Status
- Father Drive: Works
- JUCESP: Import works but returns 0 results
- JUCEMG: Site offline
- Note model: Added (but not fully tested)

## Lessons Learned
1. NEVER run `create_all()` on production database
2. Always backup before schema changes
3. Database path was wrong (pointed to data/data/ redundancy)
