"""
RGVL API - Assets routes (companies, properties)
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.models import Company, Property
from api.utils import model_to_dict, models_to_list

assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')


# ============ Companies ============

@assets_bp.route('/companies')
def get_companies():
    """List companies. Optional filter: ?person_id=X&status=ativa"""
    db = get_session()
    try:
        query = db.query(Company)

        person_id = request.args.get('person_id', type=int)
        if person_id:
            query = query.filter(Company.person_id == person_id)

        status = request.args.get('status')
        if status:
            query = query.filter(Company.registration_status == status)

        companies = query.order_by(Company.trade_name).all()
        return jsonify(models_to_list(companies))
    finally:
        db.close()


@assets_bp.route('/companies/<int:company_id>')
def get_company(company_id):
    """Get a single company by ID."""
    db = get_session()
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        return jsonify(model_to_dict(company))
    finally:
        db.close()


# ============ Properties ============

@assets_bp.route('/properties')
def get_properties():
    """List real estate properties. Optional filter: ?city=X&status=paid_off&owner=NAME"""
    db = get_session()
    try:
        query = db.query(Property)

        city = request.args.get('city')
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))

        status = request.args.get('status')
        if status:
            query = query.filter(Property.status == status)

        owner = request.args.get('owner')
        if owner:
            query = query.filter(Property.owners.ilike(f'%{owner}%'))

        properties = query.order_by(Property.address).all()
        return jsonify(models_to_list(properties))
    finally:
        db.close()


@assets_bp.route('/properties/<int:property_id>')
def get_property(property_id):
    """Get a single property by ID."""
    db = get_session()
    try:
        prop = db.query(Property).filter(Property.id == property_id).first()
        if not prop:
            return jsonify({'error': 'Property not found'}), 404
        return jsonify(model_to_dict(prop))
    finally:
        db.close()
