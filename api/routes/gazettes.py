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
                   page, title, url, tags, fonte
            FROM diarios_oficiais
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'source': r.source,
            'publication_date': r.publication_date,
            'edition': r.edition,
            'section': r.section,
            'page': r.page,
            'title': r.title,
            'url': r.url,
            'tags': r.tags,
            'fonte': r.fonte
        } for r in rows])
    finally:
        db.close()
