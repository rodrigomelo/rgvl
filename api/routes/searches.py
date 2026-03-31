from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

searches_bp = Blueprint('searches', __name__)

@searches_bp.route('/searches', methods=['GET'])
def list_searches():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, source, query_used, result, status,
                   search_date, next_attempt
            FROM search_history
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'source': r[1],
            'query_used': r[2],
            'result': r[3],
            'status': r[4],
            'search_date': r[5],
            'next_attempt': r[6]
        } for r in rows])
    finally:
        db.close()
