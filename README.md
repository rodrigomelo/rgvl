# RGVL Platform

Personal data platform for family history and research.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RGVL Platform                        │
├─────────────────────────────────────────────────────────┤
│  Frontend (Flask)                                       │
│  ├── Dashboard (port 5002)                             │
│  ├── Family Tree                                        │
│  ├── Net Worth                                          │
│  └── Documents                                          │
├─────────────────────────────────────────────────────────┤
│  API (FastAPI)                                          │
│  ├── /api/family/* (persons, tree)                     │
│  ├── /api/assets/* (properties, companies)             │
│  ├── /api/documents/* (docs, legal)                    │
│  └── /api/search/* (global search)                     │
├─────────────────────────────────────────────────────────┤
│  Database (SQLite)                                      │
│  ├── rgvl.db (main database)                           │
│  └── .backups/ (automatic backups)                     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start API (FastAPI)
cd data
python -m uvicorn src.api.main:app --reload --port 5004

# Start Web (Flask)
cd web
python server.py
# Access at http://localhost:5002
```

### Docker

```bash
# Build and run
docker-compose up -d

# Access:
# API: http://localhost:5004/docs
# Web: http://localhost:5002
```

### Tests

```bash
cd data
python -m pytest src/tests/ -v
```

## API Documentation

- **Swagger UI:** http://localhost:5004/docs
- **ReDoc:** http://localhost:5004/redoc

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Statistics |
| GET | `/api/person` | Main person |
| GET | `/api/spouse` | Spouse |
| GET | `/api/siblings` | Siblings |
| GET | `/api/nephews` | Nephews |
| GET | `/api/children` | Children |
| GET | `/api/family/summary` | Family summary |
| GET | `/api/companies` | Companies |
| GET | `/api/properties` | Properties |
| GET | `/api/net-worth` | Net worth |
| GET | `/api/contacts` | Contacts |
| GET | `/api/documents` | Documents |
| GET | `/api/legal/processes` | Legal processes |
| GET | `/api/notes` | Notes |
| GET | `/api/events` | Events |
| GET | `/api/search?q=` | Global search |

## Features

- ✅ Family tree (5 generations)
- ✅ Net worth tracking
- ✅ Company management
- ✅ Property valuation
- ✅ Legal process tracking
- ✅ Document management
- ✅ Global search
- ✅ Auto-backup
- ✅ API documentation
- ✅ Docker support
- ✅ CI/CD pipeline
- ✅ Test coverage

## Security

- API runs on 127.0.0.1 (localhost only)
- Debug mode disabled in production
- CORS configured
- Input validation
- SQL injection protection

## License

Private project - All rights reserved.
