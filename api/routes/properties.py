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
                   registration, area_sqm, current_value, status, fonte
            FROM imoveis
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'property_type': r.property_type,
            'address': r.address,
            'city': r.city,
            'state': r.state,
            'neighborhood': r.neighborhood,
            'registration': r.registration,
            'area_sqm': r.area_sqm,
            'current_value': r.current_value,
            'status': r.status,
            'fonte': r.fonte
        } for r in rows])
    finally:
        db.close()
