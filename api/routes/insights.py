from flask import Blueprint, jsonify
from api.db import get_session
from api.models import Insight

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights', methods=['GET'])
def list_insights():
    db = get_session()
    try:
        insights = db.query(Insight).all()
        return jsonify([{
            'id': i.id,
            'category': i.category,
            'title': i.title,
            'description': i.description,
            'source': i.source,
            'tags': i.tags
        } for i in insights])
    finally:
        db.close()
