"""
RGVL API - Sources routes (provenance tracking)
"""
from flask import Blueprint, jsonify
from api.db import get_session
from api.models import Pessoa, Empresa, Imovel, Evento, ProcessoJudicial, Contato, Documento, BuscaRealizada
from api.utils import model_to_dict

sources_bp = Blueprint('sources', __name__, url_prefix='/api/sources')


# Source type definitions
SOURCE_TYPES = {
    'gmail':         {'emoji': '📧', 'label': 'Gmail',          'bg': '#FCE8E6', 'text': '#C62828'},
    'google_drive':  {'emoji': '📄', 'label': 'Google Drive',    'bg': '#E8F0FE', 'text': '#1D4ED8'},
    'tjmg':          {'emoji': '🏛️', 'label': 'TJMG',           'bg': '#FEF3C7', 'text': '#92400E'},
    'tjsp':          {'emoji': '⚖️', 'label': 'TJSP',           'bg': '#F3E5F5', 'text': '#6D28D9'},
    'jucemg':        {'emoji': '📋', 'label': 'JUCEMG',          'bg': '#DBEAFE', 'text': '#1D4ED8'},
    'jucep':         {'emoji': '📋', 'label': 'JUCEP',           'bg': '#DBEAFE', 'text': '#1D4ED8'},
    'cartorio':      {'emoji': '📜', 'label': 'Cartório',        'bg': '#D1FAE5', 'text': '#065F46'},
    'web_search':    {'emoji': '🔍', 'label': 'Web Search',      'bg': '#E0E7FF', 'text': '#3730A3'},
    'familysearch':  {'emoji': '👨‍👩‍👧', 'label': 'FamilySearch',   'bg': '#FCE7F3', 'text': '#9D174D'},
    'manual':        {'emoji': '✏️', 'label': 'Manual',          'bg': '#F1F5F9', 'text': '#475569'},
    'crea':          {'emoji': '🏗️', 'label': 'CREA',            'bg': '#FED7AA', 'text': '#9A3412'},
    'linkedin':      {'emoji': '💼', 'label': 'LinkedIn',        'bg': '#E0E7FF', 'text': '#3730A3'},
    'escavador':     {'emoji': '🔎', 'label': 'Escavador',       'bg': '#EDE9FE', 'text': '#6D28D9'},
    'inteli':        {'emoji': '💡', 'label': 'INTEL',           'bg': '#ECFDF5', 'text': '#065F46'},
    'default':       {'emoji': '🔗', 'label': 'Outro',           'bg': '#F1F5F9', 'text': '#475569'},
}


def get_source_info(fonte_str):
    """Parse a fonte string into structured source info."""
    if not fonte_str:
        return {**SOURCE_TYPES['default'], 'type': 'default'}

    fonte_lower = fonte_str.lower()

    # Match known sources
    if 'gmail' in fonte_lower or 'email' in fonte_lower:
        stype = 'gmail'
    elif 'drive' in fonte_lower or 'google' in fonte_lower:
        stype = 'google_drive'
    elif 'tjmg' in fonte_lower:
        stype = 'tjmg'
    elif 'tjsp' in fonte_lower:
        stype = 'tjsp'
    elif 'jucemg' in fonte_lower:
        stype = 'jucemg'
    elif 'jucep' in fonte_lower:
        stype = 'jucep'
    elif 'cartorio' in fonte_lower or 'certid' in fonte_lower or 'registro' in fonte_lower:
        stype = 'cartorio'
    elif 'web' in fonte_lower or 'busca' in fonte_lower:
        stype = 'web_search'
    elif 'familysearch' in fonte_lower:
        stype = 'familysearch'
    elif 'linkedin' in fonte_lower:
        stype = 'linkedin'
    elif 'crea' in fonte_lower:
        stype = 'crea'
    elif 'escavador' in fonte_lower:
        stype = 'escavador'
    elif 'inteli' in fonte_lower or 'intel' in fonte_lower:
        stype = 'inteli'
    elif 'manual' in fonte_lower or 'manual' in fonte_lower:
        stype = 'manual'
    else:
        stype = 'default'

    info = SOURCE_TYPES.get(stype, SOURCE_TYPES['default']).copy()
    info['type'] = stype
    info['raw'] = fonte_str
    return info


