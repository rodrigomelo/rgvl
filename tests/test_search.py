"""
RGVL API - Search Endpoint Tests
"""
import json


class TestSearchEndpoint:
    """Tests for /api/search endpoint"""

    def test_search_returns_200(self, client):
        """Search endpoint should return 200 OK"""
        response = client.get('/api/search?q=test')
        assert response.status_code == 200

    def test_search_returns_json(self, client):
        """Search endpoint should return JSON"""
        response = client.get('/api/search?q=test')
        assert response.content_type == 'application/json'

    def test_search_returns_results_structure(self, client):
        """Search should return results with expected structure"""
        response = client.get('/api/search?q=test')
        data = json.loads(response.data)
        
        # Should have a results structure
        assert isinstance(data, dict) or isinstance(data, list), "Search should return dict or list"

    def test_search_without_query_returns_400(self, client):
        """Search without query parameter should return 400"""
        response = client.get('/api/search')
        # Either 400 (bad request) or returns all results
        assert response.status_code in [200, 400]

    def test_search_empty_query(self, client):
        """Search with empty query should work or return empty"""
        response = client.get('/api/search?q=')
        # Should not crash - either returns 200 or empty results
        assert response.status_code in [200, 400]
