from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts', methods=['GET'])
def list_contacts():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, nome, role, empresa, telefone, email,
                   is_primary, notes, fonte
            FROM contatos
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'nome': r.nome,
            'role': r.role,
            'empresa': r.empresa,
            'telefone': r.telefone,
            'email': r.email,
            'is_primary': r.is_primary,
            'notes': r.notes,
            'fonte': r.fonte
        } for r in rows])
    finally:
        db.close()
