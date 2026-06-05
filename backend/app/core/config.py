"""
YT Trend Hunter - Application Configuration
Centralized configuration management using pydantic-settings.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    """Application environment enum."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class AIProvider(str, Enum):
    """Supported AI providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LogFormat(str, Enum):
    """Log format options."""
    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values can be overridden via .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # Application
    # =========================================================================
    APP_NAME: str = "YT Trend Hunter"
    APP_VERSION: str = "1.0.0"
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-me-to-a-random-secret-key"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.APP_CORS_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == AppEnvironment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == AppEnvironment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == AppEnvironment.TESTING

    # =========================================================================
    # Database - PostgreSQL
    # =========================================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/yt_trend_hunter"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/yt_trend_hunter"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # =========================================================================
    # Redis - Cache & Task Queue
    # =========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300
    REDIS_CACHE_PREFIX: str = "ytth:"

    # =========================================================================
    # Celery - Task Queue
    # =========================================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: str = "json"
    CELERY_TIMEZONE: str = "UTC"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3000

    # =========================================================================
    # Elasticsearch - Search Engine
    # =========================================================================
    ELASTICSEARCH_HOSTS: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "ytth_"
    ELASTICSEARCH_SHARDS: int = 3
    ELASTICSEARCH_REPLICAS: int = 1

    @property
    def elasticsearch_hosts_list(self) -> List[str]:
        """Parse Elasticsearch hosts string into list."""
        return [host.strip() for host in self.ELASTICSEARCH_HOSTS.split(",")]

    # =========================================================================
    # YouTube Data API v3
    # =========================================================================
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_API_QUOTA_LIMIT: int = 10000
    YOUTUBE_API_QUOTA_SAFETY_MARGIN: float = 0.8
    YOUTUBE_API_MAX_RESULTS: int = 50
    YOUTUBE_API_MAX_COMMENTS: int = 500
    YOUTUBE_API_RATE_LIMIT: float = 1.0

    # =========================================================================
    # Google Trends
    # =========================================================================
    GOOGLE_TRENDS_ENABLED: bool = True
    GOOGLE_TRENDS_HL: str = "en-US"
    GOOGLE_TRENDS_TZ: int = 360
    GOOGLE_TRENDS_GEO: str = "US"

    # =========================================================================
    # Reddit API
    # =========================================================================
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "YT_Trend_Hunter/1.0"
    REDDIT_RATE_LIMIT: float = 1.0

    # =========================================================================
    # News API
    # =========================================================================
    NEWS_API_KEY: str = ""
    NEWS_API_RATE_LIMIT: float = 1.0

    # =========================================================================
    # AI Providers
    # =========================================================================

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 4096
    DEEPSEEK_TEMPERATURE: float = 0.7

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.7

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.7

    # Ollama (Local)
    OLLAMA_API_BASE: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_MAX_TOKENS: int = 4096
    OLLAMA_TEMPERATURE: float = 0.7

    # Default AI Provider
    AI_DEFAULT_PROVIDER: AIProvider = AIProvider.DEEPSEEK

    # =========================================================================
    # Reporting
    # =========================================================================
    REPORT_OUTPUT_DIR: str = "./reports"
    REPORT_MAX_RETENTION_DAYS: int = 90
    REPORT_AUTO_GENERATE: bool = True

    # =========================================================================
    # Automation & Scheduling
    # =========================================================================
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_GLOBAL_SCAN_INTERVAL_HOURS: int = 24
    SCHEDULER_NICHE_SCAN_INTERVAL_HOURS: int = 12
    SCHEDULER_TREND_REFRESH_INTERVAL_HOURS: int = 6
    SCHEDULER_COMPETITOR_SCAN_INTERVAL_HOURS: int = 24
    SCHEDULER_COMMENT_SCAN_INTERVAL_HOURS: int = 48

    # =========================================================================
    # Alerts & Notifications
    # =========================================================================
    ALERTS_ENABLED: bool = True
    ALERTS_EMAIL_ENABLED: bool = False
    ALERTS_SLACK_ENABLED: bool = False
    ALERTS_DISCORD_ENABLED: bool = False
    ALERTS_SLACK_WEBHOOK_URL: str = ""
    ALERTS_DISCORD_WEBHOOK_URL: str = ""
    ALERTS_SMTP_HOST: str = ""
    ALERTS_SMTP_PORT: int = 587
    ALERTS_SMTP_USER: str = ""
    ALERTS_SMTP_PASSWORD: str = ""
    ALERTS_EMAIL_FROM: str = ""
    ALERTS_EMAIL_TO: str = ""

    # =========================================================================
    # Rate Limiting
    # =========================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # =========================================================================
    # Logging
    # =========================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: LogFormat = LogFormat.JSON
    LOG_FILE: str = "./logs/yt_trend_hunter.log"

    # =========================================================================
    # Frontend
    # =========================================================================
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000/api/v1"
    NEXT_PUBLIC_APP_URL: str = "http://localhost:3000"


# Global settings instance
settings = Settings()

# Ensure log directory exists
log_path = Path(settings.LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)

# Ensure report directory exists
report_path = Path(settings.REPORT_OUTPUT_DIR)
report_path.mkdir(parents=True, exist_ok=True)
