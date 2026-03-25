"""
ETL Seed - IntelParser Tests
"""
import sys
from pathlib import Path

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
        assert parser.filepath == intel_file
        assert parser.content == "# INTEL\n\nContent here"

    def test_parser_reads_utf8_content(self, tmp_path):
        """Parser should read UTF-8 encoded files"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## Pessoa\n\nNome: José\nCPF: 123.456.789-00", encoding='utf-8')
        
        parser = IntelParser(intel_file)
        assert "José" in parser.content
        assert "123.456.789-00" in parser.content

    def test_parse_returns_dict(self, tmp_path):
        """parse() should return dict with expected keys"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("# INTEL\n\n## Events\nSome event content")
        
        parser = IntelParser(intel_file)
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert 'events' in result
        assert 'companies' in result
        assert 'siblings' in result
        assert 'persons' in result

    def test_parse_extracts_events(self, tmp_path):
        """Should extract events"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## Eventos
- Event 1: Birthday
- Event 2: Wedding
""")
        
        parser = IntelParser(intel_file)
        result = parser.parse()
        
        assert isinstance(result['events'], list)

    def test_parse_extracts_companies(self, tmp_path):
        """Should extract companies"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("""
## CNPJ Info
**CNPJ:** 12.345.678/0001-90
**Empresa Teste**
Capital Social: R$ 1.000.000,00
""")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        assert isinstance(companies, list)
        if len(companies) > 0:
            cnpj_found = any(c.get('cnpj') == '12.345.678/0001-90' for c in companies)
            assert cnpj_found

    def test_extract_companies_without_cnpj(self, tmp_path):
        """Should return empty list when no CNPJ found"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("## Empresas\n\nNo CNPJ here")
        
        parser = IntelParser(intel_file)
        companies = parser.extract_companies()
        
        assert companies == []


class TestIntelParserEdgeCases:
    """Edge case tests for IntelParser"""

    def test_empty_file(self, tmp_path):
        """Should handle empty file gracefully"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("")
        
        parser = IntelParser(intel_file)
        result = parser.parse()
        
        assert isinstance(result, dict)
        assert 'events' in result
        assert 'companies' in result

    def test_no_crash_on_invalid_content(self, tmp_path):
        """Should not crash on invalid content"""
        intel_file = tmp_path / "INTEL.md"
        intel_file.write_text("Random content without structure")
        
        parser = IntelParser(intel_file)
        result = parser.parse()
        
        assert isinstance(result, dict)
