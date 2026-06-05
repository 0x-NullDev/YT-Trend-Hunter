"""
YT Trend Hunter - Niche Analysis Endpoints
MODE 2: NICHE FOCUS MODE - Deep analysis inside a specific niche.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.collectors.youtube import YouTubeCollector
from app.services.engines import (
    comment_engine,
    idea_engine,
    opportunity_engine,
    trend_engine,
)

router = APIRouter()


@router.get("/analyze/{niche}")
async def analyze_niche(
    niche: str,
    include_ideas: bool = Query(True, description="Generate content ideas"),
    include_competitors: bool = Query(True, description="Analyze competitors"),
    include_comments: bool = Query(True, description="Analyze comments"),
) -> Dict[str, Any]:
    """
    MODE 2: NICHE FOCUS MODE
    
    Perform deep analysis inside a specific niche.
    Discovers emerging trends, rising creators, content gaps,
    audience demand, and underserved topics.
    Uses real YouTube data.
    """
    collector = YouTubeCollector()
    try:
        # 1. Search YouTube for niche content
        videos = await collector.search_videos(
            query=niche,
            max_results=20,
            order="viewCount",
        )

        # 2. Get channel details
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

        # 4. Run trend analysis
        trend_analysis = trend_engine.analyze_trend(
            videos=videos,
            channels=channels,
            comments=all_comments,
        )

        # 5. Run comment intelligence
        comment_analysis = comment_engine.analyze_comments_batch(all_comments)

        # 6. Calculate competition
        def _get_stat(channel_or_video, stat_name, default=0):
            """Extract stat from either YouTube API format or normalized format."""
            stats = channel_or_video.get("statistics", {})
            if isinstance(stats, dict):
                return int(stats.get(stat_name, default))
            return channel_or_video.get(stat_name, default)

        total_subscribers = sum(_get_stat(c, "subscriberCount") for c in channels)
        avg_subscribers = total_subscribers / max(len(channels), 1)
        total_videos = sum(_get_stat(c, "videoCount") for c in channels)
        total_views = sum(_get_stat(v, "viewCount") for v in videos)

        competition_result = trend_engine.calculate_competition_level(
            channel_count=len(channels),
            avg_subscribers=avg_subscribers,
            total_videos=total_videos,
            niche_size=max(total_views, 100000),
        )

        # 7. Calculate opportunity
        trend_strength = trend_analysis.get("trend_strength", 50)
        competition = competition_result.get("competition_level", 50)
        saturation = competition_result.get("saturation_score", 50)
        demand = comment_analysis.get("demand_score", 50)

        opportunity = opportunity_engine.calculate_opportunity_score(
            trend_score=trend_strength,
            competition_score=competition,
            saturation_score=saturation,
            demand_score=demand,
            monetization_score=60,
        )

        # 8. Channel prediction
        gap_score = trend_engine.calculate_content_gap_score(
            demand_score=demand,
            supply_gap=max(0, 100 - saturation),
            demand_momentum=50,
        )

        prediction = opportunity_engine.calculate_channel_creation_prediction(niche=niche, trend_score=trend_strength, competition_score=competition, saturation_score=saturation, demand_score=demand, estimated_audience_size=100000, avg_channel_growth_rate=5.0, upload_frequency=3)

        # 9. Build result
        def _get_channel_name(c):
            return c.get("snippet", {}).get("title", c.get("title", "Unknown"))
        
        def _get_channel_country(c):
            snippet = c.get("snippet", {})
            return snippet.get("country", c.get("country", "Unknown"))

        result = {
            "niche": niche,
            "market_overview": {
                "trend_direction": "growing" if trend_strength > 60 else "stable",
                "competition_level": "LOW" if competition < 30 else "MEDIUM" if competition < 60 else "HIGH",
                "audience_demand": "HIGH" if demand > 70 else "MEDIUM" if demand > 40 else "LOW",
                "difficulty": prediction.get("difficulty", "MEDIUM"),
                "growth_potential": prediction.get("growth_potential", "MODERATE"),
                "total_videos_analyzed": len(videos),
                "total_channels_analyzed": len(channels),
                "total_comments_analyzed": len(all_comments),
            },
            "scores": opportunity,
            "channel_prediction": prediction,
            "trending_topics": trend_analysis.get("trends", [])[:10],
            "rising_creators": [
                {
                    "name": _get_channel_name(c),
                    "subscribers": _get_stat(c, "subscriberCount"),
                    "videos": _get_stat(c, "videoCount"),
                    "views": _get_stat(c, "viewCount"),
                }
                for c in sorted(channels, key=lambda x: _get_stat(x, "subscriberCount"), reverse=True)[:10]
            ],
        }

        if include_competitors:
            result["competitor_analysis"] = {
                "top_competitors": [
                    {
                        "name": _get_channel_name(c),
                        "subscribers": _get_stat(c, "subscriberCount"),
                        "videos": _get_stat(c, "videoCount"),
                        "country": _get_channel_country(c),
                    }
                    for c in channels[:5]
                ],
                "market_concentration": "Low - Room for new entrants" if competition < 40 else "Medium" if competition < 70 else "High - Saturated",
                "content_strategy_insights": trend_analysis.get("insights", []),
            }

        if include_comments:
            result["comment_intelligence"] = {
                "total_comments_analyzed": len(all_comments),
                "signals": {
                    "requests": {"count": len(comment_analysis.get("requests", [])), "percentage": round(len(comment_analysis.get("requests", [])) / max(len(all_comments), 1) * 100, 1)},
                    "questions": {"count": len(comment_analysis.get("questions", [])), "percentage": round(len(comment_analysis.get("questions", [])) / max(len(all_comments), 1) * 100, 1)},
                    "ideas": {"count": len(comment_analysis.get("ideas", [])), "percentage": round(len(comment_analysis.get("ideas", [])) / max(len(all_comments), 1) * 100, 1)},
                    "pain_points": {"count": len(comment_analysis.get("pain_points", [])), "percentage": round(len(comment_analysis.get("pain_points", [])) / max(len(all_comments), 1) * 100, 1)},
                },
                "top_requests": comment_analysis.get("requests", [])[:5],
                "demand_signals": comment_analysis.get("demand_signals", [])[:10],
            }

        if include_ideas:
            trends = result.get("trending_topics", [])
            gaps = []
            for signal in comment_analysis.get("demand_signals", [])[:5]:
                gs = trend_engine.calculate_content_gap_score(
                    demand_score=signal.get("frequency", 50),
                    supply_gap=max(0, 100 - saturation),
                    demand_momentum=50,
                )
                gaps.append({"topic": signal.get("text", "Unknown"), "gap_score": gs})

            signals = [{"topic": g["topic"], "urgency_score": g["gap_score"]} for g in gaps]

            result["ideas"] = {
                "channel_ideas": idea_engine.generate_channel_ideas(
                    niche=niche,
                    trends=result.get("trending_topics", []),
                    demand_signals=comment_analysis.get("demand_signals", []),
                    content_gaps=gaps,
                    top_n=5,
                ),
                "video_ideas": idea_engine.generate_video_ideas(
                    niche=niche,
                    trends=result.get("trending_topics", []),
                    demand_signals=comment_analysis.get("demand_signals", []),
                    content_gaps=gaps,
                    top_n=10,
                ),
                "viral_opportunities": idea_engine.generate_viral_opportunities(
                    niche=niche,
                    trends=result.get("trending_topics", []),
                    demand_signals=comment_analysis.get("demand_signals", []),
                    top_n=5,
                ),
                "underserved_niches": idea_engine.generate_underserved_niches(
                    content_gaps=gaps,
                    top_n=5,
                ),
            }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/trends/{niche}")
async def get_niche_trends(
    niche: str,
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Get trending topics within a specific niche using real YouTube data."""
    collector = YouTubeCollector()
    try:
        videos = await collector.search_videos(
            query=niche,
            max_results=limit,
            order="viewCount",
        )
        analysis = trend_engine.analyze_trend(videos=videos, channels=[], comments=[])
        return {
            "niche": niche,
            "trends": analysis.get("trends", [])[:limit],
            "total": min(len(analysis.get("trends", [])), limit),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/creators/{niche}")
async def get_niche_creators(
    niche: str,
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Get rising creators within a specific niche."""
    collector = YouTubeCollector()
    try:
        videos = await collector.search_videos(
            query=niche,
            max_results=limit,
            order="viewCount",
        )
        channel_ids = list(set(v.get("channel_id", "") for v in videos if v.get("channel_id")))
        channels = []
        for cid in channel_ids[:limit]:
            ch = await collector.get_channel_info(cid)
            if ch:
                channels.append(ch)

        def _get_stat(c, stat_name, default=0):
            stats = c.get("statistics", {})
            if isinstance(stats, dict):
                return int(stats.get(stat_name, default))
            return c.get(stat_name, default)

        return {
            "niche": niche,
            "creators": [
                {
                    "name": c.get("snippet", {}).get("title", c.get("title", "Unknown")),
                    "subscribers": _get_stat(c, "subscriberCount"),
                    "videos": _get_stat(c, "videoCount"),
                    "views": _get_stat(c, "viewCount"),
                    "country": c.get("snippet", {}).get("country", c.get("country", "Unknown")),
                }
                for c in sorted(channels, key=lambda x: _get_stat(x, "subscriberCount"), reverse=True)[:limit]
            ],
            "total": min(len(channels), limit),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/gaps/{niche}")
async def get_niche_gaps(
    niche: str,
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Get content gaps within a specific niche."""
    collector = YouTubeCollector()
    try:
        videos = await collector.search_videos(
            query=niche,
            max_results=limit,
            order="viewCount",
        )

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

        comment_analysis = comment_engine.analyze_comments_batch(all_comments)

        gaps = []
        for signal in comment_analysis.get("demand_signals", [])[:limit]:
            gap_score = trend_engine.calculate_content_gap_score(
                demand_score=signal.get("frequency", 50),
                supply_gap=70,
                demand_momentum=signal.get("momentum", 50),
            )
            gaps.append({
                "topic": signal.get("text", "Unknown"),
                "niche": niche,
                "demand_count": signal.get("frequency", 0),
                "gap_score": round(gap_score, 1),
                "gap_type": "underserved" if gap_score > 70 else "growing_demand",
            })

        gaps.sort(key=lambda x: x["gap_score"], reverse=True)
        return {
            "niche": niche,
            "gaps": gaps[:limit],
            "total": len(gaps[:limit]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.get("/demand/{niche}")
async def get_niche_demand(
    niche: str,
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Get audience demand signals within a specific niche."""
    collector = YouTubeCollector()
    try:
        videos = await collector.search_videos(
            query=niche,
            max_results=10,
            order="viewCount",
        )

        all_comments = []
        for video in videos[:5]:
            video_id = video.get("video_id") or video.get("id", "")
            if isinstance(video_id, dict):
                video_id = video_id.get("videoId", "")
            comments = await collector.get_video_comments(
                video_id,
                max_results=100,
            )
            all_comments.extend(comments)

        comment_analysis = comment_engine.analyze_comments_batch(all_comments)

        return {
            "niche": niche,
            "demand_signals": comment_analysis.get("demand_signals", [])[:limit],
            "total_comments_analyzed": len(all_comments),
            "total": min(len(comment_analysis.get("demand_signals", [])), limit),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await collector.close()


@router.post("/analyze-comments")
async def analyze_comments(
    comments: List[str],
) -> Dict[str, Any]:
    """
    Analyze a batch of comments for intelligence signals.
    Extracts requests, complaints, questions, ideas, and pain points.
    """
    comment_dicts = [{"text": c} for c in comments]
    return comment_engine.analyze_comments_batch(comment_dicts)

