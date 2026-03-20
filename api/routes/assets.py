"""
RGVL API - Assets routes (companies, properties)
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import Empresa
from api.utils import model_to_dict, models_to_list

assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')


@assets_bp.route('/companies')
def get_companies():
    """List companies. Optional filter: ?person_id=X&status=ativa"""
    db = get_session()
    try:
        query = db.query(Empresa)

        person_id = request.args.get('person_id', type=int)
        if person_id:
            query = query.filter(Empresa.pessoa_id == person_id)

        status = request.args.get('status')
        if status:
            query = query.filter(Empresa.status_jucemg == status)

        companies = query.order_by(Empresa.nome_fantasia).all()
        return jsonify(models_to_list(companies))
    finally:
        db.close()


@assets_bp.route('/companies/<int:company_id>')
def get_company(company_id):
    """Get a single company by ID."""
    db = get_session()
    try:
        company = db.query(Empresa).filter(Empresa.id == company_id).first()
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        return jsonify(model_to_dict(company))
    finally:
        db.close()
