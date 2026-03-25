from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

searches_bp = Blueprint('searches', __name__)

@searches_bp.route('/searches', methods=['GET'])
def list_searches():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, fonte, query_usada, resultado, status,
                   data_busca, proxima_tentativa
            FROM buscas_realizadas
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'fonte': r.fonte,
            'query_usada': r.query_usada,
            'resultado': r.resultado,
            'status': r.status,
            'data_busca': r.data_busca,
            'proxima_tentativa': r.proxima_tentativa
        } for r in rows])
    finally:
        db.close()
