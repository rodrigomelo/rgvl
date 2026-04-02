# INTEL - Modular Knowledge Base

This directory contains structured research data organized by domain.

## Structure

```
intel/
├── README.md           # This file
├── timeline.md         # Life events (birth, death, marriage, etc.)
├── companies.md        # Business participations
├── legal.md           # Court cases and legal processes
├── properties.md      # Real estate and addresses
├── family.md          # Family network and relationships
└── contacts.md        # Contact information
```

## Rules

1. **INTEL is the source of truth** - All data must flow through INTEL → ETL → DB
2. **Never write directly to DB** - Always go through the parser
3. **Modular format** - Each domain has its own file
4. **Markdown tables** - Preferred format for structured data
5. **Dates** - Use ISO format (YYYY-MM-DD) or ~YYYY for approximate
6. **No reverse sync** - Database content must never be pushed back into INTEL automatically

## ETL Pipeline

```
intel/*.md → etl/seed.py → data/rgvl.db → API → Web
```

## Quality Rules

- Dates: `YYYY-MM-DD` or `~YYYY` for approximate
- Names: Full names, no abbreviations
- Sources: Always note where data came from
- Confidence: Use `[~]` prefix for uncertain data
