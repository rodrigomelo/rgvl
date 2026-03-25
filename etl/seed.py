#!/usr/bin/env python3
"""
ETL: INTEL/*.md → SQLite DB
Modular parser for domain-specific intel files.

Usage:
    python seed.py --dry-run          # Preview changes
    python seed.py --file timeline   # Parse specific file
    python seed.py --all             # Parse all intel/*.md files
"""

import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INTEL_DIR = PROJECT_ROOT / "intel"
DB_PATH = PROJECT_ROOT / "data" / "rgvl.db"


class IntelParser:
    """Parser for INTEL.md format - single file"""
    
    def __init__(self, filepath: Path = None):
        self.filepath = filepath
        self.content = ""
        if filepath:
            self.content = self._read()
    
    def _read(self) -> str:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse(self) -> dict:
        """Parse content and return structured data"""
        return {
            'events': self.extract_events(),
            'companies': self.extract_companies(),
            'siblings': self.extract_siblings(),
            'persons': self.extract_persons(),
        }
    
    def extract_events(self) -> list:
        """Extract life events from markdown tables with section tracking"""
        events = []
        lines = self.content.split('\n')
        
        current_person = 'Rodrigo Gorgulho de Vasconcellos Lanna'  # default
        current_section = ''
        
        for i, line in enumerate(lines):
            # Track current person from section headers
            if line.startswith('## '):
                section_title = line[3:].strip()
                # Check if it's a person section
                if 'Rodrigo Gorgulho' in section_title:
                    current_person = 'Rodrigo Gorgulho de Vasconcellos Lanna'
                elif 'Rodrigo Melo' in section_title:
                    current_person = 'Rodrigo Melo Lanna'
                elif 'Edmundo' in section_title and 'Avô' in section_title:
                    current_person = 'Edmundo de Vasconcellos Lanna'
                elif 'Nice' in section_title:
                    current_person = 'Nice Gorgulho de Vasconcellos Lanna'
                elif 'Henrique' in section_title:
                    current_person = 'Henrique Gorgulho de Vasconcellos Lanna'
                elif 'Marcos' in section_title:
                    current_person = 'Research'  # not a family person
            
            # Find event table
            if '| Evento |' in line or '| Evento|' in line:
                # Process rows until next header or empty row
                for j in range(i+1, min(i+30, len(lines))):
                    row = lines[j].strip()
                    
                    # Stop at next header or section
                    if row.startswith('## ') or row.startswith('##Notas'):
                        break
                    if not row:
                        continue
                    
                    if '|' in row and '---' not in row:
                        parts = [p.strip() for p in row.split('|')]
                        if len(parts) >= 4:
                            event_name = parts[1]
                            date = parts[2]
                            details = parts[3]
                            
                            # Skip header rows or empty
                            if not event_name or event_name == 'Evento' or event_name == 'Details':
                                continue
                            if date == 'Data' or date == 'Date':
                                continue
                            
                            event_type = 'other'
                            if 'Nascimento' in event_name or 'nasc' in event_name.lower():
                                event_type = 'birth'
                            elif 'Falecimento' in event_name or 'óbito' in event_name.lower():
                                event_type = 'death'
                            elif 'Casamento' in event_name or 'casamento' in event_name.lower():
                                event_type = 'marriage'
                            
                            # Skip "Data | Detalhes" placeholder
                            if event_name == 'Data' or details == 'Detalhes':
                                continue
                            
                            # Handle approximate dates
                            is_approximate = date.startswith('~') if date else False
                            clean_date = date.lstrip('~') if date else None
                            
                            if clean_date and len(clean_date) == 4 and clean_date.isdigit():
                                is_approximate = True
                            
                            desc = details
                            if is_approximate:
                                desc = f"[~] {details}"
                            
                            events.append({
                                'event_type': event_type,
                                'event_date': clean_date,
                                'description': f"{event_name}: {desc}",
                                'person_name': current_person,
                                'source': self.filepath.name if self.filepath else 'INTEL.md'
                            })
        return events
    
    def extract_companies(self) -> list:
        """Extract company data"""
        companies = []
        cnpj_pattern = r"\*\*CNPJ:\*\* (\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
        for match in re.finditer(cnpj_pattern, self.content):
            company = {
                'cnpj': match.group(1),
                'source': self.filepath.name if self.filepath else 'INTEL.md',
                'collected_at': datetime.now().isoformat()
            }
            companies.append(company)
        return companies
    
    def extract_siblings(self) -> list:
        """Extract siblings from tree"""
        siblings = []
        pattern1 = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\(nasc[.,]\s*(\d{4})\)\s*—\s*(\d+)\s*filhos?"
        for match in re.finditer(pattern1, self.content):
            name = match.group(1).strip()
            born = match.group(2)
            children_count = int(match.group(3))
            if 'Rodrigo Gorgulho' in name:
                continue
            siblings.append({
                'name': name,
                'birth_year': born,
                'children_count': children_count,
                'source': self.filepath.name if self.filepath else 'INTEL.md'
            })
        return siblings
    
    def extract_persons(self) -> list:
        """Extract person data"""
        persons = []
        # Extract CPF
        match = re.search(r"\*\*CPF:\*\* (\d{3}\.\d{3}\.\d{3}-\d{2})", self.content)
        if match:
            persons.append({
                'full_name': 'Rodrigo Gorgulho de Vasconcellos Lanna',
                'cpf': match.group(1),
                'source': self.filepath.name if self.filepath else 'INTEL.md'
            })
        return persons
    
    # Backward compatibility
    def extract_cpf_data(self) -> dict:
        """Legacy method - use extract_persons() instead"""
        persons = self.extract_persons()
        if persons:
            return persons[0]
        return {}
    
    def extract_insights(self) -> list:
        """Extract insights/facts from INTEL content - parses markdown structure"""
        insights = []
        lines = self.content.split('\n')
        
        current_section = 'other'
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Track current section
            if line.startswith('## '):
                section_lower = line.lower()
                if 'genealogy' in section_lower or 'origem' in section_lower:
                    current_section = 'genealogy'
                elif 'business' in section_lower or 'empresa' in section_lower:
                    current_section = 'business'
                elif 'timeline' in section_lower:
                    current_section = 'timeline'
                elif 'legal' in section_lower:
                    current_section = 'legal'
                elif 'patrimônio' in section_lower or 'wealth' in section_lower:
                    current_section = 'wealth'
            
            # Parse insight entries (### Title)
            if line.startswith('### '):
                title = line[4:].strip()
                description = ''
                source = ''
                tags = ''
                
                # Collect details from following lines
                j = i + 1
                while j < len(lines) and not lines[j].startswith('### ') and not lines[j].startswith('## '):
                    detail_line = lines[j].strip()
                    
                    # Extract Fact
                    if detail_line.startswith('**Fact:**') or detail_line.startswith('- **Fact:**'):
                        desc = detail_line.replace('**Fact:**', '').replace('- **Fact:**', '').strip()
                        if desc:
                            description = desc
                    
                    # Extract Source
                    if '**Source:**' in detail_line or '- **Source:**' in detail_line:
                        src = detail_line.replace('**Source:**', '').replace('- **Source:**', '').strip()
                        if src:
                            source = src
                    
                    # Extract Tags
                    if '**Tags:**' in detail_line or '- **Tags:**' in detail_line:
                        tg = detail_line.replace('**Tags:**', '').replace('- **Tags:**', '').strip()
                        if tg:
                            tags = tg
                    
                    # Extract CNPJ/Location if present
                    if '**CNPJ:**' in detail_line:
                        cnpj = detail_line.replace('**CNPJ:**', '').strip()
                        if description and cnpj:
                            description += f' (CNPJ: {cnpj})'
                    
                    j += 1
                
                # Only add if we have at least a title and description
                if title and description:
                    insights.append({
                        'category': current_section,
                        'title': title,
                        'description': description,
                        'source': source if source else 'INTEL',
                        'tags': tags,
                        'discovered_at': datetime.now().strftime('%Y-%m-%d')
                    })
                    i = j - 1  # Reset i to last processed line
            
            i += 1
        
        return insights


