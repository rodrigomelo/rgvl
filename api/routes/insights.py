from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights', methods=['GET'])
def list_insights():
    db = get_session()
    try:
        rows = db.execute(text("SELECT id, category, title, description, source, tags FROM insights")).fetchall()
        return jsonify([{
            'id': r.id,
            'category': r.category,
            'title': r.title,
            'description': r.description,
            'source': r.source,
            'tags': r.tags
        } for r in rows])
    finally:
        db.close()
