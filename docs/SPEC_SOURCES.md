# SPEC: Painel de Fontes (Sources Panel) — RGVL Portal

## 1. Overview

O painel de Fontes exibe a **procedência (provenance)** de cada dado no portal RGVL — informando ao usuário de qual fonte (Gmail, Drive, TJMG, Cartório, etc.) cada fato foi extraído.

O painel tem **duas views complementares**:
- **View 1 — Badge de Fonte por Registro**:小额 badge ao lado de cada fato no timeline/perfil, indicando a fonte de origem.
- **View 2 — Dashboard de Fontes**: Visão agregada do sistema com contadores por tipo de fonte.

---

## 2. Design Language (herdado do portal existente)

| Token | Valor | Uso |
|-------|-------|-----|
| `--primary` | `#1E3A5F` | Títulos, sidebar, botões primários |
| `--primary-light` | `#2C5282` | Acentos secundários |
| `--secondary` | `#4A90A4` | Elementos informativos |
| `--accent` | `#E8B339` | Destaques, borda ativa |
| `--success` | `#2E7D32` | Status ativo |
| `--danger` | `#C62828` | Status inativo/baixa |
| `--warning` | `#F57C00` | Alertas |
| `--bg` | `#F5F7FA` | Background geral |
| `--card-bg` | `#FFFFFF` | Cards |
| `--text` | `#2D3748` | Texto principal |
| `--text-muted` | `#718096` | Texto secundário |
| `--border` | `#E2E8F0` | Bordas |
| `--shadow` | `0 2px 8px rgba(0,0,0,0.08)` | Sombra padrão |
| `--shadow-hover` | `0 4px 12px rgba(0,0,0,0.12)` | Sombra hover |

**Tipografia**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`  
**Border-radius padrão**: `10px` para cards, `4px` para badges.

---

## 3. Source Types — Iconografia e Cores

Cada fonte tem um emoji + cor de badge própria:

| Fonte | Emoji | Cor de fundo | Cor do texto | Exemplo de dado |
|-------|-------|--------------|--------------|-----------------|
| `gmail` | 📧 | `#FCE8E6` | `#C62828` | Emails de contato familiar |
| `google_drive` | 📄 | `#E8F0FE` | `#1D4ED8` | Certidões, documentos |
| `tjmg` | 🏛️ | `#FEF3C7` | `#92400E` | Processos de BH |
| `tjsp` | ⚖️ | `#F3E5F5` | `#6D28D9` | Processos de SP |
| `jucemg` | 📋 | `#DBEAFE` | `#1D4ED8` | Empresas abertas |
| `jucep` | 📋 | `#DBEAFE` | `#1D4ED8` | Empresas (ESPÍRITO SANTO) |
| `cartorio` | 📜 | `#D1FAE5` | `#065F46` | Certidões de nascimento |
| `web_search` | 🔍 | `#E0E7FF` | `#3730A3` | Dados de busca pública |
| `familysearch` | 👨‍👩‍👧 | `#FCE7F3` | `#9D174D` | Registros genealógicos |
| `manual` | ✏️ | `#F1F5F9` | `#475569` | Inputs diretos |
| `crea` | 🏗️ | `#FED7AA` | `#9A3412` | Registros profissionais |
| `linkedin` | 💼 | `#E0E7FF` | `#3730A3` | Dados profissionais |
| `escavador` | 🔎 | `#EDE9FE` | `#6D28D9` | Dados biográficos |
| `inteli` | 💡 | `#ECFDF5` | `#065F46` | Documentos INTEL |
| `default` | 🔗 | `#F1F5F9` | `#475569` | Fonte genérica |

---

## 4. Component Inventory

### 4.1 Source Badge (`.source-badge`)

**Propósito**: Badge pequeno que aparece ao lado de cada fato no timeline ou perfil.

**Estrutura HTML**:
```html
<span class="source-badge source-[tipo]">[emoji] [label curto]</span>
```

**Estilos**:
- `display: inline-flex; align-items: center; gap: 4px;`
- `padding: 2px 8px; border-radius: 4px;`
- `font-size: 11px; font-weight: 500;`
- `min-width: 0; white-space: nowrap;`
- Cada tipo de fonte tem sua própria cor de fundo/texto (ver tabela acima)
- Hover: `cursor: help; opacity: 0.85;`