class IntelMaster:
    """Multi-file INTEL parser"""
    
    def __init__(self, intel_dir: Path = None):
        if intel_dir is None:
            intel_dir = INTEL_DIR
        self.intel_dir = intel_dir
        self.data = {
            'events': [],
            'companies': [],
            'siblings': [],
            'persons': [],
            'insights': []
        }
    
    def load_file(self, filename: str) -> dict:
        """Load and parse a single INTEL file"""
        filepath = self.intel_dir / filename
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            return {}
        
        parser = IntelParser(filepath)
        return parser.parse()
    
    def load_all(self) -> dict:
        """Load all INTEL files"""
        if not self.intel_dir.exists():
            print(f"⚠️  INTEL dir not found: {self.intel_dir}")
            return self.data
        
        for md_file in self.intel_dir.glob("*.md"):
            print(f"📖 Parsing: {md_file.name}")
            parser = IntelParser(md_file)
            parsed = parser.parse()
            
            for key in self.data:
                if key in parsed:
                    self.data[key].extend(parsed[key])
        
        return self.data
    
    def summary(self) -> str:
        """Return summary of loaded data"""
        lines = ["📊 INTEL Summary:"]
        for key, items in self.data.items():
            lines.append(f"   {key}: {len(items)} items")
        return "\n".join(lines)


