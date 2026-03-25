"""
RGVL API - Legal Endpoints Tests
"""
import json


class TestLegalProcessosEndpoint:
    """Tests for /api/legal/processes endpoints"""

    def test_processos_returns_200(self, client):
        """Processos endpoint should return 200 OK"""
        response = client.get('/api/legal/processes')
        assert response.status_code == 200

    def test_processos_returns_json(self, client):
        """Processos endpoint should return JSON"""
        response = client.get('/api/legal/processes')
        assert response.content_type == 'application/json'

    def test_processos_returns_list(self, client):
        """Processos should return a list"""
        response = client.get('/api/legal/processes')
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))


class TestLegalSummaryEndpoint:
    """Tests for /api/legal/summary endpoint"""

    def test_summary_returns_200(self, client):
        """Legal summary should return 200 OK"""
        response = client.get('/api/legal/summary')
        assert response.status_code == 200

    def test_summary_returns_json(self, client):
        """Legal summary should return JSON"""
        response = client.get('/api/legal/summary')
        assert response.content_type == 'application/json'
