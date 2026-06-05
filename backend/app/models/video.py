"""
YT Trend Hunter - Video Model
Represents a YouTube video tracked by the system.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.channel import Channel
    from app.models.comment import Comment
    from app.models.analysis import (
        TrendSignal,
        ContentGap,
        VideoInsight,
    )


class Video(BaseModel):
    """YouTube video tracked by the system."""

    __tablename__ = "videos"

    # YouTube Data
    youtube_video_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    channel_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    default_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    caption_available: Mapped[bool] = mapped_column(Boolean, default=False)

    # Publishing
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    recorded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Statistics
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    like_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    favorite_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Engagement Metrics (computed)
    like_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    view_velocity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Views per hour since publish"
    )
    like_velocity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Likes per hour since publish"
    )
    comment_velocity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Comments per hour since publish"
    )

    # Content Analysis
    title_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    title_keywords: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    description_keywords: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    content_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="tutorial, review, vlog, entertainment, educational, etc.",
    )

    # Scoring
    viral_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="videos")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="video", cascade="all, delete-orphan"
    )
    trend_signals: Mapped[List["TrendSignal"]] = relationship(
        "TrendSignal", back_populates="video", cascade="all, delete-orphan"
    )
    content_gaps: Mapped[List["ContentGap"]] = relationship(
        "ContentGap", back_populates="video", cascade="all, delete-orphan"
    )
    insights: Mapped[List["VideoInsight"]] = relationship(
        "VideoInsight", back_populates="video", cascade="all, delete-orphan"
    )

    @property
    def hours_since_publish(self) -> float:
        """Hours since video was published."""
        if not self.published_at:
            return 0
        delta = datetime.now(self.published_at.tzinfo) - self.published_at
        return delta.total_seconds() / 3600

    def __repr__(self) -> str:
        return f"<Video {self.title[:50]} ({self.youtube_video_id})>"
