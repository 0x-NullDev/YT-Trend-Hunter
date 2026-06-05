"""
YT Trend Hunter - Channel Model
Represents a YouTube channel tracked by the system.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.comment import Comment
    from app.models.analysis import (
        ChannelInsight,
        CompetitorAnalysis,
        TrendSignal,
    )


class Channel(BaseModel):
    """YouTube channel tracked by the system."""

    __tablename__ = "channels"

    # YouTube Data
    youtube_channel_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Channel Statistics
    subscriber_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    video_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    hidden_subscriber_count: Mapped[bool] = mapped_column(Boolean, default=False)

    # Channel Status
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    made_for_kids: Mapped[bool] = mapped_column(Boolean, default=False)
    topic_categories: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # Niche / Category
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Growth Metrics (computed)
    growth_rate_30d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    growth_rate_7d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_views_per_video: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upload_frequency_per_week: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    # Scoring
    channel_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    competition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    videos: Mapped[List["Video"]] = relationship(
        "Video", back_populates="channel", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="channel", cascade="all, delete-orphan"
    )
    insights: Mapped[List["ChannelInsight"]] = relationship(
        "ChannelInsight", back_populates="channel", cascade="all, delete-orphan"
    )
    competitor_analyses: Mapped[List["CompetitorAnalysis"]] = relationship(
        "CompetitorAnalysis",
        foreign_keys="CompetitorAnalysis.channel_id",
        back_populates="channel",
        cascade="all, delete-orphan",
    )
    trend_signals: Mapped[List["TrendSignal"]] = relationship(
        "TrendSignal", back_populates="channel", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Channel {self.title} ({self.youtube_channel_id})>"
