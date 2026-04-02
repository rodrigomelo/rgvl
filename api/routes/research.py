"""
RGVL API - Research routes (searches, tasks, documents, contacts)
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from api.db import get_session
from api.models import SearchHistory, ResearchTask, Document, Contact
from api.utils import models_to_list, priority_filter_values, status_filter_values

research_bp = Blueprint('research', __name__, url_prefix='/api/research')


@research_bp.route('/searches')
def get_searches():
    """List search history. Optional: ?source=FamilySearch&status=success"""
    db = get_session()
    try:
        query = db.query(SearchHistory)

        source = request.args.get('source')
        if source:
            query = query.filter(SearchHistory.source == source)

        status = request.args.get('status')
        if status:
            query = query.filter(
                func.lower(SearchHistory.status).in_(status_filter_values(status))
            )

        searches = query.order_by(SearchHistory.search_date.desc()).limit(100).all()
        return jsonify(models_to_list(searches))
    finally:
        db.close()


@research_bp.route('/tasks')
def get_tasks():
    """List research tasks. Optional: ?status=pending&priority=high"""
    db = get_session()
    try:
        query = db.query(ResearchTask)

        status = request.args.get('status')
        if status:
            query = query.filter(
                func.lower(ResearchTask.status).in_(status_filter_values(status))
            )

        priority = request.args.get('priority')
        if priority:
            query = query.filter(
                func.lower(ResearchTask.priority).in_({value.lower() for value in priority_filter_values(priority)})
            )

        tasks = query.order_by(ResearchTask.created_at.desc()).all()
        return jsonify(models_to_list(tasks))
    finally:
        db.close()


@research_bp.route('/documents')
def get_documents():
    """List documents. Optional: ?type=cpf"""
    db = get_session()
    try:
        query = db.query(Document)

        doc_type = request.args.get('type')
        if doc_type:
            query = query.filter(Document.doc_type == doc_type)

        docs = query.order_by(Document.collected_at.desc()).all()
        return jsonify(models_to_list(docs))
    finally:
        db.close()


@research_bp.route('/contacts')
def get_contacts():
    """List contacts. Optional: ?role=Lawyer"""
    db = get_session()
    try:
        query = db.query(Contact)

        role = request.args.get('role')
        if role:
            query = query.filter(Contact.role.ilike(f'%{role}%'))

        contacts = query.order_by(Contact.is_primary.desc(), Contact.name).all()
        return jsonify(models_to_list(contacts))
    finally:
        db.close()
