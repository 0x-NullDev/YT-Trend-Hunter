"""
Tests for the Opportunity Engine.
"""

import pytest

from app.services.engines.opportunity_engine import OpportunityEngine


@pytest.fixture
def engine():
    return OpportunityEngine()


class TestOpportunityEngine:
    """Test suite for OpportunityEngine."""

    def test_calculate_opportunity_score(self, engine):
        """Test opportunity score calculation."""
        score = engine.calculate_opportunity_score(
            trend_score=85,
            competition_score=20,
            saturation_score=15,
            audience_demand_score=90,
            monetization_score=70,
        )
        assert 0 <= score["opportunity_score"] <= 100
        assert "components" in score
        assert "verdict" in score

    def test_high_opportunity(self, engine):
        """Test high opportunity scenario."""
        score = engine.calculate_opportunity_score(
            trend_score=90,
            competition_score=10,
            saturation_score=5,
            audience_demand_score=95,
            monetization_score=80,
        )
        assert score["opportunity_score"] > 70
        assert score["verdict"] == "EXCELLENT"

    def test_low_opportunity(self, engine):
        """Test low opportunity scenario."""
        score = engine.calculate_opportunity_score(
            trend_score=10,
            competition_score=90,
            saturation_score=95,
            audience_demand_score=10,
            monetization_score=20,
        )
        assert score["opportunity_score"] < 30
        assert score["verdict"] == "POOR"

    def test_calculate_monetization_score(self, engine):
        """Test monetization score calculation."""
        score = engine.calculate_monetization_score(
            avg_cpm=10.0,
            sponsor_availability=80,
            product_potential=70,
            audience_purchasing_power=75,
        )
        assert 0 <= score <= 100

    def test_high_monetization(self, engine):
        """Test high monetization potential."""
        score = engine.calculate_monetization_score(
            avg_cpm=25.0,
            sponsor_availability=95,
            product_potential=90,
            audience_purchasing_power=90,
        )
        assert score > 70

    def test_rank_opportunities(self, engine):
        """Test ranking multiple opportunities."""
        opportunities = [
            {"id": "1", "opportunity_score": 85},
            {"id": "2", "opportunity_score": 60},
            {"id": "3", "opportunity_score": 95},
        ]
        ranked = engine.rank_opportunities(opportunities)
        assert ranked[0]["id"] == "3"
        assert ranked[2]["id"] == "2"

    def test_analyze_niche_opportunity(self, engine):
        """Test niche opportunity analysis."""
        result = engine.analyze_niche_opportunity(
            niche="AI Music",
            trend_score=80,
            competition_score=25,
            saturation_score=20,
            audience_demand_score=85,
            monetization_score=65,
        )
        assert "opportunity_score" in result
        assert "recommendation" in result
        assert "risk_factors" in result

    def test_calculate_channel_creation_score(self, engine):
        """Test channel creation score calculation."""
        result = engine.calculate_channel_creation_score(
            niche="AI Football Songs",
            competition_level=20,
            audience_demand=90,
            content_gap=85,
            monetization_potential=70,
        )
        assert "success_probability" in result
        assert "difficulty" in result
        assert "recommendation" in result
        assert "estimated_time_to_1k" in result

    def test_channel_creation_high_potential(self, engine):
        """Test high potential channel creation."""
        result = engine.calculate_channel_creation_score(
            niche="AI Football Songs",
            competition_level=10,
            audience_demand=95,
            content_gap=90,
            monetization_potential=80,
        )
        assert result["success_probability"]["1000"] > 80
        assert result["difficulty"] == "LOW"

    def test_channel_creation_low_potential(self, engine):
        """Test low potential channel creation."""
        result = engine.calculate_channel_creation_score(
            niche="Gaming News",
            competition_level=90,
            audience_demand=50,
            content_gap=10,
            monetization_potential=40,
        )
        assert result["success_probability"]["1000"] < 50
        assert result["difficulty"] == "HIGH"
