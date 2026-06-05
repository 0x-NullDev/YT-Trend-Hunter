"""
Tests for the Trend Detection Engine.
"""

import pytest
from datetime import datetime, timedelta

from app.services.engines.trend_detection import TrendDetectionEngine


@pytest.fixture
def engine():
    return TrendDetectionEngine()


class TestTrendDetectionEngine:
    """Test suite for TrendDetectionEngine."""

    def test_calculate_growth_velocity(self, engine):
        """Test growth velocity calculation."""
        current = 100000
        previous = 50000
        days = 30

        velocity = engine.calculate_growth_velocity(current, previous, days)
        assert velocity == pytest.approx(1666.67, rel=0.01)

    def test_growth_velocity_zero_previous(self, engine):
        """Test growth velocity when previous is zero."""
        velocity = engine.calculate_growth_velocity(1000, 0, 30)
        assert velocity == 33.33

    def test_calculate_engagement_rate(self, engine):
        """Test engagement rate calculation."""
        likes = 5000
        comments = 500
        views = 100000

        rate = engine.calculate_engagement_rate(likes, comments, views)
        assert rate == pytest.approx(5.5, rel=0.01)

    def test_engagement_rate_zero_views(self, engine):
        """Test engagement rate when views is zero."""
        rate = engine.calculate_engagement_rate(100, 10, 0)
        assert rate == 0.0

    def test_calculate_trend_strength(self, engine):
        """Test trend strength calculation."""
        result = engine.calculate_trend_strength(
            growth_velocity=1000,
            engagement_velocity=50,
            search_momentum=75,
            video_velocity=10,
        )
        assert 0 <= result["trend_strength"] <= 100
        assert "components" in result
        assert "confidence" in result

    def test_calculate_competition_level(self, engine):
        """Test competition level calculation."""
        result = engine.calculate_competition_level(
            channel_count=100,
            avg_subscribers=50000,
            total_videos=5000,
            niche_size=1000000,
        )
        assert 0 <= result["competition_level"] <= 100
        assert "saturation_score" in result

    def test_competition_low(self, engine):
        """Test low competition scenario."""
        result = engine.calculate_competition_level(
            channel_count=5,
            avg_subscribers=1000,
            total_videos=50,
            niche_size=1000000,
        )
        assert result["competition_level"] < 30

    def test_competition_high(self, engine):
        """Test high competition scenario."""
        result = engine.calculate_competition_level(
            channel_count=1000,
            avg_subscribers=500000,
            total_videos=100000,
            niche_size=100000,
        )
        assert result["competition_level"] > 70

    def test_calculate_opportunity_score(self, engine):
        """Test opportunity score calculation."""
        result = engine.calculate_opportunity_score(
            trend_strength=80,
            competition_level=20,
            saturation_score=15,
            audience_demand=90,
        )
        assert 0 <= result["opportunity_score"] <= 100
        assert "components" in result

    def test_high_opportunity(self, engine):
        """Test high opportunity scenario."""
        result = engine.calculate_opportunity_score(
            trend_strength=90,
            competition_level=10,
            saturation_score=5,
            audience_demand=95,
        )
        assert result["opportunity_score"] > 70

    def test_low_opportunity(self, engine):
        """Test low opportunity scenario."""
        result = engine.calculate_opportunity_score(
            trend_strength=10,
            competition_level=90,
            saturation_score=95,
            audience_demand=10,
        )
        assert result["opportunity_score"] < 30

    def test_calculate_search_momentum(self, engine):
        """Test search momentum calculation."""
        momentum = engine.calculate_search_momentum(
            current_searches=10000,
            previous_searches=5000,
        )
        assert momentum == 100.0

    def test_search_momentum_decline(self, engine):
        """Test declining search momentum."""
        momentum = engine.calculate_search_momentum(
            current_searches=5000,
            previous_searches=10000,
        )
        assert momentum < 0

    def test_calculate_viral_score(self, engine):
        """Test viral score calculation."""
        score = engine.calculate_viral_score(
            view_velocity=10000,
            engagement_rate=15.0,
            like_ratio=0.05,
            comment_ratio=0.005,
        )
        assert 0 <= score <= 100

    def test_calculate_content_gap_score(self, engine):
        """Test content gap score calculation."""
        score = engine.calculate_content_gap_score(
            demand_score=80,
            supply_gap=70,
            demand_momentum=60,
        )
        assert 0 <= score <= 100

    def test_high_gap(self, engine):
        """Test high content gap scenario."""
        score = engine.calculate_content_gap_score(
            demand_score=95,
            supply_gap=90,
            demand_momentum=85,
        )
        assert score > 80

    def test_low_gap(self, engine):
        """Test low content gap scenario."""
        score = engine.calculate_content_gap_score(
            demand_score=10,
            supply_gap=10,
            demand_momentum=10,
        )
        assert score < 20

    def test_normalize_value(self, engine):
        """Test value normalization."""
        normalized = engine._normalize(50000, 0, 100000)
        assert normalized == pytest.approx(0.5, rel=0.01)

    def test_normalize_edge_cases(self, engine):
        """Test normalization edge cases."""
        assert engine._normalize(0, 0, 100) == 0.0
        assert engine._normalize(100, 0, 100) == 1.0
        assert engine._normalize(50, 0, 100) == 0.5
        assert engine._normalize(50, 50, 50) == 1.0

    def test_analyze_trend(self, engine, sample_video_data):
        """Test full trend analysis."""
        result = engine.analyze_trend(
            videos=[sample_video_data],
            channels=[],
            comments=[],
        )
        assert "trends" in result
        assert "opportunities" in result
        assert "insights" in result
