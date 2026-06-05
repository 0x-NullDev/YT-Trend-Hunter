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

    def test_classify_comment_request(self, engine):
        """Test classifying a comment as a request."""
        result = engine.classify_comment("Please make a video about AI music generation")
        assert result["is_request"] is True
        assert "AI music generation" in result["extracted_request"]

    def test_classify_comment_question(self, engine):
        """Test classifying a comment as a question."""
        result = engine.classify_comment("Can someone explain how this works?")
        assert result["is_question"] is True

    def test_classify_comment_part2(self, engine):
        """Test classifying a 'Part 2' request."""
        result = engine.classify_comment("Part 2 please! This was amazing")
        assert result["is_part2_request"] is True

    def test_classify_comment_idea(self, engine):
        """Test classifying a comment as an idea."""
        result = engine.classify_comment("What if you made a video about AI art?")
        assert result["is_idea"] is True

    def test_classify_comment_pain_point(self, engine):
        """Test classifying a comment as a pain point."""
        result = engine.classify_comment("This is so confusing, nobody explains it well")
        assert result["is_pain_point"] is True

    def test_analyze_comments_batch(self, engine, sample_comment_data):
        """Test full comment batch analysis."""
        result = engine.analyze_comments_batch(sample_comment_data)
        assert "signals" in result
        assert "requests" in result["signals"]
        assert "questions" in result["signals"]
        assert "complaints" in result["signals"]
        assert "ideas" in result["signals"]
        assert "pain_points" in result["signals"]
        assert "part2_requests" in result["signals"]
        assert "demand_database" in result
        assert result["total_comments"] == 3

    def test_analyze_comments_batch_requests_detected(self, engine, sample_comment_data):
        """Test that requests are detected in batch analysis."""
        result = engine.analyze_comments_batch(sample_comment_data)
        assert result["signals"]["requests"]["count"] > 0

    def test_analyze_comments_batch_questions_detected(self, engine, sample_comment_data):
        """Test that questions are detected in batch analysis."""
        result = engine.analyze_comments_batch(sample_comment_data)
        assert result["signals"]["questions"]["count"] > 0

    def test_analyze_comments_batch_part2_detected(self, engine, sample_comment_data):
        """Test that Part 2 requests are detected in batch analysis."""
        result = engine.analyze_comments_batch(sample_comment_data)
        assert result["signals"]["part2_requests"]["count"] > 0

    def test_empty_comments(self, engine):
        """Test analysis with empty comments."""
        result = engine.analyze_comments_batch([])
        assert result["total_comments"] == 0
        assert result["analyzed_count"] == 0
        assert result["signals"]["requests"]["count"] == 0
        assert result["signals"]["questions"]["count"] == 0
        assert result["demand_database"] == []

    def test_analyze_sentiment_positive(self, engine):
        """Test sentiment analysis with positive text."""
        result = engine.analyze_sentiment("This is amazing and wonderful!")
        assert result["sentiment_score"] > 0

    def test_analyze_sentiment_negative(self, engine):
        """Test sentiment analysis with negative text."""
        result = engine.analyze_sentiment("This is terrible and awful")
        assert result["sentiment_score"] < 0

    def test_extract_keywords(self, engine):
        """Test keyword extraction."""
        keywords = engine.extract_keywords("AI music generation is the future of content creation")
        assert len(keywords) > 0
        assert "music" in keywords or "generation" in keywords or "future" in keywords

    def test_demand_database(self, engine, sample_comment_data):
        """Test demand database generation."""
        result = engine.analyze_comments_batch(sample_comment_data)
        demand_db = result["demand_database"]
        assert len(demand_db) > 0
        assert "topic" in demand_db[0]
        assert "demand_count" in demand_db[0]
        assert "urgency_score" in demand_db[0]

    def test_sentiment_distribution(self, engine, sample_comment_data):
        """Test sentiment distribution calculation."""
        result = engine.analyze_comments_batch(sample_comment_data)
        sentiment = result["sentiment"]
        assert "average_score" in sentiment
        assert "distribution" in sentiment
        assert "positive" in sentiment["distribution"]
        assert "neutral" in sentiment["distribution"]
        assert "negative" in sentiment["distribution"]

    def test_top_keywords(self, engine, sample_comment_data):
        """Test top keywords extraction from batch."""
        result = engine.analyze_comments_batch(sample_comment_data)
        assert "top_keywords" in result
        assert len(result["top_keywords"]) > 0
