"""
TJMG Collector - Searches Minas Gerais court system for legal processes
Uses Playwright for full browser automation of the TJMG consultation portal.
"""

import json
import re
import time

from data.collectors.base import BaseCollector


class TJMGPlaywrightCollector(BaseCollector):
    """Search TJMG for legal processes using browser automation."""
    NAME = "tjmg_playwright"
    DESCRIPTION = "Search TJMG legal processes via Playwright"

    BASE_URL = "https://www4.tjmg.jus.br/jurisprudencia/"

    # Names to search in legal processes
    TARGETS = [
        {"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "person_id": 6},
        {"name": "Henrique Gorgulho de Vasconcelloss Lanna", "person_id": 8},
        {"name": "Marcelo Gorgulho de Vasconcellos Lanna", "person_id": 9},
        {"name": "Edmundo de Vasconcellos Lanna", "person_id": 2},
        {"name": "Monica Maria Almeida Lanna", "person_id": None},
        {"name": "Construtora Barbosa Mello", "person_id": None},
    ]

    def collect(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.log("Playwright not installed. Run: pip install playwright && playwright install", "error")
            return

        self.log("Starting Playwright browser...")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            )
            page = context.new_page()

            try:
                for target in self.TARGETS:
                    name = target["name"]
                    self.log(f"Searching TJMG: {name}")

                    try:
                        # Navigate to TJMG consulta
                        page.goto("https://www4.tjmg.jus.br/jurisprudencia/", timeout=30000)
                        time.sleep(3)

                        # Try to find and fill the search field
                        # TJMG has multiple consultation portals
                        # Try the main search page
                        page.goto("https://esaj.tjmg.jus.br/cpopg/open.do", timeout=30000)
                        time.sleep(2)

                        # Check if we got to the consultation page
                        title = page.title()
                        self.log(f"  Page: {title}")

                        # Look for the name search field
                        selectors = [
                            'input#nomeParte',
                            'input[name="nomeParte"]',
                            'input#pesquisarNome',
                            'input[placeholder*="nome" i]',
                            'input[placeholder*="Nome" i]',
                        ]

                        found = False
                        for sel in selectors:
                            try:
                                el = page.locator(sel)
                                if el.count() > 0:
                                    el.first.fill(name)
                                    self.log(f"  Filled search: {name}")

                                    # Try to click search button
                                    page.locator('button[type="submit"], input[type="submit"], button:has-text("Pesquisar"), button:has-text("Buscar")').first.click()
                                    time.sleep(5)

                                    # Parse results
                                    results_text = page.content()
                                    process_count = results_text.count("nuProcesso")
                                    self.log(f"  Found ~{process_count} process references", "success" if process_count > 0 else "warn")

                                    if process_count > 0:
                                        # Extract process numbers
                                        processes = re.findall(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', results_text)
                                        processes = list(set(processes))

                                        for proc in processes[:10]:
                                            self.log(f"  Process: {proc}", "success")
                                            self.save_insight(
                                                category="legal_process",
                                                title=f"TJMG: {proc} — {name}",
                                                content=f"Process: {proc}\nPerson: {name}\nFound via TJMG consultation",
                                                source="tjmg",
                                                person_id=target.get("person_id"),
                                                confidence=90,
                                            )

                                    found = True
                                    break
                            except Exception:
                                continue

                        if not found:
                            self.log(f"  Could not find search field for {name}", "warn")
                            # Save as insight that we need manual search
                            self.save_insight(
                                category="legal_process",
                                title=f"TJMG manual search needed: {name}",
                                content=f"Automated search failed for {name}. Manual search at https://esaj.tjmg.jus.br/cpopg/open.do",
                                source="tjmg_playwright",
                                person_id=target.get("person_id"),
                                confidence=30,
                            )

                        time.sleep(3)

                    except Exception as e:
                        self.log(f"  Error searching {name}: {e}", "warn")

            finally:
                browser.close()
