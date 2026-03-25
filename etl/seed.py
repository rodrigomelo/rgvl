#!/usr/bin/env python3
"""
ETL: INTEL.md → SQLite DB
Reconstructs DB from INTEL.md (golden source)

Usage:
    python seed.py --dry-run  # Preview changes
    python seed.py --full     # Full rebuild (replace DB)
    python seed.py --upsert   # Merge (update only)
"""

import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INTEL_PATH = PROJECT_ROOT / "docs" / "INTEL.md"
DB_PATH = PROJECT_ROOT / "data" / "rgvl.db"

# Section patterns
SECTION_PATTERNS = {
    "persons": r"## .*Pessoa",
    "companies": r"## .*Empresa",
    "cpf_data": r"## .*CPF",
    "family_tree": r"## .*Árvore Genealógica",
}


class IntelParser:
    """Parser for INTEL.md format"""
    
    def __init__(self, intel_path: Path):
        self.intel_path = intel_path
        self.content = self._read()
    
    def _read(self) -> str:
        with open(self.intel_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_cpf_data(self) -> dict:
        """Extract RGVL CPF info"""
        data = {}
        
        # CPF number
        match = re.search(r"\*\*CPF:\*\* (\d{3}\.\d{3}\.\d{3}-\d{2})", self.content)
        if match:
            data['cpf'] = match.group(1)
        
        # Full name
        match = re.search(r"Nome:\s*([A-Z\s]+)", self.content)
        if match:
            data['full_name'] = match.group(1).strip()
        
        # Birth date
        match = re.search(r"Data de Nascimento:\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", self.content)
        if match:
            data['birth_date'] = match.group(1)
        
        # Status
        if "REGULAR" in self.content:
            data['cpf_status'] = "REGULAR"
        
        return data
    
    def extract_companies(self) -> list[dict]:
        """Extract company data"""
        companies = []
        
        # CNPJ pattern
        cnpj_pattern = r"\*\*CNPJ:\*\* (\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
        for match in re.finditer(cnpj_pattern, self.content):
            company = {
                'cnpj': match.group(1),
                'source': 'INTEL.md',
                'collected_at': datetime.now().isoformat()
            }
            
            # Extract context around CNPJ (company name, capital, etc)
            start = max(0, match.start() - 500)
            end = min(len(self.content), match.end() + 500)
            context = self.content[start:end]
            
            # Company name
            name_match = re.search(r"\*\*(.*?)\*\*", context[500:])
            if name_match:
                company['company_name'] = name_match.group(1)
            
            # Capital
            capital_match = re.search(r"Capital Social:\s*R\$\s*([\d\.,]+)", context)
            if capital_match:
                capital = capital_match.group(1).replace('.', '').replace(',', '.')
                company['capital'] = float(capital)
            
            companies.append(company)
        
        return companies
    
    def extract_family_tree(self) -> dict:
        """Extract family tree structure"""
        # Parse the tree structure
        tree = {
            'bisavos': [],
            'avos': [],
            'irmaos': [],
            'primos': []
        }
        
        # This is complex - parse from the ASCII tree
        # For now, return structure for manual mapping
        
        return tree


class DBSeeder:
    """Seeds DB from parsed INTEL data"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def upsert_person(self, person: dict) -> int:
        """Insert or update person"""
        cursor = self.conn.cursor()
        
        # Check if exists by name
        cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", 
                     (f"%{person.get('full_name', '')[:20]}%",))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE pessoas SET
                    cpf = COALESCE(?, cpf),
                    data_nascimento = COALESCE(?, data_nascimento),
                    observacoes = COALESCE(?, observacoes)
                WHERE id = ?
            """, (person.get('cpf'), person.get('birth_date'), 
                  person.get('notes'), existing['id']))
            return existing['id']
        else:
            # Insert
            cursor.execute("""
                INSERT INTO pessoas (nome_completo, cpf, data_nascimento, observacoes, fonte, created_at)
                VALUES (?, ?, ?, ?, 'INTEL.md', ?)
            """, (person.get('full_name'), person.get('cpf'), 
                  person.get('birth_date'), person.get('notes'),
                  datetime.now().isoformat()))
            return cursor.lastrowid
    
    def upsert_company(self, company: dict) -> int:
        """Insert or update company"""
        cursor = self.conn.cursor()
        
        # Check if exists by CNPJ
        cursor.execute("SELECT id FROM empresas_familia WHERE cnpj = ?", 
                     (company.get('cnpj'),))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE empresas_familia SET
                    nome_fantasia = COALESCE(?, nome_fantasia),
                    capital = COALESCE(?, capital)
                WHERE id = ?
            """, (company.get('company_name'), company.get('capital'), 
                  existing['id']))
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO empresas_familia (nome_fantasia, cnpj, capital, fonte, created_at)
                VALUES (?, ?, ?, 'INTEL.md', ?)
            """, (company.get('company_name'), company.get('cnpj'),
                  company.get('capital'), datetime.now().isoformat()))
            return cursor.lastrowid
    
    def seed(self, data: dict, mode: str = 'upsert'):
        """Seed DB from parsed data"""
        self.connect()
        
        try:
            if 'persons' in data:
                for person in data['persons']:
                    self.upsert_person(person)
            
            if 'companies' in data:
                for company in data['companies']:
                    self.upsert_company(company)
            
            self.conn.commit()
            print(f"✅ Seeded {len(data.get('persons', []))} persons")
            print(f"✅ Seeded {len(data.get('companies', []))} companies")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error: {e}")
            raise
        finally:
            self.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed DB from INTEL.md")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--full', action='store_true', help='Full rebuild')
    parser.add_argument('--upsert', action='store_true', help='Merge mode')
    args = parser.parse_args()
    
    print(f"📖 Reading INTEL from: {INTEL_PATH}")
    
    # Parse INTEL
    intel = IntelParser(INTEL_PATH)
    
    # Extract structured data
    data = {
        'persons': [],
        'companies': intel.extract_companies()
    }
    
    # Extract RGVL person
    cpf_data = intel.extract_cpf_data()
    if cpf_data:
        data['persons'].append({
            'full_name': 'Rodrigo Gorgulho de Vasconcellos Lanna',
            'cpf': cpf_data.get('cpf'),
            'birth_date': cpf_data.get('birth_date'),
            'notes': f"CPF Status: {cpf_data.get('cpf_status', 'UNKNOWN')}"
        })
    
    print(f"\n📊 Parsed data:")
    print(f"   Persons: {len(data['persons'])}")
    print(f"   Companies: {len(data['companies'])}")
    
    if args.dry_run:
        print("\n🔍 Dry run - no changes made")
        print(f"   DB: {DB_PATH}")
        return
    
    # Seed DB
    if args.full or args.upsert:
        print(f"\n🌱 Seeding DB: {DB_PATH}")
        seeder = DBSeeder(DB_PATH)
        seeder.seed(data, mode='upsert' if args.upsert else 'full')
    else:
        print("\n⚠️  No action. Use --dry-run, --upsert, or --full")


if __name__ == "__main__":
    main()
