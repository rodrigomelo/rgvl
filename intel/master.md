# RGVL Intelligence — Master Index

**Last Updated:** 2026-03-24

## Structure

| File | Description |
|---------|-----------|
| [timeline.md](./timeline.md) | Events such as birth, marriage, death, and business milestones |
| [companies.md](./companies.md) | Companies and ownership participations |
| [legal.md](./legal.md) | Legal cases |
| [properties.md](./properties.md) | Properties and addresses |
| [family.md](./family.md) | Family network and relationships |
| [ancestors.md](./ancestors.md) | Grandparents and ancestors |
| [contacts.md](./contacts.md) | Contacts and connections |

## Data Flow

```
intel/*.md → etl/seed.py → data/rgvl.db → api → web/portal
```

**Rule:** Never insert data directly into the database. Always go through INTEL.

## Status

- [ ] timeline.md — pending
- [ ] companies.md — pending
- [ ] legal.md — pending
- [ ] properties.md — pending
- [ ] family.md — pending
- [ ] contacts.md — pending
