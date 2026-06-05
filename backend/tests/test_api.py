"""
Tests for the API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    async def test_discovery_global(self, client: AsyncClient):
        """Test global discovery endpoint."""
        response = await client.get("/api/v1/discovery/global")
        assert response.status_code == 200
        data = response.json()
        assert "opportunities" in data
        assert "trends" in data
        assert "insights" in data

    async def test_discovery_global_with_params(self, client: AsyncClient):
        """Test global discovery with parameters."""
        response = await client.get(
            "/api/v1/discovery/global",
            params={"categories": "AI,Technology", "limit": 10},
        )
        assert response.status_code == 200

    async def test_discovery_trending_topics(self, client: AsyncClient):
        """Test trending topics endpoint."""
        response = await client.get("/api/v1/discovery/trending-topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data

    async def test_discovery_rising_creators(self, client: AsyncClient):
        """Test rising creators endpoint."""
        response = await client.get("/api/v1/discovery/rising-creators")
        assert response.status_code == 200
        data = response.json()
        assert "creators" in data

    async def test_discovery_content_gaps(self, client: AsyncClient):
        """Test content gaps endpoint."""
        response = await client.get("/api/v1/discovery/content-gaps")
        assert response.status_code == 200
        data = response.json()
        assert "gaps" in data

    async def test_discovery_channel_predictor(self, client: AsyncClient):
        """Test channel predictor endpoint."""
        response = await client.get(
            "/api/v1/discovery/channel-predictor",
            params={"niche": "AI Music"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "success_probability" in data
        assert "difficulty" in data

    async def test_niche_analyze(self, client: AsyncClient):
        """Test niche analysis endpoint."""
        response = await client.get("/api/v1/niche/analyze/AI%20Music")
        assert response.status_code == 200
        data = response.json()
        assert "niche" in data
        assert "analysis" in data

    async def test_niche_trends(self, client: AsyncClient):
        """Test niche trends endpoint."""
        response = await client.get("/api/v1/niche/trends/AI%20Music")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data

    async def test_niche_creators(self, client: AsyncClient):
        """Test niche creators endpoint."""
        response = await client.get("/api/v1/niche/creators/AI%20Music")
        assert response.status_code == 200
        data = response.json()
        assert "creators" in data

    async def test_niche_gaps(self, client: AsyncClient):
        """Test niche gaps endpoint."""
        response = await client.get("/api/v1/niche/gaps/AI%20Music")
        assert response.status_code == 200
        data = response.json()
        assert "gaps" in data

    async def test_niche_demand(self, client: AsyncClient):
        """Test niche demand endpoint."""
        response = await client.get("/api/v1/niche/demand/AI%20Music")
        assert response.status_code == 200
        data = response.json()
        assert "demand_signals" in data

    async def test_trends_endpoint(self, client: AsyncClient):
        """Test trends endpoint."""
        response = await client.get("/api/v1/trends/")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data

    async def test_opportunities_endpoint(self, client: AsyncClient):
        """Test opportunities endpoint."""
        response = await client.get("/api/v1/opportunities/")
        assert response.status_code == 200
        data = response.json()
        assert "opportunities" in data

    async def test_channels_endpoint(self, client: AsyncClient):
        """Test channels endpoint."""
        response = await client.get("/api/v1/channels/")
        assert response.status_code == 200
        data = response.json()
        assert "channels" in data

    async def test_videos_endpoint(self, client: AsyncClient):
        """Test videos endpoint."""
        response = await client.get("/api/v1/videos/")
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data

    async def test_comments_endpoint(self, client: AsyncClient):
        """Test comments endpoint."""
        response = await client.get("/api/v1/comments/")
        assert response.status_code == 200
        data = response.json()
        assert "comments" in data

    async def test_ideas_channel(self, client: AsyncClient):
        """Test channel ideas endpoint."""
        response = await client.get(
            "/api/v1/ideas/channel-ideas",
            params={"niche": "AI Music"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "channel_ideas" in data

    async def test_ideas_video(self, client: AsyncClient):
        """Test video ideas endpoint."""
        response = await client.get(
            "/api/v1/ideas/video-ideas",
            params={"niche": "AI Music"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "video_ideas" in data

    async def test_ideas_viral(self, client: AsyncClient):
        """Test viral opportunities endpoint."""
        response = await client.get("/api/v1/ideas/viral-opportunities")
        assert response.status_code == 200
        data = response.json()
        assert "viral_opportunities" in data

    async def test_ideas_underserved(self, client: AsyncClient):
        """Test underserved niches endpoint."""
        response = await client.get("/api/v1/ideas/underserved-niches")
        assert response.status_code == 200
        data = response.json()
        assert "underserved_niches" in data

    async def test_reports_endpoint(self, client: AsyncClient):
        """Test reports endpoint."""
        response = await client.get("/api/v1/reports/")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data

    async def test_alerts_endpoint(self, client: AsyncClient):
        """Test alerts endpoint."""
        response = await client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    async def test_users_me(self, client: AsyncClient):
        """Test user profile endpoint."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data

    async def test_404_handling(self, client: AsyncClient):
        """Test 404 error handling."""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    async def test_invalid_params(self, client: AsyncClient):
        """Test invalid parameter handling."""
        response = await client.get(
            "/api/v1/ideas/channel-ideas",
            params={"niche": ""},
        )
        assert response.status_code == 422
