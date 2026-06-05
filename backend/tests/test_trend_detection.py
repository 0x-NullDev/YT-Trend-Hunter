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
        velocity = engine.calculate_growth_velocity(100000, 50000, 30)
        assert velocity == pytest.approx(1666.67, rel=0.01)

    def test_growth_velocity_zero_previous(self, engine):
        """Test growth velocity when previous is zero."""
        velocity = engine.calculate_growth_velocity(1000, 0, 30)
        assert velocity == pytest.approx(33.33, rel=0.01)

    def test_growth_velocity_zero_days(self, engine):
        """Test growth velocity when days is zero."""
        velocity = engine.calculate_growth_velocity(1000, 500, 0)
        assert velocity == 0.0

    def test_calculate_growth_rate(self, engine):
        """Test growth rate calculation."""
        rate = engine.calculate_growth_rate(100000, 50000, 30)
        assert rate == pytest.approx(100.0, rel=0.01)

    def test_growth_rate_zero_previous(self, engine):
        """Test growth rate when previous is zero."""
        rate = engine.calculate_growth_rate(1000, 0, 30)
        assert rate == 0.0

    def test_calculate_engagement_rate(self, engine):
        """Test engagement rate calculation."""
        rate = engine.calculate_engagement_rate(5000, 500, 100000)
        assert rate == pytest.approx(5.5, rel=0.01)

    def test_engagement_rate_zero_views(self, engine):
        """Test engagement rate when views is zero."""
        rate = engine.calculate_engagement_rate(100, 10, 0)
        assert rate == 0.0

    def test_calculate_engagement_velocity(self, engine):
        """Test engagement velocity calculation."""
        ev = engine.calculate_engagement_velocity(8.0, 5.0, 30)
        assert ev == pytest.approx(0.1, rel=0.01)

    def test_calculate_trend_strength(self, engine):
        """Test trend strength calculation."""
        result = engine.calculate_trend_strength(
            growth_velocity=1000,
            engagement_velocity=50,
            search_momentum=75,
            video_velocity=10,
        )
        assert 0 <= result <= 100

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
        assert 0 <= result <= 100

    def test_high_opportunity(self, engine):
        """Test high opportunity scenario."""
        result = engine.calculate_opportunity_score(
            trend_strength=90,
            competition_level=10,
            saturation_score=5,
            audience_demand=95,
        )
        assert result > 70

    def test_low_opportunity(self, engine):
        """Test low opportunity scenario."""
        result = engine.calculate_opportunity_score(
            trend_strength=10,
            competition_level=90,
            saturation_score=95,
            audience_demand=10,
        )
        assert result < 30

    def test_calculate_search_momentum(self, engine):
        """Test search momentum calculation."""
        momentum = engine.calculate_search_momentum(
            current_search_volume=50000,
            previous_search_volume=1000,
        )
        assert momentum == pytest.approx(100.0, rel=0.01)

    def test_search_momentum_decline(self, engine):
        """Test declining search momentum."""
        momentum = engine.calculate_search_momentum(
            current_search_volume=5000,
            previous_search_volume=10000,
        )
        assert momentum >= 0  # normalized with tanh, always >= 0

    def test_search_momentum_zero_previous(self, engine):
        """Test search momentum when previous is zero."""
        momentum = engine.calculate_search_momentum(
            current_search_volume=10000,
            previous_search_volume=0,
        )
        assert momentum == 0.0

    def test_calculate_viral_score(self, engine):
        """Test viral score calculation."""
        score = engine.calculate_viral_score(
            views=100000,
            likes=5000,
            comments=500,
            subscribers=50000,
            hours_since_publish=24,
        )
        assert 0 <= score <= 100

    def test_viral_score_zero_hours(self, engine):
        """Test viral score when hours is zero."""
        score = engine.calculate_viral_score(
            views=100000,
            likes=5000,
            comments=500,
            subscribers=50000,
            hours_since_publish=0,
        )
        assert score == 0.0

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

    def test_calculate_confidence_score(self, engine):
        """Test confidence score calculation."""
        score = engine.calculate_confidence_score(
            sample_size=100,
            consistency_score=80,
            source_count=3,
            hours_since_detection=24,
        )
        assert 0 <= score <= 100

    def test_calculate_saturation_score(self, engine):
        """Test saturation score calculation."""
        score = engine.calculate_saturation_score(
            video_count=5000,
            avg_views_per_video=50000,
            channel_density=0.5,
        )
        assert 0 <= score <= 100

    def test_detect_accelerating_trend(self, engine):
        """Test accelerating trend detection."""
        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = engine.detect_accelerating_trend(data)
        assert "is_accelerating" in result
        assert "slope" in result
        assert "r_squared" in result

    def test_detect_seasonality(self, engine):
        """Test seasonality detection."""
        data = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
        result = engine.detect_seasonality(data, period=3)
        assert "has_seasonality" in result
        assert "strength" in result

    def test_calculate_channel_growth_prediction(self, engine):
        """Test channel growth prediction."""
        result = engine.calculate_channel_growth_prediction(
            current_subscribers=10000,
            subscriber_history=[5000, 6000, 7000, 8000, 9000, 10000],
            niche_growth_rate=10.0,
            competition_level=30,
            upload_frequency=3,
        )
        assert "prob_1000" in result
        assert "prob_10000" in result
        assert "prob_100000" in result
        assert "prob_1000000" in result

    def test_analyze_trend(self, engine, sample_video_data):
        """Test full trend analysis."""
        result = engine.analyze_trend(
            videos=[sample_video_data],
            channels=[],
            comments=[],
        )
        assert "trends" in result
        assert "trend_strength" in result
        assert "competition_level" in result
        assert "insights" in result
