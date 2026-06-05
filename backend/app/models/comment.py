"""
YT Trend Hunter - Comment Model
Represents a YouTube comment analyzed by the system.
This is one of the most important data sources for the Comment Intelligence Engine.
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
    from app.models.analysis import (
        CommentInsight,
        DemandSignal,
    )


class Comment(BaseModel):
    """YouTube comment analyzed by the system."""

    __tablename__ = "comments"

    # YouTube Data
    youtube_comment_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    video_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_comment_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Comment Content
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_channel_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_original: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Comment Statistics
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    is_reply: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at_yt: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Sentiment & Analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="-1.0 (negative) to 1.0 (positive)"
    )
    sentiment_label: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="positive, negative, neutral, mixed"
    )
    toxicity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    subjectivity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Comment Intelligence
    is_request: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Is this a request for content?"
    )
    is_complaint: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Is this a complaint?"
    )
    is_question: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Is this a question?"
    )
    is_idea: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Does this contain an idea?"
    )
    is_pain_point: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Does this express a pain point?"
    )
    is_demand: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Does this express unmet demand?"
    )
    is_part2_request: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Is this a request for part 2?"
    )

    # Extracted Entities
    extracted_topics: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    extracted_keywords: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    extracted_requests: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True
    )
    named_entities: Mapped[Optional[List[dict]]] = mapped_column(
        JSONB, nullable=True
    )

    # Metadata
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="comments")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="comments")
    insights: Mapped[List["CommentInsight"]] = relationship(
        "CommentInsight", back_populates="comment", cascade="all, delete-orphan"
    )
    demand_signals: Mapped[List["DemandSignal"]] = relationship(
        "DemandSignal", back_populates="comment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Comment {self.youtube_comment_id} by {self.author_name}>"
