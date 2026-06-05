"""
YT Trend Hunter - Analysis Models
Core intelligence models for trend detection, opportunity scoring, and insights.
"""

from __future__ import annotations

from datetime import datetime
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
    from app.models.video import Video
    from app.models.comment import Comment


class TrendSignal(BaseModel):
    """
    Trend Signal Model
    Represents a detected trend signal from any data source.
    This is the core data structure for the Trend Detection Engine.
    """

    __tablename__ = "trend_signals"

    # Source
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="youtube, google_trends, reddit, news, rss, etc.",
    )
    signal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="keyword, topic, channel, format, category",
    )
    signal_name: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True
    )
    signal_value: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="The actual trend value"
    )

    # Optional foreign keys
    channel_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="SET NULL"),
        nullable=True,
    )
    video_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Niche / Category
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Trend Metrics
    growth_velocity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Rate of growth per day"
    )
    engagement_velocity: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Rate of engagement per day"
    )
    search_momentum: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Search volume momentum"
    )
    trend_strength: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 trend strength score"
    )
    competition_level: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 competition level"
    )
    saturation_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 saturation score"
    )
    opportunity_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 opportunity score"
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 confidence in this signal"
    )

    # Time Series
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    peak_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Raw Data
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    channel: Mapped[Optional["Channel"]] = relationship(
        "Channel", back_populates="trend_signals"
    )
    video: Mapped[Optional["Video"]] = relationship(
        "Video", back_populates="trend_signals"
    )

    def __repr__(self) -> str:
        return f"<TrendSignal {self.signal_type}:{self.signal_value} ({self.source})>"


class Opportunity(BaseModel):
    """
    Opportunity Model
    Represents a detected opportunity for content creation.
    This is the output of the Opportunity Engine.
    """

    __tablename__ = "opportunities"

    # Opportunity Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opportunity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="channel_idea, video_idea, niche_entry, content_series, underserved_topic",
    )
    niche: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Scoring (0-100)
    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    competition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    saturation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    demand_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monetization_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Channel Creation Predictor
    prob_1000_subs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prob_10000_subs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prob_100000_subs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prob_1m_subs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="easy, medium, hard, very_hard"
    )
    growth_potential: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="low, medium, high, very_high"
    )
    audience_size_estimate: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="small, medium, large, massive"
    )
    expected_publishing_frequency: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    # Reasoning
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    data_sources: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # Action Items
    suggested_titles: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    suggested_thumbnail_text: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    suggested_tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    suggested_angles: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="new", comment="new, reviewed, actioned, dismissed"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Opportunity {self.opportunity_type}:{self.title} ({self.opportunity_score:.1f})>"


class ContentGap(BaseModel):
    """
    Content Gap Model
    Represents a detected gap between audience demand and content supply.
    """

    __tablename__ = "content_gaps"

    # Gap Details
    topic: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    niche: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Demand Metrics
    demand_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Number of requests/demands detected"
    )
    demand_growth_rate: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Growth rate of demand"
    )
    demand_urgency: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 urgency score"
    )

    # Supply Metrics
    existing_video_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Number of existing videos on this topic"
    )
    existing_channel_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Number of channels covering this topic"
    )
    top_video_views: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="Views of top video on this topic"
    )

    # Gap Score
    gap_score: Mapped[float] = mapped_column(
        Float, nullable=False, comment="0-100 gap score (higher = bigger opportunity)"
    )
    gap_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="underserved, unaddressed, growing_demand, new_topic",
    )

    # Optional foreign keys
    video_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Sources
    source_comments: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True, comment="Example comments showing demand"
    )
    source_platforms: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    video: Mapped[Optional["Video"]] = relationship(
        "Video", back_populates="content_gaps"
    )

    def __repr__(self) -> str:
        return f"<ContentGap {self.topic} (gap={self.gap_score:.1f})>"


