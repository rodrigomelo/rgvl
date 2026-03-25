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
        person = conn.execute("SELECT nome_completo FROM pessoas WHERE cpf = ?", 
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
        conn.execute("INSERT INTO pessoas (nome_completo, cpf) VALUES ('OLD', '000.000.000-00')")
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
        count = conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0]
        conn.close()
        
        assert count == 2


class TestSeedIntegrity:
    """Integrity tests for seed process"""

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
        person_count = conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0]
        company_count = conn.execute("SELECT COUNT(*) FROM empresas_familia").fetchone()[0]
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
