"""
RGVL — SQLAlchemy Models (English Schema)

All tables and columns use English names.
Brazilian-specific identifiers (CPF, CNPJ, RG) are kept as-is.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# PEOPLE & FAMILY
# =============================================================================

class Person(Base):
    """Person — core entity of the family tree."""
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identity
    full_name = Column(String(255), nullable=False)
    previous_name = Column(String(255))

    # Dates & Location
    birth_date = Column(String(10))
    birth_place = Column(String(255))
    death_date = Column(String(10))

    # Documents (Brazilian standards — keep abbreviations)
    cpf = Column(String(14), unique=True)
    cnpj = Column(String(18))
    rg = Column(String(20))

    # Contact
    email = Column(String(255))
    phone = Column(String(30))
    address = Column(Text)

    # Profession
    profession = Column(String(255))
    position = Column(String(255))
    company = Column(String(255))

    # Genealogy
    father_id = Column(Integer, ForeignKey('people.id'))
    mother_id = Column(Integer, ForeignKey('people.id'))
    spouse_id = Column(Integer, ForeignKey('people.id'))
    marriage_date = Column(String(10))

    # Metadata
    status = Column(String(20), default='active')
    generation = Column(Integer)

    # Provenance
    source = Column(String(255))
    notes = Column(Text)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Confidence
    confidence_score = Column(Integer, default=50)
    confidence = Column(String(20), default='medium')

    # Relationships
    father = relationship('Person', foreign_keys=[father_id], remote_side=[id])
    mother = relationship('Person', foreign_keys=[mother_id], remote_side=[id])
    spouse = relationship('Person', foreign_keys=[spouse_id], remote_side=[id])
    companies = relationship('Company', back_populates='owner')

    __table_args__ = (
        Index('idx_people_full_name', 'full_name'),
        Index('idx_people_cpf', 'cpf'),
        Index('idx_people_generation', 'generation'),
    )


class Relationship(Base):
    """Relationship between two people."""
    __tablename__ = 'relationships'

    id = Column(Integer, primary_key=True, autoincrement=True)

    person1_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    person2_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    relationship_type = Column(String(30), nullable=False)
    confirmed = Column(Integer, default=0)
    source = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_relationships_type', 'relationship_type'),
    )


# =============================================================================
# ASSETS — COMPANIES & PROPERTIES
# =============================================================================

class Company(Base):
    """Company linked to a family member."""
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)

    cnpj = Column(String(18), unique=True, nullable=False)
    trade_name = Column(String(255))
    legal_name = Column(String(255))
    legal_nature = Column(String(255))

    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2))

    # Partners (JSON string)
    partners = Column(Text)

    # Status
    registration_status = Column(String(20))
    opening_date = Column(String(10))
    closing_date = Column(String(10))
    capital = Column(Float)

    # Link to family
    person_id = Column(Integer, ForeignKey('people.id'))

    source = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source_confidence = Column(Integer, default=50)

    owner = relationship('Person', back_populates='companies')

    __table_args__ = (
        Index('idx_companies_cnpj', 'cnpj'),
        Index('idx_companies_person', 'person_id'),
    )


class Property(Base):
    """Real estate property."""
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, autoincrement=True)

    property_type = Column(String(50))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))
    neighborhood = Column(String(100))
    registration = Column(String(50))
    notary_office = Column(String(255))
    cnm = Column(String(50))

    # Building details
    building_name = Column(String(255))
    floor = Column(String(20))

    # Areas (sqm)
    area_sqm = Column(Float)
    area_common = Column(Float)
    area_total = Column(Float)

    # Rooms
    bedrooms = Column(Integer)
    parking_spaces = Column(Integer)
    parking_boxes = Column(String(100))

    # Ownership (JSON list)
    owners = Column(Text)

    # Financial
    purchase_date = Column(String(20))
    purchase_value = Column(Float)
    financing_value = Column(Float)
    itbi = Column(Float)
    fiscal_value = Column(Float)
    current_value = Column(Float)

    # Status
    status = Column(String(50))
    description = Column(Text)

    # Provenance
    source = Column(String(255))
    annotations = Column(Text)
    raw_data = Column(Text)
    collected_at = Column(DateTime)

    __table_args__ = (
        Index('idx_properties_address', 'address'),
        Index('idx_properties_city', 'city'),
        Index('idx_properties_registration', 'registration'),
    )


# =============================================================================
# LEGAL
# =============================================================================

class LegalCase(Base):
    """Judicial process involving a family member."""
    __tablename__ = 'legal_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)

    process_number = Column(String(50))
    court = Column(String(50))
    subject = Column(Text)
    parties = Column(Text)
    status = Column(String(100))
    value = Column(Float)
    filings = Column(Text)

    source = Column(String(255))
    raw_data = Column(Text)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    source_confidence = Column(Integer, default=50)

    __table_args__ = (
        Index('idx_legal_cases_number', 'process_number'),
        Index('idx_legal_cases_court', 'court'),
    )


# =============================================================================
# DOCUMENTS & CONTACTS
# =============================================================================

class Document(Base):
    """Document related to a family member."""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)

    doc_type = Column(String(50))
    title = Column(String(255))
    description = Column(Text)
    file_path = Column(String(500))
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)

    source = Column(String(50))
    raw_data = Column(Text)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_documents_type', 'doc_type'),
    )


class Contact(Base):
    """Contact (lawyers, relatives, institutions)."""
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255))
    role = Column(String(100))
    company = Column(String(255))
    phone = Column(String(30))
    email = Column(String(255))

    is_primary = Column(Boolean, default=False)
    notes = Column(Text)
    source = Column(String(50))
    raw_data = Column(Text)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_contacts_name', 'name'),
        Index('idx_contacts_role', 'role'),
    )


# =============================================================================
# SOCIAL PROFILES
# =============================================================================

class SocialProfile(Base):
    """Online profile (Instagram, LinkedIn, etc.)."""
    __tablename__ = 'social_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)

    person_id = Column(Integer, ForeignKey('people.id'))
    source = Column(String(50))
    username = Column(String(100))
    profile_url = Column(String(500))
    full_name = Column(String(255))
    bio = Column(Text)
    location = Column(String(255))
    company = Column(String(255))
    profession = Column(String(255))

    followers_count = Column(Integer)
    following_count = Column(Integer)
    posts_count = Column(Integer)
    profile_picture_url = Column(String(500))
    is_verified = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)

    birth_date = Column(String(10))
    email = Column(String(255))
    phone = Column(String(30))

    last_scraped_at = Column(DateTime)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    raw_data = Column(Text)

    __table_args__ = (
        Index('idx_social_profiles_source', 'source'),
        Index('idx_social_profiles_person', 'person_id'),
    )


# =============================================================================
# EVENTS
# =============================================================================

class TimelineEvent(Base):
    """Life event (birth, death, marriage, career milestone)."""
    __tablename__ = 'timeline_events'

    id = Column(Integer, primary_key=True, autoincrement=True)

    person_id = Column(Integer, ForeignKey('people.id'), nullable=True)
    event_type = Column(String(50))
    event_date = Column(String(20))
    description = Column(Text)

    reference_table = Column(String(50))
    reference_id = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    confidence = Column(Integer, default=80)
    source = Column(String(100))

    __table_args__ = (
        Index('idx_timeline_events_person', 'person_id'),
        Index('idx_timeline_events_type', 'event_type'),
    )


# =============================================================================
# RESEARCH TRACKING
# =============================================================================

class OfficialGazette(Base):
    """Publication in an official gazette."""
    __tablename__ = 'official_gazettes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = Column(String(20))
    publication_date = Column(DateTime)
    edition = Column(String(20))
    section = Column(String(50))
    page = Column(String(20))
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500))
    tags = Column(Text)
    data_source = Column(String(50))  # was 'fonte' in old schema
    raw_data = Column(Text)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_official_gazettes_date', 'publication_date'),
    )


class CollectionRun(Base):
    """Record of a collector execution."""
    __tablename__ = 'collection_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100))
    type = Column(String(50))
    original_query = Column(Text)
    result = Column(Text)
    new_records = Column(Integer)
    updated_records = Column(Integer)
    status = Column(String(20))
    error_message = Column(Text)
    executed_at = Column(DateTime)
    duration_ms = Column(Integer)


class SearchHistory(Base):
    """Record of a search performed against a data source."""
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = Column(String(100), nullable=False)
    query_used = Column(Text)
    result = Column(Text)
    status = Column(String(20), default='pending')
    search_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    next_attempt = Column(DateTime)

    __table_args__ = (
        Index('idx_search_history_source', 'source'),
    )


class ResearchTask(Base):
    """A pending research task."""
    __tablename__ = 'research_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)

    task = Column(Text, nullable=False)
    priority = Column(String(10))
    target_person = Column(String(255))
    suggested_sources = Column(Text)
    status = Column(String(20), default='pending')
    result = Column(Text)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ResearchNote(Base):
    """Research note from collectors."""
    __tablename__ = 'research_notes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(500))
    content = Column(Text)
    category = Column(String(100))
    source = Column(String(100))
    tags = Column(Text)
    importance = Column(Integer, default=2)
    raw_data = Column(Text)
    person_id = Column(Integer)
    confidence = Column(Integer, default=50)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ResearchInsight(Base):
    """Research insight extracted from data sources."""
    __tablename__ = 'research_insights'

    id = Column(Integer, primary_key=True, autoincrement=True)

    category = Column(String(100))
    title = Column(String(500))
    description = Column(Text)
    source = Column(String(100))
    discovered_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tags = Column(Text)


