"""Comments API endpoints."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def get_comments(
    video_id: str = Query(None),
    channel_id: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get comments with intelligence analysis."""
    return {"comments": [], "total": 0, "intelligence": {}}


@router.post("/analyze")
async def analyze_comments_batch():
    """Analyze a batch of comments for intelligence signals."""
    return {"status": "pending", "message": "Comment analysis endpoint"}

