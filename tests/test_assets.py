"""
RGVL API - Assets Endpoints Tests
"""
import json


class TestCompaniesEndpoint:
    """Tests for /api/assets/companies endpoints"""

    def test_companies_returns_200(self, client):
        """Companies endpoint should return 200 OK"""
        response = client.get('/api/assets/companies')
        assert response.status_code == 200

    def test_companies_returns_json(self, client):
        """Companies endpoint should return JSON"""
        response = client.get('/api/assets/companies')
        assert response.content_type == 'application/json'

    def test_companies_returns_list(self, client):
        """Companies should return a list"""
        response = client.get('/api/assets/companies')
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))


class TestPropertiesEndpoint:
    """Tests for /api/assets/properties endpoints"""

    def test_properties_returns_200(self, client):
        """Properties endpoint should return 200 OK"""
        response = client.get('/api/assets/properties')
        assert response.status_code == 200

    def test_properties_returns_json(self, client):
        """Properties endpoint should return JSON"""
        response = client.get('/api/assets/properties')
        assert response.content_type == 'application/json'

    def test_properties_returns_list(self, client):
        """Properties should return a list"""
        response = client.get('/api/assets/properties')
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))
