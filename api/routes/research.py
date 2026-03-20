"""
RGVL API - Research routes (searches, tasks)
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import BuscaRealizada, TarefaPesquisa, Pessoa
from api.utils import model_to_dict, models_to_list

research_bp = Blueprint('research', __name__, url_prefix='/api/research')


@research_bp.route('/searches')
def get_searches():
    """List search history. Optional: ?fonte=FamilySearch&status=sucesso"""
    db = get_session()
    try:
        query = db.query(BuscaRealizada)

        fonte = request.args.get('fonte')
        if fonte:
            query = query.filter(BuscaRealizada.fonte == fonte)

        status = request.args.get('status')
        if status:
            query = query.filter(BuscaRealizada.status == status)

        searches = query.order_by(BuscaRealizada.data_busca.desc()).limit(100).all()
        return jsonify(models_to_list(searches))
    finally:
        db.close()


@research_bp.route('/tasks')
def get_tasks():
    """List research tasks. Optional: ?status=pendente&prioridade=ALTA"""
    db = get_session()
    try:
        query = db.query(TarefaPesquisa)

        status = request.args.get('status')
        if status:
            query = query.filter(TarefaPesquisa.status == status)

        prioridade = request.args.get('prioridade')
        if prioridade:
            query = query.filter(TarefaPesquisa.prioridade == prioridade)

        tasks = query.order_by(TarefaPesquisa.created_at.desc()).all()
        return jsonify(models_to_list(tasks))
    finally:
        db.close()
