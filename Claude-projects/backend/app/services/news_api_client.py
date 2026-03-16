"""
News API Client Service
Integrates with NewsAPI.org and other news APIs
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.config import settings

logger = logging.getLogger(__name__)


class NewsAPIClient:
    """Client for NewsAPI.org"""

    def __init__(self):
        """Initialize NewsAPI client"""
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-API-Key": self.api_key,
            "User-Agent": "NewsPlatform/1.0"
        }
        self.timeout = 30

    async def get_top_headlines(
        self,
        category: str = "general",
        country: str = "us",
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines from NewsAPI

        Args:
            category: News category (business, entertainment, general, health, science, sports, technology)
            country: Country code (us, gb, etc.)
            page_size: Number of articles to fetch

        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        try:
            params = {
                "category": category,
                "country": country,
                "pageSize": page_size,
                "language": "en"
            }

            url = f"{self.base_url}/top-headlines?{urlencode(params)}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    logger.warning(f"NewsAPI error: {response.status_code}")
                    return []

                data = response.json()

                if data.get("status") != "ok":
                    logger.warning(f"NewsAPI returned error: {data.get('message')}")
                    return []

                articles = []
                for article_data in data.get("articles", []):
                    article = self._api_article_to_article(article_data)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} headlines from NewsAPI")
                return articles

        except Exception as e:
            logger.error(f"Error fetching top headlines: {e}")
            return []

    async def search_articles(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for articles on NewsAPI

        Args:
            query: Search query
            from_date: Start date for search
            to_date: End date for search
            language: Language code
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Number of articles to fetch

        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        try:
            params = {
                "q": query,
                "language": language,
                "sortBy": sort_by,
                "pageSize": page_size
            }

            if from_date:
                params["from"] = from_date.strftime("%Y-%m-%d")

            if to_date:
                params["to"] = to_date.strftime("%Y-%m-%d")

            url = f"{self.base_url}/everything?{urlencode(params)}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    logger.warning(f"NewsAPI error: {response.status_code}")
                    return []

                data = response.json()

                if data.get("status") != "ok":
                    logger.warning(f"NewsAPI returned error: {data.get('message')}")
                    return []

                articles = []
                for article_data in data.get("articles", []):
                    article = self._api_article_to_article(article_data)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} articles from NewsAPI for query: {query}")
                return articles

        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []

    async def get_sources(
        self,
        category: Optional[str] = None,
        language: str = "en",
        country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available news sources

        Args:
            category: Category filter
            language: Language code
            country: Country code

        Returns:
            List of source dictionaries
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        try:
            params = {
                "language": language
            }

            if category:
                params["category"] = category

            if country:
                params["country"] = country

            url = f"{self.base_url}/sources?{urlencode(params)}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    return []

                data = response.json()

                if data.get("status") != "ok":
                    return []

                return data.get("sources", [])

        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return []

    def _api_article_to_article(
        self,
        article_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert NewsAPI article format to internal format

        Args:
            article_data: Article data from NewsAPI

        Returns:
            Dictionary in internal article format
        """
        try:
            title = article_data.get("title", "")
            if not title:
                return None

            url = article_data.get("url", "")
            if not url:
                return None

            # Parse published date
            published_at = article_data.get("publishedAt")
            if published_at:
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()

            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

            return {
                "title": title,
                "content": article_data.get("content") or article_data.get("description", ""),
                "summary": article_data.get("description", ""),
                "url": url,
                "published_at": published_at,
                "author": article_data.get("author", ""),
                "image_url": article_data.get("urlToImage"),
                "source_type": "api",
                "source_name": article_data.get("source", {}).get("name", ""),
                "domain": domain
            }

        except Exception as e:
            logger.error(f"Error converting article: {e}")
            return None


class GNewsClient:
    """Client for GNews API"""

    def __init__(self):
        """Initialize GNews client"""
        self.api_key = settings.gnews_api_key
        self.base_url = "https://gnews.io/api/v4"
        self.headers = {
            "User-Agent": "NewsPlatform/1.0"
        }
        self.timeout = 30

    async def get_top_headlines(
        self,
        category: str = "general",
        max_articles: int = 100,
        language: str = "en",
        country: str = "us"
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines from GNews

        Args:
            category: News category
            max_articles: Maximum number of articles
            language: Language code
            country: Country code

        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("GNews API key not configured")
            return []

        try:
            params = {
                "token": self.api_key,
                "max": max_articles,
                "lang": language,
                "country": country
            }

            url = f"{self.base_url}/top-headlines?{urlencode(params)}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    logger.warning(f"GNews API error: {response.status_code}")
                    return []

                data = response.json()

                articles = []
                for article_data in data.get("articles", []):
                    article = self._gnews_article_to_article(article_data)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} articles from GNews")
                return articles

        except Exception as e:
            logger.error(f"Error fetching GNews headlines: {e}")
            return []

    async def search_articles(
        self,
        query: str,
        max_articles: int = 100,
        language: str = "en",
        country: str = "us"
    ) -> List[Dict[str, Any]]:
        """
        Search articles on GNews

        Args:
            query: Search query
            max_articles: Maximum number of articles
            language: Language code
            country: Country code

        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("GNews API key not configured")
            return []

        try:
            params = {
                "token": self.api_key,
                "q": query,
                "max": max_articles,
                "lang": language,
                "country": country
            }

            url = f"{self.base_url}/search?{urlencode(params)}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    logger.warning(f"GNews API error: {response.status_code}")
                    return []

                data = response.json()

                articles = []
                for article_data in data.get("articles", []):
                    article = self._gnews_article_to_article(article_data)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} articles from GNews for query: {query}")
                return articles

        except Exception as e:
            logger.error(f"Error searching GNews: {e}")
            return []

    def _gnews_article_to_article(
        self,
        article_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert GNews article format to internal format

        Args:
            article_data: Article data from GNews

        Returns:
            Dictionary in internal article format
        """
        try:
            title = article_data.get("title", "")
            if not title:
                return None

            url = article_data.get("url", "")
            if not url:
                return None

            # Parse published date
            published_at = article_data.get("publishedAt")
            if published_at:
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()

            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

            return {
                "title": title,
                "content": article_data.get("content", "") or article_data.get("description", ""),
                "summary": article_data.get("description", ""),
                "url": url,
                "published_at": published_at,
                "author": article_data.get("author", {}).get("name", ""),
                "image_url": article_data.get("image"),
                "source_type": "api",
                "source_name": article_data.get("source", {}).get("name", ""),
                "domain": domain
            }

        except Exception as e:
            logger.error(f"Error converting GNews article: {e}")
            return None


# Singleton instances
news_api_client = NewsAPIClient()
gnews_client = GNewsClient()