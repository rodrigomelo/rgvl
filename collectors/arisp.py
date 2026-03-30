"""
Arisp / Newspaper Collector - Searches for public records in newspapers and registries
Looks for obituaries, marriage notices, property transfers, and public announcements.
"""

import json
import re
import time
import httpx
from bs4 import BeautifulSoup

from data.collectors.base import BaseCollector


class ArispCollector(BaseCollector):
    """Search Arisp and newspapers for public records."""
    NAME = "arisp"
    DESCRIPTION = "Search Arisp and newspapers for public records"

    SEARCH_TERMS = [
        {"term": "Lanna", "location": "Belo Horizonte"},
        {"term": "Gorgulho", "location": "Belo Horizonte"},
        {"term": "Vasconcellos Lanna", "location": "Minas Gerais"},
        {"term": "Edmundo Mariano Lanna", "location": "obituary"},
        {"term": "Nice Gorgulho", "location": "obituary"},
    ]

    # Brazilian newspaper sites with search
    NEWSPAPERS = {
        "estado_de_minas": "https://www.em.com.br/busca?q={query}",
        "hoje_em_dia": "https://www.hojeemdia.com.br/buscar?q={query}",
        "uai": "https://www.uai.com.br/busca?q={query}",
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    def _search_newspaper(self, client, name, url_template):
        """Search a newspaper site."""
        url = url_template.format(query=name.replace(" ", "+"))
        try:
            resp = client.get(url, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                articles = soup.find_all(["article", "div"], class_=re.compile(r"result|article|news|item", re.I))
                results = []
                for art in articles[:10]:
                    title_el = art.find(["h2", "h3", "a"])
                    link_el = art.find("a", href=True)
                    if title_el:
                        results.append({
                            "title": title_el.get_text(strip=True)[:200],
                            "url": link_el["href"] if link_el else url,
                            "source": url.split("/")[2],
                        })
                return results
        except httpx.HTTPError:
            pass
        return []

    def collect(self):
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=20)

        try:
            for term_data in self.SEARCH_TERMS:
                term = term_data["term"]
                self.log(f"Searching newspapers for: {term}")

                for paper_name, url_template in self.NEWSPAPERS.items():
                    results = self._search_newspaper(client, term, url_template)
                    self.log(f"  {paper_name}: {len(results)} results")

                    for r in results:
                        self.save_insight(
                            category="newspaper",
                            title=f"[{paper_name}] {r['title'][:80]}",
                            content=f"Term: {term}\nNewspaper: {paper_name}\nURL: {r['url']}\nSource: {r['source']}",
                            source="arisp",
                            confidence=40,
                        )

                    time.sleep(2)

            # Also search Arisp (property registry info)
            self.log("Checking Arisp (property registry)...")
            try:
                resp = client.get("https://www.arisp.com.br/", timeout=10)
                if resp.status_code == 200:
                    self.log("Arisp accessible — manual search required for property records", "warn")
                    self.save_insight(
                        category="property_registry",
                        title="Arisp property registry — manual search required",
                        content="Arisp requires login/subscription for property searches. "
                                "Check property transfers, liens, and registrations for Lanna family names.",
                        source="arisp",
                        confidence=20,
                    )
            except httpx.HTTPError:
                self.log("Arisp unreachable", "warn")

        finally:
            client.close()