class DemandSignal(BaseModel):
    """
    Demand Signal Model
    Represents a specific demand signal extracted from comments or other sources.
    """

    __tablename__ = "demand_signals"

    # Signal Details
    signal_text: Mapped[str] = mapped_column(Text, nullable=False)
    signal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="request, question, complaint, idea, pain_point, part2_request",
    )
    topic: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, index=True
    )
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Source
    comment_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="SET NULL"),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="youtube_comment, reddit, etc."
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Metrics
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    engagement: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Likes/upvotes on this signal"
    )
    urgency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Analysis
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_actionable: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    comment: Mapped[Optional["Comment"]] = relationship(
        "Comment", back_populates="demand_signals"
    )

    def __repr__(self) -> str:
        return f"<DemandSignal {self.signal_type}:{self.signal_text[:50]}>"


class ChannelInsight(BaseModel):
    """
    Channel Insight Model
    Stores computed insights about a channel's performance and strategy.
    """

    __tablename__ = "channel_insights"

    channel_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Growth Insights
    subscriber_growth_7d: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )
    subscriber_growth_30d: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )
    subscriber_growth_rate_7d: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    subscriber_growth_rate_30d: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    view_growth_7d: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    view_growth_30d: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Content Strategy
    avg_upload_frequency: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Videos per week"
    )
    best_posting_day: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    best_posting_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_video_duration: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Average duration in seconds"
    )
    top_content_types: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    top_title_patterns: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    top_thumbnail_patterns: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    top_tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # Performance
    avg_views_per_video: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    viral_video_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    viral_rate: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Percentage of videos that went viral"
    )

    # Competitor Analysis
    competitor_channels: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    competitive_advantage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_gaps_found: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # AI Analysis
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendations: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    ai_growth_strategy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="insights")

    def __repr__(self) -> str:
        return f"<ChannelInsight {self.channel_id}>"


class CompetitorAnalysis(BaseModel):
    """
    Competitor Analysis Model
    Stores analysis of a competitor channel relative to a tracked channel.
    """

    __tablename__ = "competitor_analyses"

    channel_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competitor_channel_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Comparison Metrics
    subscriber_gap: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    view_gap: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    growth_rate_comparison: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    engagement_comparison: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    upload_frequency_comparison: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    # Competitor Strategy
    competitor_strengths: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    competitor_weaknesses: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    competitor_title_patterns: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    competitor_thumbnail_patterns: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    competitor_content_strategy: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    competitor_publishing_schedule: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Insights
    insight_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    threat_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="low, medium, high, critical"
    )
    opportunities_identified: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship(
        "Channel",
        foreign_keys=[channel_id],
        back_populates="competitor_analyses",
    )
    competitor: Mapped["Channel"] = relationship(
        "Channel", foreign_keys=[competitor_channel_id]
    )

    def __repr__(self) -> str:
        return f"<CompetitorAnalysis {self.channel_id} vs {self.competitor_channel_id}>"


class CommentInsight(BaseModel):
    """
    Comment Insight Model
    Stores aggregated insights from comment analysis.
    """

    __tablename__ = "comment_insights"

    comment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Analysis
    insight_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="request, complaint, question, idea, pain_point, demand, sentiment",
    )
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Categorization
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    topics: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # Actionability
    is_actionable: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="low, medium, high, critical"
    )
    suggested_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    comment: Mapped["Comment"] = relationship("Comment", back_populates="insights")

    def __repr__(self) -> str:
        return f"<CommentInsight {self.insight_type}:{self.insight_text[:50]}>"


class VideoInsight(BaseModel):
    """
    Video Insight Model
    Stores computed insights about a video's performance.
    """

    __tablename__ = "video_insights"

    video_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Performance
    view_velocity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    like_velocity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment_velocity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retention_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    virality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Content Analysis
    title_effectiveness: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 how effective is the title"
    )
    thumbnail_effectiveness: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 how effective is the thumbnail"
    )
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    keyword_density: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Audience Insights
    audience_retention_points: Mapped[Optional[List[dict]]] = mapped_column(
        JSONB, nullable=True
    )
    top_comment_themes: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    audience_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI Analysis
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendations: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="insights")

    def __repr__(self) -> str:
        return f"<VideoInsight {self.video_id}>"


