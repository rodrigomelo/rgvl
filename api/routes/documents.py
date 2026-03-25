from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents', methods=['GET'])
def list_documents():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, doc_type, title, description, file_path,
                   issue_date, expiry_date, fonte
            FROM documentos
        """)).fetchall()
        return jsonify([{
            'id': r.id,
            'doc_type': r.doc_type,
            'title': r.title,
            'description': r.description,
            'file_path': r.file_path,
            'issue_date': r.issue_date,
            'expiry_date': r.expiry_date,
            'fonte': r.fonte
        } for r in rows])
    finally:
        db.close()
