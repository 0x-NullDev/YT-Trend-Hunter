"""
Tests for the Comment Intelligence Engine.
"""

import pytest

from app.services.engines.comment_intelligence import CommentIntelligenceEngine


@pytest.fixture
def engine():
    return CommentIntelligenceEngine()


class TestCommentIntelligenceEngine:
    """Test suite for CommentIntelligenceEngine."""

    def test_extract_requests(self, engine, sample_comment_data):
        """Test extracting content requests from comments."""
        requests = engine.extract_requests(sample_comment_data)
        assert len(requests) > 0
        assert any("AI music generation" in r["text"] for r in requests)

    def test_extract_questions(self, engine, sample_comment_data):
        """Test extracting questions from comments."""
        questions = engine.extract_questions(sample_comment_data)
        assert len(questions) > 0
        assert any("how this works" in q["text"] for q in questions)

    def test_extract_part_requests(self, engine, sample_comment_data):
        """Test extracting 'Part 2' type requests."""
        part_requests = engine.extract_part_requests(sample_comment_data)
        assert len(part_requests) > 0

    def test_analyze_comments(self, engine, sample_comment_data):
        """Test full comment analysis."""
        result = engine.analyze_comments(sample_comment_data)
        assert "requests" in result
        assert "questions" in result
        assert "complaints" in result
        assert "ideas" in result
        assert "pain_points" in result
        assert "demand_signals" in result

    def test_rank_demand_signals(self, engine):
        """Test ranking demand signals by frequency."""
        signals = [
            {"text": "AI video", "frequency": 100},
            {"text": "tutorial", "frequency": 50},
            {"text": "review", "frequency": 200},
        ]
        ranked = engine.rank_demand_signals(signals)
        assert ranked[0]["text"] == "review"
        assert ranked[2]["text"] == "tutorial"

    def test_empty_comments(self, engine):
        """Test analysis with empty comments."""
        result = engine.analyze_comments([])
        assert result["requests"] == []
        assert result["questions"] == []
        assert result["demand_signals"] == []

    def test_extract_ideas(self, engine):
        """Test extracting content ideas from comments."""
        comments = [
            {"text": "You should make a video about AI art", "like_count": 100},
            {"text": "Would love to see a comparison video", "like_count": 50},
        ]
        ideas = engine.extract_ideas(comments)
        assert len(ideas) > 0

    def test_extract_pain_points(self, engine):
        """Test extracting pain points from comments."""
        comments = [
            {"text": "This is so confusing, nobody explains it well", "like_count": 80},
            {"text": "I wish there was a beginner tutorial", "like_count": 60},
        ]
        pain_points = engine.extract_pain_points(comments)
        assert len(pain_points) > 0