class NicheAnalysis(BaseModel):
    """
    Niche Analysis Model
    Stores comprehensive analysis results for a specific niche.
    """

    __tablename__ = "niche_analyses"

    niche: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, unique=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Market Size
    estimated_channel_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    estimated_video_count: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )
    estimated_total_views: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )
    estimated_monthly_search_volume: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )

    # Competition
    competition_level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="very_low, low, medium, high, very_high"
    )
    competition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    top_channels: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    channel_density: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Channels per search volume"
    )

    # Growth
    growth_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend_direction: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="declining, stable, growing, exploding"
    )
    seasonality: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Opportunity
    opportunity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monetization_potential: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="low, medium, high, very_high"
    )
    audience_demand: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="low, medium, high, very_high"
    )

    # Content Gaps
    content_gaps: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    underserved_topics: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    rising_keywords: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # AI Analysis
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendations: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<NicheAnalysis {self.niche}>"


class Idea(BaseModel):
    """
    Idea Model
    Stores generated content ideas from the Idea Generation Engine.
    """

    __tablename__ = "ideas"

    # Idea Details
    idea_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="channel_idea, video_idea, content_series, title, thumbnail_text",
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    niche: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Scoring
    potential_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 estimated potential"
    )
    viral_potential: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="0-100 estimated viral potential"
    )
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="easy, medium, hard"
    )

    # Context
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    related_opportunity_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Action
    status: Mapped[str] = mapped_column(
        String(20), default="generated", comment="generated, saved, actioned, dismissed"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Idea {self.idea_type}:{self.title[:50]}>"


class Report(BaseModel):
    """
    Report Model
    Stores generated reports of various types.
    """

    __tablename__ = "reports"

    # Report Details
    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="trend, competitor, opportunity, comment_intelligence, channel_launch, niche_analysis",
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Content
    content: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Full report data"
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_findings: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)

    # Export Formats
    markdown_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    json_export: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    csv_export_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    pdf_export_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="generated", comment="generated, sent, archived"
    )
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Report {self.report_type}:{self.title}>"


class Alert(BaseModel):
    """
    Alert Model
    Stores system alerts and notifications.
    """

    __tablename__ = "alerts"

    # Alert Details
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="opportunity_detected, saturation_increased, competitor_spike, trend_emerging, etc.",
    )
    severity: Mapped[str] = mapped_column(
        String(20), default="info", comment="info, warning, critical"
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Action
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_actioned: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Source
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    related_entity_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Alert {self.severity}:{self.title}>"


class User(BaseModel):
    """
    User Model
    Represents a platform user.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Account
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    api_key: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )

    # Preferences
    preferred_niches: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    notification_settings: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


class ScanJob(BaseModel):
    """
    Scan Job Model
    Tracks data collection and analysis jobs.
    """

    __tablename__ = "scan_jobs"

    # Job Details
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="global_scan, niche_scan, channel_scan, video_scan, comment_scan, trend_refresh",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="pending, running, completed, failed, cancelled",
    )
    niche: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Execution
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Results
    items_collected: Mapped[int] = mapped_column(Integer, default=0)
    items_processed: Mapped[int] = mapped_column(Integer, default=0)
    items_failed: Mapped[int] = mapped_column(Integer, default=0)

    # Celery Task ID
    celery_task_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<ScanJob {self.job_type}:{self.status}>"


class ApiUsage(BaseModel):
    """
    API Usage Model
    Tracks API quota usage for external services.
    """

    __tablename__ = "api_usage"

    service: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="youtube, reddit, news, etc."
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    requests_made: Mapped[int] = mapped_column(Integer, default=0)
    quota_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_limit: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("service", "date", name="uq_api_usage_service_date"),
    )

    def __repr__(self) -> str:
        return f"<ApiUsage {self.service}:{self.date.date()}>"
