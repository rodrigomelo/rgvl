"""
RGVL API - Sources routes (provenance tracking)
"""
from flask import Blueprint, jsonify
from api.db import get_session
from api.models import Person, Company, Property, TimelineEvent, LegalCase, Contact, Document
from api.utils import normalize_event_type

sources_bp = Blueprint('sources', __name__, url_prefix='/api/sources')


# Source type definitions
SOURCE_TYPES = {
    'gmail':         {'emoji': '📧', 'label': 'Gmail',          'bg': '#FCE8E6', 'text': '#C62828'},
    'google_drive':  {'emoji': '📄', 'label': 'Google Drive',    'bg': '#E8F0FE', 'text': '#1D4ED8'},
    'tjmg':          {'emoji': '🏛️', 'label': 'TJMG',           'bg': '#FEF3C7', 'text': '#92400E'},
    'tjsp':          {'emoji': '⚖️', 'label': 'TJSP',           'bg': '#F3E5F5', 'text': '#6D28D9'},
    'jucemg':        {'emoji': '📋', 'label': 'JUCEMG',          'bg': '#DBEAFE', 'text': '#1D4ED8'},
    'jucesp':        {'emoji': '📋', 'label': 'JUCESP',          'bg': '#DBEAFE', 'text': '#1D4ED8'},
    'notary':        {'emoji': '📜', 'label': 'Notary Office',   'bg': '#D1FAE5', 'text': '#065F46'},
    'web_search':    {'emoji': '🔍', 'label': 'Web Search',      'bg': '#E0E7FF', 'text': '#3730A3'},
    'familysearch':  {'emoji': '👨‍👩‍👧', 'label': 'FamilySearch',   'bg': '#FCE7F3', 'text': '#9D174D'},
    'manual':        {'emoji': '✏️', 'label': 'Manual',          'bg': '#F1F5F9', 'text': '#475569'},
    'crea':          {'emoji': '🏗️', 'label': 'CREA',            'bg': '#FED7AA', 'text': '#9A3412'},
    'linkedin':      {'emoji': '💼', 'label': 'LinkedIn',        'bg': '#E0E7FF', 'text': '#3730A3'},
    'escavador':     {'emoji': '🔎', 'label': 'Escavador',       'bg': '#EDE9FE', 'text': '#6D28D9'},
    'intel':         {'emoji': '💡', 'label': 'INTEL',           'bg': '#ECFDF5', 'text': '#065F46'},
    'other':         {'emoji': '🔗', 'label': 'Other',           'bg': '#F1F5F9', 'text': '#475569'},
}


def get_source_info(source_str):
    """Parse a source string into structured source info."""
    if not source_str:
        return {**SOURCE_TYPES['other'], 'type': 'other'}

    lower = source_str.lower()

    if 'gmail' in lower or 'email' in lower:
        stype = 'gmail'
    elif 'drive' in lower or 'google' in lower:
        stype = 'google_drive'
    elif 'tjmg' in lower:
        stype = 'tjmg'
    elif 'tjsp' in lower:
        stype = 'tjsp'
    elif 'jucemg' in lower:
        stype = 'jucemg'
    elif 'jucesp' in lower or 'jucep' in lower:
        stype = 'jucesp'
    elif 'cartorio' in lower or 'certid' in lower or 'registro' in lower:
        stype = 'notary'
    elif 'web' in lower or 'busca' in lower:
        stype = 'web_search'
    elif 'familysearch' in lower:
        stype = 'familysearch'
    elif 'linkedin' in lower:
        stype = 'linkedin'
    elif 'crea' in lower:
        stype = 'crea'
    elif 'escavador' in lower:
        stype = 'escavador'
    elif 'inteli' in lower or 'intel' in lower or lower in ('timeline.md', 'companies.md'):
        stype = 'intel'
    elif 'manual' in lower:
        stype = 'manual'
    else:
        stype = 'other'

    info = SOURCE_TYPES.get(stype, SOURCE_TYPES['other']).copy()
    info['type'] = stype
    info['raw'] = source_str
    return info


def aggregate_sources():
    """Aggregate all sources from the database."""
    db = get_session()
    try:
        counts = {}

        for model, label in [(Person, 'person'), (Company, 'company'),
                              (Property, 'property'), (LegalCase, 'legal_case')]:
            records = db.query(model).all()
            for r in records:
                src = getattr(r, 'source', '') or ''
                if src:
                    stype = get_source_info(src)['type']
                    counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                    counts[stype]['count'] += 1
                    counts[stype]['records'].add(label)

        return counts
    finally:
        db.close()


