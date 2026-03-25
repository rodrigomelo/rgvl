"""
RGVL API - Health Endpoint Tests
"""
import json


class TestHealthEndpoint:
    """Tests for /api/health endpoint"""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK"""
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON"""
        response = client.get('/api/health')
        assert response.content_type == 'application/json'

    def test_health_contains_status(self, client):
        """Health endpoint should contain status field"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded']

    def test_health_contains_database_info(self, client):
        """Health endpoint should contain database info"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'database' in data
        assert 'database_connected' in data
        assert 'database_tables' in data

    def test_health_contains_version(self, client):
        """Health endpoint should contain version"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'version' in data

    def test_health_contains_timestamp(self, client):
        """Health endpoint should contain timestamp"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'timestamp' in data
