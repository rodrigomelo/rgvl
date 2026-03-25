"""
RGVL API - Family routes (persons, relationships, events)
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import Pessoa, Relacionamento, Evento
from api.utils import model_to_dict, models_to_list

family_bp = Blueprint('family', __name__, url_prefix='/api/family')


@family_bp.route('/person/<int:person_id>')
def get_person(person_id):
    """Get a person by ID."""
    db = get_session()
    try:
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
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
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        def get_ancestors(p, depth=0, max_depth=5):
            if depth >= max_depth or not p:
                return None
            result = model_to_dict(p)
            if p.pai_id:
                result['pai'] = get_ancestors(db.query(Pessoa).get(p.pai_id), depth+1, max_depth)
            if p.mae_id:
                result['mae'] = get_ancestors(db.query(Pessoa).get(p.mae_id), depth+1, max_depth)
            if p.conjuge_id:
                result['conjuge'] = model_to_dict(db.query(Pessoa).get(p.conjuge_id))
            return result

        child_rels = db.query(Relacionamento).filter(
            Relacionamento.pessoa_de == person_id,
            Relacionamento.tipo.in_(['filho', 'filha'])
        ).all()
        child_ids = [r.pessoa_para for r in child_rels]
        children_map = {p.id: p for p in db.query(Pessoa).filter(Pessoa.id.in_(child_ids)).all()} if child_ids else {}
        children = [model_to_dict(children_map[cid]) for cid in child_ids if cid in children_map]

        sibling_ids = set()
        if person.pai_id:
            siblings_via_pai = db.query(Pessoa).filter(
                Pessoa.pai_id == person.pai_id,
                Pessoa.id != person_id
            ).all()
            sibling_ids.update(s.id for s in siblings_via_pai)
        if person.mae_id:
            siblings_via_mae = db.query(Pessoa).filter(
                Pessoa.mae_id == person.mae_id,
                Pessoa.id != person_id
            ).all()
            sibling_ids.update(s.id for s in siblings_via_mae)
        siblings_map = {p.id: p for p in db.query(Pessoa).filter(Pessoa.id.in_(sibling_ids)).all()} if sibling_ids else {}
        siblings = [model_to_dict(siblings_map[sid]) for sid in sibling_ids if sid in siblings_map]

        tree = get_ancestors(person)
        tree['filhos'] = children
        tree['irmaos'] = siblings
        return jsonify(tree)
    finally:
        db.close()


@family_bp.route('/person/<int:person_id>/relatives')
def get_relatives(person_id):
    """Get all relatives of a person."""
    db = get_session()
    try:
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        rels = db.query(Relacionamento).filter(
            (Relacionamento.pessoa_de == person_id) |
            (Relacionamento.pessoa_para == person_id)
        ).all()

        relatives = []
        for r in rels:
            other_id = r.pessoa_para if r.pessoa_de == person_id else r.pessoa_de
            other = db.query(Pessoa).get(other_id)
            if other:
                relatives.append({
                    'pessoa': model_to_dict(other),
                    'tipo': r.tipo,
                    'confirmado': bool(r.confirmado),
                    'fonte': r.fonte,
                })

        return jsonify(relatives)
    finally:
        db.close()


@family_bp.route('/generation/<int:n>')
def get_generation(n):
    """Get all people in a given generation."""
    db = get_session()
    try:
        people = db.query(Pessoa).filter(Pessoa.geracao == n).order_by(Pessoa.nome_completo).all()
        return jsonify(models_to_list(people))
    finally:
        db.close()


@family_bp.route('/summary')
def get_summary():
    """Family summary statistics."""
    db = get_session()
    try:
        total = db.query(Pessoa).count()
        confirmed = db.query(Relacionamento).filter(Relacionamento.confirmado == 1).count()
        speculative = db.query(Relacionamento).filter(Relacionamento.confirmado == 0).count()
        return jsonify({
            'total_pessoas': total,
            'total_relacionamentos': confirmed + speculative,
            'relacionamentos_confirmados': confirmed,
            'relacionamentos_espericulativos': speculative,
        })
    finally:
        db.close()


@family_bp.route('/events')
def get_events():
    """List all family events (births, deaths, marriages, career)."""
    db = get_session()
    try:
        events = db.query(Evento).order_by(Evento.event_date).all()
        return jsonify(models_to_list(events))
    finally:
        db.close()


@family_bp.route('/sources')
def get_sources():
    """Get data sources summary - counts records by fonte."""
    from sqlalchemy import text
    db = get_session()
    try:
        query = text("""
            SELECT 'pessoas' as tbl, fonte, COUNT(*) as cnt FROM pessoas WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'empresas_familia', fonte, COUNT(*) FROM empresas_familia WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'imoveis', fonte, COUNT(*) FROM imoveis WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'legal_processes', fonte, COUNT(*) FROM legal_processes WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'contatos', fonte, COUNT(*) FROM contatos WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'documentos', fonte, COUNT(*) FROM documentos WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
            UNION ALL
            SELECT 'relacionamentos', fonte, COUNT(*) FROM relacionamentos WHERE fonte IS NOT NULL AND fonte != '' GROUP BY fonte
        """)
        result = db.execute(query).fetchall()
        
        sources = {}
        for row in result:
            tbl, fonte, cnt = row[0], row[1], row[2]
            if fonte not in sources:
                sources[fonte] = {'count': 0, 'tables': [], 'types': []}
            sources[fonte]['count'] += cnt
            if tbl not in sources[fonte]['tables']:
                sources[fonte]['tables'].append(tbl)
            sources[fonte]['types'].append(fonte)
        
        sorted_sources = dict(sorted(sources.items(), key=lambda x: x[1]['count'], reverse=True))
        
        return jsonify({
            'total_sources': len(sorted_sources),
            'sources': sorted_sources
        })
    finally:
        db.close()


@family_bp.route('/timeline')
def get_timeline():
    """List all events from both events and eventos tables with person names.
    Normalizes dates, deduplicates, and sorts chronologically.
    """
    from sqlalchemy import text
    db = get_session()
    try:
        # Translation: event_type -> English label
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
            """Normalize date to YYYY-MM-DD for sorting. ~ prefix means approximate."""
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

        # Single seen dict for cross-table deduplication
        seen = {}
        def process_rows(rows, source):
            out = []
            for r in rows:
                pid, pname, etype, edate, desc = r[1], r[2], r[3], r[4], r[5]
                norm_type = TYPE_LABELS.get(etype, etype)
                norm_date, approx = normalize_date(edate)
                
                # Skip: no date known (null date)
                if norm_date is None:
                    continue
                # Skip: research events
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
                        'source': source
                    })
            return out

        # Query both tables
        events_q = text("""
        SELECT e.id, e.person_id, p.nome_completo, e.event_type, e.event_date, e.description
        FROM events e LEFT JOIN pessoas p ON e.person_id = p.id
        """)
        rows_e = db.execute(events_q).fetchall()

        timeline = process_rows(rows_e, 'events')
        timeline.sort(key=lambda x: x['norm_date'])

        return jsonify(timeline)
    finally:
        db.close()
