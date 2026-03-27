#!/usr/bin/env python3
"""
RGVL Database Export to JSON
Exports all tables to JSON format for archival and migration.
Can be run manually or via cron.

Usage:
    python export_json.py                    # Creates export in data/exports/
    python export_json.py --pretty           # Pretty-print JSON
    python export_json.py --all              # Include empty tables
"""

import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / 'data' / 'rgvl.db'
EXPORT_DIR = PROJECT_ROOT / 'data' / 'exports'

# Tables to export (order matters for foreign key dependencies)
TABLES = [
    'pessoas',
    'empresas_familia',
    'relacionamentos',
    'events',
    'legal_processes',
    'imoveis',
    'documentos',
    'contatos',
    'profiles',
    'insights',
    'tarefas_pesquisa',
    'buscas_realizadas',
    'diarios_oficiais',
]


def connect_db():
    """Connect to database with FK enforcement."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def export_table(conn, table_name: str) -> dict:
    """Export a single table to dict format."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    return {
        'table': table_name,
        'count': len(rows),
        'columns': [desc[0] for desc in cursor.description] if cursor.description else [],
        'rows': [dict(row) for row in rows]
    }


def export_all_tables(include_empty: bool = True) -> dict:
    """Export all tables to a single dict."""
    conn = connect_db()
    
    export = {
        'metadata': {
            'exported_at': datetime.now().isoformat(),
            'database': str(DB_FILE),
            'version': '1.0'
        },
        'tables': {}
    }
    
    for table in TABLES:
        try:
            table_data = export_table(conn, table)
            if include_empty or table_data['count'] > 0:
                export['tables'][table] = table_data
        except sqlite3.OperationalError as e:
            export['tables'][table] = {'error': str(e)}
    
    conn.close()
    return export


def save_export(export_data: dict, pretty: bool = False):
    """Save export to JSON file."""
    EXPORT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"rgvl_export_{timestamp}.json"
    filepath = EXPORT_DIR / filename
    
    kwargs = {'indent': 2, 'ensure_ascii': False} if pretty else {}
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, **kwargs)
    
    size_kb = filepath.stat().st_size / 1024
    total_rows = sum(t.get('count', 0) for t in export_data['tables'].values())
    
    print(f"✅ Export created: {filepath}")
    print(f"   Size: {size_kb:.1f} KB")
    print(f"   Tables: {len(export_data['tables'])}")
    print(f"   Total rows: {total_rows}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description='RGVL Database Export to JSON')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    parser.add_argument('--all', action='store_true', help='Include empty tables')
    
    args = parser.parse_args()
    
    print("📤 Starting RGVL database export...")
    
    export_data = export_all_tables(include_empty=args.all)
    save_export(export_data, pretty=args.pretty)


if __name__ == '__main__':
    main()
