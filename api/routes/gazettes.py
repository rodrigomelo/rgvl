from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

gazettes_bp = Blueprint('gazettes', __name__)

@gazettes_bp.route('/gazettes', methods=['GET'])
def list_gazettes():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, source, publication_date, edition, section,
                   page, title, url, tags, data_source
            FROM official_gazettes
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'source': r[1],
            'publication_date': r[2],
            'edition': r[3],
            'section': r[4],
            'page': r[5],
            'title': r[6],
            'url': r[7],
            'tags': r[8],
            'data_source': r[9]
        } for r in rows])
    finally:
        db.close()
