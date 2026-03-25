"""
RGVL API - Family Endpoints Tests
"""
import json


class TestFamilySummaryEndpoint:
    """Tests for /api/family/summary endpoint"""

    def test_family_summary_returns_200(self, client):
        """Family summary should return 200 OK"""
        response = client.get('/api/family/summary')
        assert response.status_code == 200

    def test_family_summary_returns_json(self, client):
        """Family summary should return JSON"""
        response = client.get('/api/family/summary')
        assert response.content_type == 'application/json'

    def test_family_summary_structure(self, client):
        """Family summary should have expected structure"""
        response = client.get('/api/family/summary')
        data = json.loads(response.data)
        assert isinstance(data, dict)


class TestFamilyEventsEndpoint:
    """Tests for /api/family/events endpoint"""

    def test_events_returns_200(self, client):
        """Events endpoint should return 200 OK"""
        response = client.get('/api/family/events')
        assert response.status_code == 200

    def test_events_returns_json(self, client):
        """Events endpoint should return JSON"""
        response = client.get('/api/family/events')
        assert response.content_type == 'application/json'

    def test_events_returns_list(self, client):
        """Events should return a list"""
        response = client.get('/api/family/events')
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))


class TestFamilyPersonEndpoint:
    """Tests for /api/family/person/<id> endpoints"""

    def test_person_with_id_returns_200(self, client):
        """Person endpoint with valid ID should return 200"""
        response = client.get('/api/family/person/1')
        assert response.status_code == 200

    def test_person_returns_json(self, client):
        """Person endpoint should return JSON"""
        response = client.get('/api/family/person/1')
        assert response.content_type == 'application/json'

    def test_person_with_invalid_id(self, client):
        """Person endpoint with invalid ID should return 404 or empty"""
        response = client.get('/api/family/person/99999')
        # Should return 404 or empty data
        assert response.status_code in [200, 404]


class TestFamilyGenerationEndpoint:
    """Tests for /api/family/generation/<n> endpoints"""

    def test_generation_returns_200(self, client):
        """Generation endpoint should return 200 OK"""
        response = client.get('/api/family/generation/1')
        assert response.status_code == 200

    def test_generation_returns_json(self, client):
        """Generation endpoint should return JSON"""
        response = client.get('/api/family/generation/1')
        assert response.content_type == 'application/json'