class DBSeeder:
    """Seeds DB from parsed INTEL data"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def upsert_person(self, person: dict) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", 
                     (f"%{person.get('full_name', '')[:20]}%",))
        existing = cursor.fetchone()
        
        if existing:
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
            cursor.execute("""
                INSERT INTO pessoas (nome_completo, cpf, data_nascimento, observacoes, fonte, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (person.get('full_name'), person.get('cpf'), 
                  person.get('birth_date'), person.get('notes'),
                  person.get('source', 'INTEL'),
                  datetime.now().isoformat()))
            return cursor.lastrowid
    
    def upsert_company(self, company: dict) -> int:
        cursor = self.conn.cursor()
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
                VALUES (?, ?, ?, ?, ?)
            """, (company.get('company_name'), company.get('cnpj'),
                  company.get('capital'), company.get('source', 'INTEL'),
                  datetime.now().isoformat()))
            return cursor.lastrowid
    
    def upsert_sibling(self, sibling: dict) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", 
                     (f"%{sibling.get('name', '')[:20]}%",))
        existing = cursor.fetchone()
        
        if existing:
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO pessoas (nome_completo, data_nascimento, geracao, fonte, created_at)
                VALUES (?, ?, 3, ?, ?)
            """, (sibling.get('name'), sibling.get('birth_year'),
                  sibling.get('source', 'INTEL'),
                  datetime.now().isoformat()))
            return cursor.lastrowid
    
    def upsert_event(self, event: dict, person_id: int = None) -> int:
        cursor = self.conn.cursor()
        
        if person_id is None:
            desc = event.get('description', '')
            if 'Rodrigo Melo' in desc or 'RGVL' in desc:
                cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", ('%Rodrigo Gorgulho%',))
            else:
                cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", ('%Rodrigo Gorgulho%',))
            
            result = cursor.fetchone()
            person_id = result['id'] if result else None
        
        # Check for duplicate before inserting
        cursor.execute("""
            SELECT id FROM events 
            WHERE person_id = ? AND event_date = ? AND description = ?
        """, (person_id, event.get('event_date'), event.get('description')))
        
        existing = cursor.fetchone()
        if existing:
            return existing['id']  # Already exists, skip
        
        cursor.execute("""
            INSERT INTO events (person_id, event_type, event_date, description, reference_table, reference_id, source, confidence)
            VALUES (?, ?, ?, ?, 'INTEL', NULL, ?, ?)
        """, (person_id, event.get('event_type'), event.get('event_date'),
              event.get('description'), 
              event.get('source', 'INTEL'),
              event.get('confidence', 'medium')))
        return cursor.lastrowid
    
    def upsert_insight(self, insight: dict) -> int:
        cursor = self.conn.cursor()
        
        # Check if insight already exists
        cursor.execute("SELECT id FROM insights WHERE title = ?", (insight.get('title'),))
        existing = cursor.fetchone()
        
        if existing:
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO insights (category, title, description, source, discovered_at)
                VALUES (?, ?, ?, ?, ?)
            """, (insight.get('category'), insight.get('title'), 
                  insight.get('description'), insight.get('source'),
                  insight.get('discovered_at')))
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
            
            if 'siblings' in data:
                for sibling in data['siblings']:
                    self.upsert_sibling(sibling)
            
            if 'events' in data:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id FROM pessoas WHERE nome_completo LIKE ?", ('%Rodrigo Gorgulho%',))
                result = cursor.fetchone()
                rgvl_id = result['id'] if result else None
                
                for event in data['events']:
                    self.upsert_event(event, person_id=rgvl_id)
            
            if 'insights' in data:
                for insight in data['insights']:
                    self.upsert_insight(insight)
            
            self.conn.commit()
            print(f"\n✅ Seeded:")
            for key, items in data.items():
                if items:
                    print(f"   {key}: {len(items)} items")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error: {e}")
            raise
        finally:
            self.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed DB from INTEL files")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--file', type=str, help='Parse specific file (e.g., timeline.md)')
    parser.add_argument('--all', action='store_true', help='Parse all intel/*.md files')
    args = parser.parse_args()
    
    if args.file:
        # Single file mode
        print(f"📖 Parsing: {args.file}")
        master = IntelMaster()
        data = master.load_file(args.file)
        print(master.summary())
        
        if not args.dry_run and data:
            seeder = DBSeeder()
            seeder.seed(data)
    
    elif args.all:
        # All files mode
        print(f"📁 INTEL dir: {INTEL_DIR}")
        master = IntelMaster()
        data = master.load_all()
        print(master.summary())
        
        if not args.dry_run and data:
            seeder = DBSeeder()
            seeder.seed(data)
    
    else:
        # Legacy single file mode (INTEL.md in docs/)
        INTEL_PATH = PROJECT_ROOT / "docs" / "INTEL.md"
        print(f"📖 Reading legacy: {INTEL_PATH}")
        
        parser = IntelParser(INTEL_PATH)
        data = parser.parse()
        
        print(f"\n📊 Parsed data:")
        for key, items in data.items():
            if items:
                print(f"   {key}: {len(items)}")
        
        if not args.dry_run and data:
            seeder = DBSeeder()
            seeder.seed(data)


if __name__ == "__main__":
    main()