**Tooltip**: Ao passar o mouse, mostrar tooltip com:
- Nome completo da fonte
- Data de coleta (se disponível)
- Quantidade de registros dessa fonte

**Tamanhos**:
- `.source-badge.sm` — 10px font, padding 1px 6px (para inside timeline events)
- `.source-badge` — default (para perfil/detalhes)
- `.source-badge.lg` — 12px font, padding 4px 10px (para dashboard cards)

### 4.2 Source Detail Row (`.source-row`)

**Propósito**: Linha com ícone, nome da fonte, contagem e badge.

**Estrutura HTML**:
```html
<div class="source-row" data-source="jucemg">
    <span class="source-badge source-jucemg lg">📋 JUCEMG</span>
    <span class="source-row-label">8 empresas</span>
    <span class="source-row-detail">Última coleta: 20/03/2026</span>
</div>
```

**Estilos**:
- `display: flex; align-items: center; gap: 12px;`
- `padding: 10px 14px;`
- `border-bottom: 1px solid var(--border);`
- Hover: background `var(--bg); cursor: pointer;`
- Click: abre modal/painel lateral com detalhes dessa fonte

### 4.3 Sources Panel Section (`.section` + `#sources`)

**Propósito**: Section completa no portal, acessível via sidebar.

**Posição na sidebar**: Entre "Timeline" e o final.

**Estrutura**:
```
📜 Fontes dos Dados
├── Tabs: [Vista Badge] [Dashboard]
├── Tab: Vista Badge
│   ├── Per person: lista de fatos + badges de fonte
│   └── Exemplo:
│       Edmundo de Vasconcellos
│       ├── Nascimento 📜 Cartório BH
│       ├── Óbito 📜 Cartório SP
│       ├── Casamento 🏛️ TJMG - 1944
│       └── Empresas 📋 JUCEMG (3)
│
└── Tab: Dashboard
    ├── Grid de cards por fonte com contadores
    └── Barra de confiança geral
```

### 4.4 Sources Modal / Side Panel (`.source-detail-panel`)

**Propósito**: Ao clicar em uma fonte ou badge, mostrar painel lateral com todos os registros.

**Estrutura**:
- Painel lateral direito (300-400px)
- Overlay escuro no fundo
- Lista de registros daquela fonte
- Botão fechar

### 4.5 Source Confidence Bar (`.source-confidence`)

**Propósito**: Barra indicando quanto do sistema está coberto por fontes verificadas.

**Visual**:
- Barra de progresso colorida
- Label: "X% dos dados com fonte verificada"
- Cores: verde (>80%), amarelo (50-80%), vermelho (<50%)

---

## 5. Interaction Specifications

### 5.1 Badge Interactions
| Ação | Comportamento |
|------|---------------|
| Hover | Tooltip com detalhes da fonte (200ms delay) |
| Click | Abre source-detail-panel com lista de registros |
| Passive | Só exibe — não bloqueia interação do elemento pai |

### 5.2 Dashboard Interactions
| Ação | Comportamento |
|------|---------------|
| Hover em card | Elevação de sombra, escala 1.02 |
| Click em card | Abre panel com lista de registros |
| Click em tab | Alterna entre badge view e dashboard |

### 5.3 Side Panel Interactions
| Ação | Comportamento |
|------|---------------|
| Click fora | Fecha panel |
| ESC key | Fecha panel |
| Click X | Fecha panel |
| Scroll interno | Scroll da lista de registros |

---

## 6. API Changes Required

### 6.1 New Endpoint: `GET /api/sources/summary`

Retorna agregação de todas as fontes do sistema.

**Response**:
```json
{
  "total_records": 142,
  "records_with_source": 138,
  "confidence_percent": 97,
  "sources": [
    {
      "type": "jucemg",
      "label": "JUCEMG",
      "emoji": "📋",
      "count": 8,
      "records": ["empresa", "pessoa"],
      "last_collected": "2026-03-20",
      "color_bg": "#DBEAFE",
      "color_text": "#1D4ED8"
    },
    ...
  ]
}
```

### 6.2 New Endpoint: `GET /api/sources/person/:id`

Retorna todas as fontes vinculadas a uma pessoa específica.

**Response**:
```json
{
  "person_id": 6,
  "person_name": "Rodrigo Gorgulho de Vasconcellos Lanna",
  "facts": [
    {
      "fact_type": "birth",
      "fact_label": "Nascimento",
      "source_type": "cartorio",
      "source_emoji": "📜",
      "source_label": "Cartório BH",
      "source_detail": "Certidão original",
      "date": "1955-12-17",
      "location": "Belo Horizonte, MG"
    },
    ...
  ]
}
```

