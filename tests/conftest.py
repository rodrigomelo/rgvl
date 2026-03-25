"""
RGVL API - Test Suite Configuration
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ['AUTH_DISABLED'] = 'true'
os.environ['FLASK_ENV'] = 'testing'

import pytest
from api.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """Headers with disabled auth for testing"""
    return {'Content-Type': 'application/json'}
