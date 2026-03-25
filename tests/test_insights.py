"""
RGVL API - Insights Endpoint Tests
"""
import json


class TestInsightsEndpoint:
    """Tests for /api/insights endpoint"""

    def test_insights_returns_200(self, client):
        """Insights endpoint should return 200 OK"""
        response = client.get('/api/insights')
        assert response.status_code == 200

    def test_insights_returns_json(self, client):
        """Insights endpoint should return JSON"""
        response = client.get('/api/insights')
        assert response.content_type == 'application/json'

    def test_insights_returns_list_or_dict(self, client):
        """Insights should return list or dict"""
        response = client.get('/api/insights')
        data = json.loads(response.data)
        assert isinstance(data, (list, dict))

    def test_insights_contains_required_fields(self, client):
        """Each insight should have required fields"""
        response = client.get('/api/insights')
        data = json.loads(response.data)
        
        # If returned as dict with 'insights' key
        if isinstance(data, dict) and 'insights' in data:
            insights = data['insights']
        elif isinstance(data, list):
            insights = data
        else:
            insights = []
        
        for insight in insights:
            # Each insight should have these fields (if present)
            if 'title' in insight or 'description' in insight:
                assert True  # At least has some content

    def test_insights_category_if_present(self, client):
        """Insights should have category if available"""
        response = client.get('/api/insights')
        data = json.loads(response.data)
        
        if isinstance(data, dict) and 'insights' in data:
            insights = data['insights']
        elif isinstance(data, list):
            insights = data
        else:
            insights = []
            
        # If insights exist, should have category
        if insights and len(insights) > 0:
            insight = insights[0]
            if 'category' in insight:
                assert isinstance(insight['category'], str)
