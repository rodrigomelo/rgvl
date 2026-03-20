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

        # Recursive ancestor helper
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

        # Get children via relationships
        child_rels = db.query(Relacionamento).filter(
            Relacionamento.pessoa_de == person_id,
            Relacionamento.tipo.in_(['filho', 'filha'])
        ).all()
        child_ids = [r.pessoa_para for r in child_rels]
        children_map = {p.id: p for p in db.query(Pessoa).filter(Pessoa.id.in_(child_ids)).all()} if child_ids else {}
        children = [model_to_dict(children_map[cid]) for cid in child_ids if cid in children_map]

        # Get siblings via same parents (pai_id or mae_id)
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
    """Get all people in a given generation (1=cousins, 2=RGVL, 3=parents/siblings, 4=grandparents, 5=great-grandparents)."""
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
