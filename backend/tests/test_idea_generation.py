"""
Tests for the Idea Generation Engine.
"""

import pytest

from app.services.engines.idea_generation import IdeaGenerationEngine


@pytest.fixture
def engine():
    return IdeaGenerationEngine()


class TestIdeaGenerationEngine:
    """Test suite for IdeaGenerationEngine."""

    def test_generate_channel_ideas(self, engine):
        """Test channel idea generation."""
        ideas = engine.generate_channel_ideas(
            niche="AI Music",
            count=5,
        )
        assert len(ideas) == 5
        for idea in ideas:
            assert "name" in idea
            assert "description" in idea
            assert "reasoning" in idea
            assert "potential_score" in idea

    def test_generate_video_ideas(self, engine):
        """Test video idea generation."""
        ideas = engine.generate_video_ideas(
            niche="AI Music",
            count=10,
        )
        assert len(ideas) == 10
        for idea in ideas:
            assert "title" in idea
            assert "description" in idea
            assert "estimated_engagement" in idea

    def test_generate_viral_opportunities(self, engine):
        """Test viral opportunity generation."""
        opportunities = engine.generate_viral_opportunities(
            niche="AI Music",
            count=5,
        )
        assert len(opportunities) == 5
        for opp in opportunities:
            assert "title" in opp
            assert "viral_potential" in opp
            assert "reasoning" in opp

    def test_generate_underserved_niches(self, engine):
        """Test underserved niche generation."""
        niches = engine.generate_underserved_niches(count=5)
        assert len(niches) == 5
        for niche in niches:
            assert "name" in niche
            assert "demand_score" in niche
            assert "supply_score" in niche
            assert "gap_score" in niche

    def test_generate_content_series(self, engine):
        """Test content series generation."""
        series = engine.generate_content_series(
            niche="AI Music",
            topic="AI Music Production",
            parts=5,
        )
        assert "title" in series
        assert "episodes" in series
        assert len(series["episodes"]) == 5

    def test_generate_publishing_plan(self, engine):
        """Test publishing plan generation."""
        plan = engine.generate_publishing_plan(
            niche="AI Music",
            weeks=4,
            videos_per_week=3,
        )
        assert "schedule" in plan
        assert "total_videos" in plan
        assert plan["total_videos"] == 12

    def test_generate_title_suggestions(self, engine):
        """Test title suggestion generation."""
        titles = engine.generate_title_suggestions(
            topic="AI Music Generation",
            count=10,
        )
        assert len(titles) == 10
        for title in titles:
            assert "title" in title
            assert "click_potential" in title

    def test_generate_thumbnail_text(self, engine):
        """Test thumbnail text generation."""
        thumbnails = engine.generate_thumbnail_text(
            topic="AI Music Tutorial",
            count=5,
        )
        assert len(thumbnails) == 5
        for thumb in thumbnails:
            assert "text" in thumb
            assert "style" in thumb

    def test_generate_content_angles(self, engine):
        """Test content angle generation."""
        angles = engine.generate_content_angles(
            topic="AI Music",
            count=5,
        )
        assert len(angles) == 5
        for angle in angles:
            assert "angle" in angle
            assert "hook" in angle
            assert "target_audience" in angle
