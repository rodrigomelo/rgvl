from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

properties_bp = Blueprint('properties', __name__)

@properties_bp.route('/properties', methods=['GET'])
def list_properties():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, property_type, address, city, state, neighborhood,
                   registration, area_sqm, current_value, status, source
            FROM properties
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'property_type': r[1],
            'address': r[2],
            'city': r[3],
            'state': r[4],
            'neighborhood': r[5],
            'registration': r[6],
            'area_sqm': r[7],
            'current_value': r[8],
            'status': r[9],
            'source': r[10]
        } for r in rows])
    finally:
        db.close()
