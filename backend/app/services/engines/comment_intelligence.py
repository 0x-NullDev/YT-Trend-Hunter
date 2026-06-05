"""
YT Trend Hunter - Comment Intelligence Engine
Analyzes YouTube comments at scale to extract:
- Content requests ("Please make a video about X")
- Complaints ("Why is nobody talking about Z?")
- Recurring questions ("Can someone explain Y?")
- Content ideas ("Part 2 please", "Can you do this for football?")
- Audience pain points
- Unmet demand signals

This is one of the most valuable features of the platform.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import nltk
from loguru import logger
from textblob import TextBlob

# Download NLTK data if needed
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class CommentIntelligenceEngine:
    """
    Comment Intelligence Engine
    Analyzes YouTube comments to extract actionable insights.
    
    Key capabilities:
    1. Request Detection - "Please make a video about X"
    2. Complaint Detection - "Why is nobody talking about Z?"
    3. Question Detection - "Can someone explain Y?"
    4. Idea Detection - "Part 2 please", "Can you do this for football?"
    5. Pain Point Detection - Audience frustrations and unmet needs
    6. Demand Aggregation - Aggregate and rank findings
    7. Sentiment Analysis - Overall audience sentiment
    """

    # Patterns for detecting different comment types
    REQUEST_PATTERNS = [
        r"(?i)(please\s+)?(make|create|do|cover|explain|review|try|test|show)\s+(a|an|the|some|more)?\s*(video\s+)?(about|on|of|for)?\s*(.+)",
        r"(?i)(can\s+you|could\s+you|would\s+you|will\s+you)\s+(please\s+)?(make|create|do|cover|explain|review|try|test|show)\s+(.+)",
        r"(?i)(i\s+(want|need|would\s+love|wish))\s+(to\s+see|you\s+(to\s+)?(make|create|do|cover|explain|review))\s+(.+)",
        r"(?i)(you\s+should|you\s+need\s+to|you\s+ought\s+to)\s+(make|create|do|cover|explain|review|try|test|show)\s+(.+)",
        r"(?i)(how\s+about|what\s+about|what\s+if\s+you)\s+(making|creating|doing|covering|explaining|reviewing)\s+(.+)",
        r"(?i)(please\s+)?(make|do)\s+(a\s+)?(part\s+\d+|sequel|follow\s+up|series)\s+(on|about|of)?\s*(.+)",
    ]

    COMPLAINT_PATTERNS = [
        r"(?i)(why\s+(is|are|does|do|did|has|have|haven't|hasn't|isn't|aren't))\s+(no\s+one|nobody|no\s+channel|no\s+creator)\s+(.+)",
        r"(?i)(i\s+(can't|cannot|couldn't)\s+find|there\s+(is|are)\s+no|there\s+isn't|there\s+aren't)\s+(.+)",
        r"(?i)(why\s+(is|are|does|do|did|has|have))\s+(there\s+)?(so\s+)?(little|few|no)\s+(.+)",
        r"(?i)(it's\s+(so\s+)?(hard|difficult|impossible)\s+to\s+find)\s+(.+)",
        r"(?i)(i'm\s+(so\s+)?(tired|bored|fed\s+up)\s+of|enough\s+with)\s+(.+)",
        r"(?i)(this\s+(is|was)\s+(so\s+)?(disappointing|frustrating|annoying|bad|terrible))\s+(.+)",
    ]

    QUESTION_PATTERNS = [
        r"(?i)(can\s+someone|can\s+anyone|could\s+someone|could\s+anyone|does\s+anyone)\s+(explain|tell|help|answer|clarify)\s+(.+)",
        r"(?i)(what\s+is|what\s+are|what's|how\s+does|how\s+do|how\s+can|why\s+does|why\s+do|why\s+is|why\s+are)\s+(.+)",
        r"(?i)(i\s+don't\s+understand|i\s+don't\s+get|i'm\s+confused\s+about|can\s+you\s+explain)\s+(.+)",
        r"(?i)(has\s+anyone|has\s+anybody)\s+(tried|used|done|experienced|seen)\s+(.+)",
        r"(?i)(does\s+anyone\s+else|anyone\s+else)\s+(think|feel|know|have|wonder)\s+(.+)",
    ]

    IDEA_PATTERNS = [
        r"(?i)(part\s+\d+|part\s+two|part\s+three|sequel|follow\s+up|next\s+video)\s+(please|when|pls|soon|next)",
        r"(?i)(can\s+you\s+do\s+this\s+for|can\s+you\s+make\s+this\s+for|do\s+this\s+with)\s+(.+)",
        r"(?i)(you\s+should\s+(collab|collaborate|team\s+up|partner)\s+with)\s+(.+)",
        r"(?i)(what\s+if\s+you|imagine\s+if\s+you|would\s+be\s+cool\s+if)\s+(.+)",
        r"(?i)(i\s+have\s+(a\s+)?(great|awesome|amazing|cool)\s+(idea|suggestion))\s+(.+)",
    ]

    PAIN_POINT_PATTERNS = [
        r"(?i)(i\s+(struggle|struggled|have\s+trouble|had\s+trouble|find\s+it\s+hard)\s+(with|to|understanding|finding))\s+(.+)",
        r"(?i)(it's\s+(so\s+)?(annoying|frustrating|confusing|complicated|difficult|hard))\s+(.+)",
        r"(?i)(i\s+(waste|wasted|lose|lost)\s+(so\s+)?(much\s+)?(time|money|effort))\s+(.+)",
        r"(?i)(nobody\s+(explains|talks\s+about|covers|teaches|shows))\s+(.+)",
        r"(?i)(i\s+wish\s+(someone|there\s+was|there\s+were|i\s+could))\s+(.+)",
    ]

    PART2_PATTERNS = [
        r"(?i)^(part\s+\d+|part\s+two|part\s+2|pt\.?\s*2|pt\.?\s*two)\s*$",
        r"(?i)^(part\s+\d+|part\s+two|part\s+2|pt\.?\s*2|pt\.?\s*two)[\s!,\.\?]+",
        r"(?i)(need|want|when\s+is|waiting\s+for|looking\s+forward\s+to)\s+(part\s+\d+|part\s+two|part\s+2|sequel)",
        r"(?i)(more\s+of\s+this|more\s+content\s+like\s+this|more\s+videos\s+like\s+this)",
        r"(?i)(please\s+)?(make|do|upload)\s+(a\s+)?(part\s+\d+|part\s+two|part\s+2|sequel)",
    ]

    def __init__(self):
        self.logger = logger.bind(engine="comment_intelligence")
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception:
            self.stop_words = set()

    # =========================================================================
    # Comment Classification
    # =========================================================================

    def classify_comment(self, text: str) -> Dict[str, Any]:
        """
        Classify a comment into multiple categories.
        
        Args:
            text: Comment text
            
        Returns:
            Dict with classification results
        """
        result = {
            "is_request": False,
            "is_complaint": False,
            "is_question": False,
            "is_idea": False,
            "is_pain_point": False,
            "is_part2_request": False,
            "extracted_request": None,
            "extracted_topic": None,
            "confidence": 0.0,
        }

        # Check each pattern type
        request_match = self._match_pattern(text, self.REQUEST_PATTERNS)
        complaint_match = self._match_pattern(text, self.COMPLAINT_PATTERNS)
        question_match = self._match_pattern(text, self.QUESTION_PATTERNS)
        idea_match = self._match_pattern(text, self.IDEA_PATTERNS)
        pain_point_match = self._match_pattern(text, self.PAIN_POINT_PATTERNS)
        part2_match = self._match_pattern(text, self.PART2_PATTERNS)

        if request_match:
            result["is_request"] = True
            result["extracted_request"] = request_match
            result["extracted_topic"] = self._extract_topic(text, request_match)

        if complaint_match:
            result["is_complaint"] = True
            if not result["extracted_topic"]:
                result["extracted_topic"] = self._extract_topic(text, complaint_match)

        if question_match:
            result["is_question"] = True
            if not result["extracted_topic"]:
                result["extracted_topic"] = self._extract_topic(text, question_match)

        if idea_match:
            result["is_idea"] = True
            if not result["extracted_topic"]:
                result["extracted_topic"] = self._extract_topic(text, idea_match)

        if pain_point_match:
            result["is_pain_point"] = True
            if not result["extracted_topic"]:
                result["extracted_topic"] = self._extract_topic(text, pain_point_match)

        if part2_match:
            result["is_part2_request"] = True

        # Calculate confidence
        signals = sum([
            result["is_request"],
            result["is_complaint"],
            result["is_question"],
            result["is_idea"],
            result["is_pain_point"],
            result["is_part2_request"],
        ])
        result["confidence"] = min(signals / 3, 1.0)  # Max confidence at 3+ signals

        return result

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a comment.
        
        Args:
            text: Comment text
            
        Returns:
            Dict with sentiment analysis
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            if polarity > 0.3:
                label = "positive"
            elif polarity < -0.3:
                label = "negative"
            else:
                label = "neutral"

            return {
                "sentiment_score": polarity,
                "sentiment_label": label,
                "subjectivity_score": subjectivity,
            }
        except Exception:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "subjectivity_score": 0.0,
            }

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key topics/keywords from comment text.
        
        Args:
            text: Comment text
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        try:
            # Tokenize and clean
            tokens = word_tokenize(text.lower())
            # Remove stopwords and punctuation
            keywords = [
                token for token in tokens
                if token.isalnum()
                and token not in self.stop_words
                and len(token) > 2
            ]
            # Return most common
            return list(dict(Counter(keywords).most_common(top_n)).keys())
        except Exception:
            return []

    # =========================================================================
    # Batch Analysis
    # =========================================================================

    def analyze_comments_batch(
        self,
        comments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze a batch of comments and aggregate results.
        
        Args:
            comments: List of comment dicts with 'text' key
            
        Returns:
            Dict with aggregated analysis
        """
        total = len(comments)
        if total == 0:
            return self._empty_aggregation()

        classified = []
        requests = []
        complaints = []
        questions = []
        ideas = []
        pain_points = []
        part2_requests = []
        all_keywords = []
        sentiment_scores = []

        for comment in comments:
            text = comment.get("text", "")
            if not text:
                continue

            # Classify
            classification = self.classify_comment(text)
            sentiment = self.analyze_sentiment(text)
            keywords = self.extract_keywords(text)

            classified.append({
                **comment,
                **classification,
                **sentiment,
                "keywords": keywords,
            })

            # Collect signals
            if classification["is_request"]:
                requests.append({
                    "text": text,
                    "topic": classification["extracted_topic"],
                    "request": classification["extracted_request"],
                })

            if classification["is_complaint"]:
                complaints.append({
                    "text": text,
                    "topic": classification["extracted_topic"],
                })

            if classification["is_question"]:
                questions.append({
                    "text": text,
                    "topic": classification["extracted_topic"],
                })

            if classification["is_idea"]:
                ideas.append({
                    "text": text,
                    "topic": classification["extracted_topic"],
                })

            if classification["is_pain_point"]:
                pain_points.append({
                    "text": text,
                    "topic": classification["extracted_topic"],
                })

            if classification["is_part2_request"]:
                part2_requests.append(text)

            all_keywords.extend(keywords)
            sentiment_scores.append(sentiment["sentiment_score"])

        # Aggregate results
        return {
            "total_comments": total,
            "analyzed_count": len(classified),
            "signals": {
                "requests": {
                    "count": len(requests),
                    "percentage": (len(requests) / total * 100) if total > 0 else 0,
                    "items": self._rank_signals(requests),
                },
                "complaints": {
                    "count": len(complaints),
                    "percentage": (len(complaints) / total * 100) if total > 0 else 0,
                    "items": self._rank_signals(complaints),
                },
                "questions": {
                    "count": len(questions),
                    "percentage": (len(questions) / total * 100) if total > 0 else 0,
                    "items": self._rank_signals(questions),
                },
                "ideas": {
                    "count": len(ideas),
                    "percentage": (len(ideas) / total * 100) if total > 0 else 0,
                    "items": self._rank_signals(ideas),
                },
                "pain_points": {
                    "count": len(pain_points),
                    "percentage": (len(pain_points) / total * 100) if total > 0 else 0,
                    "items": self._rank_signals(pain_points),
                },
                "part2_requests": {
                    "count": len(part2_requests),
                    "percentage": (len(part2_requests) / total * 100) if total > 0 else 0,
                },
            },
            "top_keywords": self._aggregate_keywords(all_keywords, top_n=20),
            "sentiment": {
                "average_score": sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0,
                "distribution": self._calculate_sentiment_distribution(sentiment_scores),
            },
            "demand_database": self._build_demand_database(requests, questions, pain_points),
        }

    # =========================================================================
    # Demand Database
    # =========================================================================

    def _build_demand_database(
        self,
        requests: List[Dict],
        questions: List[Dict],
        pain_points: List[Dict],
    ) -> List[Dict[str, Any]]:
        """
        Build a ranked demand database from signals.
        
        Args:
            requests: List of request signals
            questions: List of question signals
            pain_points: List of pain point signals
            
        Returns:
            List of ranked demand items
        """
        demand_map = defaultdict(lambda: {
            "requests": 0,
            "questions": 0,
            "pain_points": 0,
            "total_signals": 0,
            "example_texts": [],
        })

        # Aggregate by topic
        for req in requests:
            topic = req.get("topic") or "general"
            demand_map[topic]["requests"] += 1
            demand_map[topic]["total_signals"] += 1
            if len(demand_map[topic]["example_texts"]) < 3:
                demand_map[topic]["example_texts"].append(req["text"])

        for q in questions:
            topic = q.get("topic") or "general"
            demand_map[topic]["questions"] += 1
            demand_map[topic]["total_signals"] += 1
            if len(demand_map[topic]["example_texts"]) < 3:
                demand_map[topic]["example_texts"].append(q["text"])

        for pp in pain_points:
            topic = pp.get("topic") or "general"
            demand_map[topic]["pain_points"] += 1
            demand_map[topic]["total_signals"] += 1
            if len(demand_map[topic]["example_texts"]) < 3:
                demand_map[topic]["example_texts"].append(pp["text"])

        # Convert to list and rank
        demand_items = []
        for topic, data in demand_map.items():
            demand_items.append({
                "topic": topic,
                "demand_count": data["total_signals"],
                "requests": data["requests"],
                "questions": data["questions"],
                "pain_points": data["pain_points"],
                "example_texts": data["example_texts"],
                "urgency_score": min(data["total_signals"] / 10, 1) * 100,
            })

        # Sort by demand count
        demand_items.sort(key=lambda x: x["demand_count"], reverse=True)
        return demand_items

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _match_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """
        Match text against a list of regex patterns.
        
        Args:
            text: Text to match
            patterns: List of regex patterns
            
        Returns:
            Optional[str]: Matched group or None
        """
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Return the last group (the extracted content)
                groups = match.groups()
                if groups:
                    return groups[-1].strip()
                return match.group(0).strip()
        return None

    def _extract_topic(self, text: str, matched_text: str) -> str:
        """
        Extract the main topic from a matched comment.
        
        Args:
            text: Full comment text
            matched_text: Matched portion
            
        Returns:
            str: Extracted topic
        """
        # Use the matched text as the topic
        if matched_text and len(matched_text) < 200:
            return matched_text.strip()
        # Fall back to first sentence
        sentences = text.split(".")
        return sentences[0].strip() if sentences else text[:100]

    def _rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Rank signals by frequency of similar topics.
        
        Args:
            signals: List of signal dicts
            
        Returns:
            List of ranked signals
        """
        if not signals:
            return []

        # Count topic frequency
        topic_counts = Counter()
        for signal in signals:
            topic = signal.get("topic", "general")
            topic_counts[topic] += 1

        # Rank by frequency
        ranked = []
        seen_topics = set()
        for signal in signals:
            topic = signal.get("topic", "general")
            if topic not in seen_topics:
                ranked.append({
                    "topic": topic,
                    "frequency": topic_counts[topic],
                    "example": signal.get("text", "")[:200],
                })
                seen_topics.add(topic)

        ranked.sort(key=lambda x: x["frequency"], reverse=True)
        return ranked[:20]  # Top 20

    def _aggregate_keywords(self, keywords: List[str], top_n: int = 20) -> List[Dict]:
        """
        Aggregate and rank keywords by frequency.
        
        Args:
            keywords: List of keywords
            top_n: Number of top keywords to return
            
        Returns:
            List of keyword dicts with frequency
        """
        counter = Counter(keywords)
        return [
            {"keyword": kw, "frequency": count}
            for kw, count in counter.most_common(top_n)
        ]

    def _calculate_sentiment_distribution(
        self,
        scores: List[float],
    ) -> Dict[str, float]:
        """
        Calculate sentiment distribution.
        
        Args:
            scores: List of sentiment scores
            
        Returns:
            Dict with distribution percentages
        """
        if not scores:
            return {"positive": 0, "neutral": 0, "negative": 0}

        total = len(scores)
        positive = sum(1 for s in scores if s > 0.3)
        negative = sum(1 for s in scores if s < -0.3)
        neutral = total - positive - negative

        return {
            "positive": (positive / total * 100),
            "neutral": (neutral / total * 100),
            "negative": (negative / total * 100),
        }

    def _empty_aggregation(self) -> Dict[str, Any]:
        """Return empty aggregation result."""
        return {
            "total_comments": 0,
            "analyzed_count": 0,
            "signals": {
                "requests": {"count": 0, "percentage": 0, "items": []},
                "complaints": {"count": 0, "percentage": 0, "items": []},
                "questions": {"count": 0, "percentage": 0, "items": []},
                "ideas": {"count": 0, "percentage": 0, "items": []},
                "pain_points": {"count": 0, "percentage": 0, "items": []},
                "part2_requests": {"count": 0, "percentage": 0},
            },
            "top_keywords": [],
            "sentiment": {
                "average_score": 0,
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
            },
            "demand_database": [],
        }


# Global engine instance
comment_engine = CommentIntelligenceEngine()
