"""
FamilySearch Collector - Searches FamilySearch.org for genealogical records
Uses the FamilySearch public search to find birth, marriage, death, and census records.
"""

import json
import re
import httpx
from bs4 import BeautifulSoup

from data.collectors.base import BaseCollector


class FamilySearchCollector(BaseCollector):
    """Search FamilySearch for genealogical records."""
    NAME = "familysearch"
    DESCRIPTION = "Search FamilySearch.org for genealogical records"

    BASE_URL = "https://www.familysearch.org"

    # Target names with known details
    TARGETS = [
        {
            "name": "Edmundo Mariano da Costa Lanna",
            "person_id": 1,
            "birth_year": "~1920",
            "death_year": "~2000",
            "location": "Belo Horizonte, MG",
            "search_terms": ["Edmundo Mariano Lanna", "Edmundo M Lanna", "Edmundo Costa Lanna"],
        },
        {
            "name": "Nice Gorgulho de Vasconcellos Lanna",
            "person_id": 3,
            "birth_year": "~1925",
            "location": "Belo Horizonte, MG",
            "search_terms": ["Nice Gorgulho Lanna", "Nice Vasconcellos Lanna", "Nice Gorgulho"],
        },
        {
            "name": "Edmundo de Vasconcellos Lanna",
            "person_id": 2,
            "birth_year": "~1950",
            "location": "Belo Horizonte, MG",
            "search_terms": ["Edmundo Vasconcellos Lanna", "Edmundo V Lanna"],
        },
        {
            "name": "Joana Ivanete Silva Melo",
            "person_id": 27,
            "birth_year": "~1960",
            "location": "Itaituba, PA",
            "search_terms": ["Joana Ivanete Melo", "Joana Silva Melo"],
        },
        {
            "name": "Jaime de Araujo Melo",
            "person_id": 28,
            "birth_year": "~1955",
            "location": "Itaituba, PA",
            "search_terms": ["Jaime Araujo Melo"],
        },
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml",
    }

    def _search_person(self, client, name, birth_year=None, death_year=None, location=None):
        """Search FamilySearch for a person."""
        # Build search URL
        params = {
            "q": f'givenName="{name.split()[0]}" surname="{name.split()[-1]}"',
            "f.collectionCountry": "Brasil",
        }
        if birth_year:
            params["f.birthLikeDate.from"] = str(int(birth_year.replace("~", "")) - 5)
            params["f.birthLikeDate.to"] = str(int(birth_year.replace("~", "")) + 5)
        if location:
            params["f.birthLikePlace"] = location

        search_url = f"{self.BASE_URL}/search/record/results"

        try:
            resp = client.get(search_url, params=params)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")

                # Extract result count
                count_el = soup.find("span", class_="results-count")
                count = count_el.text.strip() if count_el else "0"

                # Extract individual results
                results = []
                for item in soup.select(".search-result-item, .result-item"):
                    title = item.find("a", class_="result-title")
                    details = item.find("div", class_="result-details")

                    if title:
                        results.append({
                            "title": title.text.strip(),
                            "url": title.get("href", ""),
                            "details": details.text.strip()[:300] if details else "",
                        })

                return {"count": count, "results": results[:10]}
        except httpx.HTTPError as e:
            self.log(f"Search error: {e}", "warn")

        return {"count": "0", "results": []}

    def collect(self):
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=30)

        try:
            for target in self.TARGETS:
                self.log(f"Searching: {target['name']}")

                for term in target.get("search_terms", [target["name"]]):
                    result = self._search_person(
                        client,
                        term,
                        birth_year=target.get("birth_year"),
                        location=target.get("location"),
                    )

                    count = result.get("count", "0")
                    self.log(f"  '{term}': {count} results")

                    if result.get("results"):
                        for r in result["results"]:
                            self.save_insight(
                                category="genealogy",
                                title=f"FamilySearch: {r['title'][:80]}",
                                content=f"Person: {target['name']}\nSearch: {term}\n"
                                        f"URL: {self.BASE_URL}{r['url']}\n"
                                        f"Details: {r['details'][:200]}",
                                source="familysearch",
                                person_id=target.get("person_id"),
                                confidence=50,
                            )

        finally:
            client.close()

        self.log(f"Processed {len(self.TARGETS)} targets")
