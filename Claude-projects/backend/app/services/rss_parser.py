"""
RSS Feed Parser Service
"""

import feedparser
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import hashlib

from app.config import settings

logger = logging.getLogger(__name__)


class RSSParser:
    """RSS feed parser for fetching news from RSS feeds"""

    def __init__(self):
        """Initialize RSS parser"""
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    async def parse_feed(
        self,
        feed_url: str,
        max_articles: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Parse RSS feed and return articles

        Args:
            feed_url: URL of the RSS feed
            max_articles: Maximum number of articles to parse

        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Parsing RSS feed: {feed_url}")

            feed = feedparser.parse(
                feed_url,
                agent=self.user_agent
            )

            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")

            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_url}")
                return []

            articles = []
            count = 0

            for entry in feed.entries:
                if count >= max_articles:
                    break

                article = self._entry_to_article(entry, feed_url)
                if article:
                    articles.append(article)
                    count += 1

            logger.info(f"Parsed {len(articles)} articles from {feed_url}")
            return articles

        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            return []

    def _entry_to_article(
        self,
        entry: Any,
        feed_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Convert RSS entry to article format

        Args:
            entry: RSS feed entry
            feed_url: Source feed URL

        Returns:
            Dictionary in article format
        """
        try:
            # Extract basic fields
            title = entry.get('title', 'No title')
            link = entry.get('link', '')
            published = self._parse_date(entry.get('published'))

            # Extract content
            content = entry.get('summary', '')
            if not content:
                content = entry.get('description', '')

            # Try to get full content from content field
            if hasattr(entry, 'content'):
                content_list = entry.get('content', [])
                if content_list and isinstance(content_list, list):
                    content = content_list[0].get('value', content)

            # Extract author
            author = entry.get('author', '')
            if not author and hasattr(entry, 'author_detail'):
                author = entry.author_detail.get('name', '')

            # Extract image
            image_url = None
            if hasattr(entry, 'enclosures'):
                enclosures = entry.get('enclosures', [])
                for enclosure in enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href')
                        break

            # Try to extract image from content
            if not image_url and content:
                image_url = self._extract_image_url(content)

            # Create summary
            summary = self._clean_html(content)[:500]

            # Extract domain for source
            domain = urlparse(feed_url).netloc

            return {
                "title": title,
                "content": content,
                "summary": summary,
                "url": link,
                "published_at": published,
                "author": author,
                "image_url": image_url,
                "source_type": "rss",
                "feed_url": feed_url,
                "domain": domain
            }

        except Exception as e:
            logger.error(f"Error converting entry to article: {e}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse date string to datetime object

        Args:
            date_str: Date string

        Returns:
            Datetime object
        """
        if not date_str:
            return datetime.now()

        try:
            # feedparser handles most date formats
            parsed = feedparser._parse_date(date_str)
            if parsed and len(parsed) >= 6:
                return datetime(*parsed[:6])
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")

        return datetime.now()

    def _clean_html(self, html: str) -> str:
        """
        Clean HTML tags from content

        Args:
            html: HTML string

        Returns:
            Clean text
        """
        # Simple HTML tag removal
        import re
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def _extract_image_url(self, html: str) -> Optional[str]:
        """
        Extract first image URL from HTML content

        Args:
            html: HTML string

        Returns:
            Image URL or None
        """
        import re
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
        match = img_pattern.search(html)
        if match:
            return match.group(1)
        return None

    def get_feed_info(self, feed_url: str) -> Dict[str, Any]:
        """
        Get feed metadata

        Args:
            feed_url: URL of the RSS feed

        Returns:
            Dictionary with feed metadata
        """
        try:
            feed = feedparser.parse(feed_url)

            return {
                "title": feed.feed.get('title', 'Unknown'),
                "description": feed.feed.get('description', ''),
                "link": feed.feed.get('link', ''),
                "language": feed.feed.get('language', 'en'),
                "updated": self._parse_date(feed.feed.get('updated')),
                "entry_count": len(feed.entries)
            }

        except Exception as e:
            logger.error(f"Error getting feed info: {e}")
            return {
                "title": "Unknown",
                "description": "",
                "link": "",
                "language": "en",
                "updated": None,
                "entry_count": 0
            }

    def validate_feed(self, feed_url: str) -> bool:
        """
        Validate if URL is a valid RSS/Atom feed

        Args:
            feed_url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed validation error: {feed.bozo_exception}")

            return bool(feed.entries)

        except Exception as e:
            logger.error(f"Error validating feed: {e}")
            return False


# Singleton instance
rss_parser = RSSParser()