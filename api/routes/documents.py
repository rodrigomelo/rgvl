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
                   issue_date, expiry_date, source
            FROM documents
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'doc_type': r[1],
            'title': r[2],
            'description': r[3],
            'file_path': r[4],
            'issue_date': r[5],
            'expiry_date': r[6],
            'source': r[7]
        } for r in rows])
    finally:
        db.close()
