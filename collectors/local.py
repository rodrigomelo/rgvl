"""
Local Collector - Loads data from local workspace files
Collects contacts, documents, and notes from USER.md and other local files.
"""

import re
from datetime import datetime
from pathlib import Path

from data.collectors.base import BaseCollector


class LocalCollector(BaseCollector):
    NAME = "local"
    DESCRIPTION = "Load local structured data files"

    def collect(self):
        workspace = Path.home() / '.openclaw' / 'workspace-hermes'
        user_md = workspace / 'USER.md'

        if not user_md.exists():
            self.log("USER.md not found, skipping", "warn")
            return

        content = user_md.read_text()

        # Extract contacts
        contacts = []
        email = re.search(r'[\w.-]+@[\w.-]+\.\w+', content)
        if email:
            contacts.append(('email', email.group()))
        phone = re.search(r'\+55\s*\d{2}\s*\d{4,5}[-\s]*\d{4}', content)
        if phone:
            contacts.append(('phone', phone.group()))
        telegram = re.search(r'@[\w]+', content)
        if telegram:
            contacts.append(('telegram', telegram.group()))

        if contacts:
            self.log(f"Found {len(contacts)} contacts in USER.md")
        else:
            self.log("No contacts found in USER.md")

        # Extract documents
        cpf = re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}', content)
        if cpf:
            self.save_document('cpf', f'CPF: {cpf.group()}', fonte='local_file')

        # Save notes from workspace files
        for filepath in [user_md, workspace / 'MEMORY.md', workspace / 'AGENTS.md']:
            if filepath.exists():
                self.save_insight(
                    category='workspace',
                    title=filepath.stem,
                    content=filepath.read_text()[:500],
                    source='local_file'
                )
