# RGVL Platform

Personal data platform for family history research — the Lanna family, spanning 5+ generations.

## Quick Start

```bash
# Install dependencies
pip install flask flask-cors sqlalchemy requests python-dotenv

# Seed the database (from INTEL.md research data)
python -m etl.seed

# Start API (port 5003)
python -m api.main

# Start Web Dashboard (port 5002, separate terminal)
cd web && python server.py
```

Access:
- **API:** http://localhost:5003 (docs at `/`)
- **Dashboard:** http://localhost:5002

## Data

| Entity | Count | Description |
|--------|-------|-------------|
| Pessoas | 26 | People across 5 generations |
| Relacionamentos | 30 | Family relationships (confirmed + speculative) |
| Empresas | 7 | Family companies (active + closed) |
| Tarefas | 5 | Pending research tasks |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/family/person/:id` | Person detail |
| GET | `/api/family/person/:id/tree` | Full family tree for a person |
| GET | `/api/family/person/:id/relatives` | All relatives |
| GET | `/api/family/generation/:n` | People by generation |
| GET | `/api/family/summary` | Family statistics |
| GET | `/api/assets/companies` | Companies (filter: `?person_id=X&status=ativa`) |
| GET | `/api/research/tasks` | Research tasks (filter: `?status=pendente`) |
| GET | `/api/research/searches` | Search history |
| GET | `/api/search?q=` | Global search |
| GET | `/api/stats` | Database statistics |
| GET | `/api/health` | Health check |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full documentation.

## Docker

```bash
docker-compose up -d
# API: http://localhost:5003
# Web: http://localhost:5002
```

## License

Private project — All rights reserved.
