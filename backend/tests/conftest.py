"""
Pytest configuration and fixtures for YT Trend Hunter tests.
"""

from __future__ import annotations

from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.core.config import settings


@pytest.fixture
def app() -> FastAPI:
    """Create a fresh FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_youtube_collector():
    """Mock the YouTube collector."""
    with patch("app.services.collectors.youtube.YouTubeCollector") as mock:
        collector = AsyncMock()
        collector.search_videos.return_value = []
        collector.get_channel_info.return_value = {}
        collector.get_video_details.return_value = []
        collector.get_video_comments.return_value = []
        collector.get_trending_videos.return_value = []
        mock.return_value = collector
        yield mock


@pytest.fixture
def mock_ai_provider():
    """Mock the AI provider."""
    with patch("app.services.ai.base.ai_provider") as mock:
        mock.analyze_text = AsyncMock(return_value="AI analysis result")
        mock.generate_insights = AsyncMock(
            return_value={"insights": ["Test insight"]}
        )
        mock.classify_content = AsyncMock(
            return_value={"test_category": 0.95}
        )
        yield mock


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("app.core.redis_client.redis_client") as mock:
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        mock.delete = AsyncMock(return_value=True)
        mock.exists = AsyncMock(return_value=False)
        yield mock


@pytest.fixture
def sample_video_data():
    """Sample video data for testing."""
    return {
        "id": "test_video_123",
        "title": "Test Video Title",
        "description": "Test video description for testing",
        "channel_id": "test_channel_123",
        "channel_title": "Test Channel",
        "published_at": "2024-01-01T00:00:00Z",
        "view_count": 100000,
        "like_count": 5000,
        "comment_count": 500,
        "duration_seconds": 600,
        "category_id": "22",
        "tags": ["test", "video", "tutorial"],
    }


@pytest.fixture
def sample_channel_data():
    """Sample channel data for testing."""
    return {
        "id": "test_channel_123",
        "title": "Test Channel",
        "description": "A test YouTube channel",
        "subscriber_count": 50000,
        "video_count": 200,
        "view_count": 5000000,
        "country": "US",
        "published_at": "2020-01-01T00:00:00Z",
        "topic_categories": ["Technology", "Education"],
    }


@pytest.fixture
def sample_comment_data():
    """Sample comment data for testing."""
    return [
        {
            "id": "comment_1",
            "text": "Please make a video about AI music generation",
            "author": "user1",
            "like_count": 50,
            "published_at": "2024-01-15T00:00:00Z",
        },
        {
            "id": "comment_2",
            "text": "Can someone explain how this works?",
            "author": "user2",
            "like_count": 30,
            "published_at": "2024-01-14T00:00:00Z",
        },
        {
            "id": "comment_3",
            "text": "Part 2 please! This was amazing",
            "author": "user3",
            "like_count": 100,
            "published_at": "2024-01-13T00:00:00Z",
        },
    ]
