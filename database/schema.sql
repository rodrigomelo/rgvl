-- ================================================================
-- RGVL Canonical Schema Reference
-- Updated: 2026-04-01
-- Source of truth: api/models.py
-- ================================================================

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    previous_name TEXT,
    birth_date TEXT,
    birth_place TEXT,
    death_date TEXT,
    cpf TEXT UNIQUE,
    cnpj TEXT,
    rg TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    profession TEXT,
    position TEXT,
    company TEXT,
    father_id INTEGER REFERENCES people(id),
    mother_id INTEGER REFERENCES people(id),
    spouse_id INTEGER REFERENCES people(id),
    marriage_date TEXT,
    status TEXT DEFAULT 'active',
    generation INTEGER,
    source TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence_score INTEGER DEFAULT 50,
    confidence TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person1_id INTEGER NOT NULL REFERENCES people(id),
    person2_id INTEGER NOT NULL REFERENCES people(id),
    relationship_type TEXT NOT NULL,
    confirmed INTEGER DEFAULT 0,
    source TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj TEXT UNIQUE NOT NULL,
    trade_name TEXT,
    legal_name TEXT,
    legal_nature TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    partners TEXT,
    registration_status TEXT,
    opening_date TEXT,
    closing_date TEXT,
    capital REAL,
    person_id INTEGER REFERENCES people(id),
    source TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_confidence INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_type TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    neighborhood TEXT,
    registration TEXT,
    notary_office TEXT,
    cnm TEXT,
    building_name TEXT,
    floor TEXT,
    area_sqm REAL,
    area_common REAL,
    area_total REAL,
    bedrooms INTEGER,
    parking_spaces INTEGER,
    parking_boxes TEXT,
    owners TEXT,
    purchase_date TEXT,
    purchase_value REAL,
    financing_value REAL,
    itbi REAL,
    fiscal_value REAL,
    current_value REAL,
    status TEXT,
    description TEXT,
    source TEXT,
    annotations TEXT,
    raw_data TEXT,
    collected_at DATETIME
);

CREATE TABLE IF NOT EXISTS legal_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_number TEXT,
    court TEXT,
    subject TEXT,
    parties TEXT,
    status TEXT,
    value REAL,
    filings TEXT,
    source TEXT,
    raw_data TEXT,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_confidence INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type TEXT,
    title TEXT,
    description TEXT,
    file_path TEXT,
    issue_date DATETIME,
    expiry_date DATETIME,
    source TEXT,
    raw_data TEXT,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    company TEXT,
    phone TEXT,
    email TEXT,
    is_primary INTEGER DEFAULT 0,
    notes TEXT,
    source TEXT,
    raw_data TEXT,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS social_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER REFERENCES people(id),
    source TEXT,
    username TEXT,
    profile_url TEXT,
    full_name TEXT,
    bio TEXT,
    location TEXT,
    company TEXT,
    profession TEXT,
    followers_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    profile_picture_url TEXT,
    is_verified INTEGER DEFAULT 0,
    is_private INTEGER DEFAULT 0,
    birth_date TEXT,
    email TEXT,
    phone TEXT,
    last_scraped_at DATETIME,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_data TEXT
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER REFERENCES people(id),
    event_type TEXT,
    event_date TEXT,
    description TEXT,
    reference_table TEXT,
    reference_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence TEXT DEFAULT 'medium',
    source TEXT
);

CREATE TABLE IF NOT EXISTS official_gazettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    publication_date DATETIME,
    edition TEXT,
    section TEXT,
    page TEXT,
    title TEXT,
    content TEXT,
    url TEXT,
    tags TEXT,
    data_source TEXT,
    raw_data TEXT,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    type TEXT,
    original_query TEXT,
    result TEXT,
    new_records INTEGER,
    updated_records INTEGER,
    status TEXT,
    error_message TEXT,
    executed_at DATETIME,
    duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    query_used TEXT,
    result TEXT,
    status TEXT DEFAULT 'pending',
    search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    next_attempt DATETIME
);

CREATE TABLE IF NOT EXISTS research_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    priority TEXT,
    target_person TEXT,
    suggested_sources TEXT,
    status TEXT DEFAULT 'pending',
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    category TEXT,
    source TEXT,
    tags TEXT,
    importance INTEGER DEFAULT 2,
    raw_data TEXT,
    person_id INTEGER,
    confidence INTEGER DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    description TEXT,
    source TEXT,
    discovered_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_people_full_name ON people(full_name);
CREATE INDEX IF NOT EXISTS idx_people_cpf ON people(cpf);
CREATE INDEX IF NOT EXISTS idx_people_generation ON people(generation);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_companies_cnpj ON companies(cnpj);
CREATE INDEX IF NOT EXISTS idx_companies_person ON companies(person_id);
CREATE INDEX IF NOT EXISTS idx_properties_address ON properties(address);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_registration ON properties(registration);
CREATE INDEX IF NOT EXISTS idx_legal_cases_number ON legal_cases(process_number);
CREATE INDEX IF NOT EXISTS idx_legal_cases_court ON legal_cases(court);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
CREATE INDEX IF NOT EXISTS idx_contacts_role ON contacts(role);
CREATE INDEX IF NOT EXISTS idx_social_profiles_source ON social_profiles(source);
CREATE INDEX IF NOT EXISTS idx_social_profiles_person ON social_profiles(person_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_person ON timeline_events(person_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_type ON timeline_events(event_type);
CREATE INDEX IF NOT EXISTS idx_official_gazettes_date ON official_gazettes(publication_date);
CREATE INDEX IF NOT EXISTS idx_search_history_source ON search_history(source);
