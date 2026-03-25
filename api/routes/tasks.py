from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
def list_tasks():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, tarefa, prioridade, pessoa_alvo,
                   fontes_sugeridas, status, resultado
            FROM tarefas_pesquisa
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'tarefa': r.tarefa,
            'prioridade': r.prioridade,
            'pessoa_alvo': r.pessoa_alvo,
            'fontes_sugeridas': r.fontes_sugeridas,
            'status': r.status,
            'resultado': r.resultado
        } for r in rows])
    finally:
        db.close()
