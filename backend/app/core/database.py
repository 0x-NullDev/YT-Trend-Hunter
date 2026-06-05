"""
YT Trend Hunter - Database Configuration
Async SQLAlchemy engine and session management with PostgreSQL.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from loguru import logger
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = metadata


class DatabaseManager:
    """
    Manages database engine, sessions, and lifecycle.
    Provides async context manager support for FastAPI lifespan.
    """

    def __init__(self):
        self._engine = None
        self._session_factory = None
        self.is_connected = False

    async def initialize(self):
        """Initialize database engine and session factory."""
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.is_development,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        self.is_connected = True
        logger.info("Database engine initialized")

    async def close(self):
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self.is_connected = False
            logger.info("Database connections closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency that provides a database session.
        Used by FastAPI dependency injection.
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_db(self) -> AsyncIterator[AsyncSession]:
        """
        Context manager for database sessions.
        Used in background tasks and scripts.
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_all_tables(self):
        """Create all database tables."""
        if not self._engine:
            raise RuntimeError("Database not initialized.")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    async def check_health(self) -> bool:
        """Check database connectivity."""
        if not self._engine:
            return False
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
database = DatabaseManager()
