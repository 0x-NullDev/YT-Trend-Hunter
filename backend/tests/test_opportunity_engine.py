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
            demand_score=90,
            monetization_score=70,
        )
        assert 0 <= score["opportunity_score"] <= 100
        assert "trend_score" in score
        assert "competition_score" in score
        assert "saturation_score" in score
        assert "demand_score" in score
        assert "monetization_score" in score

    def test_high_opportunity(self, engine):
        """Test high opportunity scenario."""
        score = engine.calculate_opportunity_score(
            trend_score=90,
            competition_score=10,
            saturation_score=5,
            demand_score=95,
            monetization_score=80,
        )
        assert score["opportunity_score"] > 70

    def test_low_opportunity(self, engine):
        """Test low opportunity scenario."""
        score = engine.calculate_opportunity_score(
            trend_score=10,
            competition_score=90,
            saturation_score=95,
            demand_score=10,
            monetization_score=20,
        )
        assert score["opportunity_score"] < 30

    def test_calculate_monetization_score(self, engine):
        """Test monetization score calculation."""
        score = engine.calculate_monetization_score(
            niche="AI Music",
            avg_cpm=10.0,
            avg_views_per_video=50000,
            sponsorship_potential=80,
            product_potential=70,
            affiliate_potential=75,
        )
        assert 0 <= score <= 100

    def test_high_monetization(self, engine):
        """Test high monetization potential."""
        score = engine.calculate_monetization_score(
            niche="Finance",
            avg_cpm=25.0,
            avg_views_per_video=100000,
            sponsorship_potential=95,
            product_potential=90,
            affiliate_potential=90,
        )
        assert score > 70

    def test_rank_opportunities(self, engine):
        """Test ranking multiple opportunities."""
        opportunities = [
            {"id": "1", "opportunity_score": 85},
            {"id": "2", "opportunity_score": 60},
            {"id": "3", "opportunity_score": 95},
        ]
        ranked = engine.rank_opportunities(opportunities, top_n=3)
        assert ranked[0]["id"] == "3"
        assert ranked[2]["id"] == "2"

    def test_calculate_channel_creation_prediction(self, engine):
        """Test channel creation prediction."""
        result = engine.calculate_channel_creation_prediction(
            niche="AI Football Songs",
            trend_score=80,
            competition_score=20,
            saturation_score=15,
            demand_score=90,
            estimated_audience_size=500000,
            avg_channel_growth_rate=15.0,
            upload_frequency=3,
        )
        assert "success_probability" in result
        assert "difficulty" in result
        assert "reasoning" in result
        assert "1000_subscribers" in result["success_probability"]
        assert "10000_subscribers" in result["success_probability"]
        assert "100000_subscribers" in result["success_probability"]
        assert "1000000_subscribers" in result["success_probability"]

    def test_channel_creation_high_potential(self, engine):
        """Test high potential channel creation."""
        result = engine.calculate_channel_creation_prediction(
            niche="AI Football Songs",
            trend_score=90,
            competition_score=10,
            saturation_score=10,
            demand_score=95,
            estimated_audience_size=1000000,
            avg_channel_growth_rate=25.0,
            upload_frequency=5,
        )
        assert result["success_probability"]["1000_subscribers"] > 80
        assert result["difficulty"] in ["Very Easy", "Easy"]

    def test_channel_creation_low_potential(self, engine):
        """Test low potential channel creation."""
        result = engine.calculate_channel_creation_prediction(
            niche="Gaming News",
            trend_score=30,
            competition_score=90,
            saturation_score=95,
            demand_score=40,
            estimated_audience_size=10000000,
            avg_channel_growth_rate=2.0,
            upload_frequency=1,
        )
        assert result["success_probability"]["1000_subscribers"] < 50
        assert result["difficulty"] in ["Hard", "Very Hard"]

    def test_generate_opportunity_summary(self, engine):
        """Test opportunity summary generation."""
        opportunity = {
            "title": "AI Music Channel",
            "niche": "AI Music",
            "opportunity_type": "channel",
            "opportunity_score": 85,
            "trend_score": 80,
            "competition_score": 20,
            "saturation_score": 15,
            "demand_score": 90,
            "monetization_score": 70,
            "prob_1000_subs": 92,
            "prob_10000_subs": 84,
            "prob_100000_subs": 61,
            "prob_1000000_subs": 28,
            "difficulty_level": "Easy",
            "reasoning": "Rapidly growing niche with low channel density",
        }
        summary = engine.generate_opportunity_summary(opportunity)
        assert isinstance(summary, str)
        assert "AI Music Channel" in summary
        assert "85/100" in summary
        assert "92%" in summary
