"""
Tests for the Idea Generation Engine.
"""

import pytest

from app.services.engines.idea_generation import IdeaGenerationEngine


@pytest.fixture
def engine():
    return IdeaGenerationEngine()


@pytest.fixture
def sample_trends():
    return [
        "AI Music Generation",
        "AI Cover Songs",
        "AI Voice Cloning",
        "AI Beat Making",
        "AI Mastering",
    ]


@pytest.fixture
def sample_demand_signals():
    return [
        {
            "text": "AI music tutorial for beginners",
            "topic": "AI Music Tutorial",
            "demand_count": 150,
            "urgency_score": 85,
            "example_texts": ["Please make a tutorial on AI music generation"],
        },
        {
            "text": "How to make AI covers",
            "topic": "AI Cover Songs",
            "demand_count": 120,
            "urgency_score": 78,
            "example_texts": ["Can you show how to make AI covers?"],
        },
        {
            "text": "Best AI music tools",
            "topic": "AI Music Tools",
            "demand_count": 90,
            "urgency_score": 72,
            "example_texts": ["What are the best AI music tools?"],
        },
    ]


@pytest.fixture
def sample_content_gaps():
    return [
        {
            "topic": "AI Music for Beginners",
            "demand_count": 200,
            "existing_video_count": 15,
            "gap_score": 85,
            "description": "High demand for beginner AI music content",
            "niche": "AI Music",
        },
        {
            "topic": "AI Music Production Tips",
            "demand_count": 150,
            "existing_video_count": 25,
            "gap_score": 75,
            "description": "Growing demand for production tips",
            "niche": "AI Music",
        },
        {
            "topic": "AI Music Copyright Guide",
            "demand_count": 180,
            "existing_video_count": 8,
            "gap_score": 90,
            "description": "High demand for copyright guidance",
            "niche": "AI Music",
        },
    ]


class TestIdeaGenerationEngine:
    """Test suite for IdeaGenerationEngine."""

    def test_generate_channel_ideas(self, engine, sample_trends, sample_demand_signals, sample_content_gaps):
        """Test channel idea generation."""
        ideas = engine.generate_channel_ideas(
            niche="AI Music",
            trends=sample_trends,
            demand_signals=sample_demand_signals,
            content_gaps=sample_content_gaps,
            top_n=5,
        )
        assert len(ideas) <= 5
        assert len(ideas) > 0
        for idea in ideas:
            assert "title" in idea
            assert "description" in idea
            assert "reasoning" in idea
            assert "potential_score" in idea

    def test_generate_video_ideas(self, engine, sample_trends, sample_demand_signals, sample_content_gaps):
        """Test video idea generation."""
        ideas = engine.generate_video_ideas(
            niche="AI Music",
            trends=sample_trends,
            demand_signals=sample_demand_signals,
            content_gaps=sample_content_gaps,
            top_n=10,
        )
        assert len(ideas) <= 10
        assert len(ideas) > 0
        for idea in ideas:
            assert "title" in idea
            assert "description" in idea
            assert "potential_score" in idea

    def test_generate_viral_opportunities(self, engine, sample_trends, sample_demand_signals):
        """Test viral opportunity generation."""
        opportunities = engine.generate_viral_opportunities(
            niche="AI Music",
            trends=sample_trends,
            demand_signals=sample_demand_signals,
            top_n=5,
        )
        assert len(opportunities) <= 5
        assert len(opportunities) > 0
        for opp in opportunities:
            assert "title" in opp
            assert "viral_potential" in opp
            assert "reasoning" in opp

    def test_generate_underserved_niches(self, engine, sample_content_gaps):
        """Test underserved niche generation."""
        niches = engine.generate_underserved_niches(
            content_gaps=sample_content_gaps,
            top_n=5,
        )
        assert len(niches) <= 5
        assert len(niches) > 0
        for niche in niches:
            assert "title" in niche
            assert "gap_score" in niche
            assert "demand_count" in niche

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

    def test_generate_publishing_plan(self, engine, sample_trends, sample_demand_signals, sample_content_gaps):
        """Test publishing plan generation."""
        video_ideas = engine.generate_video_ideas(
            niche="AI Music",
            trends=sample_trends,
            demand_signals=sample_demand_signals,
            content_gaps=sample_content_gaps,
            top_n=20,
        )
        plan = engine.generate_publishing_plan(
            niche="AI Music",
            video_ideas=video_ideas,
            weeks=4,
            videos_per_week=3,
        )
        assert "schedule" in plan
        assert "total_videos" in plan
        assert plan["total_videos"] == 12

    def test_generate_title(self, engine):
        """Test title generation."""
        title = engine._generate_title("AI Music", "AI Music", content_type="tutorial")
        assert isinstance(title, str)
        assert len(title) > 0

    def test_generate_thumbnail_text(self, engine):
        """Test thumbnail text generation."""
        text = engine._generate_thumbnail_text("AI Music Tutorial")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_generate_content_angles(self, engine, sample_trends):
        """Test content angle generation (via video ideas)."""
        # Content angles are generated as part of video ideas
        ideas = engine.generate_video_ideas(
            niche="AI Music",
            trends=sample_trends,
            demand_signals=[],
            content_gaps=[],
            top_n=5,
        )
        assert len(ideas) > 0
        for idea in ideas:
            assert "title" in idea
            assert "source" in idea
