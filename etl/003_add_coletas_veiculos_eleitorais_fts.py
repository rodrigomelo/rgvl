#!/usr/bin/env python3
"""
Migration 003: Add collection tracking, vehicles, electoral data, FTS5
Run: python data/migrations/003_add_coletas_veiculos_eleitorais_fts.py

This migration:
1. Creates `coletas` table for tracking collection history
2. Creates `veiculos` table for Detran-MG data
3. Creates `dados_eleitorais` table for TRE-MG data
4. Adds confidence_score to pessoas
5. Adds source_confidence to legal_processes and empresas_familia
6. Creates FTS5 virtual table for full-text search on pessoas
"""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / 'data' / 'rgvl.db'


def migrate(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    migrations_applied = []
    
    # 1. Create coletas table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coletas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fonte VARCHAR(50) NOT NULL,
            tipo VARCHAR(30) NOT NULL CHECK(tipo IN ('api', 'scraper', 'manual', 'browser')),
            query_original TEXT,
            resultado JSON,
            registros_novos INTEGER DEFAULT 0,
            registros_atualizados INTEGER DEFAULT 0,
            status VARCHAR(20) NOT NULL CHECK(status IN ('success', 'partial', 'failed')),
            error_msg TEXT,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_ms INTEGER
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coletas_fonte ON coletas(fonte)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coletas_status ON coletas(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coletas_executed ON coletas(executed_at DESC)")
    migrations_applied.append("coletas")
    
    # 2. Create veiculos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER,
            placa VARCHAR(10),
            chassi VARCHAR(20),
            marca_modelo VARCHAR(100),
            ano_fabricacao INTEGER,
            ano_modelo INTEGER,
            cor VARCHAR(30),
            combustivel VARCHAR(20),
            categoria VARCHAR(50),
            municipio VARCHAR(100),
            uf VARCHAR(2),
            situacao VARCHAR(30),
            data_aquisicao DATE,
            fonte VARCHAR(100),
            raw_data JSON,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(pessoa_id) REFERENCES pessoas(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_pessoa ON veiculos(pessoa_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_placa ON veiculos(placa)")
    migrations_applied.append("veiculos")
    
    # 3. Create dados_eleitorais table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dados_eleitorais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER,
            nome_eleitoral VARCHAR(255),
            titulo_eleitor VARCHAR(20),
            zona VARCHAR(10),
            secao VARCHAR(10),
            municipio VARCHAR(100),
            uf VARCHAR(2),
            endereco VARCHAR(500),
            situacao VARCHAR(30),
            data_ultima_atualizacao DATE,
            fonte VARCHAR(100),
            raw_data JSON,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(pessoa_id) REFERENCES pessoas(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eleitorais_pessoa ON dados_eleitorais(pessoa_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eleitorais_titulo ON dados_eleitorais(titulo_eleitor)")
    migrations_applied.append("dados_eleitorais")
    
    # 4. Add confidence_score to pessoas
    try:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN confidence_score INTEGER DEFAULT 50")
        cursor.execute("""
            UPDATE pessoas SET confidence_score = (
                CASE 
                    WHEN cpf IS NOT NULL AND data_nascimento IS NOT NULL THEN 80
                    WHEN cpf IS NOT NULL OR data_nascimento IS NOT NULL THEN 60
                    ELSE 40
                END
            )
        """)
        migrations_applied.append("pessoas.confidence_score")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("  confidence_score already exists, skipping")
        else:
            raise
    
    # 5. Add source_confidence to legal_processes
    try:
        cursor.execute("ALTER TABLE legal_processes ADD COLUMN source_confidence VARCHAR(10) DEFAULT 'medium'")
        migrations_applied.append("legal_processes.source_confidence")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("  source_confidence in legal_processes already exists, skipping")
        else:
            raise
    
    # 6. Add source_confidence to empresas_familia
    try:
        cursor.execute("ALTER TABLE empresas_familia ADD COLUMN source_confidence VARCHAR(10) DEFAULT 'medium'")
        migrations_applied.append("empresas_familia.source_confidence")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("  source_confidence in empresas_familia already exists, skipping")
        else:
            raise
    
    # 7. Create FTS5 table
    cursor.execute("DROP TABLE IF EXISTS pessoas_fts")
    cursor.execute("""
        CREATE VIRTUAL TABLE pessoas_fts USING fts5(
            nome_completo,
            nome_anterior,
            profissao,
            cidade_nascimento,
            content='pessoas',
            content_rowid='id'
        )
    """)
    # Populate FTS from existing pessoas
    cursor.execute("""
        INSERT INTO pessoas_fts(rowid, nome_completo, nome_anterior, profissao, cidade_nascimento)
        SELECT id, nome_completo, COALESCE(nome_anterior, ''), COALESCE(profissao, ''), COALESCE(local_nascimento, '')
        FROM pessoas
    """)
    migrations_applied.append("pessoas_fts FTS5")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Migration 003 applied: {', '.join(migrations_applied)}")
    return migrations_applied


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("🔍 Dry run - would apply these changes:")
        print("  - coletas table (collection tracking)")
        print("  - veiculos table (Detran-MG vehicles)")
        print("  - dados_eleitorais table (TRE-MG electoral data)")
        print("  - pessoas.confidence_score column")
        print("  - legal_processes.source_confidence column")
        print("  - empresas_familia.source_confidence column")
        print("  - pessoas_fts FTS5 virtual table")
    else:
        migrate(DB_PATH)
