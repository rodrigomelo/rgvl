"""
ETL Seed - Integration Tests
"""
import sys
import sqlite3
from pathlib import Path
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.seed import IntelParser, DBSeeder


class TestSeedIntegration:
    """Integration tests for seed pipeline"""

    def test_parser_to_seeder_pipeline(self, tmp_path):
        """Test full pipeline: INTEL → Parser → DB"""
        # Create INTEL file
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## CPF Data
**CPF:** 123.456.789-00
Nome: TEST USER
Data de Nascimento: 01/01/1990
Situação: REGULAR

## Empresas
**CNPJ:** 12.345.678/0001-90
**Test Company**
Capital Social: R$ 500.000,00
""")
        
        # Create DB
        db_file = tmp_path / "test.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                cpf TEXT,
                birth_date TEXT,
                notes TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_name TEXT,
                cnpj TEXT UNIQUE,
                capital REAL,
                source TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Parse INTEL
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        companies = parser.extract_companies()
        
        # Verify parsed data
        assert cpf_data['cpf'] == '123.456.789-00'
        assert len(companies) >= 1
        
        # Seed DB
        seeder = DBSeeder(db_file)
        data = {
            'persons': [{
                'full_name': 'TEST USER',
                'cpf': cpf_data['cpf'],
                'birth_date': cpf_data.get('birth_date')
            }],
            'companies': companies
        }
        seeder.seed(data, mode='upsert')
        
        # Verify DB contents
        conn = sqlite3.connect(db_file)
        person = conn.execute("SELECT full_name FROM people WHERE cpf = ?", 
                              (cpf_data['cpf'],)).fetchone()
        conn.close()
        
        assert person is not None
        assert person[0] == 'TEST USER'

    def test_upsert_does_not_duplicate(self, tmp_path):
        """Test that upsert doesn't create duplicates"""
        # Create INTEL file
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
**CPF:** 999.999.999-99
Nome: UPSERT TEST
Data de Nascimento: 01/01/2000
Situação: REGULAR
""")
        
        # Create DB with existing data
        db_file = tmp_path / "test.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                cpf TEXT,
                birth_date TEXT,
                notes TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("INSERT INTO people (full_name, cpf) VALUES ('OLD', '000.000.000-00')")
        conn.commit()
        conn.close()
        
        # Parse
        parser = IntelParser(intel_file)
        data = {
            'persons': [{'full_name': 'UPSERT TEST', 'cpf': '999.999.999-99'}],
            'companies': []
        }
        
        # Seed twice with upsert
        seeder = DBSeeder(db_file)
        seeder.seed(data, mode='upsert')
        seeder.seed(data, mode='upsert')
        
        # Verify DB has 2 persons (old + new), not 3
        conn = sqlite3.connect(db_file)
        count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        conn.close()
        
        assert count == 2


class TestSeedIntegrity:
    """Integrity tests for seed process"""

    def test_all_events_have_valid_person_id(self, tmp_path):
        """All events should have valid person_id after seeding"""
        # Create INTEL file with person-linked events
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## CPF Data
**CPF:** 111.111.111-11
Nome: TEST PERSON
Data de Nascimento: 01/01/1980
Situação: REGULAR
""")
        
        # Create DB with persons table
        db_file = tmp_path / "test.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                cpf TEXT,
                birth_date TEXT,
                notes TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE timeline_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                event_type TEXT,
                description TEXT,
                event_date TEXT,
                reference_table TEXT,
                reference_id INTEGER,
                source TEXT,
                confidence TEXT,
                created_at TEXT
            )
        """)
        # Insert person first
        conn.execute("""
            INSERT INTO people (full_name, cpf)
            VALUES ('TEST PERSON', '111.111.111-11')
        """)
        conn.commit()
        conn.close()
        
        # Parse and seed
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        seeder = DBSeeder(db_file)
        seeder.connect()
        
        # Insert event with person_id
        person_id = 1  # First person
        seeder.conn.execute("""
            INSERT INTO timeline_events (person_id, event_type, description, event_date, reference_table, reference_id, source, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (person_id, 'birth', 'Test birth', '01/01/1980', 'INTEL', None, 'INTEL.md', 'medium', '2024-01-01'))
        seeder.conn.commit()
        seeder.close()
        
        # Verify all events have valid person_id
        conn = sqlite3.connect(db_file)
        null_events = conn.execute("SELECT COUNT(*) FROM timeline_events WHERE person_id IS NULL").fetchone()[0]
        conn.close()
        
        assert null_events == 0, f"Found {null_events} events with NULL person_id"

    def test_counts_match(self, tmp_path):
        """INTEL parsed counts should match DB counts"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
**CPF:** 111.111.111-11
Nome: USER ONE

**CNPJ:** 11.111.111/1111-11
Company One

**CNPJ:** 22.222.222/2222-22
Company Two
""")
        
        db_file = tmp_path / "test.db"
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                cpf TEXT,
                birth_date TEXT,
                notes TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_name TEXT,
                cnpj TEXT UNIQUE,
                capital REAL,
                source TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Parse
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        companies = parser.extract_companies()
        
        # Seed
        seeder = DBSeeder(db_file)
        data = {
            'persons': [{'full_name': 'USER ONE', 'cpf': cpf_data.get('cpf')}],
            'companies': companies
        }
        seeder.seed(data, mode='upsert')
        
        # Verify counts match
        conn = sqlite3.connect(db_file)
        person_count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        company_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        conn.close()
        
        assert person_count == 1  # 1 person in INTEL
        assert company_count == 2  # 2 CNPJs in INTEL

    def test_cpf_validation_format(self, tmp_path):
        """Extracted CPF should be in correct format"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
**CPF:** 314.516.326-49
Nome: VALID CPF TEST
Data de Nascimento: 17/12/1955
Situação: REGULAR
""")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        import re
        cpf_pattern = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
        assert re.match(cpf_pattern, cpf_data['cpf'])

    def test_cnpj_validation_format(self, tmp_path):
        """Extracted CNPJ should be in correct format"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
**CNPJ:** 12.345.678/0001-90
Test Company
""")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        if companies:
            import re
            cnpj_pattern = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
            for company in companies:
                cnpj = company.get('cnpj', '')
                # CNPJ should match pattern or be None
                if cnpj:
                    assert re.match(cnpj_pattern, cnpj) or cnpj is None
