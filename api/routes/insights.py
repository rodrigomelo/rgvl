from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights', methods=['GET'])
def list_insights():
    db = get_session()
    try:
        rows = db.execute(text("SELECT id, category, title, description, source FROM research_insights")).fetchall()
        return jsonify([{
            'id': r[0],
            'category': r[1],
            'title': r[2],
            'description': r[3],
            'source': r[4]
        } for r in rows])
    finally:
        db.close()
