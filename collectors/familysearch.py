"""
FamilySearch Collector - Searches FamilySearch.org for genealogical records

Uses Playwright for browser automation since FamilySearch blocks httpx/curl.
Target records: births in BH 1950-1960, marriage of Edmundo de Vasconcellos Lanna + Nice Gorgulho.

Known issues:
- FamilySearch blocks direct HTTP access (403 Cloudflare)
- Playwright headless is partially blocked
- Manual search recommended: https://www.familysearch.org/en/
"""

import json
import time

from collectors.base import BaseCollector


class FamilySearchCollector(BaseCollector):
    """Search FamilySearch for genealogical records via Playwright."""

    NAME = "familysearch"
    DESCRIPTION = "Search FamilySearch.org for genealogical records"

    BASE_URL = "https://www.familysearch.org"

    TARGETS = [
        {
            "name": "Edmundo de Vasconcellos Lanna",
            "person_id": 2,
            "birth_year": "~1950",
            "location": "Belo Horizonte, MG",
            "search_terms": [
                "Edmundo Vasconcellos Lanna",
                "Edmundo de Vasconcellos Lanna",
                "Edmundo V Lanna",
            ],
            "type": "birth",
        },
        {
            "name": "Nice Gorgulho de Vasconcellos Lanna",
            "person_id": 3,
            "birth_year": "~1925",
            "location": "Belo Horizonte, MG",
            "search_terms": [
                "Nice Gorgulho Lanna",
                "Nice Gorgulho de Vasconcellos Lanna",
                "Nice de Vasconcellos Lanna",
            ],
            "type": "birth",
        },
        {
            "name": "Edmundo de Vasconcellos Lanna + Nice Gorgulho",
            "person_id": 2,
            "location": "Belo Horizonte, MG",
            "search_terms": [
                "Edmundo Vasconcellos Lanna Nice Gorgulho",
                "Edmundo de Vasconcellos Nice Gorgulho",
            ],
            "type": "marriage",
        },
        {
            "name": "Edmundo Mariano da Costa Lanna",
            "person_id": 1,
            "birth_year": "~1920",
            "location": "Belo Horizonte, MG",
            "search_terms": [
                "Edmundo Mariano Lanna",
                "Edmundo Costa Lanna",
            ],
            "type": "birth",
        },
    ]

    def collect(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.log("Playwright not installed. Run: pip install playwright && playwright install chromium", "error")
            self.save_insight(
                category="genealogy",
                title="FamilySearch: Playwright not available",
                content="Playwright is required for FamilySearch scraping. Install with: pip install playwright && playwright install chromium",
                source="familysearch",
                confidence=0,
            )
            return

        self.log("Starting Playwright for FamilySearch...")

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                extra_http_headers={
                    "Accept-Language": "pt-BR,pt;q=0.9",
                },
            )
            page = context.new_page()

            # Block heavy resources to speed up loading
            page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,css}", lambda route: route.abort())

            try:
                # Try direct search URL
                page.goto(f"{self.BASE_URL}/en/brasil/", timeout=20000)
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)

                # Check if blocked
                title = page.title()
                if "403" in title or "Forbidden" in title or not page.inner_text("body"):
                    self.log("FamilySearch is blocking automated access (403)", "error")
                    self.save_insight(
                        category="genealogy",
                        title="FamilySearch: Blocked by Cloudflare (403)",
                        content=(
                            "FamilySearch blocks automated access. Manual search required:\n"
                            "1. Visit https://www.familysearch.org/en/\n"
                            "2. Create free account\n"
                            "3. Search for: Edmundo de Vasconcellos Lanna + Nice Gorgulho\n"
                            "4. Check births in Belo Horizonte 1920-1960\n"
                            "5. Check marriages in Belo Horizonte 1940-1970\n"
                        ),
                        source="familysearch",
                        confidence=0,
                    )
                    return

                for target in self.TARGETS:
                    for term in target.get("search_terms", [target["name"]]):
                        self.log(f"Searching: {term}")
                        self._search_term(page, term, target)
                        time.sleep(2)

            except Exception as e:
                self.log(f"Error: {e}", "error")
                self.save_insight(
                    category="genealogy",
                    title=f"FamilySearch error: {str(e)[:100]}",
                    content=f"Error during FamilySearch search: {e}",
                    source="familysearch",
                    confidence=0,
                )
            finally:
                browser.close()

    def _search_term(self, page, term, target):
        """Search a single term and save results."""
        try:
            # Navigate to search with query parameter
            encoded_term = term.replace(" ", "%20")
            search_url = f"{self.BASE_URL}/search/record/results?count=20&query=%22{encoded_term}%22"

            page.goto(search_url, timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=8000)
            time.sleep(3)

            content = page.inner_text("body")
            if not content or len(content) < 50:
                self.log(f"  Empty response for '{term}'", "warn")
                return

            # Extract result entries
            # FamilySearch shows results in record list format
            import re
            processos = re.findall(r'\d{7,}', content)
            result_count = len(processos)

            # Look for specific data: dates, locations
            birth_years = re.findall(r'19[2-6]\d', content)
            locations = re.findall(r'Belo Horizonte|MG|Brasil', content, re.IGNORECASE)

            self.log(f"  Found ~{result_count} matches, years: {set(birth_years[:10])}, locations: {set(locations[:5])}")

            if result_count > 0:
                self.save_insight(
                    category="genealogy",
                    title=f"FamilySearch: {term[:60]}",
                    content=json.dumps({
                        "search_term": term,
                        "target_name": target.get("name"),
                        "type": target.get("type", "unknown"),
                        "result_count": result_count,
                        "years_found": list(set(birth_years[:10])),
                        "locations_found": list(set(locations[:5])),
                        "page_url": page.url,
                        "page_content_preview": content[:500],
                    }, ensure_ascii=False),
                    source="familysearch",
                    person_id=target.get("person_id"),
                    confidence=50,
                )

        except Exception as e:
            self.log(f"  Error searching '{term}': {e}", "warn")
