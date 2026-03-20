# RGVL - Base de Conhecimento (INTERNO)
# Última atualização: 2026-03-20

⚠️ **RGVL = designação interna. NÃO USAR em buscas externas!**
⚠️ **Usar nome completo: Rodrigo Gorgulho de Vasconcellos Lanna**

---

## 🌳 Árvore Genealógica (5 Gerações)

> **Nota:** Dados estruturados (pessoas, empresas, imóveis, processos) estão no banco `data/rgvl.db`.
> Consultar via API: `http://localhost:5003/api/family/summary`

### Geração 5 — Bisavós
```
Edmundo Mariano da Costa Lanna (1878-1968) — Dentista
+ Maria da Glória de Vasconcellos
       │
       ├── Edmundo de Vasconcellos Lanna (1922-1992)
       ├── Thereza de Vasconcellos Lanna (1923-2006)
       └── Maria Auxiliadora de Vasconcellos Lanna (1925-2018)
```

### Geração 4 — Avós
```
Edmundo de Vasconcellos Lanna (1922-1992) ⚰️ — Dentista
+ Nice Gorgulho de Vasconcellos Lanna (1926-2019) ⚰️
       │
       ├── Henrique (nasc. 1966) — 6 filhos
       ├── Rodrigo Gorgulho (nasc. 1955) — 1 filho confirmado
       ├── Marcelo — 4 filhos
       └── Júnia — 5 filhos
```

### Geração 3 — Pais + Tios
- **Rodrigo Gorgulho de Vasconcellos Lanna** — Engenheiro Civil, Diretor na Construtora Barbosa Mello desde 2013. Casado com Rosália desde 1992.
- **Rosália Fagundes Ladeira** — Arquiteta, sócia F Ladeira Consultoria.
- **Henrique** — Engenheiro/Agrônomo. ERH Lanna Engenharia (baixada jun/2024). 16+ processos TJMG.
- **Marcelo** — 22-25 processos TJMG (BMG, AF Administradora). Casado com Mônica Maria Almeida Lanna.
- **Júnia** — Presidente AVOSC (2016). CNPJ 17.508.888/0001-70.

### Geração 2 — Rodrigo Melo (você)
- Nascido ~1980 em Itaituba/PA
- Nome anterior: Rodrigo da Silva Melo → alterado em 2025 para Rodrigo Melo Lanna
- VP J.P. Morgan Asset Management, São Paulo
- Reconhecimento de paternidade: fev/2017 (escritura pública)

### Geração 1 — Primos (15 conhecidos)
- **Henrique** (6): Luiza, Fernanda, Alessandra, Paula, Antônio Bahury, João Vítor
- **Marcelo** (4): Marcela, Andre, Bruno, Edmundo
- **Júnia** (5): Andrea, Paula Lanna Silva, Vivi, Pichita, Julia

---

## 📜 História da Paternidade

| Evento | Data | Detalhes |
|--------|------|----------|
| Nascimento | ~1980-1981 | Rodrigo Melo nascido em Itaituba/PA |
| Primeiro contato | ~2008 | Via telefone da avó paterna (cadastrado em haras) |
| Segundo contato | ~2011-2012 | Email de trabalho encontrado |
| Consulta jurídica | Nov 2016 | Advogado Rodrigo da Cunha Pereira |
| Pesquisa Facebook | Nov 2016 | Mapeamento completo da família via redes sociais |
| Reconhecimento | Fev 2017 | Escritura pública voluntária no cartório |
| Abandono afetivo | Dez 2018 | Processo consultado mas não ajuizado |
| Alteração de nome | 2025 | Rodrigo da Silva Melo → Rodrigo Melo Lanna |

**Mãe do Rodrigo:** A ser confirmada (não relacionada à família Lanna)

---

## 🔍 Fontes Consultadas
- FamilySearch.org (perfil Edmundo: G9PX-G84)
- consultasocio.com (empresas)
- advdinamico.com.br (sócios)
- consultacrea.com.br (CREA)
- escavador.com (Júnia - AVOSC)
- venda-imoveis.caixa.gov.br (propriedade Edmundo)
- familialana.com (genealogia - livro de 1943, páginas 125-142)
- Registro público de imóveis — 3° Ofício (Cartório Bolívar), BH (matrícula 121.974)
- Registro público de imóveis — 2° Ofício de Registro de Imóveis, BH (matrícula 15.902)

---

## 📧 Emails Importantes (Arquivados)

| Thread ID | Assunto | Data | Importância |
|-----------|---------|------|-------------|
| 159fa891a9a5546f | ESCRITURA DE RECONHECIMENTO DE PATERNIDADE | 2017 | 🔴 Crítica |
| 16780f7dcc8a9212 | Caso Rodrigo Melo Lanna - Abandono paterno afetivo | 2018 | 🔴 Alta |
| 167e65a8b383218f | Contatos com o Rodrigo Lanna | 2018-2019 | 🔴 Alta |
| 14d11fe198456ce0 | Rodrigo Gorgulho Vasconcelos Lanna | 2015 | 🟡 Média |
| 12e074d9d4c753ec | RODRIGO GORGULHO VASCONCELOS LANNA | 2011 | 🟡 Média |

---

## ⚠️ Limites LGPD
- Apenas dados públicos
- Não coletar: saúde, finanças pessoais, comunicações privadas

---

## 📌 Para Agentes

Dados estruturados estão no DB (`data/rgvl.db`). Nunca editar o DB manualmente.
Todas as alterações passam pelo ETL (`etl/seed.py`).

Consultas via API (porta 5003):
- `/api/family/person/<id>` — Pessoa com árvore
- `/api/family/summary` — Estatísticas
- `/api/assets/companies` — Empresas
- `/api/assets/properties` — Imóveis
- `/api/legal/processes` — Processos judiciais
- `/api/research/tasks` — Tarefas pendentes
- `/api/search?q=` — Busca global