### 6.3 Changes to Existing Endpoints

**`GET /api/family/timeline`** — adicionar campo `source_type` e `source_label`:
```json
{
  "id": 1,
  "event_type": "birth",
  "person_name": "Edmundo de Vasconcellos Lanna",
  "description": "nasceu em Barra Longa/MG",
  "event_date": "1922-04-24",
  "source_type": "cartorio",
  "source_emoji": "📜",
  "source_label": "Cartório Barra Longa"
}
```

**`GET /api/family/person/:id`** — já tem campo `fonte` (string simples). Manter retrocompatível.

---

## 7. CSS Additions (add to inline `<style>` in index.html)

### New CSS Variables
```css
/* Source badge colors */
--source-gmail-bg: #FCE8E6; --source-gmail-text: #C62828;
--source-drive-bg: #E8F0FE; --source-drive-text: #1D4ED8;
--source-tjmg-bg: #FEF3C7; --source-tjsp-text: #92400E;
--source-tjsp-bg: #F3E5F5; --source-tjsp-text: #6D28D9;
--source-jucemg-bg: #DBEAFE; --source-jucemg-text: #1D4ED8;
--source-jucep-bg: #DBEAFE; --source-jucep-text: #1D4ED8;
--source-cartorio-bg: #D1FAE5; --source-cartorio-text: #065F46;
--source-web-bg: #E0E7FF; --source-web-text: #3730A3;
--source-familysearch-bg: #FCE7F3; --source-familysearch-text: #9D174D;
--source-manual-bg: #F1F5F9; --source-manual-text: #475569;
--source-crea-bg: #FED7AA; --source-crea-text: #9A3412;
--source-linkedin-bg: #E0E7FF; --source-linkedin-text: #3730A3;
--source-escavador-bg: #EDE9FE; --source-escavador-text: #6D28D9;
--source-inteli-bg: #ECFDF5; --source-inteli-text: #065F46;
--source-default-bg: #F1F5F9; --source-default-text: #475569;
```

### Source Badge Classes
```css
.source-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  min-width: 0;
  white-space: nowrap;
  box-sizing: border-box;
  cursor: help;
  transition: opacity 0.2s;
}
.source-badge:hover { opacity: 0.85; }
.source-badge.sm { font-size: 10px; padding: 1px 6px; }
.source-badge.lg { font-size: 12px; padding: 4px 10px; }
/* Source type colors */
.source-badge.source-gmail { background: var(--source-gmail-bg); color: var(--source-gmail-text); }
.source-badge.source-google_drive { background: var(--source-drive-bg); color: var(--source-drive-text); }
.source-badge.source-tjmg { background: #FEF3C7; color: #92400E; }
.source-badge.source-tjsp { background: var(--source-tjsp-bg); color: var(--source-tjsp-text); }
.source-badge.source-jucemg { background: var(--source-jucemg-bg); color: var(--source-jucemg-text); }
.source-badge.source-jucep { background: var(--source-jucep-bg); color: var(--source-jucep-text); }
.source-badge.source-cartorio { background: var(--source-cartorio-bg); color: var(--source-cartorio-text); }
.source-badge.source-web_search { background: var(--source-web-bg); color: var(--source-web-text); }
.source-badge.source-familysearch { background: var(--source-familysearch-bg); color: var(--source-familysearch-text); }
.source-badge.source-manual { background: var(--source-manual-bg); color: var(--source-manual-text); }
.source-badge.source-crea { background: var(--source-crea-bg); color: var(--source-crea-text); }
.source-badge.source-linkedin { background: var(--source-linkedin-bg); color: var(--source-linkedin-text); }
.source-badge.source-escavador { background: var(--source-escavador-bg); color: var(--source-escavador-text); }
.source-badge.source-inteli { background: var(--source-inteli-bg); color: var(--source-inteli-text); }
.source-badge.source-default { background: var(--source-default-bg); color: var(--source-default-text); }
```

### Source Row
```css
.source-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  border-radius: 0;
  transition: background 0.15s;
}
.source-row:hover { background: var(--bg); }
.source-row:last-child { border-bottom: none; }
.source-row-label { font-size: 13px; color: var(--text); flex: 1; }
.source-row-detail { font-size: 11px; color: var(--text-muted); }
```