@sources_bp.route('/summary')
def get_summary():
    """Get system-wide sources summary."""
    counts = aggregate_sources()

    sources = []
    total = 0
    for stype, data in counts.items():
        info = SOURCE_TYPES.get(stype, SOURCE_TYPES['other']).copy()
        info['type'] = stype
        info['count'] = data['count']
        info['records'] = sorted(list(data['records']))
        sources.append(info)
        total += data['count']

    sources.sort(key=lambda x: x['count'], reverse=True)

    seen = {s['type'] for s in sources}
    for stype, info in SOURCE_TYPES.items():
        if stype not in seen:
            info_copy = info.copy()
            info_copy['type'] = stype
            info_copy['count'] = 0
            info_copy['records'] = []
            sources.append(info_copy)

    estimated_total = total + 20
    confidence = int((total / estimated_total) * 100) if estimated_total > 0 else 0

    return jsonify({
        'total_records': total,
        'total_estimated': estimated_total,
        'confidence_percent': min(confidence, 100),
        'sources': sources,
    })


@sources_bp.route('/records')
def get_all_records():
    """Get all records grouped by source."""
    db = get_session()
    try:
        records = []

        # People
        people = db.query(Person).filter(Person.source.isnot(None), Person.source != '').all()
        for p in people:
            info = get_source_info(p.source)
            records.append({
                'person_id': p.id,
                'person_name': p.full_name,
                'source': p.source,
                'source_type': info['type'],
                'source_emoji': info['emoji'],
                'source_label': info['label'],
                'record_type': 'person',
                'record_label': 'Person',
                'record_id': p.id
            })

        # Companies
        companies = db.query(Company).filter(Company.source.isnot(None), Company.source != '').all()
        for c in companies:
            info = get_source_info(c.source)
            records.append({
                'person_id': c.person_id,
                'source': c.source,
                'source_type': info['type'],
                'source_emoji': info['emoji'],
                'source_label': info['label'],
                'record_type': 'company',
                'record_label': c.trade_name or c.legal_name or 'Company',
                'record_id': c.id
            })

        # Properties
        props = db.query(Property).filter(Property.source.isnot(None), Property.source != '').all()
        for i in props:
            info = get_source_info(i.source)
            records.append({
                'source': i.source,
                'source_type': info['type'],
                'source_emoji': info['emoji'],
                'source_label': info['label'],
                'record_type': 'property',
                'record_label': (i.address or 'Property')[:50],
                'record_id': i.id
            })

        # Legal cases
        cases = db.query(LegalCase).filter(LegalCase.source.isnot(None), LegalCase.source != '').all()
        for l in cases:
            info = get_source_info(l.source)
            records.append({
                'source': l.source,
                'source_type': info['type'],
                'source_emoji': info['emoji'],
                'source_label': info['label'],
                'record_type': 'legal_case',
                'record_label': l.process_number or 'Case',
                'record_id': l.id
            })

        return jsonify({
            'records': records,
            'total': len(records)
        })
    finally:
        db.close()


@sources_bp.route('/person/<int:person_id>')
def get_person_sources(person_id):
    """Get all sources for a specific person."""
    db = get_session()
    try:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        facts = []

        if person.birth_date:
            facts.append({
                'fact_type': 'birth',
                'fact_label': 'Birth',
                'date': person.birth_date,
                'location': person.birth_place,
                **get_source_info(person.source or '')
            })

        if person.death_date:
            facts.append({
                'fact_type': 'death',
                'fact_label': 'Death',
                'date': person.death_date,
                **get_source_info(person.source or '')
            })

        if person.marriage_date:
            facts.append({
                'fact_type': 'marriage',
                'fact_label': 'Marriage',
                'date': person.marriage_date,
                **get_source_info(person.source or '')
            })

        events = db.query(TimelineEvent).filter(TimelineEvent.person_id == person_id).all()
        for e in events:
            facts.append({
                'fact_type': normalize_event_type(e.event_type or 'event'),
                'fact_label': normalize_event_type(e.event_type or 'event').replace('_', ' ').title(),
                'date': e.event_date,
                'description': e.description,
                **get_source_info(e.source or '')
            })

        companies = db.query(Company).filter(Company.person_id == person_id).all()
        for c in companies:
            facts.append({
                'fact_type': 'company',
                'fact_label': c.trade_name or c.legal_name or 'Company',
                'date': c.opening_date,
                **get_source_info(c.source or '')
            })

        return jsonify({
            'person_id': person.id,
            'person_name': person.full_name,
            'facts': facts,
        })
    finally:
        db.close()


@sources_bp.route('/timeline')
def get_timeline_with_sources():
    """Get timeline events with source info."""
    db = get_session()
    try:
        events = db.query(TimelineEvent).order_by(TimelineEvent.event_date.asc()).all()
        result = []

        for e in events:
            person = db.query(Person).filter(Person.id == e.person_id).first()
            source_info = get_source_info(e.source or '')
            result.append({
                'id': e.id,
                'event_type': normalize_event_type(e.event_type),
                'person_id': e.person_id,
                'person_name': person.full_name if person else 'Unknown',
                'description': e.description,
                'event_date': e.event_date,
                'source_type': source_info['type'],
                'source_emoji': source_info['emoji'],
                'source_label': source_info['label'],
                'source_raw': source_info.get('raw', ''),
            })
        return jsonify(result)
    finally:
        db.close()
