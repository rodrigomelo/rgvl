"""
RGVL API Tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "RGVL" in response.json()["service"]

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "persons" in data
    assert "companies" in data

def test_person():
    response = client.get("/api/person")
    assert response.status_code == 200
    data = response.json()
    assert "full_name" in data

def test_spouse():
    response = client.get("/api/spouse")
    assert response.status_code == 200

def test_siblings():
    response = client.get("/api/siblings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_nephews():
    response = client.get("/api/nephews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_children():
    response = client.get("/api/children")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_companies():
    response = client.get("/api/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_properties():
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_net_worth():
    response = client.get("/api/net-worth")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "properties" in data
    assert "companies" in data

def test_contacts():
    response = client.get("/api/contacts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_legal_processes():
    response = client.get("/api/legal/processes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_notes():
    response = client.get("/api/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_family_summary():
    response = client.get("/api/family/summary")
    assert response.status_code == 200
    data = response.json()
    assert "person" in data
    assert "spouse" in data
    assert "siblings" in data

def test_search():
    response = client.get("/api/search?q=Rodrigo")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_search_short():
    response = client.get("/api/search?q=R")
    assert response.status_code == 422  # Validation error