### Sources Section Layout
```css
.sources-tabs { display: flex; gap: 0; margin-bottom: 16px; border-bottom: 2px solid var(--border); }
.sources-tab { padding: 8px 16px; font-size: 13px; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; }
.sources-tab:hover { color: var(--primary); }
.sources-tab.active { color: var(--primary); border-bottom-color: var(--accent); font-weight: 600; }
.sources-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.sources-card { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; cursor: pointer; transition: all 0.2s; }
.sources-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-1px); }
.sources-card-emoji { font-size: 24px; margin-bottom: 8px; }
.sources-card-name { font-size: 14px; font-weight: 600; color: var(--primary); margin-bottom: 4px; }
.sources-card-count { font-size: 20px; font-weight: 700; color: var(--text); }
.sources-card-detail { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.sources-confidence { margin-bottom: 20px; }
.sources-confidence-bar { height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.sources-confidence-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
.sources-confidence-fill.high { background: var(--success); }
.sources-confidence-fill.medium { background: var(--warning); }
.sources-confidence-fill.low { background: var(--danger); }
.sources-confidence-label { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
```

### Source Detail Panel (Modal)
```css
.source-panel-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; justify-content: flex-end; }
.source-panel { width: 380px; max-width: 90vw; background: var(--card-bg); height: 100%; overflow-y: auto; padding: 20px; box-shadow: -4px 0 20px rgba(0,0,0,0.15); }
.source-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid var(--accent); }
.source-panel-title { font-size: 16px; font-weight: 600; color: var(--primary); }
.source-panel-close { background: none; border: none; font-size: 20px; cursor: pointer; color: var(--text-muted); }
.source-panel-close:hover { color: var(--text); }
.source-panel-item { padding: 12px; background: var(--bg); border-radius: 8px; margin-bottom: 10px; border: 1px solid var(--border); }
.source-panel-item-fact { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.source-panel-item-detail { font-size: 12px; color: var(--text-muted); }
```

---

## 8. Tab Labels (Portuguese)

- Tab 1: "📜 Por Registro" (Badge view)
- Tab 2: "📊 Dashboard" (Overview)
- Section title: "📜 Fontes dos Dados"

---

## 9. Implementation Order

### Phase 1: CSS + Helper JS (Day 1)
1. Adicionar todas as CSS variables de source ao `:root`
2. Adicionar classes `.source-badge`, `.source-row`, `.sources-*`, `.source-panel-*`
3. Criar helper function `getSourceBadgeHTML(type, label, size)` em JS
4. Criar helper function `getSourceInfo(type)` retornando {emoji, label, bg, text}

### Phase 2: API Endpoints (Day 1-2)
1. Criar `GET /api/sources/summary` endpoint
2. Criar `GET /api/sources/person/:id` endpoint
3. Atualizar `GET /api/family/timeline` para incluir `source_type`, `source_emoji`, `source_label`

### Phase 3: Sources Section UI (Day 2)
1. Adicionar nav item "📜 Fontes" na sidebar
2. Criar `#sources` section com tabs (badge view + dashboard)
3. Implementar badge view: para cada pessoa, listar fatos com badges
4. Implementar dashboard view: grid de cards com contadores
5. Adicionar barra de confiança

### Phase 4: Per-Record Badges (Day 2-3)
1. Modificar render do timeline para adicionar badges de fonte
2. Modificar render do perfil para adicionar badges de fonte nos info-cards
3. Modificar render de empresas para adicionar badge de fonte

### Phase 5: Source Detail Panel (Day 3)
1. Implementar `.source-panel-overlay` com click-outside-to-close
2. ESC key fecha o panel
3. Panel mostra lista de registros daquela fonte

---

## 10. Retrocompatibilidade

- Se um registro não tem campo `fonte` ou `source`, exibir badge com `source-default` (🔗).
- API endpoints existentes não mudam de contract — apenas adicionam campos opcionais.
- Se `/api/sources/summary` falhar, mostrar seção "Fontes" com mensagem "Endpoints não disponíveis ainda".

---

## 11. Accessibility

- Badges usam `cursor: help` para indicar tooltip
- Painel modal usa focus trap
- Cores devem manter contraste WCAG AA mesmo com as cores de source
- Em mobile: cards empilham em 1 coluna
