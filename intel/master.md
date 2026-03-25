# RGVL Intelligence — Master Index

**Last Updated:** 2026-03-24

## Estrutura

| Arquivo | Descrição |
|---------|-----------|
| [timeline.md](./timeline.md) | Eventos (nascimento, casamento, morte, empresa) |
| [companies.md](./companies.md) | Empresas e participações |
| [legal.md](./legal.md) | Processos judiciais |
| [properties.md](./properties.md) | Imóveis e endereços |
| [family.md](./family.md) | Rede familiar e relacionamentos |
| [ancestors.md](./ancestors.md) | Avós e ancestrais |
| [contacts.md](./contacts.md) | Contatos e connections |

## Fluxo de Dados

```
intel/*.md → etl/seed.py → data/rgvl.db → api → web/portal
```

**Regra:** Nunca inserir dados direto no DB. Sempre passar pelo INTEL.

## Status

- [ ] timeline.md — pending
- [ ] companies.md — pending
- [ ] legal.md — pending
- [ ] properties.md — pending
- [ ] family.md — pending
- [ ] contacts.md — pending
