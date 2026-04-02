"""
RGVL Data Quality Tests
"""
import sys
from pathlib import Path

from sqlalchemy import func, or_

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.db import get_session
from api.models import Company, Contact, Document, LegalCase, Person, TimelineEvent
from api.utils import normalize_confidence


class TestDataQuality:
    """Tests for data quality rules"""

    def test_events_have_source(self):
        """All events should have a source - no orphan data"""
        db = get_session()
        try:
            count = db.query(TimelineEvent).filter(
                or_(TimelineEvent.source.is_(None), TimelineEvent.source == '')
            ).count()
            assert count == 0
        finally:
            db.close()

    def test_events_have_confidence(self):
        """All events should have confidence level"""
        db = get_session()
        try:
            rows = db.query(TimelineEvent.confidence).all()
            normalized_values = [normalize_confidence(value) for value, in rows]
            missing_count = sum(value is None for value in normalized_values)
            out_of_range_count = sum(
                not (
                    isinstance(value, int) and 0 <= value <= 100
                    or value in {'low', 'medium', 'high'}
                )
                for value in normalized_values
            )
            assert missing_count == 0
            assert out_of_range_count == 0
        finally:
            db.close()

    def test_no_duplicate_events(self):
        """No duplicate events (same person, type, date)"""
        db = get_session()
        try:
            duplicates = db.query(
                TimelineEvent.person_id,
                TimelineEvent.event_type,
                TimelineEvent.event_date,
                func.count(TimelineEvent.id).label('count'),
            ).group_by(
                TimelineEvent.person_id,
                TimelineEvent.event_type,
                TimelineEvent.event_date,
            ).having(func.count(TimelineEvent.id) > 1).all()
            assert duplicates == []
        finally:
            db.close()

    def test_people_have_full_name(self):
        """All people should have full_name."""
        db = get_session()
        try:
            count = db.query(Person).filter(
                or_(Person.full_name.is_(None), Person.full_name == '')
            ).count()
            assert count == 0
        finally:
            db.close()

    def test_companies_have_cnpj(self):
        """All companies should have CNPJ"""
        db = get_session()
        try:
            count = db.query(Company).filter(
                or_(Company.cnpj.is_(None), Company.cnpj == '')
            ).count()
            assert count == 0
        finally:
            db.close()

    def test_no_unconfirmed_data_in_main_tables(self):
        """Main tables should not have unconfirmed data"""
        db = get_session()
        try:
            missing_sources = {
                'people': db.query(Person).filter(or_(Person.source.is_(None), Person.source == '')).count(),
                'companies': db.query(Company).filter(or_(Company.source.is_(None), Company.source == '')).count(),
                'legal_cases': db.query(LegalCase).filter(or_(LegalCase.source.is_(None), LegalCase.source == '')).count(),
                'documents': db.query(Document).filter(or_(Document.source.is_(None), Document.source == '')).count(),
                'contacts': db.query(Contact).filter(or_(Contact.source.is_(None), Contact.source == '')).count(),
                'events': db.query(TimelineEvent).filter(or_(TimelineEvent.source.is_(None), TimelineEvent.source == '')).count(),
            }
            assert missing_sources == {key: 0 for key in missing_sources}
        finally:
            db.close()
