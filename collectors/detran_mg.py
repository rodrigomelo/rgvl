"""
Detran-MG Collector - Searches for vehicle registrations and driver licenses
Uses the DETRAN-MG public consultation portal.
"""

import json
import httpx
from bs4 import BeautifulSoup

from data.collectors.base import BaseCollector


class DetranMGCollector(BaseCollector):
    """Search Detran-MG for vehicle and license info."""
    NAME = "detran_mg"
    DESCRIPTION = "Search Detran-MG for vehicle registrations"

    BASE_URL = "https://portalservicos.detran.mg.gov.br"

    TARGETS = [
        {"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "cpf": "314.516.326-49", "person_id": 6},
        {"name": "Henrique Gorgulho de Vasconcellos Lanna", "person_id": 8},
        {"name": "Marcelo Gorgulho de Vasconcellos Lanna", "person_id": 9},
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    def collect(self):
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=20)

        try:
            # Check if portal is accessible
            self.log("Checking Detran-MG portal...")
            resp = client.get(self.BASE_URL)
            if resp.status_code == 200:
                self.log("Portal accessible", "success")

                # Save tarefa for manual lookup
                for target in self.TARGETS:
                    cpf = target.get("cpf", "")
                    if cpf:
                        self.save_insight(
                            category="vehicle",
                            title=f"Detran-MG: {target['name']}",
                            content=f"CPF: {cpf}. Check vehicle registrations and infractions at {self.BASE_URL}",
                            source="detran_mg",
                            person_id=target.get("person_id"),
                            confidence=40,
                        )
                    else:
                        self.log(f"  No CPF for {target['name']}, skipping vehicle search", "warn")
            else:
                self.log(f"Portal returned HTTP {resp.status_code}", "warn")

        except httpx.HTTPError as e:
            self.log(f"Connection error: {e}", "error")
        finally:
            client.close()

        self.log("Note: Detran-MG requires CPF + birth date for full search", "warn")
