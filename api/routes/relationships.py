from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

relationships_bp = Blueprint('relationships', __name__)

@relationships_bp.route('/relationships', methods=['GET'])
def list_relationships():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, person1_id, person2_id, relationship_type,
                   confirmed, source, notes
            FROM relationships
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'person1_id': r[1],
            'person2_id': r[2],
            'relationship_type': r[3],
            'confirmed': r[4],
            'source': r[5],
            'notes': r[6]
        } for r in rows])
    finally:
        db.close()
