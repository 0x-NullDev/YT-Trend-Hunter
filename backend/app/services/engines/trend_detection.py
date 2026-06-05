"""
YT Trend Hunter - Trend Detection Engine
Mathematical formulas and algorithms for detecting emerging trends on YouTube.

SCORING FORMULAS:
=================

1. GROWTH VELOCITY (GV)
   Measures how fast a metric is growing over time.
   GV = (current_value - previous_value) / time_delta
   
   For subscribers: GV_subs = (subs_now - subs_30d_ago) / 30
   For views: GV_views = (views_now - views_7d_ago) / 7

2. ENGAGEMENT VELOCITY (EV)
   Measures how fast engagement is growing.
   EV = (current_engagement_rate - previous_engagement_rate) / time_delta
   
   Engagement Rate = (likes + comments) / views * 100

3. SEARCH MOMENTUM (SM)
   Measures search volume growth rate.
   SM = (current_search_volume - previous_search_volume) / previous_search_volume * 100
   
   Normalized: SM_norm = tanh(SM / 100) * 100

4. TREND STRENGTH (TS)
   Composite score of how strong a trend is.
   TS = w1 * GV_norm + w2 * EV_norm + w3 * SM_norm + w4 * VV_norm
   
   Where:
   - GV_norm = normalized growth velocity (0-100)
   - EV_norm = normalized engagement velocity (0-100)
   - SM_norm = normalized search momentum (0-100)
   - VV_norm = normalized video velocity (0-100)
   - w1, w2, w3, w4 = weights (default: 0.3, 0.25, 0.25, 0.2)

5. COMPETITION LEVEL (CL)
   Measures how competitive a niche/topic is.
   CL = min(channel_count / max_channels, 1) * 70 + 
        min(avg_channel_size / max_channel_size, 1) * 30
   
   Where:
   - channel_count = number of channels in niche
   - max_channels = threshold (e.g., 1000)
   - avg_channel_size = average subscriber count
   - max_channel_size = threshold (e.g., 100000)

6. SATURATION SCORE (SS)
   Measures how saturated a topic is.
   SS = min(video_count / max_videos, 1) * 50 +
        min(avg_views_per_video / max_views, 1) * 30 +
        min(channel_density, 1) * 20
   
   Where:
   - channel_density = channels / search_volume

7. OPPORTUNITY SCORE (OS)
   The primary score for identifying opportunities.
   OS = TS * 0.3 + (100 - CL) * 0.25 + (100 - SS) * 0.25 + AD * 0.2
   
   Where:
   - TS = Trend Strength (0-100)
   - CL = Competition Level (0-100)
   - SS = Saturation Score (0-100)
   - AD = Audience Demand (0-100)

8. TREND CONFIDENCE SCORE (TCS)
   How confident we are in the trend signal.
   TCS = sample_size_score * 0.3 + 
         consistency_score * 0.3 +
         source_diversity * 0.2 +
         recency_score * 0.2
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger
from scipy import stats

from app.core.config import settings


class TrendDetectionEngine:
    """
    Trend Detection Engine
    Detects, measures, and scores emerging trends across YouTube and other sources.
    """

    # Default weights for composite scores
    TREND_STRENGTH_WEIGHTS = {
        "growth_velocity": 0.30,
        "engagement_velocity": 0.25,
        "search_momentum": 0.25,
        "video_velocity": 0.20,
    }

    OPPORTUNITY_WEIGHTS = {
        "trend_strength": 0.30,
        "competition_inverse": 0.25,
        "saturation_inverse": 0.25,
        "audience_demand": 0.20,
    }

    CONFIDENCE_WEIGHTS = {
        "sample_size": 0.30,
        "consistency": 0.30,
        "source_diversity": 0.20,
        "recency": 0.20,
    }

    def __init__(self):
        self.logger = logger.bind(engine="trend_detection")

    # =========================================================================
    # Core Mathematical Formulas
    # =========================================================================

    def calculate_growth_velocity(
        self,
        current_value: float,
        previous_value: float,
        time_delta_days: float,
    ) -> float:
        """
        Calculate Growth Velocity.
        
        GV = (current_value - previous_value) / time_delta
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            time_delta_days: Time difference in days
            
        Returns:
            float: Growth velocity (per day)
        """
        if time_delta_days <= 0:
            return 0.0
        return (current_value - previous_value) / time_delta_days

    def calculate_growth_rate(
        self,
        current_value: float,
        previous_value: float,
        time_delta_days: float,
    ) -> float:
        """
        Calculate Growth Rate (percentage).
        
        GR = ((current_value - previous_value) / previous_value) * (30 / time_delta_days) * 100
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            time_delta_days: Time difference in days
            
        Returns:
            float: Monthly growth rate percentage
        """
        if previous_value <= 0 or time_delta_days <= 0:
            return 0.0
        monthly_rate = ((current_value - previous_value) / previous_value) * (30 / time_delta_days) * 100
        return monthly_rate

    def calculate_engagement_rate(
        self,
        likes: int,
        comments: int,
        views: int,
    ) -> float:
        """
        Calculate Engagement Rate.
        
        ER = (likes + comments) / views * 100
        
        Args:
            likes: Number of likes
            comments: Number of comments
            views: Number of views
            
        Returns:
            float: Engagement rate percentage
        """
        if views <= 0:
            return 0.0
        return (likes + comments) / views * 100

    def calculate_engagement_velocity(
        self,
        current_er: float,
        previous_er: float,
        time_delta_days: float,
    ) -> float:
        """
        Calculate Engagement Velocity.
        
        EV = (current_er - previous_er) / time_delta_days
        
        Args:
            current_er: Current engagement rate
            previous_er: Previous engagement rate
            time_delta_days: Time difference in days
            
        Returns:
            float: Engagement velocity
        """
        if time_delta_days <= 0:
            return 0.0
        return (current_er - previous_er) / time_delta_days

    def calculate_search_momentum(
        self,
        current_search_volume: float,
        previous_search_volume: float,
    ) -> float:
        """
        Calculate Search Momentum.
        
        SM = ((current - previous) / previous) * 100
        SM_norm = tanh(SM / 100) * 100
        
        Args:
            current_search_volume: Current search volume
            previous_search_volume: Previous search volume
            
        Returns:
            float: Normalized search momentum (0-100)
        """
        if previous_search_volume <= 0:
            return 0.0
        raw_momentum = ((current_search_volume - previous_search_volume) / previous_search_volume) * 100
        # Normalize using tanh to bound between 0-100
        normalized = math.tanh(raw_momentum / 100) * 100
        return max(0, normalized)

    def calculate_view_velocity(
        self,
        total_views: int,
        video_count: int,
        days_since_first_video: float,
    ) -> float:
        """
        Calculate View Velocity.
        
        VV = (total_views / video_count) / days_since_first_video
        
        Args:
            total_views: Total channel views
            video_count: Number of videos
            days_since_first_video: Days since first video
            
        Returns:
            float: Views per video per day
        """
        if video_count <= 0 or days_since_first_video <= 0:
            return 0.0
        return (total_views / video_count) / days_since_first_video

    def calculate_trend_strength(
        self,
        growth_velocity: float,
        engagement_velocity: float,
        search_momentum: float,
        video_velocity: float,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate Trend Strength (0-100).
        
        TS = w1 * GV_norm + w2 * EV_norm + w3 * SM_norm + w4 * VV_norm
        
        Args:
            growth_velocity: Growth velocity value
            engagement_velocity: Engagement velocity value
            search_momentum: Search momentum (0-100)
            video_velocity: Video velocity value
            weights: Custom weights dictionary
            
        Returns:
            float: Trend strength score (0-100)
        """
        w = weights or self.TREND_STRENGTH_WEIGHTS

        # Normalize each component to 0-100
        gv_norm = self._normalize_score(growth_velocity, max_val=1000)
        ev_norm = self._normalize_score(engagement_velocity, max_val=10)
        sm_norm = min(max(search_momentum, 0), 100)
        vv_norm = self._normalize_score(video_velocity, max_val=100)

        ts = (
            w["growth_velocity"] * gv_norm
            + w["engagement_velocity"] * ev_norm
            + w["search_momentum"] * sm_norm
            + w["video_velocity"] * vv_norm
        )

        return min(max(ts, 0), 100)

    def calculate_competition_level(
        self,
        channel_count: int,
        avg_subscribers: float = 0,
        total_videos: int = 0,
        niche_size: int = 100000,
        avg_channel_subscribers: Optional[float] = None,
        max_channels: int = 1000,
        max_subscribers: int = 100000,
    ) -> Dict[str, float]:
        """
        Calculate Competition Level (0-100) and Saturation Score.
        
        CL = min(channel_count / max_channels, 1) * 70 +
             min(avg_channel_size / max_channel_size, 1) * 30
        
        SS = min(video_count / max_videos, 1) * 50 +
             min(avg_views / max_views, 1) * 30 +
             min(channel_density, 1) * 20
        
        Args:
            channel_count: Number of channels in niche
            avg_subscribers: Average subscriber count (alias for avg_channel_subscribers)
            total_videos: Total number of videos
            niche_size: Total views in niche (for saturation)
            avg_channel_subscribers: Alternative parameter name
            max_channels: Channel count threshold
            max_subscribers: Subscriber count threshold
            
        Returns:
            Dict with competition_level and saturation_score
        """
        # Use whichever parameter was provided
        avg_subs = avg_channel_subscribers if avg_channel_subscribers is not None else avg_subscribers
        
        channel_score = min(channel_count / max_channels, 1) * 70
        size_score = min(avg_subs / max_subscribers, 1) * 30
        competition_level = min(channel_score + size_score, 100)
        
        # Calculate saturation
        video_score = min(total_videos / 10000, 1) * 50
        view_score = min(niche_size / 10000000, 1) * 30
        density_score = min(channel_count / max(channel_count + 1, 1), 1) * 20
        saturation_score = min(video_score + view_score + density_score, 100)
        
        return {
            "competition_level": competition_level,
            "saturation_score": saturation_score,
        }

    def calculate_saturation_score(
        self,
        video_count: int,
        avg_views_per_video: float,
        channel_density: float,
        max_videos: int = 10000,
        max_views: int = 100000,
    ) -> float:
        """
        Calculate Saturation Score (0-100).
        
        SS = min(video_count / max_videos, 1) * 50 +
             min(avg_views / max_views, 1) * 30 +
             min(channel_density, 1) * 20
        
        Args:
            video_count: Number of videos on topic
            avg_views_per_video: Average views per video
            channel_density: Channels per search volume
            max_videos: Video count threshold
            max_views: View count threshold
            
        Returns:
            float: Saturation score (0-100)
        """
        video_score = min(video_count / max_videos, 1) * 50
        view_score = min(avg_views_per_video / max_views, 1) * 30
        density_score = min(channel_density, 1) * 20
        return min(video_score + view_score + density_score, 100)

    def calculate_content_gap_score(
        self,
        demand_count: int = 0,
        existing_video_count: int = 1,
        demand_growth_rate: float = 0,
        demand_score: float = 50,
        supply_gap: float = 50,
        demand_momentum: float = 50,
    ) -> float:
        """
        Calculate Content Gap Score (0-100).
        
        CGS = min(demand / supply, 1) * 50 + momentum * 0.3 + growth * 0.2
        
        A high score means high demand with low supply - a content opportunity.
        
        Args:
            demand_count: Number of demand signals (requests, questions)
            existing_video_count: Number of existing videos on topic
            demand_growth_rate: Growth rate of demand (0-100)
            demand_score: Alternative - demand score (0-100)
            supply_gap: Alternative - supply gap (0-100)
            demand_momentum: Alternative - demand momentum (0-100)
            
        Returns:
            float: Content gap score (0-100)
        """
        if demand_count > 0 and existing_video_count > 0:
            # Use detailed calculation
            demand_supply_ratio = min(demand_count / max(existing_video_count, 1), 10) / 10 * 50
            momentum_score = min(demand_growth_rate, 100) * 0.3
            growth_score = min(demand_growth_rate, 100) * 0.2
            return min(demand_supply_ratio + momentum_score + growth_score, 100)
        else:
            # Use simplified calculation
            gap = max(0, demand_score - (100 - supply_gap))
            momentum_component = demand_momentum * 0.3
            gap_component = gap * 0.7
            return min(max(gap_component + momentum_component, 0), 100)

    def calculate_opportunity_score(
        self,
        trend_strength: float,
        competition_level: float,
        saturation_score: float,
        audience_demand: float,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate Opportunity Score (0-100).
        
        OS = TS * 0.3 + (100 - CL) * 0.25 + (100 - SS) * 0.25 + AD * 0.2
        
        Args:
            trend_strength: Trend strength (0-100)
            competition_level: Competition level (0-100)
            saturation_score: Saturation score (0-100)
            audience_demand: Audience demand (0-100)
            weights: Custom weights dictionary
            
        Returns:
            float: Opportunity score (0-100)
        """
        w = weights or self.OPPORTUNITY_WEIGHTS

        competition_inverse = 100 - competition_level
        saturation_inverse = 100 - saturation_score

        os = (
            w["trend_strength"] * trend_strength
            + w["competition_inverse"] * competition_inverse
            + w["saturation_inverse"] * saturation_inverse
            + w["audience_demand"] * audience_demand
        )

        return min(max(os, 0), 100)

    def calculate_confidence_score(
        self,
        sample_size: int,
        consistency_score: float,
        source_count: int,
        hours_since_detection: float,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate Trend Confidence Score (0-100).
        
        TCS = sample_size_score * 0.3 +
              consistency_score * 0.3 +
              source_diversity * 0.2 +
              recency_score * 0.2
        
        Args:
            sample_size: Number of data points
            consistency_score: How consistent the signal is (0-100)
            source_count: Number of different sources
            hours_since_detection: Hours since first detected
            weights: Custom weights dictionary
            
        Returns:
            float: Confidence score (0-100)
        """
        w = weights or self.CONFIDENCE_WEIGHTS

        # Sample size score: logarithmic scale
        ss_score = min(math.log10(sample_size + 1) / 4 * 100, 100) if sample_size > 0 else 0

        # Source diversity score
        sd_score = min(source_count / 5 * 100, 100)

        # Recency score: decays over time
        recency_score = max(0, 100 - (hours_since_detection / 24) * 10)

        tcs = (
            w["sample_size"] * ss_score
            + w["consistency"] * consistency_score
            + w["source_diversity"] * sd_score
            + w["recency"] * recency_score
        )

        return min(max(tcs, 0), 100)

    def calculate_viral_score(
        self,
        views: int,
        likes: int,
        comments: int,
        subscribers: int,
        hours_since_publish: float,
    ) -> float:
        """
        Calculate Viral Score for a video.
        
        VS = (view_velocity_score * 0.4 +
              engagement_rate_score * 0.3 +
              like_to_view_ratio_score * 0.2 +
              comment_to_view_ratio_score * 0.1)
        
        Args:
            views: Video views
            likes: Video likes
            comments: Video comments
            subscribers: Channel subscribers at time of upload
            hours_since_publish: Hours since video was published
            
        Returns:
            float: Viral score (0-100)
        """
        if hours_since_publish <= 0:
            return 0.0

        # View velocity (views per hour)
        view_velocity = views / hours_since_publish
        # Normalize: 1000 views/hour = 100 score
        vv_score = min(view_velocity / 1000 * 100, 100)

        # Engagement rate
        er = self.calculate_engagement_rate(likes, comments, views)
        er_score = min(er * 10, 100)  # 10% ER = 100 score

        # Like-to-view ratio
        lvr = (likes / views * 100) if views > 0 else 0
        lvr_score = min(lvr * 10, 100)  # 10% like rate = 100 score

        # Comment-to-view ratio
        cvr = (comments / views * 100) if views > 0 else 0
        cvr_score = min(cvr * 50, 100)  # 2% comment rate = 100 score

        vs = vv_score * 0.4 + er_score * 0.3 + lvr_score * 0.2 + cvr_score * 0.1
        return min(max(vs, 0), 100)

    # =========================================================================
    # Trend Detection Methods
    # =========================================================================

    def detect_accelerating_trend(
        self,
        time_series_data: List[float],
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Detect if a trend is accelerating using linear regression.
        
        Uses the slope of the regression line to determine acceleration.
        A positive and increasing slope indicates acceleration.
        
        Args:
            time_series_data: List of values over time
            threshold: Minimum R² value for significance
            
        Returns:
            Dict with acceleration metrics
        """
        if len(time_series_data) < 3:
            return {
                "is_accelerating": False,
                "slope": 0.0,
                "r_squared": 0.0,
                "acceleration": 0.0,
            }

        x = np.arange(len(time_series_data))
        y = np.array(time_series_data)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Calculate acceleration (second derivative)
        if len(time_series_data) >= 5:
            # Split into two halves and compare slopes
            mid = len(time_series_data) // 2
            first_half = time_series_data[:mid]
            second_half = time_series_data[mid:]

            if len(first_half) >= 2 and len(second_half) >= 2:
                x1 = np.arange(len(first_half))
                y1 = np.array(first_half)
                slope1, _, _, _, _ = stats.linregress(x1, y1)

                x2 = np.arange(len(second_half))
                y2 = np.array(second_half)
                slope2, _, _, _, _ = stats.linregress(x2, y2)

                acceleration = slope2 - slope1
            else:
                acceleration = 0.0
        else:
            acceleration = 0.0

        return {
            "is_accelerating": slope > 0 and r_value ** 2 > threshold,
            "slope": slope,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "acceleration": acceleration,
            "direction": "up" if slope > 0 else "down",
        }

    def detect_seasonality(
        self,
        time_series_data: List[float],
        period: int = 7,
    ) -> Dict[str, Any]:
        """
        Detect seasonal patterns in time series data.
        
        Args:
            time_series_data: List of values over time
            period: Expected period (7 for weekly, 30 for monthly)
            
        Returns:
            Dict with seasonality metrics
        """
        if len(time_series_data) < period * 2:
            return {"has_seasonality": False, "strength": 0.0}

        # Autocorrelation at given period
        n = len(time_series_data)
        mean = np.mean(time_series_data)
        var = np.var(time_series_data)

        if var == 0:
            return {"has_seasonality": False, "strength": 0.0}

        # Calculate autocorrelation
        lagged = time_series_data[: n - period]
        original = time_series_data[period:]

        correlation = np.corrcoef(original, lagged)[0, 1] if len(original) > 1 else 0

        return {
            "has_seasonality": abs(correlation) > 0.3,
            "strength": abs(correlation) * 100,
            "correlation": correlation,
            "period": period,
        }

    def calculate_channel_growth_prediction(
        self,
        current_subscribers: int,
        subscriber_history: List[int],
        niche_growth_rate: float,
        competition_level: float,
        upload_frequency: float,
    ) -> Dict[str, float]:
        """
        Predict channel growth using historical data and niche factors.
        
        Uses exponential growth model with competition dampening.
        
        Args:
            current_subscribers: Current subscriber count
            subscriber_history: Historical subscriber counts
            niche_growth_rate: Average growth rate in niche (%)
            competition_level: Competition level (0-100)
            upload_frequency: Videos per week
            
        Returns:
            Dict with predicted subscriber milestones and probabilities
        """
        # Calculate historical growth rate
        if len(subscriber_history) >= 2:
            historical_rate = self.calculate_growth_rate(
                subscriber_history[-1], subscriber_history[0], len(subscriber_history)
            )
        else:
            historical_rate = niche_growth_rate

        # Adjust for competition
        competition_factor = 1 - (competition_level / 100)
        adjusted_rate = historical_rate * competition_factor

        # Adjust for upload frequency
        frequency_factor = min(upload_frequency / 3, 2)  # 3 videos/week = optimal
        adjusted_rate *= frequency_factor

        # Predict milestones (in months)
        milestones = {
            "1000": 1000,
            "10000": 10000,
            "100000": 100000,
            "1000000": 1000000,
        }

        predictions = {}
        for label, target in milestones.items():
            if target <= current_subscribers:
                predictions[f"prob_{label}"] = 1.0
                continue

            # Months to reach target
            if adjusted_rate > 0:
                months_to_target = math.log(target / current_subscribers) / math.log(1 + adjusted_rate / 100)
            else:
                months_to_target = float("inf")

            # Probability based on time horizon (decay over time)
            if months_to_target <= 3:
                probability = 0.95
            elif months_to_target <= 6:
                probability = 0.85
            elif months_to_target <= 12:
                probability = 0.70
            elif months_to_target <= 24:
                probability = 0.50
            elif months_to_target <= 36:
                probability = 0.30
            else:
                probability = 0.10

            # Adjust for competition
            probability *= (1 - competition_level / 100 * 0.5)

            predictions[f"prob_{label}"] = min(max(probability, 0), 1)

        return predictions

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _normalize_score(self, value: float, max_val: float = 100) -> float:
        """
        Normalize a value to 0-100 scale using tanh.
        
        Args:
            value: Raw value
            max_val: Maximum expected value
            
        Returns:
            float: Normalized score (0-100)
        """
        if max_val <= 0:
            return 0.0
        normalized = math.tanh(value / max_val) * 100
        return max(0, normalized)

    def calculate_weighted_average(
        self,
        values: List[float],
        weights: List[float],
    ) -> float:
        """
        Calculate weighted average of values.
        
        Args:
            values: List of values
            weights: List of weights (must sum to 1)
            
        Returns:
            float: Weighted average
        """
        if not values or not weights:
            return 0.0
        if len(values) != len(weights):
            raise ValueError("Values and weights must have same length")
        return sum(v * w for v, w in zip(values, weights))

    def calculate_exponential_moving_average(
        self,
        values: List[float],
        alpha: float = 0.3,
    ) -> List[float]:
        """
        Calculate exponential moving average.
        
        EMA_t = alpha * value_t + (1 - alpha) * EMA_{t-1}
        
        Args:
            values: List of values over time
            alpha: Smoothing factor (0-1)
            
        Returns:
            List of EMA values
        """
        if not values:
            return []

        ema = [values[0]]
        for value in values[1:]:
            ema.append(alpha * value + (1 - alpha) * ema[-1])
        return ema

    def detect_outliers(
        self,
        values: List[float],
        threshold: float = 2.0,
    ) -> List[int]:
        """
        Detect outliers using Z-score method.
        
        Args:
            values: List of values
            threshold: Z-score threshold
            
        Returns:
            List of outlier indices
        """
        if len(values) < 3:
            return []

        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        outliers = []
        for i, value in enumerate(values):
            z_score = (value - mean) / std
            if abs(z_score) > threshold:
                outliers.append(i)

        return outliers

    # =========================================================================
    # High-Level Analysis Methods
    # =========================================================================

    def analyze_trend(
        self,
        videos: List[Dict[str, Any]],
        channels: List[Dict[str, Any]],
        comments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        High-level trend analysis combining all detection methods.
        
        Args:
            videos: List of video items from YouTube API
            channels: List of channel items from YouTube API
            comments: List of comment items from YouTube API
            
        Returns:
            Dict with trend analysis results
        """
        # Extract metrics from videos
        total_views = sum(
            int(v.get("statistics", {}).get("viewCount", 0))
            for v in videos if isinstance(v.get("statistics"), dict)
        )
        total_likes = sum(
            int(v.get("statistics", {}).get("likeCount", 0))
            for v in videos if isinstance(v.get("statistics"), dict)
        )
        total_comments_count = sum(
            int(v.get("statistics", {}).get("commentCount", 0))
            for v in videos if isinstance(v.get("statistics"), dict)
        )

        # Calculate engagement rate
        engagement_rate = self.calculate_engagement_rate(
            likes=total_likes,
            comments=total_comments_count,
            views=max(total_views, 1),
        )

        # Calculate trend strength
        trend_strength = self.calculate_trend_strength(
            growth_velocity=50,  # Default - would need historical data
            engagement_velocity=min(engagement_rate * 10, 100),
            search_momentum=50,
            video_velocity=min(len(videos) * 5, 100),
        )

        # Calculate competition level
        competition_result = self.calculate_competition_level(
            channel_count=len(channels),
            avg_subscribers=sum(
                int(c.get("statistics", {}).get("subscriberCount", 0))
                for c in channels if isinstance(c.get("statistics"), dict)
            ) / max(len(channels), 1),
            total_videos=sum(
                int(c.get("statistics", {}).get("videoCount", 0))
                for c in channels if isinstance(c.get("statistics"), dict)
            ),
            niche_size=max(total_views, 100000),
        )

        # Extract trending topics from video titles
        trends = []
        for v in videos[:20]:
            title = v.get("snippet", {}).get("title", "")
            if title:
                trends.append({
                    "title": title,
                    "channel": v.get("snippet", {}).get("channelTitle", ""),
                    "views": int(v.get("statistics", {}).get("viewCount", 0)) if isinstance(v.get("statistics"), dict) else 0,
                    "published_at": v.get("snippet", {}).get("publishedAt", ""),
                })

        # Generate insights
        insights = []
        if trend_strength > 70:
            insights.append("Strong upward trend detected in this category")
        if competition_result.get("competition_level", 50) < 30:
            insights.append("Low competition - good opportunity for new creators")
        if engagement_rate > 10:
            insights.append("High engagement rates indicate strong audience interest")
        if len(channels) < 20:
            insights.append("Limited number of creators - room for growth")

        return {
            "trend_strength": trend_strength,
            "competition_level": competition_result.get("competition_level", 50),
            "saturation_score": competition_result.get("saturation_score", 50),
            "content_gap_score": max(0, 100 - competition_result.get("saturation_score", 50)),
            "engagement_rate": engagement_rate,
            "total_views": total_views,
            "total_videos_analyzed": len(videos),
            "total_channels_analyzed": len(channels),
            "total_comments_analyzed": len(comments),
            "trends": trends,
            "insights": insights,
            "rising_channels": sorted(
                [
                    {
                        "title": c.get("snippet", {}).get("title", c.get("title", "Unknown")),
                        "subscribers": int(c.get("statistics", {}).get("subscriberCount", 0)) if isinstance(c.get("statistics"), dict) else c.get("subscriber_count", 0),
                        "videos": int(c.get("statistics", {}).get("videoCount", 0)) if isinstance(c.get("statistics"), dict) else c.get("video_count", 0),
                        "views": int(c.get("statistics", {}).get("viewCount", 0)) if isinstance(c.get("statistics"), dict) else c.get("view_count", 0),
                    }
                    for c in channels
                ],
                key=lambda x: x.get("subscribers", 0),
                reverse=True,
            ),
        }


# Global engine instance
trend_engine = TrendDetectionEngine()
