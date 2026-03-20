"""
RGVL ETL - Migrate Old Schema to Canonical Schema

Migrates data from the legacy dual-schema (old tables + new tables living
side-by-side in data/rgvl.db) into a single clean canonical schema.

Steps:
  1. Create all canonical tables (via SQLAlchemy models)
  2. Migrate data from old orphan tables into canonical tables
  3. Fix known data inconsistencies (Barbosa Mello capital, missing companies)
  4. Drop all old-schema orphan tables
  5. Verify counts and consistency

Usage:
    cd rgvl && python -m etl.migrate_to_canonical
"""
import json
import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db import engine, get_session, DB_PATH
from api.models import (
    Base, Pessoa, Relacionamento, Empresa, Imovel,
    ProcessoJudicial, Documento, Contato, DiarioOficial,
    Perfil, BuscaRealizada, TarefaPesquisa
)


def migrate():
    print('=' * 60)
    print('RGVL Migration — Old Schema → Canonical Schema')
    print('=' * 60)
    print(f'📦 Database: {DB_PATH}')

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # ── PHASE 1: Show before state ────────────────────────────────────────────
    print('\n📊 Before state:')
    for table in ['pessoas', 'empresas_familia', 'relacionamentos',
                  'properties', 'legal_processes', 'documents',
                  'contacts', 'official_gazettes', 'profiles',
                  'persons', 'companies', 'spouses', 'siblings',
                  'nephews', 'children', 'notes']:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'   {table:30s}: {count} rows')
        except Exception:
            print(f'   {table:30s}: (does not exist)')

    # ── PHASE 2: Create canonical tables ──────────────────────────────────────
    print('\n🔨 Creating canonical tables...')
    Base.metadata.create_all(bind=engine)
    print('   ✅ All canonical tables created')

    # ── PHASE 3: Migrate imoveis from properties ──────────────────────────────
    print('\n🏠 Migrating imoveis (from properties)...')
    cursor.execute("SELECT COUNT(*) FROM properties")
    prop_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO imoveis (
            property_type, address, city, state, neighborhood,
            registration, cartorio, cnm, building_name, floor,
            area_sqm, area_common, area_total,
            bedrooms, parking_spaces, parking_boxes,
            owners, purchase_date, purchase_value, financing_value,
            itbi, fiscal_value, current_value,
            status, description, annotations, raw_data, collected_at
        ) SELECT
            property_type, address, city, state, neighborhood,
            registration, cartorio, cnm, building_name, floor,
            area_sqm, area_common, area_total,
            bedrooms, parking_spaces, parking_boxes,
            owners, purchase_date, purchase_value, financing_value,
            itbi, fiscal_value, current_value,
            status, description, annotations, raw_data, collected_at
        FROM properties
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM imoveis')
    print(f'   ✅ Migrated {prop_count} properties → imoveis')

    # ── PHASE 4: Migrate legal_processes → processos_judiciais ─────────────────
    print('\n⚖️  Migrating processos_judiciais (from legal_processes)...')
    cursor.execute("SELECT COUNT(*) FROM legal_processes")
    proc_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO processos_judiciais (
            process_number, court, subject, parties,
            status, value, filings, fonte, raw_data,
            collected_at, updated_at
        ) SELECT
            process_number, court, subject, parties,
            status, value, filings, 'TJMG/TRT3 (INTEL.md)' AS fonte,
            raw_data, collected_at, updated_at
        FROM legal_processes
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM processos_judiciais')
    print(f'   ✅ Migrated {proc_count} legal_processes → processos_judiciais')

    # ── PHASE 5: Migrate documents → documentos ───────────────────────────────
    print('\n📄 Migrating documentos (from documents)...')
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO documentos (
            doc_type, title, description, file_path,
            issue_date, expiry_date, fonte, raw_data, collected_at
        ) SELECT
            doc_type, title, description, file_path,
            issue_date, expiry_date, source, raw_data, collected_at
        FROM documents
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM documentos')
    print(f'   ✅ Migrated {doc_count} documents → documentos')

    # ── PHASE 6: Migrate contacts → contatos ──────────────────────────────────
    print('\n📒 Migrating contatos (from contacts)...')
    cursor.execute("SELECT COUNT(*) FROM contacts")
    cont_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO contatos (
            nome, role, empresa, telefone, email,
            is_primary, notes, fonte, raw_data, collected_at
        ) SELECT
            name, role, company, phone, email,
            is_primary, notes, source, raw_data, collected_at
        FROM contacts
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM contatos')
    print(f'   ✅ Migrated {cont_count} contacts → contatos')

    # ── PHASE 7: Migrate official_gazettes → diarios_oficiais ────────────────
    print('\n📰 Migrating diarios_oficiais (from official_gazettes)...')
    cursor.execute("SELECT COUNT(*) FROM official_gazettes")
    gaz_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO diarios_oficiais (
            source, publication_date, edition, section, page,
            title, content, url, tags, fonte, raw_data, collected_at
        ) SELECT
            source, publication_date, edition, section, page,
            title, content, url, tags, source, raw_data, collected_at
        FROM official_gazettes
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM diarios_oficiais')
    print(f'   ✅ Migrated {gaz_count} official_gazettes → diarios_oficiais')

    # ── PHASE 8: Migrate profiles → perfis ───────────────────────────────────
    print('\n👤 Migrating perfis (from profiles)...')
    cursor.execute("SELECT COUNT(*) FROM profiles")
    prof_count = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO perfis (
            source, external_id, name, bio, location,
            empresa, email, avatar_url, profile_url,
            raw_data, collected_at, updated_at
        ) SELECT
            source, external_id, name, bio, location,
            company, email, avatar_url, profile_url,
            raw_data, collected_at, updated_at
        FROM profiles
    """)
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM perfis')
    print(f'   ✅ Migrated {prof_count} profiles → perfis')

    # ── PHASE 9: Fix Barbosa Mello capital (281 → 282) ─────────────────────────
    print('\n🔧 Fixing data inconsistencies...')
    cursor.execute("""
        UPDATE empresas_familia
        SET capital = 154768282.0, observacoes = REPLACE(observacoes, 'R$ 154.768.281', 'R$ 154.768.282')
        WHERE nome_fantasia = 'Construtora Barbosa Mello'
    """)
    conn.commit()
    cursor.execute("SELECT capital FROM empresas_familia WHERE nome_fantasia = 'Construtora Barbosa Mello'")
    capital = cursor.fetchone()[0]
    print(f'   ✅ Barbosa Mello capital fixed → {capital:,.0f}')

    # ── PHASE 10: Add missing companies ────────────────────────────────────────
    print('\n🏢 Adding missing companies...')
    missing_companies = [
        ('EBTE Engenharia e Montagens LTDA', '00.000.000/0001-03', 'EBTE', 'Engenharia e Montagens', 'ativa', None, None),
        ('Consórcio Uchoa', '00.000.000/0001-01', 'Consórcio Uchoa', 'Consórcio', 'baixa', None, None),
        ('Consórcio TKL', '00.000.000/0001-02', 'Consórcio TKL', 'Consórcio', 'baixa', None, None),
    ]
    for razao, cnpj, nome_fant, nature, status, capital_val, pessoa_id in missing_companies:
        try:
            cursor.execute("""
                INSERT INTO empresas_familia
                    (cnpj, nome_fantasia, razao_social, natureza_juridica, status_jucemg, capital, fonte, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, 'INTEL.md (migrated)', 'Migrado do schema antigo — confirmar dados')
            """, (cnpj, nome_fant, razao, nature, status, capital_val))
            print(f'   ✅ Added: {nome_fant}')
        except Exception as e:
            print(f'   ⚠️  {nome_fant}: {e}')
    conn.commit()

    # ── PHASE 11: Drop old orphan tables ─────────────────────────────────────
    print('\n🗑️  Dropping old orphan tables...')
    old_tables = [
        # Legacy canonical (replaced by seed.py fresh data):
        'persons', 'companies', 'spouses', 'siblings', 'nephews', 'children',
        'contacts', 'documents', 'profiles', 'legal_processes',
        'official_gazettes', 'notes',
        # Old properties (replaced by imoveis):
        'properties',
    ]
    for table in old_tables:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
            print(f'   ✅ Dropped: {table}')
        except Exception as e:
            print(f'   ⚠️  {table}: {e}')
    conn.commit()

    # ── PHASE 12: Verify ───────────────────────────────────────────────────────
    print('\n📊 After state (canonical schema):')
    canonical_tables = [
        'pessoas', 'relacionamentos', 'empresas_familia', 'imoveis',
        'processos_judiciais', 'documentos', 'contatos',
        'diarios_oficiais', 'perfis', 'buscas_realizadas', 'tarefas_pesquisa'
    ]
    for table in canonical_tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'   {table:30s}: {count} rows')
        except Exception as e:
            print(f'   {table:30s}: ERROR — {e}')

    # Verify Barbosa Mello
    cursor.execute("SELECT nome_fantasia, cnpj, capital, status_jucemg FROM empresas_familia ORDER BY nome_fantasia")
    print('\n🏢 Empresas (canonical):')
    for row in cursor.fetchall():
        print(f'   {row[0]:40s} {row[1]:20s} cap={str(row[2] or "-"):>15s}  {row[3]}')

    conn.close()
    print('\n✅ Migration complete!')


if __name__ == '__main__':
    migrate()
