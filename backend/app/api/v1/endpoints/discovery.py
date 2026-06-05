"""
YT Trend Hunter - Discovery Endpoints
Global Discovery Mode - scans YouTube across categories to find opportunities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.services.collectors.youtube import YouTubeAPIError, YouTubeCollector
from app.services.engines import (
    comment_engine,
    idea_engine,
    opportunity_engine,
    trend_engine,
)

router = APIRouter()

# Default categories for global discovery
DEFAULT_CATEGORIES = [
    "AI", "Technology", "Gaming", "Music", "Sports", "Football",
    "Finance", "Investing", "Education", "Business", "Startups",
    "Crypto", "Politics", "News", "Entertainment", "Movies", "TV",
    "Fitness", "Health", "Travel", "History", "Science",
    "Self Improvement", "Productivity", "Comedy",
]


@router.get("/global")
async def global_discovery(
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    limit: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """
    MODE 1: GLOBAL DISCOVERY MODE
    
    Scan YouTube globally across categories and identify the highest-potential
    opportunities. Returns trending topics, rising creators, content gaps,
    and channel creation predictions.
    """
    selected_categories = (
        [c.strip() for c in categories.split(",") if c.strip()]
        if categories
        else DEFAULT_CATEGORIES
    )

    collector = YouTubeCollector()
    all_opportunities = []

    try:
        for category in selected_categories[:limit]:
            # 1. Search YouTube for trending videos in this category
            videos = await collector.search_videos(
                query=category,
                max_results=10,
                order="viewCount",
            )

            if not videos:
                continue

            # 2. Get channel details for the video creators
            channel_ids = list(set(v.get("channel_id", "") for v in videos if v.get("channel_id")))
            channels = []
            for cid in channel_ids[:5]:
                ch = await collector.get_channel_info(cid)
                if ch:
                    channels.append(ch)

            # 3. Get comments from top videos for demand analysis
            all_comments = []
            for video in videos[:3]:
                video_id = video.get("video_id") or video.get("id", "")
                if isinstance(video_id, dict):
                    video_id = video_id.get("videoId", "")
                comments = await collector.get_video_comments(
                    video_id,
                    max_results=50,
                )
                all_comments.extend(comments)

            # 4. Run trend analysis
            trend_analysis = trend_engine.analyze_trend(
                videos=videos,
                channels=channels,
                comments=all_comments,
            )

            # 5. Run comment intelligence
            comment_analysis = comment_engine.analyze_comments_batch(all_comments)

            # 6. Calculate opportunity score
            trend_strength = trend_analysis.get("trend_strength", 50)
            competition = trend_analysis.get("competition_level", 50)
            saturation = trend_analysis.get("saturation_score", 50)
            demand = comment_analysis.get("demand_score", 50)

            scores = opportunity_engine.calculate_opportunity_score(
                trend_score=trend_strength,
                competition_score=competition,
                saturation_score=saturation,
                demand_score=demand,
                monetization_score=60,
            )

            # 7. Generate channel prediction
            prediction = opportunity_engine.calculate_channel_creation_prediction(
                niche=niche,
                trend_score=trend_strength,
                competition_score=competition,
                saturation_score=saturation,
                demand_score=demand,
                estimated_audience_size=100000,
                avg_channel_growth_rate=5.0,
                upload_frequency=3,
            )

            # 8. Generate ideas
            channel_ideas = idea_engine.generate_channel_ideas(category, count=3)
            video_ideas = idea_engine.generate_video_ideas(category, count=5)

            all_opportunities.append({
                "category": category,
                **scores,
                "trend_insights": trend_analysis.get("insights", []),
                "demand_signals": comment_analysis.get("demand_signals", [])[:5],
                "channel_prediction": prediction,
                "channel_ideas": channel_ideas,
                "video_ideas": video_ideas,
                "trending_topics": trend_analysis.get("trends", [])[:5],
            })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scanning category: {str(e)}",
        )
    finally:
        await collector.close()

    # Sort by opportunity score descending
    all_opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    return {
        "mode": "global_discovery",
        "categories_scanned": len(all_opportunities),
        "categories": [o["category"] for o in all_opportunities],
        "opportunities": all_opportunities[:limit],
        "summary": {
            "total_opportunities": len(all_opportunities),
            "highest_score_category": all_opportunities[0]["category"] if all_opportunities else None,
            "highest_score": all_opportunities[0].get("opportunity_score", 0) if all_opportunities else 0,
        },
    }


@router.get("/trending-topics")
async def get_trending_topics(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Get trending topics across YouTube.
    Optionally filter by category.
    """
    collector = YouTubeCollector()
    try:
        query = category or "trending"
        videos = await collector.search_videos(
            query=query,
            max_results=limit,
            order="viewCount",
        )

        # Analyze for trends
        analysis = trend_engine.analyze_trend(videos=videos, channels=[], comments=[])

        return {
            "category": category or "all",
            "trending_topics": analysis.get("trends", []),
            "total": len(analysis.get("trends", [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/rising-creators")
async def get_rising_creators(
    category: Optional[str] = Query(None),
    min_growth_rate: float = Query(10, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Find fastest-growing YouTube channels.
    Detect channels with unusual subscriber growth.
    """
    collector = YouTubeCollector()
    try:
        query = category or "trending creators"
        videos = await collector.search_videos(
            query=query,
            max_results=limit,
            order="viewCount",
        )

        # Get channel details
        channel_ids = list(set(v.get("channel_id", "") for v in videos if v.get("channel_id")))
        channels = []
        for cid in channel_ids[:limit]:
            ch = await collector.get_channel_info(cid)
            if ch:
                channels.append(ch)

        # Analyze for rising creators
        analysis = trend_engine.analyze_trend(videos=videos, channels=channels, comments=[])

        return {
            "category": category or "all",
            "min_growth_rate": min_growth_rate,
            "rising_creators": analysis.get("rising_channels", channels)[:limit],
            "total": min(len(channels), limit),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/content-gaps")
async def get_content_gaps(
    category: Optional[str] = Query(None),
    min_gap_score: float = Query(50, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Find content gaps - topics with high demand but low supply.
    """
    collector = YouTubeCollector()
    try:
        query = category or "trending"
        videos = await collector.search_videos(
            query=query,
            max_results=limit,
            order="viewCount",
        )

        # Get comments to find demand signals
        all_comments = []
        for video in videos[:5]:
            video_id = video.get("video_id") or video.get("id", "")
            if isinstance(video_id, dict):
                video_id = video_id.get("videoId", "")
            comments = await collector.get_video_comments(
                video_id,
                max_results=50,
            )
            all_comments.extend(comments)

        # Analyze comments for demand
        comment_analysis = comment_engine.analyze_comments_batch(all_comments)

        # Analyze trends for gaps
        trend_analysis = trend_engine.analyze_trend(videos=videos, channels=[], comments=all_comments)

        gaps = []
        for signal in comment_analysis.get("demand_signals", [])[:limit]:
            gap_score = trend_engine.calculate_content_gap_score(
                demand_score=signal.get("frequency", 50),
                supply_gap=70,
                demand_momentum=signal.get("momentum", 50),
            )
            gaps.append({
                "topic": signal.get("text", "Unknown"),
                "niche": category or "General",
                "demand_count": signal.get("frequency", 0),
                "existing_video_count": max(1, int(signal.get("frequency", 50) * (100 - gap_score) / 100)),
                "gap_score": round(gap_score, 1),
                "gap_type": "underserved" if gap_score > 70 else "growing_demand",
            })

        gaps.sort(key=lambda x: x["gap_score"], reverse=True)

        return {
            "category": category or "all",
            "min_gap_score": min_gap_score,
            "content_gaps": gaps[:limit],
            "total": len(gaps[:limit]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/channel-predictor")
async def channel_creation_predictor(
    niche: str = Query(..., description="Niche to analyze"),
    upload_frequency: int = Query(3, ge=1, le=14),
) -> Dict[str, Any]:
    """
    Channel Creation Predictor - flagship feature.
    Predict success probability for a new channel in any niche.
    Uses real YouTube data to calculate predictions.
    Requires a valid YOUTUBE_API_KEY in .env.
    """
    collector = YouTubeCollector()
    try:
        # 1. Search for existing content in this niche
        videos = await collector.search_videos(
            query=niche,
            max_results=20,
            order="viewCount",
        )

        # 2. Get channel details for competitors
        channel_ids = list(set(v.get("channel_id", "") for v in videos if v.get("channel_id")))
        channels = []
        for cid in channel_ids[:10]:
            ch = await collector.get_channel_info(cid)
            if ch:
                channels.append(ch)

        # 3. Get comments for demand analysis
        all_comments = []
        for video in videos[:5]:
            video_id = video.get("video_id") or video.get("id", "")
            if isinstance(video_id, dict):
                video_id = video_id.get("videoId", "")
            comments = await collector.get_video_comments(
                video_id,
                max_results=50,
            )
            all_comments.extend(comments)

        # 4. Calculate metrics from real data
        # Handle both YouTube API format and normalized format
        def _get_stat(channel_or_video, stat_name, default=0):
            """Extract stat from either YouTube API format or normalized format."""
            stats = channel_or_video.get("statistics", {})
            if isinstance(stats, dict):
                return int(stats.get(stat_name, default))
            return channel_or_video.get(stat_name, default)

        total_subscribers = sum(
            _get_stat(c, "subscriberCount") for c in channels
        )
        avg_subscribers = total_subscribers / max(len(channels), 1)
        total_videos = sum(
            _get_stat(c, "videoCount") for c in channels
        )
        total_views = sum(
            _get_stat(v, "viewCount") for v in videos
        )

        # 5. Calculate competition level
        competition_result = trend_engine.calculate_competition_level(
            channel_count=len(channels),
            avg_subscribers=avg_subscribers,
            total_videos=total_videos,
            niche_size=max(total_views, 100000),
        )

        # 6. Calculate audience demand from comments
        comment_analysis = comment_engine.analyze_comments_batch(all_comments)
        audience_demand = comment_analysis.get("demand_score", 50)

        # 7. Calculate content gap
        gap_score = trend_engine.calculate_content_gap_score(
            demand_count=int(audience_demand * 10),
            existing_video_count=max(1, total_videos),
            demand_growth_rate=50,
        )

        # 8. Generate channel creation prediction
        prediction = opportunity_engine.calculate_channel_creation_prediction(
            niche=niche,
            trend_score=trend_strength,
            competition_score=competition,
            saturation_score=saturation,
            demand_score=demand,
            estimated_audience_size=100000,
            avg_channel_growth_rate=5.0,
            upload_frequency=3,
        )

        # 9. Generate ideas
        channel_ideas = idea_engine.generate_channel_ideas(niche, count=5)
        video_ideas = idea_engine.generate_video_ideas(niche, count=10)

        prediction["channel_ideas"] = channel_ideas
        prediction["video_ideas"] = video_ideas
        prediction["competition_analysis"] = {
            "total_competitors": len(channels),
            "avg_subscribers": int(avg_subscribers),
            "total_videos_analyzed": len(videos),
            "top_competitors": [
                {
                    "name": c.get("snippet", {}).get("title", c.get("title", "Unknown")),
                    "subscribers": _get_stat(c, "subscriberCount"),
                }
                for c in channels[:5]
            ],
        }

        return prediction

    except YouTubeAPIError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "YouTube API quota exceeded",
                "message": str(e),
                "solution": "Get a new API key at https://console.cloud.google.com/ and update YOUTUBE_API_KEY in .env",
                "endpoints_that_still_work": [
                    "/health",
                    "/docs",
                    "/api/v1/reports/generate",
                    "/api/v1/ideas/underserved-niches",
                ],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()

