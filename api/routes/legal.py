"""
RGVL API - Legal routes
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import ProcessoJudicial
from api.utils import model_to_dict, models_to_list

legal_bp = Blueprint('legal', __name__, url_prefix='/api/legal')


@legal_bp.route('/processes')
def get_processes():
    """List judicial processes. Optional filter: ?court=TJT3&status=andamento"""
    db = get_session()
    try:
        query = db.query(ProcessoJudicial)

        court = request.args.get('court')
        if court:
            query = query.filter(ProcessoJudicial.court.ilike(f'%{court}%'))

        status = request.args.get('status')
        if status:
            query = query.filter(ProcessoJudicial.status.ilike(f'%{status}%'))

        processos = query.order_by(ProcessoJudicial.collected_at.desc()).all()
        return jsonify(models_to_list(processos))
    finally:
        db.close()


@legal_bp.route('/processes/<int:process_id>')
def get_processo(process_id):
    """Get a single judicial process by ID."""
    db = get_session()
    try:
        processo = db.query(ProcessoJudicial).filter(ProcessoJudicial.id == process_id).first()
        if not processo:
            return jsonify({'error': 'Process not found'}), 404
        return jsonify(model_to_dict(processo))
    finally:
        db.close()


@legal_bp.route('/summary')
def get_legal_summary():
    """Legal summary."""
    from sqlalchemy import func
    db = get_session()
    try:
        total = db.query(ProcessoJudicial).count()
        by_court = dict(
            db.query(ProcessoJudicial.court, func.count(ProcessoJudicial.id))
            .group_by(ProcessoJudicial.court)
            .all()
        )
        return jsonify({
            'total': total,
            'by_court': by_court,
        })
    finally:
        db.close()
