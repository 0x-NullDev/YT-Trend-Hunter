"""
YT Trend Hunter - Celery Worker
Task queue for background processing, scheduled scans, and async operations.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from celery import Celery
from celery.schedules import crontab
from loguru import logger

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "yt_trend_hunter",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scan_tasks",
        "app.tasks.analysis_tasks",
        "app.tasks.report_tasks",
        "app.tasks.alert_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
)

# =============================================================================
# Scheduled Tasks (Celery Beat)
# =============================================================================

celery_app.conf.beat_schedule = {
    # Daily global scan
    "daily-global-scan": {
        "task": "app.tasks.scan_tasks.run_global_scan",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        "options": {"queue": "scans"},
    },
    # Hourly trending topics update
    "hourly-trending-update": {
        "task": "app.tasks.scan_tasks.update_trending_topics",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"queue": "scans"},
    },
    # Daily niche analysis for tracked niches
    "daily-niche-analysis": {
        "task": "app.tasks.analysis_tasks.run_niche_analysis",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
        "options": {"queue": "analysis"},
    },
    # Weekly competitor analysis
    "weekly-competitor-analysis": {
        "task": "app.tasks.analysis_tasks.run_competitor_analysis",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),  # Monday 4 AM
        "options": {"queue": "analysis"},
    },
    # Daily comment intelligence
    "daily-comment-intelligence": {
        "task": "app.tasks.analysis_tasks.run_comment_intelligence",
        "schedule": crontab(hour=5, minute=0),  # 5 AM daily
        "options": {"queue": "analysis"},
    },
    # Weekly opportunity report
    "weekly-opportunity-report": {
        "task": "app.tasks.report_tasks.generate_weekly_report",
        "schedule": crontab(hour=6, minute=0, day_of_week=0),  # Sunday 6 AM
        "options": {"queue": "reports"},
    },
    # Check for alerts every 30 minutes
    "check-alerts": {
        "task": "app.tasks.alert_tasks.check_alerts",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": "alerts"},
    },
}


@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """Debug task to verify Celery is working."""
    logger.info(f"Celery worker is running. Request: {self.request!r}")
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
