"""
RGVL API - Family routes
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import Pessoa, Relacionamento
from api.utils import model_to_dict, models_to_list

family_bp = Blueprint('family', __name__, url_prefix='/api/family')


@family_bp.route('/person/<int:person_id>')
def get_person(person_id):
    """Get a single person by ID."""
    db = get_session()
    try:
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        return jsonify(model_to_dict(person))
    finally:
        db.close()


@family_bp.route('/person/<int:person_id>/relatives')
def get_relatives(person_id):
    """Get all relatives of a person."""
    db = get_session()
    try:
        relationships = db.query(Relacionamento).filter(
            (Relacionamento.pessoa_de == person_id) |
            (Relacionamento.pessoa_para == person_id)
        ).all()

        results = []
        for rel in relationships:
            d = model_to_dict(rel)
            # Fetch the related person's name
            other_id = rel.pessoa_para if rel.pessoa_de == person_id else rel.pessoa_de
            other = db.query(Pessoa).filter(Pessoa.id == other_id).first()
            d['pessoa_nome'] = other.nome_completo if other else None
            d['pessoa_status'] = other.status if other else None
            results.append(d)

        return jsonify(results)
    finally:
        db.close()


@family_bp.route('/person/<int:person_id>/tree')
def get_tree(person_id):
    """Get a person and their direct family (parents, spouse, children, siblings)."""
    db = get_session()
    try:
        person = db.query(Pessoa).filter(Pessoa.id == person_id).first()
        if not person:
            return jsonify({'error': 'Person not found'}), 404

        result = model_to_dict(person)

        # Parents
        if person.pai_id:
            pai = db.query(Pessoa).filter(Pessoa.id == person.pai_id).first()
            result['pai'] = model_to_dict(pai)
        if person.mae_id:
            mae = db.query(Pessoa).filter(Pessoa.id == person.mae_id).first()
            result['mae'] = model_to_dict(mae)

        # Spouse
        if person.conjuge_id:
            conjuge = db.query(Pessoa).filter(Pessoa.id == person.conjuge_id).first()
            result['conjuge'] = model_to_dict(conjuge)

        # Children (people whose pai or mae is this person)
        children = db.query(Pessoa).filter(
            (Pessoa.pai_id == person_id) | (Pessoa.mae_id == person_id)
        ).all()
        result['filhos'] = models_to_list(children)

        # Siblings (people who share a parent)
        sibling_conditions = []
        if person.pai_id:
            sibling_conditions.append(Pessoa.pai_id == person.pai_id)
        if person.mae_id:
            sibling_conditions.append(Pessoa.mae_id == person.mae_id)

        if sibling_conditions:
            from sqlalchemy import or_
            siblings = db.query(Pessoa).filter(
                or_(*sibling_conditions),
                Pessoa.id != person_id
            ).all()
            result['irmaos'] = models_to_list(siblings)
        else:
            result['irmaos'] = []

        return jsonify(result)
    finally:
        db.close()


@family_bp.route('/generation/<int:gen>')
def get_by_generation(gen):
    """List all people in a given generation."""
    db = get_session()
    try:
        people = db.query(Pessoa).filter(Pessoa.geracao == gen).order_by(Pessoa.nome_completo).all()
        return jsonify(models_to_list(people))
    finally:
        db.close()


@family_bp.route('/summary')
def get_summary():
    """Family summary statistics."""
    db = get_session()
    try:
        total = db.query(Pessoa).count()
        by_gen = {}
        for gen in range(1, 7):
            count = db.query(Pessoa).filter(Pessoa.geracao == gen).count()
            if count > 0:
                by_gen[f'geracao_{gen}'] = count

        confirmed_rels = db.query(Relacionamento).filter(Relacionamento.confirmado == 1).count()
        speculative_rels = db.query(Relacionamento).filter(Relacionamento.confirmado == 0).count()

        return jsonify({
            'total_pessoas': total,
            'por_geracao': by_gen,
            'relacionamentos_confirmados': confirmed_rels,
            'relacionamentos_especulativos': speculative_rels,
        })
    finally:
        db.close()
