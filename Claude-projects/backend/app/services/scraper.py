"""
Web Scraper Service
Using BeautifulSoup and Playwright for dynamic content
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
import httpx

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for fetching news from websites"""

    def __init__(self):
        """Initialize web scraper"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.timeout = 30

    async def scrape_url(
        self,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single URL for article content

        Args:
            url: URL to scrape

        Returns:
            Dictionary with article data or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)

                if response.status_code != 200:
                    logger.warning(f"Failed to scrape {url}: Status {response.status_code}")
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')
                return self._parse_article(soup, url)

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def scrape_blog(
        self,
        base_url: str,
        max_articles: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape blog posts from a tech company blog

        Args:
            base_url: Base URL of the blog
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(base_url, headers=self.headers, follow_redirects=True)

                if response.status_code != 200:
                    logger.warning(f"Failed to scrape blog {base_url}: Status {response.status_code}")
                    return []

                soup = BeautifulSoup(response.text, 'html.parser')
                article_links = self._extract_article_links(soup, base_url)

                articles = []
                count = 0

                for link in article_links[:max_articles]:
                    article = await self.scrape_url(link)
                    if article:
                        articles.append(article)
                        count += 1
                        # Small delay to be respectful
                        await asyncio.sleep(0.5)

                logger.info(f"Scraped {len(articles)} articles from {base_url}")
                return articles

        except Exception as e:
            logger.error(f"Error scraping blog {base_url}: {e}")
            return []

    def _parse_article(
        self,
        soup: BeautifulSoup,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse article from BeautifulSoup object

        Args:
            soup: BeautifulSoup object
            url: Article URL

        Returns:
            Dictionary with article data
        """
        try:
            # Try common title selectors
            title_selectors = [
                'h1',
                'article h1',
                '.article-title',
                '.entry-title',
                '.post-title',
                '[class*="title"]'
            ]

            title = None
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    break

            if not title:
                logger.warning(f"No title found for {url}")
                return None

            # Try common content selectors
            content_selectors = [
                'article',
                '.article-content',
                '.entry-content',
                '.post-content',
                '.content',
                '[class*="content"]',
                'main'
            ]

            content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator='\n', strip=True)
                    if len(content) > 200:  # Make sure it's actual content
                        break

            if not content:
                # Fallback to body
                content = soup.get_text(separator='\n', strip=True)

            # Extract author
            author = None
            author_selectors = [
                '.author',
                '.byline',
                '.post-author',
                '[class*="author"]'
            ]
            for selector in author_selectors:
                element = soup.select_one(selector)
                if element:
                    author = element.get_text(strip=True)
                    break

            # Extract publish date
            published = None
            date_selectors = [
                'time[datetime]',
                '.publish-date',
                '.post-date',
                '[class*="date"]'
            ]
            for selector in date_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'time':
                        published = element.get('datetime')
                    else:
                        published = element.get_text(strip=True)
                    break

            # Parse date
            if published:
                published = self._parse_date(published)
            else:
                published = datetime.now()

            # Extract image
            image_url = None
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_url = og_image.get('content')

            if not image_url:
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image:
                    image_url = twitter_image.get('content')

            # Make image URL absolute
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(url, image_url)

            # Create summary
            summary = content[:500]

            # Extract domain
            domain = urlparse(url).netloc

            return {
                "title": title,
                "content": content,
                "summary": summary,
                "url": url,
                "published_at": published,
                "author": author,
                "image_url": image_url,
                "source_type": "scraper",
                "domain": domain
            }

        except Exception as e:
            logger.error(f"Error parsing article from {url}: {e}")
            return None

    def _extract_article_links(
        self,
        soup: BeautifulSoup,
        base_url: str
    ) -> List[str]:
        """
        Extract article links from a blog page

        Args:
            soup: BeautifulSoup object
            base_url: Base URL

        Returns:
            List of article URLs
        """
        links = []

        # Common link selectors for articles
        link_selectors = [
            'a[href*="/article/"]',
            'a[href*="/blog/"]',
            'a[href*="/post/"]',
            'article a[href]',
            '.article-link a[href]'
        ]

        for selector in link_selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if href:
                    # Make URL absolute
                    absolute_url = urljoin(base_url, href)

                    # Only include links from same domain
                    if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                        links.append(absolute_url)

        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        return unique_links

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object

        Args:
            date_str: Date string

        Returns:
            Datetime object
        """
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return datetime.now()


# Singleton instance
web_scraper = WebScraper()