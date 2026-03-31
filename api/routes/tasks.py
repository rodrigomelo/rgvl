from flask import Blueprint, jsonify
from api.db import get_session
from sqlalchemy import text

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
def list_tasks():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT id, task, priority, target_person,
                   suggested_sources, status, result
            FROM research_tasks
        """)).fetchall()
        return jsonify([{
            'id': r[0],
            'task': r[1],
            'priority': r[2],
            'target_person': r[3],
            'suggested_sources': r[4],
            'status': r[5],
            'result': r[6]
        } for r in rows])
    finally:
        db.close()
