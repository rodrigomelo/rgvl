"""
RGVL API - Legal routes
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import LegalCase
from api.utils import model_to_dict, models_to_list

legal_bp = Blueprint('legal', __name__, url_prefix='/api/legal')


@legal_bp.route('/processes')
def get_processes():
    """List judicial processes. Optional filter: ?court=TJMG&status=andamento"""
    db = get_session()
    try:
        query = db.query(LegalCase)

        court = request.args.get('court')
        if court:
            query = query.filter(LegalCase.court.ilike(f'%{court}%'))

        status = request.args.get('status')
        if status:
            query = query.filter(LegalCase.status.ilike(f'%{status}%'))

        cases = query.order_by(LegalCase.collected_at.desc()).all()
        return jsonify(models_to_list(cases))
    finally:
        db.close()


@legal_bp.route('/processes/<int:process_id>')
def get_case(process_id):
    """Get a single judicial case by ID."""
    db = get_session()
    try:
        case = db.query(LegalCase).filter(LegalCase.id == process_id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        return jsonify(model_to_dict(case))
    finally:
        db.close()


@legal_bp.route('/summary')
def get_legal_summary():
    """Legal summary."""
    from sqlalchemy import func
    db = get_session()
    try:
        total = db.query(LegalCase).count()
        by_court = dict(
            db.query(LegalCase.court, func.count(LegalCase.id))
            .group_by(LegalCase.court)
            .all()
        )
        return jsonify({
            'total': total,
            'by_court': by_court,
        })
    finally:
        db.close()