def aggregate_sources():
    """Aggregate all sources from the database."""
    db = get_session()
    try:
        counts = {}

        # People
        pessoas = db.query(Pessoa).all()
        for p in pessoas:
            fonte = p.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('pessoa')

        # Companies
        empresas = db.query(Empresa).all()
        for c in empresas:
            fonte = c.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('empresa')

        # Events
        eventos = db.query(Evento).all()
        for e in eventos:
            fonte = e.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('evento')

        # Searches
        buscas = db.query(BuscaRealizada).all()
        for b in buscas:
            fonte = b.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('busca')

        # Properties
        imoveis = db.query(Imovel).all()
        for i in imoveis:
            fonte = i.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('imovel')

        # Processes
        processos = db.query(ProcessoJudicial).all()
        for p in processos:
            fonte = p.fonte or ''
            if fonte:
                stype = get_source_info(fonte)['type']
                counts[stype] = counts.get(stype, {'count': 0, 'records': set()})
                counts[stype]['count'] += 1
                counts[stype]['records'].add('processo')

        return counts
    finally:
        db.close()


@sources_bp.route('/summary')
def get_summary():
    """Get system-wide sources summary."""
    counts = aggregate_sources()

    # Build ordered sources list (most used first)
    sources = []
    total = 0
    for stype, data in counts.items():
        info = SOURCE_TYPES.get(stype, SOURCE_TYPES['default']).copy()
        info['type'] = stype
        info['count'] = data['count']
        info['records'] = sorted(list(data['records']))
        sources.append(info)
        total += data['count']

    sources.sort(key=lambda x: x['count'], reverse=True)

    # Add sources with zero count for completeness (show all known types)
    seen = {s['type'] for s in sources}
    for stype, info in SOURCE_TYPES.items():
        if stype not in seen:
            info_copy = info.copy()
            info_copy['type'] = stype
            info_copy['count'] = 0
            info_copy['records'] = []
            sources.append(info_copy)

    total_records = total
    # Assume ~20% of records don't have fonte
    estimated_total = total + 20
    confidence = int((total / estimated_total) * 100) if estimated_total > 0 else 0

    return jsonify({
        'total_records': total_records,
        'total_estimated': estimated_total,
        'confidence_percent': min(confidence, 100),
        'sources': sources,
    })


@sources_bp.route('/person/<int:person_id>')
def get_person_sources(person_id):
    """Get all sources for a specific person."""
    db = get_session()
    try:
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        facts = []

        # Birth
        if person.data_nascimento:
            facts.append({
                'fact_type': 'birth',
                'fact_label': 'Nascimento',
                'date': person.data_nascimento,
                'location': person.local_nascimento,
                **get_source_info(person.fonte or '')
            })

        # Death
        if person.data_falecimento:
            facts.append({
                'fact_type': 'death',
                'fact_label': 'Falecimento',
                'date': person.data_falecimento,
                **get_source_info(person.fonte or '')
            })

        # Marriage
        if person.data_casamento:
            facts.append({
                'fact_type': 'marriage',
                'fact_label': 'Casamento',
                'date': person.data_casamento,
                **get_source_info(person.fonte or '')
            })

        # Events for this person
        eventos = db.query(Evento).filter(Evento.pessoa_id == person_id).all()
        for e in eventos:
            facts.append({
                'fact_type': e.tipo or 'event',
                'fact_label': e.tipo or 'Evento',
                'date': e.data.strftime('%Y-%m-%d') if e.data else None,
                'description': e.descricao,
                **get_source_info(e.fonte or '')
            })

        # Companies for this person
        empresas = db.query(Empresa).filter(Empresa.pessoa_id == person_id).all()
        for c in empresas:
            facts.append({
                'fact_type': 'company',
                'fact_label': c.nome_fantasia or c.razao_social or 'Empresa',
                'date': c.data_abertura,
                **get_source_info(c.fonte or '')
            })

        return jsonify({
            'person_id': person.id,
            'person_name': person.nome_completo,
            'facts': facts,
        })
    finally:
        db.close()


@sources_bp.route('/timeline')
def get_timeline_with_sources():
    """Get timeline events with source info embedded."""
    db = get_session()
    try:
        eventos = db.query(Evento).order_by(Evento.data.asc()).all()
        result = []
        for e in eventos:
            pessoa = db.query(Pessoa).filter(Pessoa.id == e.pessoa_id).first()
            source_info = get_source_info(e.fonte or '')
            result.append({
                'id': e.id,
                'event_type': e.tipo,
                'person_id': e.pessoa_id,
                'person_name': pessoa.nome_completo if pessoa else 'Desconhecido',
                'description': e.descricao,
                'event_date': e.data.strftime('%Y-%m-%d') if e.data else None,
                'source_type': source_info['type'],
                'source_emoji': source_info['emoji'],
                'source_label': source_info['label'],
                'source_raw': source_info.get('raw', ''),
            })
        return jsonify(result)
    finally:
        db.close()
