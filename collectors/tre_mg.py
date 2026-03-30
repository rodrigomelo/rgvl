"""
TRE-MG Collector - Searches electoral court records
Uses the TRE-MG public portal for voter registration and electoral info.
"""

import json
import httpx
from bs4 import BeautifulSoup

from data.collectors.base import BaseCollector


class TREMGCollector(BaseCollector):
    """Search TRE-MG for electoral records."""
    NAME = "tre_mg"
    DESCRIPTION = "Search TRE-MG for electoral records"

    BASE_URL = "https://www.tre-mg.jus.br"

    TARGETS = [
        {"name": "Rodrigo Gorgulho de Vasconcelloss Lanna", "person_id": 6},
        {"name": "Henrique Gorgulho de Vasconcellos Lanna", "person_id": 8},
        {"name": "Marcelo Gorgulho de Vasconcelloss Lanna", "person_id": 9},
        {"name": "Edmundo de Vasconcellos Lanna", "person_id": 2},
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    def collect(self):
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=20)

        try:
            # TRE-MG has a situacao-eleitoral service
            self.log("Checking TRE-MG portal...")
            resp = client.get(f"{self.BASE_URL}/eleitor/situacao-eleitoral")
            if resp.status_code == 200:
                self.log("Portal accessible", "success")

                for target in self.TARGETS:
                    self.save_insight(
                        category="electoral",
                        title=f"TRE-MG: {target['name']}",
                        content=f"Check electoral status at {self.BASE_URL}/eleitor/situacao-eleitoral. "
                                f"Requires name + birth date + mother's name.",
                        source="tre_mg",
                        person_id=target.get("person_id"),
                        confidence=30,
                    )
            else:
                self.log(f"Portal returned HTTP {resp.status_code}", "warn")

        except httpx.HTTPError as e:
            self.log(f"Connection error: {e}", "error")
        finally:
            client.close()

        self.log("Note: TRE-MG requires name + birth date + mother's name for search", "warn")
