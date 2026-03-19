# RGVL Platform

This is the monorepo for the RGVL data and web platform.

## Structure

- `data/` — RGVL Data API (Flask, SQLite, collectors)
- `web/` — RGVL Web Dashboard (Flask, HTML/JS frontend)
- `docs/` — Documentation and architecture
- `scripts/` — Utility and dev scripts
- `.github/`, `.vscode/`, etc. — Project configs

## Quick Start

### Data API
```bash
cd data
pip install -r requirements.txt
python -m api.main
# Runs on http://localhost:5004
```

### Web Dashboard
```bash
cd web
pip install -r requirements.txt
python server.py
# Runs on http://localhost:5003
```

## About

RGVL is a personal data platform for family history and research.
