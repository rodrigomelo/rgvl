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

# Create all tables
Base.metadata.create_all(bind=engine)

# App
app = Flask(__name__)
CORS(app)

# Register blueprints
from api.routes.family import family_bp
from api.routes.assets import assets_bp
from api.routes.legal import legal_bp
from api.routes.research import research_bp
from api.routes.sources import sources_bp

app.register_blueprint(family_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(research_bp)
app.register_blueprint(sources_bp)


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
    from api.models import Pessoa, Relacionamento, Empresa, Imovel, ProcessoJudicial, Documento, Contato, Evento, BuscaRealizada, TarefaPesquisa

    db = get_session()
    try:
        return jsonify({
            'pessoas': db.query(Pessoa).count(),
            'relacionamentos': db.query(Relacionamento).count(),
            'empresas': db.query(Empresa).count(),
            'imoveis': db.query(Imovel).count(),
            'processos': db.query(ProcessoJudicial).count(),
            'documentos': db.query(Documento).count(),
            'eventos': db.query(Evento).count(),
            'contatos': db.query(Contato).count(),
            'buscas': db.query(BuscaRealizada).count(),
            'tarefas': db.query(TarefaPesquisa).count(),
            'tarefas_pendentes': db.query(TarefaPesquisa).filter(
                TarefaPesquisa.status == 'pendente'
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
    from api.models import Pessoa, Empresa, TarefaPesquisa, Imovel

    db = get_session()
    try:
        like = f'%{q}%'

        people = db.query(Pessoa).filter(
            (Pessoa.nome_completo.ilike(like)) |
            (Pessoa.empresa.ilike(like)) |
            (Pessoa.observacoes.ilike(like))
        ).limit(20).all()

        companies = db.query(Empresa).filter(
            (Empresa.nome_fantasia.ilike(like)) |
            (Empresa.razao_social.ilike(like)) |
            (Empresa.cnpj.ilike(like))
        ).limit(20).all()

        tasks = db.query(TarefaPesquisa).filter(
            (TarefaPesquisa.tarefa.ilike(like)) |
            (TarefaPesquisa.pessoa_alvo.ilike(like))
        ).limit(20).all()

        properties = db.query(Imovel).filter(
            (Imovel.address.ilike(like)) |
            (Imovel.building_name.ilike(like)) |
            (Imovel.neighborhood.ilike(like)) |
            (Imovel.owners.ilike(like))
        ).limit(20).all()

        from api.utils import model_to_dict
        return jsonify({
            'query': q,
            'results': {
                'pessoas': [model_to_dict(p) for p in people],
                'empresas': [model_to_dict(c) for c in companies],
                'tarefas': [model_to_dict(t) for t in tasks],
                'imoveis': [model_to_dict(p) for p in properties],
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
