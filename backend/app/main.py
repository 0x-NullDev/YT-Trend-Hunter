"""
YT Trend Hunter - Main Application
FastAPI application entry point with middleware, routers, and startup/shutdown hooks.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.database import database
from app.core.logging import setup_logging
from app.core.redis_client import redis_client
from app.core.security import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler for startup/shutdown."""
    # Startup
    setup_logging()
    logger.info("🚀 YT Trend Hunter starting up...")

    # Initialize database
    await database.initialize()
    logger.info("✅ Database initialized")

    # Initialize Redis
    await redis_client.initialize()
    logger.info("✅ Redis initialized")

    yield

    # Shutdown
    logger.info("🛑 YT Trend Hunter shutting down...")
    await database.close()
    await redis_client.close()
    logger.info("✅ Connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered YouTube Opportunity Discovery Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiter
rate_limiter = RateLimiter()


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting."""
    client_ip = request.client.host if request.client else "unknown"
    is_limited, remaining = await rate_limiter.check_rate_limit(client_ip)

    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": 60,
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# =========================================================================
# Health Check
# =========================================================================


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV.value,
        "database": "connected" if database.is_connected else "disconnected",
        "redis": "connected" if redis_client.is_connected else "disconnected",
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered YouTube Opportunity Discovery Platform",
        "docs": "/docs",
        "health": "/health",
    }


# =========================================================================
# Import and include routers
# =========================================================================

# Import routers here to avoid circular imports
from app.api.v1.router import api_v1_router

app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="info",
    )
