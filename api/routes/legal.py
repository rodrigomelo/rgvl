"""
RGVL API - Legal routes
"""
from flask import Blueprint, jsonify, request
from api.db import get_session
from api.utils import model_to_dict, models_to_list

legal_bp = Blueprint('legal', __name__, url_prefix='/api/legal')


@legal_bp.route('/processes')
def get_processes():
    """Placeholder for legal processes — populated when court data is available."""
    return jsonify([])


@legal_bp.route('/summary')
def get_legal_summary():
    """Legal summary."""
    return jsonify({
        'total': 0,
        'note': 'Legal process data will be integrated from Escavador/TJMG sources.'
    })
