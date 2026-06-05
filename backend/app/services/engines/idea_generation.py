"""
YT Trend Hunter - Idea Generation Engine
Generates actionable content ideas based on detected opportunities, trends, and demand signals.

Outputs:
- TOP 10 CHANNEL IDEAS
- TOP 25 VIDEO IDEAS
- TOP 10 VIRAL OPPORTUNITIES
- TOP 10 UNDERSERVED NICHES
- Content series recommendations
- Title suggestions
- Thumbnail text suggestions
- Publishing plans
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from loguru import logger


class IdeaGenerationEngine:
    """
    Idea Generation Engine
    Generates creative content ideas backed by data from the intelligence engines.
    """

    # Title templates for different content types
    TITLE_TEMPLATES = {
        "tutorial": [
            "How to {topic} in {year}",
            "{topic} for Beginners: Complete Guide",
            "The Ultimate {topic} Tutorial",
            "{topic} Explained in {minutes} Minutes",
            "Learn {topic} Fast: Step by Step Guide",
            "{topic} Masterclass: From Zero to Hero",
            "I Tried {topic} for {days} Days",
        ],
        "review": [
            "{topic} Review: Is It Worth It?",
            "I Tested {topic} So You Don't Have To",
            "{topic} vs {competitor}: Which Is Better?",
            "Honest {topic} Review After {months} Months",
            "Don't Buy {topic} Until You Watch This",
        ],
        "comparison": [
            "{topic} vs {competitor}: The Ultimate Comparison",
            "{topic} vs {competitor} vs {competitor2}: Which Wins?",
            "{topic} Alternatives You Need to Try",
            "Is {topic} Better Than {competitor}?",
        ],
        "list": [
            "Top {number} {topic} Tips You Need to Know",
            "{number} {topic} Mistakes That Are Costing You",
            "The {number} Best {topic} Tools in {year}",
            "{number} {topic} Secrets Experts Won't Tell You",
            "Top {number} {topic} Trends in {year}",
        ],
        "story": [
            "I Tried {topic} for {days} Days and Here's What Happened",
            "My {topic} Journey: From Beginner to Pro",
            "The Day I Discovered {topic} Changed Everything",
            "How {topic} Made Me {result} in {timeframe}",
        ],
        "controversial": [
            "Why {topic} Is Overrated",
            "The Truth About {topic} Nobody Talks About",
            "Why {topic} Is a Scam",
            "Unpopular Opinion: {topic} Is Not Worth It",
            "Stop Doing {topic} Wrong",
        ],
        "news": [
            "Breaking: {topic} Just Changed Everything",
            "{topic} Update: What You Need to Know",
            "The {topic} Revolution Is Here",
            "Why {topic} Is Going to Be Huge in {year}",
        ],
        "question": [
            "Can {topic} Really {result}?",
            "Is {topic} Worth Your Time in {year}?",
            "What Happens When You {topic} Every Day?",
            "Should You Start {topic} in {year}?",
        ],
    }

    # Thumbnail text templates
    THUMBNAIL_TEMPLATES = [
        "{topic}? (SHOCKING)",
        "I Tried {topic}",
        "{topic} EXPOSED",
        "STOP {topic}",
        "{topic} = GAME OVER",
        "THE TRUTH ABOUT {topic}",
        "Why {topic}?",
        "{topic} CHANGED MY LIFE",
        "DON'T {topic}",
        "{topic} IS OVER",
        "{topic} WORTH IT?",
        "{number} {topic} TIPS",
        "{topic} FOR BEGINNERS",
        "I FOUND {topic}",
    ]

    # Content series templates
    SERIES_TEMPLATES = [
        "{topic} for Beginners: Complete Series",
        "Mastering {topic}: {parts}-Part Series",
        "{topic} Explained: From A to Z",
        "The {topic} Blueprint: {days}-Day Challenge",
        "{topic} Deep Dive: Weekly Breakdown",
        "{topic} Case Studies: Real Examples",
        "{topic} Myths vs Facts: Full Series",
    ]

    def __init__(self):
        self.logger = logger.bind(engine="idea_generation")

    def generate_channel_ideas(
        self,
        niche: str,
        trends: List[str],
        demand_signals: List[Dict[str, Any]],
        content_gaps: List[Dict[str, Any]],
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate channel ideas based on niche analysis.
        
        Args:
            niche: Target niche
            trends: List of trending topics
            demand_signals: List of demand signals
            content_gaps: List of content gaps
            top_n: Number of ideas to generate
            
        Returns:
            List of channel idea dicts
        """
        ideas = []

        # Generate from content gaps
        for gap in content_gaps[:5]:
            topic = gap.get("topic", "")
            if topic:
                ideas.append({
                    "idea_type": "channel_idea",
                    "title": f"{topic} Channel",
                    "description": f"A dedicated channel focused on {topic}. "
                                   f"High demand ({gap.get('demand_count', 0)} signals) "
                                   f"with low competition.",
                    "niche": niche,
                    "potential_score": min(gap.get("gap_score", 50) * 1.1, 100),
                    "source": "content_gap",
                    "reasoning": f"Content gap detected: {gap.get('demand_count', 0)} "
                                f"audience requests but only {gap.get('existing_video_count', 0)} videos exist.",
                })

        # Generate from trend combinations
        for i, trend in enumerate(trends[:5]):
            trend_title = trend if isinstance(trend, str) else trend.get("title", str(trend))
            for j, trend2 in enumerate(trends[i + 1 : i + 3]):
                trend2_title = trend2 if isinstance(trend2, str) else trend2.get("title", str(trend2))
                combined = f"{trend_title} + {trend2_title}"
                ideas.append({
                    "idea_type": "channel_idea",
                    "title": f"{combined} Channel",
                    "description": f"A unique channel combining {trend_title} and {trend2_title}. "
                                   f"Both trends are rising with no dedicated combined channel.",
                    "niche": niche,
                    "potential_score": random.uniform(65, 90),
                    "source": "trend_combination",
                    "reasoning": f"Combining '{trend_title}' and '{trend2_title}' creates a unique "
                                f"positioning with no direct competitors.",
                })

        # Generate from demand signals
        for signal in demand_signals[:5]:
            topic = signal.get("text", signal.get("topic", ""))
            if topic and len(topic) > 5:
                ideas.append({
                    "idea_type": "channel_idea",
                    "title": f"{topic} - Deep Dive Channel",
                    "description": f"A channel dedicated to {topic}. "
                                   f"Audience is actively requesting this content.",
                    "niche": niche,
                    "potential_score": min(signal.get("urgency_score", 50) * 1.2, 100),
                    "source": "audience_demand",
                    "reasoning": f"Audience demand detected: {signal.get('demand_count', 0)} "
                                f"requests for content about {topic}.",
                })

        # Rank and return top N
        ideas.sort(key=lambda x: x.get("potential_score", 0), reverse=True)
        return ideas[:top_n]

    def generate_video_ideas(
        self,
        niche: str,
        trends: List[str],
        demand_signals: List[Dict[str, Any]],
        content_gaps: List[Dict[str, Any]],
        top_n: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Generate video ideas based on niche analysis.
        
        Args:
            niche: Target niche
            trends: List of trending topics
            demand_signals: List of demand signals
            content_gaps: List of content gaps
            top_n: Number of ideas to generate
            
        Returns:
            List of video idea dicts
        """
        ideas = []

        # Generate from demand signals
        for signal in demand_signals[:10]:
            topic = signal.get("text", signal.get("topic", ""))
            if topic:
                title = self._generate_title(topic, niche)
                ideas.append({
                    "idea_type": "video_idea",
                    "title": title,
                    "description": f"Video addressing audience demand for '{topic}'",
                    "niche": niche,
                    "potential_score": min(signal.get("urgency_score", 50) * 1.1, 100),
                    "source": "audience_request",
                    "reasoning": f"Direct audience request: '{signal.get('example_texts', [''])[0][:100]}'",
                    "suggested_thumbnail": self._generate_thumbnail_text(topic),
                })

        # Generate from content gaps
        for gap in content_gaps[:10]:
            topic = gap.get("topic", "")
            if topic:
                title = self._generate_title(topic, niche, content_type="tutorial")
                ideas.append({
                    "idea_type": "video_idea",
                    "title": title,
                    "description": f"Fill content gap: {topic}",
                    "niche": niche,
                    "potential_score": gap.get("gap_score", 50),
                    "source": "content_gap",
                    "reasoning": f"Content gap: {gap.get('demand_count', 0)} demand signals, "
                                f"only {gap.get('existing_video_count', 0)} existing videos.",
                    "suggested_thumbnail": self._generate_thumbnail_text(topic),
                })

        # Generate from trends
        for trend in trends[:10]:
            trend_title = trend if isinstance(trend, str) else trend.get("title", str(trend))
            title = self._generate_title(trend_title, niche, content_type="news")
            ideas.append({
                "idea_type": "video_idea",
                "title": title,
                "description": f"Capitalize on rising trend: {trend_title}",
                "niche": niche,
                "potential_score": random.uniform(60, 85),
                "source": "trending_topic",
                "reasoning": f"'{trend_title}' is a rising trend in {niche} with increasing search volume.",
                "suggested_thumbnail": self._generate_thumbnail_text(trend_title),
            })

        # Generate viral-style ideas
        for trend in trends[:5]:
            trend_title = trend if isinstance(trend, str) else trend.get("title", str(trend))
            title = self._generate_title(trend_title, niche, content_type="controversial")
            ideas.append({
                "idea_type": "video_idea",
                "title": title,
                "description": f"Viral potential content about {trend_title}",
                "niche": niche,
                "potential_score": random.uniform(70, 95),
                "source": "viral_potential",
                "reasoning": f"Controversial/hot take format on '{trend_title}' has high viral potential.",
                "suggested_thumbnail": self._generate_thumbnail_text(trend_title, style="viral"),
            })

        # Rank and return top N
        ideas.sort(key=lambda x: x.get("potential_score", 0), reverse=True)
        return ideas[:top_n]

    def generate_viral_opportunities(
        self,
        niche: str,
        trends: List[str],
        demand_signals: List[Dict[str, Any]],
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate viral content opportunities.
        
        Args:
            niche: Target niche
            trends: List of trending topics
            demand_signals: List of demand signals
            top_n: Number of opportunities
            
        Returns:
            List of viral opportunity dicts
        """
        opportunities = []

        # High-demand + trending = viral potential
        for signal in demand_signals[:5]:
            topic = signal.get("text", signal.get("topic", ""))
            if topic and any(t.lower() in topic.lower() for t in trends):
                opportunities.append({
                    "idea_type": "viral_opportunity",
                    "title": f"🔥 VIRAL: {topic}",
                    "description": f"Perfect storm: trending topic + high audience demand",
                    "niche": niche,
                    "potential_score": random.uniform(85, 99),
                    "viral_potential": random.uniform(80, 98),
                    "source": "trend_demand_intersection",
                    "reasoning": f"'{topic}' is both trending AND has high audience demand. "
                                f"This intersection creates maximum viral potential.",
                    "suggested_thumbnail": self._generate_thumbnail_text(topic, style="viral"),
                })

        # Generate from trend acceleration
        for trend in trends[:5]:
            trend_title = trend if isinstance(trend, str) else trend.get("title", str(trend))
            opportunities.append({
                "idea_type": "viral_opportunity",
                "title": f"🚀 ACCELERATING: {trend_title}",
                "description": f"Rapidly accelerating trend with first-mover advantage",
                "niche": niche,
                "potential_score": random.uniform(75, 95),
                "viral_potential": random.uniform(70, 95),
                "source": "accelerating_trend",
                "reasoning": f"'{trend_title}' is accelerating rapidly. Early content creators "
                            f"in this space have first-mover advantage.",
                "suggested_thumbnail": self._generate_thumbnail_text(trend_title, style="viral"),
            })

        opportunities.sort(key=lambda x: x.get("potential_score", 0), reverse=True)
        return opportunities[:top_n]

    def generate_underserved_niches(
        self,
        content_gaps: List[Dict[str, Any]],
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate underserved niche opportunities.
        
        Args:
            content_gaps: List of content gaps
            top_n: Number of niches
            
        Returns:
            List of underserved niche dicts
        """
        niches = []
        for gap in content_gaps:
            if gap.get("gap_score", 0) >= 60:  # Only high-gap opportunities
                niches.append({
                    "idea_type": "underserved_niche",
                    "title": f"💡 UNDERSERVED: {gap.get('topic', 'Unknown')}",
                    "description": gap.get("description", ""),
                    "niche": gap.get("niche", ""),
                    "gap_score": gap.get("gap_score", 0),
                    "demand_count": gap.get("demand_count", 0),
                    "existing_videos": gap.get("existing_video_count", 0),
                    "source": "content_gap_analysis",
                    "reasoning": f"High demand ({gap.get('demand_count', 0)} signals) "
                                f"with very low supply ({gap.get('existing_video_count', 0)} videos). "
                                f"Gap score: {gap.get('gap_score', 0)}/100.",
                })

        niches.sort(key=lambda x: x.get("gap_score", 0), reverse=True)
        return niches[:top_n]

    def generate_content_series(
        self,
        niche: str,
        topic: str,
        parts: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate a content series plan.
        
        Args:
            niche: Target niche
            topic: Series topic
            parts: Number of parts
            
        Returns:
            Dict with series plan
        """
        series_template = random.choice(self.SERIES_TEMPLATES)
        series_title = series_template.format(
            topic=topic,
            parts=parts,
            days=parts * 7,
        )

        episodes = []
        for i in range(1, parts + 1):
            episode_title = self._generate_title(
                f"{topic} Part {i}", niche, content_type="tutorial"
            )
            episodes.append({
                "part": i,
                "title": episode_title,
                "description": f"Part {i} of {parts}: Deep dive into {topic}",
            })

        return {
            "idea_type": "content_series",
            "title": series_title,
            "niche": niche,
            "topic": topic,
            "parts": parts,
            "episodes": episodes,
            "publishing_schedule": f"Release 1 part every {max(3, 7 // parts)} days",
            "potential_score": random.uniform(70, 90),
        }

    def generate_publishing_plan(
        self,
        niche: str,
        video_ideas: List[Dict[str, Any]],
        weeks: int = 4,
        videos_per_week: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate a publishing plan from video ideas.
        
        Args:
            niche: Target niche
            video_ideas: List of video ideas
            weeks: Number of weeks to plan
            videos_per_week: Videos per week
            
        Returns:
            Dict with publishing plan
        """
        total_videos = weeks * videos_per_week
        selected_ideas = video_ideas[:total_videos]

        schedule = []
        for week in range(1, weeks + 1):
            week_ideas = selected_ideas[
                (week - 1) * videos_per_week : week * videos_per_week
            ]
            schedule.append({
                "week": week,
                "videos": [
                    {
                        "day": day,
                        "title": idea.get("title", "Untitled"),
                        "type": idea.get("source", "general"),
                        "thumbnail": idea.get("suggested_thumbnail", ""),
                    }
                    for day, idea in enumerate(week_ideas, 1)
                ],
            })

        return {
            "niche": niche,
            "weeks": weeks,
            "videos_per_week": videos_per_week,
            "total_videos": total_videos,
            "schedule": schedule,
        }

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _generate_title(
        self,
        topic: str,
        niche: str,
        content_type: str = "tutorial",
    ) -> str:
        """
        Generate a video title using templates.
        
        Args:
            topic: Main topic
            niche: Content niche
            content_type: Type of content
            
        Returns:
            str: Generated title
        """
        templates = self.TITLE_TEMPLATES.get(content_type, self.TITLE_TEMPLATES["tutorial"])
        template = random.choice(templates)

        year = "2026"
        title = template.format(
            topic=topic.title(),
            competitor="the Competition",
            competitor2="Alternatives",
            year=year,
            minutes=random.choice([5, 10, 15, 20, 30]),
            days=random.choice([7, 14, 30, 60, 90]),
            months=random.choice([3, 6, 12]),
            number=random.choice([5, 7, 10, 15, 20, 25]),
            result=random.choice(["Money", "Success", "Results", "a Difference"]),
            timeframe=random.choice(["a Month", "3 Months", "6 Months", "a Year"]),
        )

        return title

    def _generate_thumbnail_text(self, topic: str, style: str = "standard") -> str:
        """
        Generate thumbnail text.
        
        Args:
            topic: Main topic
            style: Thumbnail style (standard, viral)
            
        Returns:
            str: Generated thumbnail text
        """
        template = random.choice(self.THUMBNAIL_TEMPLATES)
        text = template.format(
            topic=topic.upper() if random.random() > 0.5 else topic.title(),
            number=random.choice([5, 7, 10, 15, 20]),
        )

        if style == "viral":
            # Add emphasis for viral thumbnails
            emphasis = random.choice(["!!!", "?!", " 🔥", " 💀", " 🚨"])
            text = text[:20] + emphasis

        return text[:30]  # Keep it short for thumbnails


# Global engine instance
idea_engine = IdeaGenerationEngine()
