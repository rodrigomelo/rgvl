"""
RGVL API - Stats Endpoint Tests
"""
import json


class TestStatsEndpoint:
    """Tests for /api/stats endpoint"""

    def test_stats_returns_200(self, client):
        """Stats endpoint should return 200 OK"""
        response = client.get('/api/stats')
        assert response.status_code == 200

    def test_stats_returns_json(self, client):
        """Stats endpoint should return JSON"""
        response = client.get('/api/stats')
        assert response.content_type == 'application/json'

    def test_stats_contains_counts(self, client):
        """Stats endpoint should contain entity counts"""
        response = client.get('/api/stats')
        data = json.loads(response.data)
        
        # Should have counts for all entities
        expected_fields = ['pessoas', 'empresas', 'imoveis', 'processos', 'documentos']
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int), f"{field} should be an integer"

    def test_stats_all_fields_are_integers(self, client):
        """All stat fields should be integers"""
        response = client.get('/api/stats')
        data = json.loads(response.data)
        
        for key, value in data.items():
            assert isinstance(value, int), f"{key} should be an integer, got {type(value)}"

    def test_stats_non_negative(self, client):
        """All counts should be non-negative"""
        response = client.get('/api/stats')
        data = json.loads(response.data)
        
        for key, value in data.items():
            assert value >= 0, f"{key} should be non-negative"
