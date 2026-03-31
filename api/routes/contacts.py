from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts', methods=['GET'])
def list_contacts():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, name, role, company, phone, email,
                   is_primary, notes, source
            FROM contacts
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'name': r[1],
            'role': r[2],
            'company': r[3],
            'phone': r[4],
            'email': r[5],
            'is_primary': r[6],
            'notes': r[7],
            'source': r[8]
        } for r in rows])
    finally:
        db.close()
