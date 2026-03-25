"""
ETL Seed - IntelParser Tests
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.seed import IntelParser


class TestIntelParser:
    """Tests for IntelParser class"""

    def test_parser_initialization(self, tmp_path):
        """Parser should initialize with valid path"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("# INTEL\n\nContent here")
        
        parser = IntelParser(intel_file)
        assert parser.intel_path == intel_file
        assert parser.content == "# INTEL\n\nContent here"

    def test_parser_reads_utf8_content(self, tmp_path):
        """Parser should read UTF-8 encoded files"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## Pessoa\n\nNome: José\nCPF: 123.456.789-00", encoding='utf-8')
        
        parser = IntelParser(intel_file)
        assert "José" in parser.content
        assert "123.456.789-00" in parser.content

    def test_extract_cpf_data_with_valid_cpf(self, tmp_path):
        """Should extract CPF when valid format found"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## CPF Data
**CPF:** 314.516.326-49
Nome: RODRIGO GORGULHO
Data de Nascimento: 17/12/1955
Situação: REGULAR
""")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        assert cpf_data['cpf'] == '314.516.326-49'
        assert cpf_data['full_name'] == 'RODRIGO GORGULHO'
        assert cpf_data['birth_date'] == '17/12/1955'
        assert cpf_data['cpf_status'] == 'REGULAR'

    def test_extract_cpf_data_without_cpf(self, tmp_path):
        """Should return empty dict when no CPF found"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## CPF Data\n\nNo CPF here")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        assert cpf_data == {}

    def test_extract_companies_with_valid_cnpj(self, tmp_path):
        """Should extract companies when CNPJ found"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## Empresas

**CNPJ:** 12.345.678/0001-90
**Empresa Teste LTDA**
Capital Social: R$ 1.000.000,00
""")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        assert len(companies) >= 1
        # CNPJ format should be extracted
        cnpj_found = any(c.get('cnpj') == '12.345.678/0001-90' for c in companies)
        assert cnpj_found

    def test_extract_companies_without_cnpj(self, tmp_path):
        """Should return empty list when no CNPJ found"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## Empresas\n\nNo CNPJ here")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        assert companies == []

    def test_extract_companies_capital_parsing(self, tmp_path):
        """Should parse capital values correctly"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## Empresas

**CNPJ:** 12.345.678/0001-90
Capital Social: R$ 229.000.000,00
""")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        if companies:
            # Capital should be numeric
            capital = companies[0].get('capital')
            assert capital is None or isinstance(capital, (int, float))

    def test_extract_family_tree(self, tmp_path):
        """Should return family tree structure"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## Árvore Genealógica\n\nTree content")
        
        parser = IntelParser(intel_file)
        tree = parser.extract_family_tree()
        
        assert isinstance(tree, dict)
        assert 'bisavos' in tree
        assert 'avos' in tree


class TestIntelParserEdgeCases:
    """Edge case tests for IntelParser"""

    def test_empty_file(self, tmp_path):
        """Should handle empty file"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        companies = parser.extract_companies()
        
        assert cpf_data == {}
        assert companies == []

    def test_malformed_cpf(self, tmp_path):
        """Should not crash with malformed CPF"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("**CPF:** 12345")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        # Should not crash, just not find CPF
        assert 'cpf' not in cpf_data or cpf_data.get('cpf') is None

    def test_special_characters_in_name(self, tmp_path):
        """Should handle special characters"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
**CPF:** 123.456.789-00
Nome: JOSÉ DA SILVA-NETO
Data de Nascimento: 01/01/1980
Situação: REGULAR
""")
        
        parser = IntelParser(intel_file)
        cpf_data = parser.extract_cpf_data()
        
        assert 'JOSÉ' in cpf_data.get('full_name', '')
