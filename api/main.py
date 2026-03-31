"""
RGVL API - Main application
Flask REST API for the Lanna family research platform.
Runs on port 5003.
"""
import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db import engine, DB_PATH
from api.models import Base
from api.auth import require_auth, get_token_from_header, verify_token

# Create all tables
Base.metadata.create_all(bind=engine)

# App
app = Flask(__name__)
# CORS is handled manually
@app.after_request
def add_cors_headers(response):
    # Allow any origin for development (restrict in production)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

# Public routes that don't require auth
PUBLIC_ROUTES = ['/', '/api/health', '/api/stats', '/api/search']

@app.before_request
def check_auth():
    """Check if route requires authentication"""
    from flask import request, jsonify, g
    
    # Always allow OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return None
    
    # Skip auth for public routes
    if request.path in PUBLIC_ROUTES:
        return None
    
    # Skip if it's not an API route
    if not request.path.startswith('/api/'):
        return None
    
    # Skip auth if AUTH_DISABLED is set (for development/testing)
    if os.getenv('AUTH_DISABLED', 'false').lower() == 'true':
        import warnings
        warnings.warn('AUTH DISABLED - DO NOT USE IN PRODUCTION')
        return None
    
    # Check for token
    token = get_token_from_header()
    
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    # Verify token using Auth0 userinfo endpoint
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    # Store user in request context
    g.user = payload
    return None

# Register blueprints
from api.routes.family import family_bp
from api.routes.assets import assets_bp
from api.routes.legal import legal_bp
from api.routes.contacts import contacts_bp
from api.routes.documents import documents_bp
from api.routes.gazettes import gazettes_bp
from api.routes.tasks import tasks_bp
from api.routes.searches import searches_bp
from api.routes.relationships import relationships_bp
from api.routes.research import research_bp
from api.routes.sources import sources_bp
from api.routes.insights import insights_bp
from api.routes.properties import properties_bp

app.register_blueprint(family_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(research_bp)
app.register_blueprint(sources_bp)
app.register_blueprint(insights_bp, url_prefix='/api')
app.register_blueprint(properties_bp, url_prefix='/api')
app.register_blueprint(contacts_bp, url_prefix='/api')
app.register_blueprint(documents_bp, url_prefix='/api')
app.register_blueprint(gazettes_bp, url_prefix='/api')
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(searches_bp, url_prefix='/api')
app.register_blueprint(relationships_bp, url_prefix='/api')


# ============ Root ============

@app.route('/')
def root():
    return jsonify({
        'name': 'RGVL Data API',
        'version': '5.0.0',
        'status': 'running',
        'database': str(DB_PATH),
        'endpoints': {
            'family': {
                'person': '/api/family/person/<id>',
                'relatives': '/api/family/person/<id>/relatives',
                'tree': '/api/family/person/<id>/tree',
                'generation': '/api/family/generation/<n>',
                'summary': '/api/family/summary',
                'events': '/api/family/events',
            },
            'assets': {
                'companies': '/api/assets/companies',
                'company': '/api/assets/companies/<id>',
                'properties': '/api/assets/properties',
                'property': '/api/assets/properties/<id>',
            },
            'legal': {
                'processes': '/api/legal/processes',
                'process': '/api/legal/processes/<id>',
                'summary': '/api/legal/summary',
            },
            'research': {
                'searches': '/api/research/searches',
                'tasks': '/api/research/tasks',
                'documents': '/api/research/documents',
                'contacts': '/api/research/contacts',
            },
            'sources': {
                'summary': '/api/sources/summary',
                'person': '/api/sources/person/<id>',
                'timeline': '/api/sources/timeline',
            },
            'system': {
                'health': '/api/health',
                'stats': '/api/stats',
                'search': '/api/search?q=',
            },
        }
    })


# ============ Health ============

@app.route('/api/health')
def health():
    import sqlite3
    from datetime import datetime, timezone

    db_ok = False
    db_tables = 0
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        db_tables = cursor.fetchone()[0]
        conn.close()
        db_ok = True
    except Exception:
        pass

    return jsonify({
        'status': 'healthy' if db_ok else 'degraded',
        'database': str(DB_PATH),
        'database_exists': DB_PATH.exists(),
        'database_connected': db_ok,
        'database_tables': db_tables,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '5.0.0'
    })


# ============ Stats ============

@app.route('/api/stats')
def get_stats():
    from api.db import get_session
    from api.models import Person, Relationship, Company, Property, LegalCase, Document, Contact, TimelineEvent, SearchHistory, ResearchTask

    db = get_session()
    try:
        return jsonify({
            'people': db.query(Person).count(),
            'relationships': db.query(Relationship).count(),
            'companies': db.query(Company).count(),
            'properties': db.query(Property).count(),
            'legal_cases': db.query(LegalCase).count(),
            'documents': db.query(Document).count(),
            'events': db.query(TimelineEvent).count(),
            'contacts': db.query(Contact).count(),
            'searches': db.query(SearchHistory).count(),
            'tasks': db.query(ResearchTask).count(),
            'tasks_pending': db.query(ResearchTask).filter(
                ResearchTask.status == 'pendente'
            ).count(),
        })
    finally:
        db.close()


# ============ Global Search ============

@app.route('/api/search')
def global_search():
    """Full-text search across people, companies, and tasks."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'error': 'Query parameter q is required'}), 400

    from api.db import get_session
    from api.models import Person, Company, ResearchTask, Property

    db = get_session()
    try:
        like = f'%{q}%'

        people = db.query(Person).filter(
            (Person.full_name.ilike(like)) |
            (Person.company.ilike(like)) |
            (Person.notes.ilike(like))
        ).limit(20).all()

        companies = db.query(Company).filter(
            (Company.trade_name.ilike(like)) |
            (Company.legal_name.ilike(like)) |
            (Company.cnpj.ilike(like))
        ).limit(20).all()

        tasks = db.query(ResearchTask).filter(
            (ResearchTask.task.ilike(like)) |
            (ResearchTask.target_person.ilike(like))
        ).limit(20).all()

        properties = db.query(Property).filter(
            (Property.address.ilike(like)) |
            (Property.building_name.ilike(like)) |
            (Property.neighborhood.ilike(like)) |
            (Property.owners.ilike(like))
        ).limit(20).all()

        from api.utils import model_to_dict
        return jsonify({
            'query': q,
            'results': {
                'people': [model_to_dict(p) for p in people],
                'companies': [model_to_dict(c) for c in companies],
                'tasks': [model_to_dict(t) for t in tasks],
                'properties': [model_to_dict(p) for p in properties],
            },
            'total': len(people) + len(companies) + len(tasks) + len(properties),
        })
    finally:
        db.close()


# ============ Run ============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    print(f'🔨 RGVL API starting on port {port}')
    print(f'📦 Database: {DB_PATH}')
    app.run(host='0.0.0.0', port=port, debug=False)
