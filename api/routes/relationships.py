from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

relationships_bp = Blueprint('relationships', __name__)

@relationships_bp.route('/relationships', methods=['GET'])
def list_relationships():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, pessoa_de, pessoa_para, tipo,
                   confirmado, fonte, observacao
            FROM relacionamentos
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'pessoa_de': r.pessoa_de,
            'pessoa_para': r.pessoa_para,
            'tipo': r.tipo,
            'confirmado': r.confirmado,
            'fonte': r.fonte,
            'observacao': r.observacao
        } for r in rows])
    finally:
        db.close()
