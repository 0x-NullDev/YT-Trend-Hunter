"""
YT Trend Hunter - API v1 Router
Main API router that includes all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    discovery,
    niche,
    trends,
    opportunities,
    channels,
    videos,
    comments,
    ideas,
    reports,
    alerts,
    users,
    analysis,
)

api_v1_router = APIRouter()

# Include all endpoint routers
api_v1_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
api_v1_router.include_router(niche.router, prefix="/niche", tags=["Niche Analysis"])
api_v1_router.include_router(trends.router, prefix="/trends", tags=["Trends"])
api_v1_router.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
api_v1_router.include_router(channels.router, prefix="/channels", tags=["Channels"])
api_v1_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_v1_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_v1_router.include_router(ideas.router, prefix="/ideas", tags=["Ideas"])
api_v1_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_v1_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
