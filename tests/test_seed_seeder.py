"""
ETL Seed - DBSeeder Tests
"""
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.seed import DBSeeder


class TestDBSeeder:
    """Tests for DBSeeder class"""

    def test_seeder_initialization(self, tmp_path):
        """Seeder should initialize with db path"""
        db_file = tmp_path / "test.db"
        seeder = DBSeeder(db_file)
        
        assert seeder.db_path == db_file
        assert seeder.conn is None

    def test_connect_and_close(self, tmp_path):
        """Should connect and close properly"""
        db_file = tmp_path / "test.db"
        seeder = DBSeeder(db_file)
        
        seeder.connect()
        assert seeder.conn is not None
        
        seeder.close()
        # After close, conn should be None or closed

    def test_upsert_person_insert(self, tmp_path):
        """Should insert new person"""
        db_file = tmp_path / "test.db"
        
        # Create minimal schema
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT,
                cpf TEXT,
                data_nascimento TEXT,
                observacoes TEXT,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        person = {
            'full_name': 'Test Person',
            'cpf': '123.456.789-00',
            'birth_date': '01/01/2000'
        }
        
        person_id = seeder.upsert_person(person)
        assert person_id is not None
        
        seeder.close()

    def test_upsert_person_update(self, tmp_path):
        """Should update existing person"""
        db_file = tmp_path / "test.db"
        
        # Create schema with existing person
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT,
                cpf TEXT,
                data_nascimento TEXT,
                observacoes TEXT,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            INSERT INTO pessoas (nome_completo, cpf) 
            VALUES ('Test Person', '000.000.000-00')
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        person = {
            'full_name': 'Test Person',
            'cpf': '123.456.789-00'
        }
        
        person_id = seeder.upsert_person(person)
        assert person_id is not None
        
        # Verify update
        seeder.conn.execute("SELECT cpf FROM pessoas WHERE id = ?", (person_id,))
        result = seeder.conn.fetchone()
        assert result['cpf'] == '123.456.789-00'
        
        seeder.close()

    def test_upsert_company_insert(self, tmp_path):
        """Should insert new company"""
        db_file = tmp_path / "test.db"
        
        # Create minimal schema
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS empresas_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                capital REAL,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        company = {
            'company_name': 'Test Company',
            'cnpj': '12.345.678/0001-90',
            'capital': 1000000.0
        }
        
        company_id = seeder.upsert_company(company)
        assert company_id is not None
        
        seeder.close()

    def test_upsert_company_update(self, tmp_path):
        """Should update existing company by CNPJ"""
        db_file = tmp_path / "test.db"
        
        # Create schema with existing company
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS empresas_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                capital REAL,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            INSERT INTO empresas_familia (nome_fantasia, cnpj, capital) 
            VALUES ('Old Name', '12.345.678/0001-90', 100.0)
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        company = {
            'company_name': 'New Name',
            'cnpj': '12.345.678/0001-90',
            'capital': 2000000.0
        }
        
        company_id = seeder.upsert_company(company)
        assert company_id is not None
        
        seeder.close()

    def test_seed_commits_data(self, tmp_path):
        """Should commit data to database"""
        db_file = tmp_path / "test.db"
        
        # Create schema
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT,
                cpf TEXT,
                data_nascimento TEXT,
                observacoes TEXT,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS empresas_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                capital REAL,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        
        data = {
            'persons': [
                {'full_name': 'Person 1', 'cpf': '111.111.111-11'},
                {'full_name': 'Person 2', 'cpf': '222.222.222-22'}
            ],
            'companies': [
                {'company_name': 'Company 1', 'cnpj': '11.111.111/1111-11', 'capital': 100.0}
            ]
        }
        
        seeder.seed(data, mode='upsert')
        
        # Verify data was committed
        conn = sqlite3.connect(db_file)
        person_count = conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0]
        company_count = conn.execute("SELECT COUNT(*) FROM empresas_familia").fetchone()[0]
        conn.close()
        
        assert person_count == 2
        assert company_count == 1


class TestDBSeederEdgeCases:
    """Edge case tests for DBSeeder"""

    def test_upsert_with_missing_fields(self, tmp_path):
        """Should handle missing fields gracefully"""
        db_file = tmp_path / "test.db"
        
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT,
                cpf TEXT,
                data_nascimento TEXT,
                observacoes TEXT,
                fonte TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        # Person with only name
        person = {'full_name': 'Test Person'}
        person_id = seeder.upsert_person(person)
        
        assert person_id is not None
        seeder.close()

    def test_seed_with_empty_data(self, tmp_path):
        """Should handle empty data gracefully"""
        db_file = tmp_path / "test.db"
        
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        seeder = DBSeeder(db_file)
        
        # Should not crash
        seeder.seed({'persons': [], 'companies': []}, mode='upsert')
        
        # Verify no data was added
        conn = sqlite3.connect(db_file)
        count = conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0]
        conn.close()
        
        assert count == 0
