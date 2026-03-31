"""
English Migration Plan — RGVL Database Refactor
=================================================

Phase 1: Create English tables + migration script
Phase 2: Update SQLAlchemy models  
Phase 3: Update API routes
Phase 4: Update web frontend
Phase 5: Update collectors
Phase 6: Drop old tables

Table mapping (Portuguese → English):
--------------------------------------
pessoas              → people
empresas_familia     → companies
imoveis              → properties
contatos             → contacts
documentos           → documents
legal_processes      → legal_cases
events               → timeline_events (already English, rename for clarity)
relacionamentos      → relationships
profiles             → social_profiles
perfis_sociais       → social_profiles (merge with profiles)
insights             → research_insights
notes                → research_notes
coletas              → collection_runs
buscas_realizadas    → search_history
dados_eleitorais     → electoral_records
diarios_oficiais     → official_gazettes
veiculos             → vehicles
tarefas_pesquisa     → research_tasks
tre_dados            → tre_records

Column mapping (key Portuguese → English):
-------------------------------------------
nome_completo        → full_name
nome_anterior        → previous_name
data_nascimento      → birth_date
local_nascimento     → birth_place
data_falecimento     → death_date
cpf                  → cpf (keep - Brazilian standard)
cnpj                 → cnpj (keep - Brazilian standard)
rg                   → rg (keep - Brazilian standard)
telefone             → phone
endereco             → address
profissao            → profession
cargo                → position
empresa              → company
pai_id               → father_id
mae_id               → mother_id
conjuge_id           → spouse_id
data_casamento       → marriage_date
geracao              → generation
fonte                → source
observacoes          → notes
nome_fantasia        → trade_name
razao_social         → legal_name
natureza_juridica    → legal_nature
cidade               → city
socios               → partners
status_jucemg        → registration_status
data_abertura        → opening_date
data_baixa           → closing_date
pessoa_id            → person_id
collected_at         → collected_at (keep)
raw_data             → raw_data (keep)
created_at           → created_at (keep)
updated_at           → updated_at (keep)
"""
