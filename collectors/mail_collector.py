"""
Gmail Collector - Scans Rodrigo's Gmail for family-related documents and data
Uses the gog CLI to search and extract emails.
"""

import json
import subprocess
import re
from datetime import datetime

from data.collectors.base import BaseCollector


class GmailCollector(BaseCollector):
    """Scans Gmail for family documents, legal processes, and personal data."""
    NAME = "gmail"
    DESCRIPTION = "Scan Gmail for family documents and data"

    # Search queries for family-related emails
    SEARCH_QUERIES = [
        '"Rodrigo Gorgulho" OR "Vasconcellos Lanna"',
        '"Dados do meu pai" OR "certidão" OR "escritura"',
        '"MOBI FREI CANECA" OR "financiamento" OR "Bradesco"',
        '"investigação de paternidade" OR "abandono"',
        '"Rodrigo-Melo-Lanna" OR "alteração de sobrenome"',
        '"Edmundo Lanna" OR "Henrique Lanna" OR "Marcelo Lanna"',
        '"Joana Ivanete" OR "Nice Gorgulho"',
    ]

    def _gog_search(self, query, max_results=20):
        """Run gog gmail search and return parsed results."""
        try:
            cmd = ['gog', 'gmail', 'search', query, '--max', str(max_results), '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            self.log(f"gog search error: {e}", "warn")
        return {"threads": []}

    def _gog_read_message(self, subject_query, max_results=3):
        """Read email body by subject."""
        try:
            cmd = ['gog', 'gmail', 'messages', 'search', f'subject:"{subject_query}"',
                   '--max', str(max_results), '--json', '--include-body']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        return {"messages": []}

    def _extract_person_data(self, text):
        """Extract personal data from email text using regex."""
        data = {}
        # CPF
        cpf = re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
        if cpf:
            data['cpf'] = cpf.group()
        # RG
        rg = re.search(r'(?:RG|rg)[:\s]*(\d{2}\.\d{3}\.\d{3}-\d{1}|\d+\.\d+\.\d+-\d+)', text)
        if rg:
            data['rg'] = rg.group(1) if rg.lastindex else rg.group()
        # Birth date
        date = re.search(r'(?:nascido|nascimento|birth)[:\s]*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if date:
            data['birth_date'] = date.group(1)
        # Email
        email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        if email:
            data['email'] = email.group()
        # Phone
        phone = re.search(r'\+55\s*\(?\d{2}\)?\s*\d{4,5}[-\s]*\d{4}', text)
        if phone:
            data['phone'] = phone.group()
        return data

    def collect(self):
        """Scan Gmail for family-related emails."""
        all_threads = []

        for query in self.SEARCH_QUERIES:
            self.log(f"Searching: {query[:50]}...")
            result = self._gog_search(query)
            threads = result.get("threads", [])
            for t in threads:
                all_threads.append({
                    "date": t.get("date", ""),
                    "subject": t.get("subject", ""),
                    "from": t.get("from", ""),
                    "snippet": t.get("snippet", ""),
                    "messageCount": t.get("messageCount", 0),
                })
            self.log(f"  Found {len(threads)} threads")

        # Deduplicate by subject
        seen = set()
        unique = []
        for t in all_threads:
            key = t["subject"][:80]
            if key not in seen:
                seen.add(key)
                unique.append(t)

        self.log(f"Total unique threads: {len(unique)}")

        # Save as insights
        for t in unique:
            subject = t["subject"][:100]
            content = f"Date: {t['date']}\nFrom: {t['from']}\nSubject: {subject}\n\n{t['snippet']}"

            session = self._get_session()
            models = self._get_models()

            existing = session.query(models.ResearchInsight).filter(
                models.ResearchInsight.title == subject,
                models.ResearchInsight.source == "gmail"
            ).first()

            if not existing:
                insight = models.ResearchInsight(
                    category="email_thread",
                    title=subject,
                    description=content[:500],
                    source="gmail",
                )
                session.add(insight)
                self.results["added"] += 1
            else:
                self.results["skipped"] += 1

        # Extract personal data from key emails
        key_subjects = [
            "Dados do meu pai",
            "ESCRITURA DE RECONHECIMENTO DE PATERNIDADE",
            "Rodrigo Gorgulho Vasconcelos Lanna",
        ]
        for subj in key_subjects:
            self.log(f"Reading email: {subj[:40]}...")
            msgs = self._gog_read_message(subj)
            for m in msgs.get("messages", []):
                body = m.get("body", "") or m.get("snippet", "")
                if body:
                    person_data = self._extract_person_data(body)
                    if person_data:
                        self.log(f"Extracted: {list(person_data.keys())}", "success")
                        # Save as note
                        session = self._get_session()
                        models = self._get_models()
                        note = models.ResearchNote(
                            title=f"Gmail data extraction: {subj[:60]}",
                            content=json.dumps(person_data, ensure_ascii=False),
                            category="person_data",
                            source="gmail",
                            importance=1,
                            raw_data=json.dumps(person_data, ensure_ascii=False),
                        )
                        session.add(note)
                        self.results["added"] += 1
