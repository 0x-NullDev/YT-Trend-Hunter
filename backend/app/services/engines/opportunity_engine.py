"""
YT Trend Hunter - Opportunity Engine
Proprietary Opportunity Scoring System that identifies the most promising
content creation opportunities on YouTube.

The engine combines multiple signals into a unified opportunity score:
1. Trend Score - How hot is this topic right now?
2. Competition Score - How many creators are already in this space?
3. Saturation Score - How much content already exists?
4. Audience Demand Score - What are people actively requesting?
5. Monetization Score - How monetizable is this niche?
6. Channel Creation Predictor - What are the chances of success?
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from app.services.engines.trend_detection import trend_engine


class OpportunityEngine:
    """
    Opportunity Engine
    Ranks and scores content creation opportunities using proprietary algorithms.
    """

    # Weights for the composite opportunity score
    OPPORTUNITY_SCORE_WEIGHTS = {
        "trend_score": 0.25,
        "competition_inverse": 0.20,
        "saturation_inverse": 0.15,
        "demand_score": 0.25,
        "monetization_score": 0.15,
    }

    # Difficulty thresholds
    DIFFICULTY_THRESHOLDS = {
        "very_easy": (0, 20),
        "easy": (20, 40),
        "medium": (40, 60),
        "hard": (60, 80),
        "very_hard": (80, 100),
    }

    def __init__(self):
        self.logger = logger.bind(engine="opportunity")

    def calculate_opportunity_score(
        self,
        trend_score: float,
        competition_score: float,
        saturation_score: float,
        demand_score: float,
        monetization_score: float,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Calculate the composite Opportunity Score.
        
        OS = w1 * TS + w2 * (100 - CS) + w3 * (100 - SS) + w4 * DS + w5 * MS
        
        Args:
            trend_score: Trend strength (0-100)
            competition_score: Competition level (0-100)
            saturation_score: Saturation level (0-100)
            demand_score: Audience demand (0-100)
            monetization_score: Monetization potential (0-100)
            weights: Custom weights
            
        Returns:
            Dict with opportunity score and component scores
        """
        w = weights or self.OPPORTUNITY_SCORE_WEIGHTS

        competition_inverse = 100 - competition_score
        saturation_inverse = 100 - saturation_score

        opportunity_score = (
            w["trend_score"] * trend_score
            + w["competition_inverse"] * competition_inverse
            + w["saturation_inverse"] * saturation_inverse
            + w["demand_score"] * demand_score
            + w["monetization_score"] * monetization_score
        )

        opportunity_score = min(max(opportunity_score, 0), 100)

        return {
            "opportunity_score": round(opportunity_score, 1),
            "trend_score": round(trend_score, 1),
            "competition_score": round(competition_score, 1),
            "saturation_score": round(saturation_score, 1),
            "demand_score": round(demand_score, 1),
            "monetization_score": round(monetization_score, 1),
            "competition_inverse": round(competition_inverse, 1),
            "saturation_inverse": round(saturation_inverse, 1),
        }

    def calculate_channel_creation_prediction(
        self,
        niche: str,
        trend_score: float,
        competition_score: float,
        saturation_score: float,
        demand_score: float,
        estimated_audience_size: int,
        avg_channel_growth_rate: float,
        upload_frequency: float = 3,
    ) -> Dict[str, Any]:
        """
        Predict success probability for a new channel in a niche.
        
        This is the flagship Channel Creation Predictor feature.
        
        Args:
            niche: Niche name
            trend_score: Trend strength (0-100)
            competition_score: Competition level (0-100)
            saturation_score: Saturation level (0-100)
            demand_score: Audience demand (0-100)
            estimated_audience_size: Estimated total audience
            avg_channel_growth_rate: Average growth rate in niche (%)
            upload_frequency: Expected videos per week
            
        Returns:
            Dict with success predictions
        """
        # Calculate base success probability
        base_probability = (
            (trend_score / 100) * 0.3
            + (1 - competition_score / 100) * 0.25
            + (1 - saturation_score / 100) * 0.15
            + (demand_score / 100) * 0.3
        )

        # Adjust for upload frequency
        frequency_factor = min(upload_frequency / 3, 2)  # 3/week = optimal
        base_probability *= min(frequency_factor, 1.5)

        # Calculate milestone probabilities
        milestones = {
            "1000": 1000,
            "10000": 10000,
            "100000": 100000,
            "1000000": 1000000,
        }

        predictions = {}
        for label, target in milestones.items():
            # Probability decays as target increases
            decay = math.log10(target / 1000) * 0.15
            prob = base_probability * (1 - decay)
            predictions[f"prob_{label}_subs"] = round(min(max(prob, 0), 1) * 100, 1)

        # Determine difficulty level
        difficulty_score = (competition_score * 0.4 + saturation_score * 0.3 + (100 - demand_score) * 0.3)
        difficulty = self._get_difficulty_level(difficulty_score)

        # Determine growth potential
        growth_potential_score = (trend_score * 0.4 + demand_score * 0.4 + (100 - competition_score) * 0.2)
        growth_potential = self._get_growth_potential(growth_potential_score)

        # Audience size estimate
        audience_size = self._estimate_audience_size(estimated_audience_size)

        return {
            "niche": niche,
            "success_probability": {
                "1000_subscribers": predictions["prob_1000_subs"],
                "10000_subscribers": predictions["prob_10000_subs"],
                "100000_subscribers": predictions["prob_100000_subs"],
                "1000000_subscribers": predictions["prob_1000000_subs"],
            },
            "difficulty": difficulty,
            "competition": self._get_competition_label(competition_score),
            "audience_demand": self._get_demand_label(demand_score),
            "growth_potential": growth_potential,
            "audience_size_estimate": audience_size,
            "expected_publishing_frequency": f"{upload_frequency} videos/week",
            "reasoning": self._generate_prediction_reasoning(
                niche, trend_score, competition_score, demand_score, difficulty
            ),
        }

    def calculate_monetization_score(
        self,
        niche: str,
        avg_cpm: float = 5.0,
        avg_views_per_video: float = 10000,
        sponsorship_potential: float = 50,
        product_potential: float = 50,
        affiliate_potential: float = 50,
    ) -> float:
        """
        Calculate monetization potential for a niche (0-100).
        
        Args:
            niche: Niche name
            avg_cpm: Average CPM in dollars
            avg_views_per_video: Average views per video
            sponsorship_potential: Sponsorship potential (0-100)
            product_potential: Digital/physical product potential (0-100)
            affiliate_potential: Affiliate marketing potential (0-100)
            
        Returns:
            float: Monetization score (0-100)
        """
        # CPM score (typical range: $1-$50)
        cpm_score = min(avg_cpm / 50 * 100, 100)

        # Views score
        views_score = min(math.log10(avg_views_per_video) / 6 * 100, 100)

        # Revenue stream diversity
        diversity_score = (
            sponsorship_potential * 0.4
            + product_potential * 0.3
            + affiliate_potential * 0.3
        )

        # Composite score
        monetization_score = (
            cpm_score * 0.3
            + views_score * 0.2
            + diversity_score * 0.5
        )

        return min(max(monetization_score, 0), 100)

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Rank a list of opportunities by opportunity score.
        
        Args:
            opportunities: List of opportunity dicts
            top_n: Number of top opportunities to return
            
        Returns:
            List of ranked opportunities
        """
        ranked = sorted(
            opportunities,
            key=lambda x: x.get("opportunity_score", 0),
            reverse=True,
        )
        return ranked[:top_n]

    def generate_opportunity_summary(
        self,
        opportunity: Dict[str, Any],
    ) -> str:
        """
        Generate a human-readable summary of an opportunity.
        
        Args:
            opportunity: Opportunity dict
            
        Returns:
            str: Formatted summary
        """
        lines = [
            f"🎯 Opportunity: {opportunity.get('title', 'Unknown')}",
            f"   Niche: {opportunity.get('niche', 'Unknown')}",
            f"   Type: {opportunity.get('opportunity_type', 'Unknown')}",
            f"   Score: {opportunity.get('opportunity_score', 0)}/100",
            "",
            "   Component Scores:",
            f"   ├─ Trend Score: {opportunity.get('trend_score', 0)}/100",
            f"   ├─ Competition: {opportunity.get('competition_score', 0)}/100",
            f"   ├─ Saturation: {opportunity.get('saturation_score', 0)}/100",
            f"   ├─ Demand: {opportunity.get('demand_score', 0)}/100",
            f"   └─ Monetization: {opportunity.get('monetization_score', 0)}/100",
        ]

        if opportunity.get("prob_1000_subs") is not None:
            lines.extend([
                "",
                "   Channel Creation Predictor:",
                f"   ├─ 1K subs: {opportunity['prob_1000_subs']}%",
                f"   ├─ 10K subs: {opportunity['prob_10000_subs']}%",
                f"   ├─ 100K subs: {opportunity['prob_100000_subs']}%",
                f"   └─ 1M subs: {opportunity['prob_1000000_subs']}%",
                f"   Difficulty: {opportunity.get('difficulty_level', 'Unknown')}",
            ])

        if opportunity.get("reasoning"):
            lines.extend([
                "",
                f"   Reasoning: {opportunity['reasoning']}",
            ])

        return "\n".join(lines)

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _get_difficulty_level(self, score: float) -> str:
        """Convert numeric difficulty score to label."""
        for level, (low, high) in self.DIFFICULTY_THRESHOLDS.items():
            if low <= score < high:
                return level.replace("_", " ").title()
        return "Medium"

    def _get_growth_potential(self, score: float) -> str:
        """Convert numeric growth potential to label."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        return "Very Low"

    def _get_competition_label(self, score: float) -> str:
        """Convert numeric competition score to label."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        return "Very Low"

    def _get_demand_label(self, score: float) -> str:
        """Convert numeric demand score to label."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        return "Very Low"

    def _estimate_audience_size(self, estimated_size: int) -> str:
        """Convert audience size to label."""
        if estimated_size >= 10000000:
            return "Massive"
        elif estimated_size >= 1000000:
            return "Large"
        elif estimated_size >= 100000:
            return "Medium"
        elif estimated_size >= 10000:
            return "Small"
        return "Niche"

    def _generate_prediction_reasoning(
        self,
        niche: str,
        trend_score: float,
        competition_score: float,
        demand_score: float,
        difficulty: str,
    ) -> str:
        """Generate reasoning for channel creation prediction."""
        parts = []

        if trend_score >= 70:
            parts.append(f"'{niche}' is a rapidly growing niche")
        elif trend_score >= 50:
            parts.append(f"'{niche}' shows steady growth")
        else:
            parts.append(f"'{niche}' is a stable niche")

        if competition_score <= 30:
            parts.append("with low channel density")
        elif competition_score <= 50:
            parts.append("with moderate competition")
        else:
            parts.append("with high competition")

        if demand_score >= 70:
            parts.append("and very high audience demand")
        elif demand_score >= 50:
            parts.append("and growing audience demand")

        parts.append(f"(Difficulty: {difficulty})")

        return " ".join(parts)


# Global engine instance
opportunity_engine = OpportunityEngine()
