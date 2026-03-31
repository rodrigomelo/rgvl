"""
TJMG Playwright Collector - Searches TJMG court processes

Uses the PJe Consulta Pública at:
https://pje-consulta-publica.tjmg.jus.br/

Supports:
- Name-based search (Nome da Parte)
- CNPJ/CPF-based search
- Date range filters

Searches for: Marcelo Lanna, Rodrigo Lanna, Edmundo Lanna, etc.
"""

import json
import re
import time

from collectors.base import BaseCollector


class TJMGPlaywrightCollector(BaseCollector):
    """Search TJMG court processes via Playwright browser automation."""

    NAME = "tjmg_playwright"
    DESCRIPTION = "TJMG court process search via PJe Playwright"

    PJE_URL = "https://pje-consulta-publica.tjmg.jus.br/"

    TARGETS = [
        # Name, person_id in DB, CPF (optional - can improve search)
        {"name": "Marcelo Gorgulho de Vasconcellos Lanna", "person_id": 9},
        {"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "person_id": 6},
        {"name": "Henrique Gorgulho de Vasconcellos Lanna", "person_id": 8},
        {"name": "Edmundo de Vasconcellos Lanna", "person_id": 2},
        {"name": "Monica Maria Almeida Lanna", "person_id": None},
        {"name": "Maria Angela Bolivar Lanna Drumond", "person_id": None},
        {"name": "Julio Cesar de Melo Franco Filho", "person_id": None},
        {"name": "Construtora Barbosa Mello", "person_id": None, "cnpj": "17.185.786/0001-61"},
    ]

    def _init_browser(self):
        """Initialize Playwright browser."""
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
        )
        page = context.new_page()
        return pw, browser, context, page

    def _submit_search(self, page, name=None, cnpj=None, cpj=None):
        """Submit search form and return page HTML/text."""
        page.evaluate("""
        () => {
            // Clear any existing results
            const inputs = document.querySelectorAll('input[type=text]');
            inputs.forEach(i => {
                if (i.id.includes('nomeParte')) {
                    i.value = '';
                    i.dispatchEvent(new Event('input', {bubbles: true}));
                }
            });
        }
        """)

        if name:
            page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input[type=text]');
                for (let inp of inputs) {{
                    const id = inp.id || '';
                    if (id.includes('nomeParte')) {{
                        inp.value = "{name}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
                        console.log('Set nomeParte to: {name}');
                        break;
                    }}
                }}
            }}
            """)
            time.sleep(1)

        if cnpj:
            # Fill CNPJ field
            cnpj_digits = cnpj.replace(".", "").replace("/", "").replace("-", "")
            page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input[type=text]');
                for (let inp of inputs) {{
                    const id = inp.id || '';
                    const ph = inp.placeholder || '';
                    if (ph.includes('CNPJ') || id.includes('cnpj')) {{
                        inp.value = "{cnpj_digits}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        break;
                    }}
                }}
            }}
            """)

        time.sleep(1)

        # Submit form using JavaScript click
        result = page.evaluate("""
        () => {
            // Try all buttons
            const buttons = document.querySelectorAll('button');
            let clicked = false;
            for (let btn of buttons) {
                const text = (btn.innerText || '').trim();
                const id = btn.id || '';
                if (text === 'Pesquisar' || text.includes('Pesquisar')) {
                    btn.click();
                    clicked = true;
                    break;
                }
            }
            
            // Also try submitting the form directly
            if (!clicked) {
                const forms = document.querySelectorAll('form');
                for (let form of forms) {
                    if (form.action && form.action.includes('ConsultaPublica')) {
                        // Try submitting via AJAX
                        const submitEvent = new Event('submit', {bubbles: true, cancelable: true});
                        form.dispatchEvent(submitEvent);
                        clicked = true;
                        break;
                    }
                }
            }
            
            return { clicked };
        }
        """)

        time.sleep(6)
        return result.get("clicked", False)

    def _parse_results(self, page) -> list:
        """Parse process results from the page."""
        content = page.inner_text("body")
        results = []

        # Extract process numbers (format: 0000000-00.0000.0.00.0000)
        processos = re.findall(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', content)
        processos = list(dict.fromkeys(processos))

        # Try to get more details from the table
        try:
            rows = page.locator("table tr").all()
            for row in rows:
                try:
                    cells = row.locator("td").all()
                    if len(cells) >= 2:
                        cell_texts = [c.inner_text().strip() for c in cells]
                        text = " | ".join(cell_texts)
                        # Check if it looks like a process entry
                        if re.search(r'\d{7}-\d{2}', text):
                            proc_match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', text)
                            if proc_match:
                                results.append({
                                    "process_number": proc_match.group(),
                                    "details": text[:200],
                                })
                except:
                    pass
        except:
            pass

        return results

    def _save_processos(self, processos: list, person_id, person_name, source="tjmg_playwright"):
        """Save found processes to the DB."""
        from datetime import datetime, timezone

        for proc in processos:
            proc_num = proc.get("process_number", "").strip()
            if not proc_num:
                continue

            # Check if already exists
            existing = self._get_session().query(
                self._get_models().LegalProcess
            ).filter(
                self._get_models().LegalProcess.process_number == proc_num
            ).first()

            if existing:
                self.results["skipped"] += 1
                continue

            lp = self._get_models().LegalProcess(
                process_number=proc_num,
                court="TJMG",
                subject=proc.get("details", "")[:200],
                status="em_andamento",
                source_confidence="medium",
                raw_data=json.dumps(proc, ensure_ascii=False),
            )
            self._get_session().add(lp)
            self.results["added"] += 1
            self.log(f"  + {proc_num}", "success")

    def collect(self):
        try:
            pw, browser, context, page = self._init_browser()
        except Exception as e:
            self.log(f"Failed to initialize Playwright: {e}", "error")
            return

        try:
            page.goto(self.PJE_URL, timeout=25000)
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)

            # Check page loaded correctly
            if "Consulta pública" not in page.inner_text("body"):
                self.log("Page did not load correctly - PJe may be down", "error")
                self.save_insight(
                    category="legal_process",
                    title="TJMG PJe: Page load failed",
                    content=f"Could not load PJe consultation page at {self.PJE_URL}",
                    source="tjmg_playwright",
                    confidence=0,
                )
                return

            self.log(f"PJe loaded: {page.url}", "success")

            for target in self.TARGETS:
                name = target.get("name")
                person_id = target.get("person_id")

                self.log(f"Searching: {name}")
                clicked = self._submit_search(page, name=name, cnpj=target.get("cnpj"))

                if not clicked:
                    self.log(f"  Could not submit search for {name}", "warn")
                    continue

                # Parse results
                content = page.inner_text("body")

                # Check for result count
                result_match = re.search(r'resultados?\s*encontrados?\s*[:\s]*(\d+)', content, re.IGNORECASE)
                count = int(result_match.group(1)) if result_match else 0

                processos = self._parse_results(page)
                self.log(f"  Found {len(processos)} processes (count says {count})")

                if processos:
                    self._save_processos(processos, person_id, name)
                    # Save insight
                    self.save_insight(
                        category="legal_process",
                        title=f"TJMG: {name} — {len(processos)} processes",
                        content=json.dumps({
                            "name": name,
                            "process_count": len(processos),
                            "processos": [p.get("process_number") for p in processos],
                        }, ensure_ascii=False),
                        source="tjmg_playwright",
                        person_id=person_id,
                        confidence=80,
                    )
                else:
                    # Note the zero results
                    self.save_insight(
                        category="legal_process",
                        title=f"TJMG: {name} — 0 processes in PJe",
                        content=(
                            f"Searched TJMG PJe for '{name}' — returned 0 results.\n"
                            f"Possible reasons:\n"
                            f"1. Name not indexed in PJe\n"
                            f"2. Processes are under 'segredo de justiça'\n"
                            f"3. Processes are in TJSP or other court\n"
                            f"4. Name format differs from court records\n"
                            f"5. Try searching at https://pje-consulta-publica.tjmg.jus.br/"
                        ),
                        source="tjmg_playwright",
                        person_id=person_id,
                        confidence=30,
                    )

                # Reset form for next search (navigate back)
                page.goto(self.PJE_URL, timeout=20000)
                page.wait_for_load_state("networkidle", timeout=12000)
                time.sleep(2)

        except Exception as e:
            self.log(f"Error: {e}", "error")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
            pw.stop()

    def run(self):
        self.log_start()
        try:
            self.collect()
            self._commit()
        except Exception as e:
            self._rollback()
            self.results["errors"].append(str(e))
            self.log(f"Fatal error: {e}", "error")
        finally:
            self._close_session()
            self.log_end()
        return self.results


if __name__ == "__main__":
    collector = TJMGPlaywrightCollector()
    collector.run()
