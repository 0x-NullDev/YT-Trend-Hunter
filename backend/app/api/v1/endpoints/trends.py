"""Trends API endpoints."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def get_trends(
    category: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Get current trends across YouTube."""
    return {"category": category, "trends": [], "total": 0}


@router.get("/{trend_id}")
async def get_trend_detail(trend_id: str):
    """Get detailed information about a specific trend."""
    return {"trend_id": trend_id, "detail": "Trend detail endpoint"}

