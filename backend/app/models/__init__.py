"""
YT Trend Hunter - Database Models
All SQLAlchemy models for the platform.
"""

from app.models.base import BaseModel, TimestampMixin, UUIDMixin
from app.models.channel import Channel
from app.models.video import Video
from app.models.comment import Comment
from app.models.analysis import (
    Alert,
    ApiUsage,
    ChannelInsight,
    CommentInsight,
    CompetitorAnalysis,
    ContentGap,
    DemandSignal,
    Idea,
    NicheAnalysis,
    Opportunity,
    Report,
    ScanJob,
    TrendSignal,
    User,
    VideoInsight,
)

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "Channel",
    "Video",
    "Comment",
    "TrendSignal",
    "Opportunity",
    "ContentGap",
    "DemandSignal",
    "ChannelInsight",
    "CompetitorAnalysis",
    "CommentInsight",
    "VideoInsight",
    "NicheAnalysis",
    "Idea",
    "Report",
    "Alert",
    "User",
    "ScanJob",
    "ApiUsage",
]
