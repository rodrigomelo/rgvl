"""
RGVL API - Family routes (persons, relationships, events, timeline)
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import Person, Relationship, TimelineEvent
from api.utils import model_to_dict, models_to_list

family_bp = Blueprint('family', __name__, url_prefix='/api/family')


@family_bp.route('/person/<int:person_id>')
def get_person(person_id):
    """Get a person by ID."""
    db = get_session()
    try:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        return jsonify(model_to_dict(person))
    finally:
        db.close()


@family_bp.route('/person/<int:person_id>/tree')
def get_family_tree(person_id):
    """Get full family tree for a person (up to 5 generations)."""
    db = get_session()
    try:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        def get_ancestors(p, depth=0, max_depth=5):
            if depth >= max_depth or not p:
                return None
            result = model_to_dict(p)
            if p.father_id:
                result['father'] = get_ancestors(db.query(Person).get(p.father_id), depth+1, max_depth)
            if p.mother_id:
                result['mother'] = get_ancestors(db.query(Person).get(p.mother_id), depth+1, max_depth)
            if p.spouse_id:
                result['spouse'] = model_to_dict(db.query(Person).get(p.spouse_id))
            return result

        child_rels = db.query(Relationship).filter(
            Relationship.person1_id == person_id,
            Relationship.relationship_type.in_(['filho', 'filha'])
        ).all()
        child_ids = [r.person2_id for r in child_rels]
        children_map = {p.id: p for p in db.query(Person).filter(Person.id.in_(child_ids)).all()} if child_ids else {}
        children = [model_to_dict(children_map[cid]) for cid in child_ids if cid in children_map]

        sibling_ids = set()
        if person.father_id:
            siblings_via_father = db.query(Person).filter(
                Person.father_id == person.father_id,
                Person.id != person_id
            ).all()
            sibling_ids.update(s.id for s in siblings_via_father)
        if person.mother_id:
            siblings_via_mother = db.query(Person).filter(
                Person.mother_id == person.mother_id,
                Person.id != person_id
            ).all()
            sibling_ids.update(s.id for s in siblings_via_mother)
        siblings_map = {p.id: p for p in db.query(Person).filter(Person.id.in_(sibling_ids)).all()} if sibling_ids else {}
        siblings = [model_to_dict(siblings_map[sid]) for sid in sibling_ids if sid in siblings_map]

        tree = get_ancestors(person)
        tree['children'] = children
        tree['siblings'] = siblings
        return jsonify(tree)
    finally:
        db.close()


@family_bp.route('/person/<int:person_id>/relatives')
def get_relatives(person_id):
    """Get all relatives of a person."""
    db = get_session()
    try:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        rels = db.query(Relationship).filter(
            (Relationship.person1_id == person_id) |
            (Relationship.person2_id == person_id)
        ).all()

        relatives = []
        for r in rels:
            other_id = r.person2_id if r.person1_id == person_id else r.person1_id
            other = db.query(Person).get(other_id)
            if other:
                relatives.append({
                    'person': model_to_dict(other),
                    'type': r.relationship_type,
                    'confirmed': bool(r.confirmed),
                    'source': r.source,
                })

        return jsonify(relatives)
    finally:
        db.close()


@family_bp.route('/generation/<int:n>')
def get_generation(n):
    """Get all people in a given generation."""
    db = get_session()
    try:
        people = db.query(Person).filter(Person.generation == n).order_by(Person.full_name).all()
        return jsonify(models_to_list(people))
    finally:
        db.close()


@family_bp.route('/summary')
def get_summary():
    """Family summary statistics."""
    db = get_session()
    try:
        total = db.query(Person).count()
        confirmed = db.query(Relationship).filter(Relationship.confirmed == 1).count()
        speculative = db.query(Relationship).filter(Relationship.confirmed == 0).count()
        return jsonify({
            'total_people': total,
            'total_relationships': confirmed + speculative,
            'confirmed_relationships': confirmed,
            'speculative_relationships': speculative,
        })
    finally:
        db.close()


@family_bp.route('/events')
def get_events():
    """List all family events."""
    db = get_session()
    try:
        events = db.query(TimelineEvent).order_by(TimelineEvent.event_date).all()
        return jsonify(models_to_list(events))
    finally:
        db.close()


@family_bp.route('/sources')
def get_sources():
    """Get data sources summary — counts records by source across English tables."""
    from sqlalchemy import text
    db = get_session()
    try:
        query = text("""
            SELECT 'people' as tbl, source, COUNT(*) as cnt FROM people WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'companies', source, COUNT(*) FROM companies WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'properties', source, COUNT(*) FROM properties WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'legal_cases', source, COUNT(*) FROM legal_cases WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'contacts', source, COUNT(*) FROM contacts WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'documents', source, COUNT(*) FROM documents WHERE source IS NOT NULL AND source != '' GROUP BY source
            UNION ALL
            SELECT 'relationships', source, COUNT(*) FROM relationships WHERE source IS NOT NULL AND source != '' GROUP BY source
        """)
        result = db.execute(query).fetchall()

        sources = {}
        for row in result:
            tbl, src, cnt = row[0], row[1], row[2]
            if src not in sources:
                sources[src] = {'count': 0, 'tables': [], 'types': []}
            sources[src]['count'] += cnt
            if tbl not in sources[src]['tables']:
                sources[src]['tables'].append(tbl)
            sources[src]['types'].append(src)

        sorted_sources = dict(sorted(sources.items(), key=lambda x: x[1]['count'], reverse=True))

        return jsonify({
            'total_sources': len(sorted_sources),
            'sources': sorted_sources
        })
    finally:
        db.close()


@family_bp.route('/timeline')
def get_timeline():
    """List all events with person names. Normalizes dates, deduplicates, sorts chronologically."""
    from sqlalchemy import text
    db = get_session()
    try:
        TYPE_LABELS = {
            'birth': 'birth', 'nascimento': 'birth',
            'death': 'death', 'falecimento': 'death',
            'marriage': 'marriage', 'casamento': 'marriage',
            'company': 'company',
            'juridico': 'legal', 'pesquisa': 'research',
            'contato_familiar': 'family_contact',
            'reconhecimento_paternidade': 'paternity',
            'alteracao_nome': 'name_change',
        }

        def normalize_date(edate):
            raw = str(edate) if edate else ''
            approx = False
            if raw.startswith('~'):
                approx = True
                raw = raw[1:]
            if not raw:
                return None, approx
            parts = raw.split('-')
            if len(parts) == 1:
                return f"{parts[0]}-01-01", approx
            elif len(parts) == 2:
                return f"{parts[0]}-{parts[1]}-01", approx
            else:
                return raw, approx

        seen = {}
        def process_rows(rows, source):
            out = []
            for r in rows:
                pid, pname, etype, edate, desc = r[1], r[2], r[3], r[4], r[5]
                norm_type = TYPE_LABELS.get(etype, etype)
                norm_date, approx = normalize_date(edate)

                if norm_date is None:
                    continue
                if norm_type == 'research':
                    continue

                key = (pid, norm_date, norm_type)
                if key not in seen:
                    seen[key] = True
                    out.append({
                        'id': r[0],
                        'person_id': pid,
                        'person_name': pname or 'Unknown',
                        'event_type': norm_type,
                        'event_date': edate,
                        'norm_date': norm_date or '9999-12-31',
                        'approx': approx,
                        'description': desc,
                        'source': r[6] if len(r) > 6 else source,
                        'confidence': r[7] if len(r) > 7 else 'medium'
                    })
            return out

        events_q = text("""
        SELECT e.id, e.person_id, p.full_name, e.event_type, e.event_date, e.description, e.source, e.confidence
        FROM timeline_events e LEFT JOIN people p ON e.person_id = p.id
        """)
        rows_e = db.execute(events_q).fetchall()

        timeline = process_rows(rows_e, 'timeline_events')
        timeline.sort(key=lambda x: x['norm_date'])

        return jsonify(timeline)
    finally:
        db.close()
