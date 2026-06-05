"""Opportunities API endpoints."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def get_opportunities(
    niche: str = Query(None),
    min_score: float = Query(50, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
):
    """Get ranked content opportunities."""
    return {"niche": niche, "opportunities": [], "total": 0}


@router.get("/{opportunity_id}")
async def get_opportunity_detail(opportunity_id: str):
    """Get detailed information about a specific opportunity."""
    return {"opportunity_id": opportunity_id, "detail": "Opportunity detail endpoint"}

