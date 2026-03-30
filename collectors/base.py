"""
Base Collector for RGVL Data Collection System

All collectors inherit from this base class. Provides:
- DB session management
- Standardized output formatting
- Deduplication helpers
- Error handling
- Progress logging
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

# Setup project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class BaseCollector(ABC):
    """Base class for all RGVL data collectors."""

    # Subclasses override these
    NAME = "base"
    DESCRIPTION = "Base collector"
    REQUIRES_AUTH = False  # Set True if collector needs API keys/tokens

    def __init__(self):
        self.db = None
        self.session = None
        self.results = {"added": 0, "updated": 0, "skipped": 0, "errors": []}

    # --- DB Management ---

    def _get_session(self):
        """Get a DB session (lazy import to avoid circular imports)."""
        if self.session is None:
            from api.db import SessionLocal
            self.session = SessionLocal()
        return self.session

    def _close_session(self):
        """Close DB session if open."""
        if self.session:
            self.session.close()
            self.session = None

    def _commit(self):
        """Commit current transaction."""
        if self.session:
            self.session.commit()

    def _rollback(self):
        """Rollback current transaction."""
        if self.session:
            self.session.rollback()

    # --- Model Helpers (lazy imports) ---

    def _get_models(self):
        """Lazy import all models. Returns the models module."""
        import api.models as m
        return m

    # --- Deduplication ---

    def _exists(self, model_class, **filters):
        """Check if a record matching filters already exists."""
        session = self._get_session()
        query = session.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        return query.first() is not None

    # --- Logging ---

    def log(self, msg, level="info"):
        """Log a message with collector name prefix."""
        prefix = {"info": "  ", "success": "  ✅", "warn": "  ⚠️", "error": "  ❌"}
        print(f"{prefix.get(level, '  ')} [{self.NAME}] {msg}")

    def log_start(self):
        """Log collection start."""
        print(f"\n{'='*50}")
        print(f" 🔍 {self.DESCRIPTION}")
        print(f"    {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*50}")

    def log_end(self):
        """Log collection results."""
        r = self.results
        total = r["added"] + r["updated"] + r["skipped"]
        print(f"\n  📊 Added: {r['added']} | Updated: {r['updated']} | Skipped: {r['skipped']}")
        if r["errors"]:
            print(f"  ⚠️  Errors: {len(r['errors'])}")
            for e in r["errors"][:5]:
                print(f"      - {e}")
        print(f"\n  ✅ {self.NAME} complete! ({total} records processed)")

    # --- Profile Helper ---

    def save_profile(self, source, external_id, name="", bio="", url="", avatar_url="", raw_data=None):
        """Save or update a profile record."""
        models = self._get_models()
        session = self._get_session()

        existing = session.query(models.Perfil).filter(
            models.Perfil.source == source,
            models.Perfil.external_id == external_id
        ).first()

        if existing:
            if name: existing.name = name
            if bio: existing.bio = bio
            if url: existing.profile_url = url
            if avatar_url: existing.avatar_url = avatar_url
            if raw_data: existing.raw_data = json.dumps(raw_data, ensure_ascii=False)
            existing.updated_at = datetime.now(timezone.utc)
            self.results["updated"] += 1
            self.log(f"Updated {source}: {external_id}", "success")
        else:
            profile = models.Perfil(
                source=source,
                external_id=external_id,
                name=name,
                bio=bio,
                profile_url=url,
                avatar_url=avatar_url,
                raw_data=json.dumps(raw_data, ensure_ascii=False) if raw_data else None,
            )
            session.add(profile)
            self.results["added"] += 1
            self.log(f"Added {source}: {external_id}", "success")

    # --- Event Helper ---

    def save_event(self, person_id, event_type, event_date, description, source, confidence=80):
        """Save or update a timeline event."""
        models = self._get_models()
        session = self._get_session()

        existing = session.query(models.Evento).filter(
            models.Evento.person_id == person_id,
            models.Evento.event_type == event_type,
            models.Evento.event_date == event_date,
            models.Evento.description == description
        ).first()

        if existing:
            self.results["skipped"] += 1
            return existing

        event = models.Evento(
            person_id=person_id,
            event_type=event_type,
            event_date=event_date,
            description=description,
            source=source,
            confidence=confidence,
        )
        session.add(event)
        self.results["added"] += 1
        self.log(f"Event: {event_date} {event_type} - {description[:50]}...", "success")
        return event

    # --- Document Helper ---

    def save_document(self, doc_type, title, description="", fonte="", issue_date=None, file_path=None, raw_data=None):
        """Save or update a document record."""
        models = self._get_models()
        session = self._get_session()

        existing = session.query(models.Documento).filter(
            models.Documento.title == title
        ).first()

        if existing:
            self.results["skipped"] += 1
            return existing

        doc = models.Documento(
            doc_type=doc_type,
            title=title,
            description=description,
            fonte=fonte,
            issue_date=issue_date,
            file_path=file_path,
            raw_data=json.dumps(raw_data, ensure_ascii=False) if raw_data else None,
        )
        session.add(doc)
        self.results["added"] += 1
        self.log(f"Doc: {title[:60]}", "success")
        return doc

    # --- Insight Helper ---

    def save_insight(self, category, title, content, source, person_id=None, confidence=80):
        """Save a research insight."""
        session = self._get_session()
        models = self._get_models()

        insight = models.Insight(
            category=category,
            title=title,
            content=content,
            source=source,
            person_id=person_id,
            confidence=confidence,
        )
        session.add(insight)
        self.results["added"] += 1
        self.log(f"Insight: {title[:50]}", "success")

    # --- Abstract Methods ---

    @abstractmethod
    def collect(self):
        """Main collection logic. Override in subclass."""
        pass

    def run(self):
        """Run the collector with error handling."""
        self.log_start()
        try:
            self.collect()
            self._commit()
        except Exception as e:
            self._rollback()
            self.results["errors"].append(str(e))
            self.log(f"Fatal error: {e}", "error")
            import traceback
            traceback.print_exc()
        finally:
            self._close_session()
            self.log_end()
        return self.results
