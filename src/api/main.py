"""
Legacy RGVL FastAPI prototype.

This module is retained for historical reference only.
The supported runtime is the Flask application in api/main.py.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.entity import (
    Person, Spouse, Sibling, Nephew, Child, Company,
    Property, Contact, Document, LegalProcess, Note, Event, OfficialGazette
)
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime
from typing import Optional, List
import json

# ============ Helpers ============

def to_dict(obj):
    """Convert SQLAlchemy object to dictionary"""
    if obj is None:
        return None
    d = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            d[column.name] = value.isoformat()
        elif isinstance(value, str) and value.startswith('['):
            try:
                d[column.name] = json.loads(value)
            except:
                d[column.name] = value
        else:
            d[column.name] = value
    return d

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Keep session open for response

# ============ App ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 RGVL API starting...")
    yield
    # Shutdown
    print("👋 RGVL API shutting down...")

app = FastAPI(
    title="RGVL Data API",
    description="Personal data platform for family history and research",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Health & Info ============

@app.get("/")
async def root():
    return {
        "service": "RGVL Data API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    db = get_db()
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except:
        db_connected = False
    
    tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database_connected": db_connected,
        "database_exists": True,
        "database": str(engine.url),
        "database_tables": len(tables),
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/stats")
async def stats():
    db = get_db()
    return {
        "persons": db.query(Person).count(),
        "spouses": db.query(Spouse).count(),
        "siblings": db.query(Sibling).count(),
        "nephews": db.query(Nephew).count(),
        "children": db.query(Child).count(),
        "companies": db.query(Company).count(),
        "properties": db.query(Property).count(),
        "contacts": db.query(Contact).count(),
        "documents": db.query(Document).count(),
        "legal_processes": db.query(LegalProcess).count(),
        "notes": db.query(Note).count(),
        "events": db.query(Event).count() if 'events' in [t[0] for t in db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()] else 0
    }

# ============ Person ============

@app.get("/api/person")
async def get_person():
    db = get_db()
    person = db.query(Person).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return to_dict(person)

@app.post("/api/person")
@app.put("/api/person")
async def update_person(data: dict):
    db = get_db()
    person = db.query(Person).first()
    if not person:
        person = Person()
        db.add(person)
    
    for key, value in data.items():
        if hasattr(person, key):
            setattr(person, key, value)
    
    person.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(person)
    return to_dict(person)

# ============ Spouse ============

@app.get("/api/spouse")
async def get_spouse():
    db = get_db()
    spouse = db.query(Spouse).first()
    return to_dict(spouse) if spouse else None

# ============ Siblings ============

@app.get("/api/siblings")
async def get_siblings():
    db = get_db()
    siblings = db.query(Sibling).all()
    return [to_dict(s) for s in siblings]

# ============ Nephews ============

@app.get("/api/nephews")
async def get_nephews():
    db = get_db()
    nephews = db.query(Nephew).order_by(Nephew.name).all()
    return [to_dict(n) for n in nephews]

# ============ Children ============

@app.get("/api/children")
async def get_children():
    db = get_db()
    children = db.query(Child).order_by(Child.name).all()
    return [to_dict(c) for c in children]

# ============ Family Summary ============

@app.get("/api/family/summary")
async def family_summary():
    db = get_db()
    person = db.query(Person).first()
    spouse = db.query(Spouse).first()
    siblings = db.query(Sibling).all()
    nephews = db.query(Nephew).all()
    children = db.query(Child).all()
    
    return {
        "person": to_dict(person),
        "spouse": to_dict(spouse),
        "siblings": {
            "total": len(siblings),
            "list": [to_dict(s) for s in siblings]
        },
        "children": {
            "total": len(children),
            "list": [to_dict(c) for c in children]
        },
        "nephews": {
            "total": len(nephews),
            "list": [to_dict(n) for n in nephews]
        }
    }

# ============ Companies ============

@app.get("/api/companies")
async def get_companies():
    db = get_db()
    companies = db.query(Company).order_by(Company.trade_name).all()
    return [to_dict(c) for c in companies]

@app.get("/api/companies/{company_id}")
async def get_company(company_id: int):
    db = get_db()
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return to_dict(company)

# ============ Properties ============

@app.get("/api/properties")
async def get_properties():
    db = get_db()
    properties = db.query(Property).order_by(Property.address).all()
    return [to_dict(p) for p in properties]

@app.get("/api/properties/{property_id}")
async def get_property(property_id: int):
    db = get_db()
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return to_dict(prop)

# ============ Net Worth ============

@app.get("/api/net-worth")
async def net_worth():
    db = get_db()
    
    # Properties
    properties = db.query(Property).filter(Property.current_value.isnot(None)).all()
    total_properties = sum(p.current_value for p in properties if p.current_value)
    
    # Companies
    companies = db.query(Company).filter(Company.capital.isnot(None)).all()
    total_companies = sum(c.capital for c in companies if c.capital)
    
    return {
        "properties": {
            "total": len(properties),
            "value": total_properties,
            "details": [
                {
                    "address": p.address,
                    "value": p.current_value,
                    "type": p.property_type
                }
                for p in properties
            ]
        },
        "companies": {
            "total": len(companies),
            "capital": total_companies,
            "details": [
                {
                    "name": c.trade_name or c.legal_name,
                    "capital": c.capital,
                    "status": c.status
                }
                for c in companies
            ]
        },
        "total": total_properties + total_companies
    }

# ============ Contacts ============

@app.get("/api/contacts")
async def get_contacts():
    db = get_db()
    contacts = db.query(Contact).order_by(Contact.name).all()
    return [to_dict(c) for c in contacts]

# ============ Documents ============

@app.get("/api/documents")
async def get_documents(doc_type: Optional[str] = None):
    db = get_db()
    query = db.query(Document)
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    docs = query.all()
    return [to_dict(d) for d in docs]

# ============ Legal Processes ============

@app.get("/api/legal/processes")
async def get_legal_processes(court: Optional[str] = None):
    db = get_db()
    query = db.query(LegalProcess)
    if court:
        query = query.filter(LegalProcess.court == court)
    processes = query.order_by(LegalProcess.process_number).all()
    return [to_dict(p) for p in processes]

@app.get("/api/legal/summary")
async def legal_summary():
    db = get_db()
    processes = db.query(LegalProcess).all()
    
    by_court = {}
    for p in processes:
        if p.court not in by_court:
            by_court[p.court] = 0
        by_court[p.court] += 1
    
    return {
        "total": len(processes),
        "by_court": by_court
    }

# ============ Notes ============

@app.get("/api/notes")
async def get_notes(category: Optional[str] = None):
    db = get_db()
    query = db.query(Note)
    if category:
        query = query.filter(Note.category == category)
    notes = query.order_by(Note.collected_at.desc()).all()
    return [to_dict(n) for n in notes]

# ============ Events ============

@app.get("/api/events")
async def get_events():
    db = get_db()
    try:
        events = db.execute(text("SELECT * FROM events ORDER BY date DESC")).fetchall()
        columns = ['id', 'title', 'description', 'date', 'category', 'person_id', 'collected_at']
        return [dict(zip(columns, e)) for e in events]
    except:
        return []

# ============ Search ============

@app.get("/api/search")
async def search(q: str = Query(..., min_length=2)):
    db = get_db()
    results = []
    
    # Search in persons
    persons = db.query(Person).filter(
        Person.full_name.ilike(f"%{q}%")
    ).all()
    for p in persons:
        results.append({"type": "person", "name": p.full_name, "id": p.id})
    
    # Search in siblings
    siblings = db.query(Sibling).filter(
        Sibling.name.ilike(f"%{q}%")
    ).all()
    for s in siblings:
        results.append({"type": "sibling", "name": s.name, "id": s.id})
    
    # Search in nephews
    nephews = db.query(Nephew).filter(
        Nephew.name.ilike(f"%{q}%")
    ).all()
    for n in nephews:
        results.append({"type": "nephew", "name": n.name, "id": n.id})
    
    # Search in companies
    companies = db.query(Company).filter(
        Company.trade_name.ilike(f"%{q}%") | 
        Company.legal_name.ilike(f"%{q}%")
    ).all()
    for c in companies:
        results.append({"type": "company", "name": c.trade_name or c.legal_name, "id": c.id})
    
    return {"query": q, "results": results, "total": len(results)}

# ============ Main ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5003)
