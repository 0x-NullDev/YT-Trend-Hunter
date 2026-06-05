"""
YT Trend Hunter - YouTube Data API v3 Collector
Handles all YouTube API interactions: search, channels, videos, comments, playlists.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from loguru import logger

from app.core.config import settings


class YouTubeAPIError(Exception):
    """Custom exception for YouTube API errors."""
    pass


class YouTubeCollector:
    """
    YouTube Data API v3 collector.
    Handles rate limiting, pagination, and data extraction.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"
    MAX_RESULTS_PER_PAGE = 50
    MAX_RETRIES = 3

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logger.bind(service="youtube_collector")

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Accept": "application/json"}
            )

    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        retries: int = MAX_RETRIES,
    ) -> Dict[str, Any]:
        """
        Make a request to the YouTube API with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., 'search', 'videos', 'channels')
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            API response as dict
        """
        await self._ensure_session()
        params["key"] = self.api_key

        for attempt in range(retries):
            try:
                url = f"{self.BASE_URL}/{endpoint}"
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403:
                        error_text = await response.text()
                        # Check if it's comments disabled (not quota exceeded)
                        if "commentsDisabled" in error_text:
                            self.logger.warning(f"Comments disabled for this video")
                            return {"items": [], "error": "commentsDisabled"}
                        elif "quotaExceeded" in error_text or "quota" in error_text.lower():
                            self.logger.warning(f"API quota exceeded: {error_text}")
                            raise YouTubeAPIError(
                                "YouTube API quota exceeded. "
                                "Get a new API key at https://console.cloud.google.com/ "
                                "or wait until quota resets."
                            )
                        else:
                            self.logger.warning(f"API error 403: {error_text}")
                            return {"items": [], "error": "forbidden"}
                    elif response.status == 429:
                        wait = min(2 ** attempt * 10, 120)
                        self.logger.warning(f"Rate limited, waiting {wait}s")
                        await asyncio.sleep(wait)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"API error {response.status}: {error_text}")
                        if attempt < retries - 1:
                            await asyncio.sleep(2 ** attempt)
            except YouTubeAPIError:
                raise
            except Exception as e:
                self.logger.error(f"Request failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)

        return {}

    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance",
        published_after: Optional[datetime] = None,
        region_code: str = "US",
        relevance_language: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube.
        
        Args:
            query: Search query
            max_results: Maximum results (max 50 per page)
            order: Sort order (relevance, date, viewCount, rating)
            published_after: Filter by publish date
            region_code: Region code (e.g., 'US', 'IN', 'GB')
            relevance_language: Language filter
            
        Returns:
            List of video items
        """
        params = {
            "part": "snippet",
            "q": query,
            "maxResults": min(max_results, self.MAX_RESULTS_PER_PAGE),
            "order": order,
            "regionCode": region_code,
            "relevanceLanguage": relevance_language,
            "type": "video",
        }

        if published_after:
            params["publishedAfter"] = published_after.isoformat() + "Z"

        all_items = []
        next_page_token = None

        while len(all_items) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = await self._make_request("search", params)
            items = data.get("items", [])
            
            # Normalize items: extract videoId from nested id object
            for item in items:
                item_id = item.get("id", {})
                if isinstance(item_id, dict):
                    item["video_id"] = item_id.get("videoId", "")
                else:
                    item["video_id"] = item_id
            
            all_items.extend(items)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        return all_items[:max_results]

    async def get_channel_info(
        self,
        channel_id: str,
    ) -> Dict[str, Any]:
        """
        Get detailed channel information.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel details with statistics
        """
        params = {
            "part": "snippet,statistics,brandingSettings,topicDetails",
            "id": channel_id,
        }
        data = await self._make_request("channels", params)
        items = data.get("items", [])
        return items[0] if items else {}

    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        order: str = "date",
    ) -> List[Dict[str, Any]]:
        """
        Get videos from a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum results
            order: Sort order (date, viewCount, rating)
            
        Returns:
            List of video items
        """
        # First get the upload playlist ID
        channel = await self.get_channel_info(channel_id)
        if not channel:
            return []

        upload_playlist = (
            channel.get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
        if not upload_playlist:
            return []

        params = {
            "part": "snippet,contentDetails",
            "playlistId": upload_playlist,
            "maxResults": min(max_results, self.MAX_RESULTS_PER_PAGE),
        }

        all_items = []
        next_page_token = None

        while len(all_items) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = await self._make_request("playlistItems", params)
            items = data.get("items", [])
            all_items.extend(items)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        return all_items[:max_results]

    async def get_video_details(
        self,
        video_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Get detailed information for multiple videos.
        
        Args:
            video_ids: List of YouTube video IDs (max 50)
            
        Returns:
            List of video details with statistics
        """
        # Process in batches of 50
        all_details = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            params = {
                "part": "snippet,statistics,contentDetails,topicDetails",
                "id": ",".join(batch),
            }
            data = await self._make_request("videos", params)
            all_details.extend(data.get("items", []))

        return all_details

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100,
        order: str = "relevance",
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum comments
            order: Sort order (relevance, time)
            
        Returns:
            List of comment items
        """
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_results, 100),
            "order": order,
        }

        all_comments = []
        next_page_token = None

        while len(all_comments) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = await self._make_request("commentThreads", params)
            items = data.get("items", [])
            all_comments.extend(items)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        return all_comments[:max_results]

    async def get_trending_videos(
        self,
        region_code: str = "US",
        category_id: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get trending videos.
        
        Args:
            region_code: Region code
            category_id: YouTube category ID
            max_results: Maximum results
            
        Returns:
            List of trending video items
        """
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(max_results, self.MAX_RESULTS_PER_PAGE),
        }

        if category_id:
            params["videoCategoryId"] = category_id

        all_videos = []
        next_page_token = None

        while len(all_videos) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = await self._make_request("videos", params)
            items = data.get("items", [])
            all_videos.extend(items)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        return all_videos[:max_results]

    async def search_channels(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance",
    ) -> List[Dict[str, Any]]:
        """
        Search for channels on YouTube.
        
        Args:
            query: Search query
            max_results: Maximum results
            order: Sort order
            
        Returns:
            List of channel items
        """
        params = {
            "part": "snippet",
            "q": query,
            "maxResults": min(max_results, self.MAX_RESULTS_PER_PAGE),
            "order": order,
            "type": "channel",
        }

        all_items = []
        next_page_token = None

        while len(all_items) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = await self._make_request("search", params)
            items = data.get("items", [])
            all_items.extend(items)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        return all_items[:max_results]

    async def get_video_categories(
        self,
        region_code: str = "US",
    ) -> List[Dict[str, Any]]:
        """
        Get video categories.
        
        Args:
            region_code: Region code
            
        Returns:
            List of category items
        """
        params = {
            "part": "snippet",
            "regionCode": region_code,
        }
        data = await self._make_request("videoCategories", params)
        return data.get("items", [])

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
