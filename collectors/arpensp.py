"""
Arpensp Collector - Searches Arpensp (Associação dos Registradores de SP) for civil records
Uses web scraping to find birth, marriage, and death certificates.
"""

import re
import json
import httpx
from bs4 import BeautifulSoup

from data.collectors.base import BaseCollector


class ArpenspCollector(BaseCollector):
    """Search Arpensp for civil records of family members."""
    NAME = "arpensp"
    DESCRIPTION = "Search Arpensp for civil records (birth, marriage, death)"

    BASE_URL = "https://arpensp.org.br"

    # Target names to search
    TARGETS = [
        {"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "person_id": 6, "type": "nascimento"},
        {"name": "Nice Gorgulho de Vasconcellos Lanna", "person_id": 3, "type": "nascimento"},
        {"name": "Edmundo de Vasconcellos Lanna", "person_id": 2, "type": "nascimento"},
        {"name": "Henrique Gorgulho de Vasconcellos Lanna", "person_id": 8, "type": "nascimento"},
        {"name": "Marcelo Gorgulho de Vasconcellos Lanna", "person_id": 9, "type": "nascimento"},
        {"name": "Júnia Gorgulho de Vasconcellos Lanna", "person_id": 10, "type": "nascimento"},
        {"name": "Edmundo Mariano da Costa Lanna", "person_id": 1, "type": "obito"},
        {"name": "Nice Gorgulho de Vasconcellos Lanna", "person_id": 3, "type": "obito"},
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    def collect(self):
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=20)

        try:
            for target in self.TARGETS:
                name = target["name"]
                record_type = target["type"]
                self.log(f"Searching {record_type}: {name}")

                # Arpensp uses a search form - try the public search
                try:
                    search_url = f"{self.BASE_URL}/certidao/{record_type}"
                    resp = client.get(search_url)
                    if resp.status_code == 200:
                        # Parse the search page
                        soup = BeautifulSoup(resp.text, "html.parser")
                        forms = soup.find_all("form")
                        self.log(f"  Found {len(forms)} forms on {record_type} page")

                        # Save insight about available search
                        self.save_insight(
                            category="civil_registry",
                            title=f"Arpensp {record_type}: {name}",
                            content=f"Search page available at {search_url}. Name: {name}",
                            source="arpensp",
                            person_id=target.get("person_id"),
                            confidence=30,
                        )
                    else:
                        self.log(f"  HTTP {resp.status_code}", "warn")
                except httpx.HTTPError as e:
                    self.log(f"  Error: {e}", "warn")

        finally:
            client.close()

        self.log("Note: Arpensp requires manual search with date/cartório info", "warn")
        self.log("Use https://arpensp.org.br for interactive searches", "info")
