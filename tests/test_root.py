"""
RGVL API - Root Endpoint Tests
"""
import json


class TestRootEndpoint:
    """Tests for / (root) endpoint"""

    def test_root_returns_200(self, client):
        """Root endpoint should return 200 OK"""
        response = client.get('/')
        assert response.status_code == 200

    def test_root_returns_json(self, client):
        """Root endpoint should return JSON"""
        response = client.get('/')
        assert response.content_type == 'application/json'

    def test_root_contains_name(self, client):
        """Root should contain API name"""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'name' in data
        assert 'RGVL' in data['name']

    def test_root_contains_version(self, client):
        """Root should contain version"""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'version' in data

    def test_root_contains_endpoints(self, client):
        """Root should contain endpoints"""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'endpoints' in data
