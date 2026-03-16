"""
News Aggregation Orchestrator
Coordinates all data sources and manages article deduplication
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Source, Article, SourceType, ArticleCategory
from app.database.schemas import ArticleCreate
from app.services.twitter_client import twitter_client
from app.services.rss_parser import rss_parser
from app.services.scraper import web_scraper
from app.services.news_api_client import news_api_client, gnews_client

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Main news aggregation orchestrator"""

    def __init__(self):
        """Initialize aggregator"""
        self.sources_processed = 0
        self.articles_added = 0
        self.articles_updated = 0

    async def aggregate_all(
        self,
        db: AsyncSession,
        max_per_source: int = 50
    ) -> Dict[str, int]:
        """
        Aggregate news from all configured sources

        Args:
            db: Database session
            max_per_source: Maximum articles per source

        Returns:
            Dictionary with statistics
        """
        logger.info("Starting news aggregation from all sources")

        self.sources_processed = 0
        self.articles_added = 0
        self.articles_updated = 0

        try:
            # Get all active sources from database
            result = await db.execute(
                select(Source).where(Source.id > 0)
            )
            sources = result.scalars().all()

            logger.info(f"Found {len(sources)} sources to aggregate")

            # Process each source
            for source in sources:
                try:
                    await self.aggregate_from_source(db, source, max_per_source)
                    self.sources_processed += 1
                    # Update last_fetched_at
                    source.last_fetched_at = datetime.now()

                except Exception as e:
                    logger.error(f"Error aggregating from source {source.id}: {e}")

            await db.commit()

            logger.info(
                f"Aggregation complete. Sources: {self.sources_processed}, "
                f"Added: {self.articles_added}, Updated: {self.articles_updated}"
            )

            return {
                "sources_processed": self.sources_processed,
                "articles_added": self.articles_added,
                "articles_updated": self.articles_updated
            }

        except Exception as e:
            logger.error(f"Error in aggregate_all: {e}")
            await db.rollback()
            raise

    async def aggregate_from_source(
        self,
        db: AsyncSession,
        source: Source,
        max_articles: int
    ):
        """
        Aggregate news from a specific source

        Args:
            db: Database session
            source: Source model
            max_articles: Maximum articles to fetch
        """
        logger.info(f"Aggregating from {source.name} ({source.type})")

        articles_data = []

        # Fetch articles based on source type
        if source.type == SourceType.TWITTER:
            articles_data = await self._fetch_from_twitter(source, max_articles)
        elif source.type == SourceType.RSS:
            articles_data = await self._fetch_from_rss(source, max_articles)
        elif source.type == SourceType.SCRAPER:
            articles_data = await self._fetch_from_scraper(source, max_articles)
        elif source.type == SourceType.API:
            articles_data = await self._fetch_from_api(source, max_articles)
        else:
            logger.warning(f"Unknown source type: {source.type}")
            return

        # Process and store articles
        for article_data in articles_data:
            await self._process_article(db, article_data, source)

    async def _fetch_from_twitter(
        self,
        source: Source,
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """Fetch from Twitter/X"""
        try:
            # Extract hashtag or username from URL or description
            hashtag = self._extract_hashtag_from_source(source)

            if hashtag.startswith("@"):
                return await twitter_client.fetch_tweets_by_user(
                    hashtag,
                    max_results=max_articles
                )
            else:
                return await twitter_client.fetch_tweets_by_hashtag(
                    hashtag,
                    max_results=max_articles
                )

        except Exception as e:
            logger.error(f"Error fetching from Twitter: {e}")
            return []

    async def _fetch_from_rss(
        self,
        source: Source,
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """Fetch from RSS feed"""
        return await rss_parser.parse_feed(source.url, max_articles)

    async def _fetch_from_scraper(
        self,
        source: Source,
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """Fetch from web scraper"""
        return await web_scraper.scrape_blog(source.url, max_articles)

    async def _fetch_from_api(
        self,
        source: Source,
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """Fetch from news API"""
        # Try NewsAPI first
        try:
            # Check if source specifies a category
            category = "general"
            if source.description:
                category = source.description.lower()

            articles = await news_api_client.get_top_headlines(
                category=category,
                page_size=max_articles
            )

            if articles:
                return articles

        except Exception as e:
            logger.error(f"Error with NewsAPI: {e}")

        # Fallback to GNews
        try:
            return await gnews_client.get_top_headlines(max_articles=max_articles)
        except Exception as e:
            logger.error(f"Error with GNews: {e}")

        return []

    def _extract_hashtag_from_source(self, source: Source) -> str:
        """Extract hashtag or username from source"""
        if source.description:
            return source.description
        return source.name

    async def _process_article(
        self,
        db: AsyncSession,
        article_data: Dict[str, Any],
        source: Source
    ):
        """Process and store a single article"""
        try:
            # Check if article already exists
            result = await db.execute(
                select(Article).where(Article.url == article_data["url"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing article
                existing.title = article_data.get("title", existing.title)
                existing.content = article_data.get("content", existing.content)
                existing.summary = article_data.get("summary", existing.summary)
                existing.image_url = article_data.get("image_url", existing.image_url)
                existing.updated_at = datetime.now()
                self.articles_updated += 1
            else:
                # Create new article
                # Infer category from content
                category = self._infer_category(article_data)

                article = Article(
                    title=article_data.get("title"),
                    content=article_data.get("content"),
                    summary=article_data.get("summary"),
                    url=article_data.get("url"),
                    published_at=article_data.get("published_at"),
                    source_id=source.id,
                    category=category,
                    author=article_data.get("author"),
                    image_url=article_data.get("image_url")
                )
                db.add(article)
                self.articles_added += 1

        except Exception as e:
            logger.error(f"Error processing article: {e}")

    def _infer_category(self, article_data: Dict[str, Any]) -> ArticleCategory:
        """Infer article category from content"""
        title = article_data.get("title", "").lower()
        content = article_data.get("content", "").lower()

        tech_keywords = [
            "tech", "technology", "software", "ai", "artificial intelligence",
            "machine learning", "programming", "code", "developer", "app",
            "startup", "silicon valley"
        ]

        business_keywords = [
            "business", "market", "stock", "economy", "finance", "investor",
            "startup", "company", "corporate", "revenue", "profit"
        ]

        politics_keywords = [
            "politic", "government", "election", "congress", "senate",
            "president", "minister", "parliament", "vote", "policy"
        ]

        health_keywords = [
            "health", "medical", "doctor", "hospital", "disease", "vaccine",
            "covid", "treatment", "medicine", "patient"
        ]

        science_keywords = [
            "science", "research", "study", "discovery", "scientist",
            "experiment", "space", "physics", "biology", "chemistry"
        ]

        # Check keywords
        text = title + " " + content

        for keyword in tech_keywords:
            if keyword in text:
                return ArticleCategory.TECH

        for keyword in business_keywords:
            if keyword in text:
                return ArticleCategory.BUSINESS

        for keyword in politics_keywords:
            if keyword in text:
                return ArticleCategory.POLITICS

        for keyword in health_keywords:
            if keyword in text:
                return ArticleCategory.HEALTH

        for keyword in science_keywords:
            if keyword in text:
                return ArticleCategory.SCIENCE

        return ArticleCategory.NEWS

    async def deduplicate_articles(
        self,
        db: AsyncSession
    ) -> int:
        """
        Remove duplicate articles based on similarity

        Args:
            db: Database session

        Returns:
            Number of duplicates removed
        """
        logger.info("Starting article deduplication")

        try:
            # Get all articles
            result = await db.execute(select(Article))
            articles = result.scalars().all()

            # Group by similarity
            removed = 0
            seen = {}

            for article in articles:
                # Create a simple key from title
                key = self._create_similarity_key(article.title)

                if key in seen:
                    # Mark for deletion (keep the newer one)
                    if article.published_at > seen[key].published_at:
                        await db.delete(seen[key])
                        seen[key] = article
                    else:
                        await db.delete(article)
                    removed += 1
                else:
                    seen[key] = article

            await db.commit()

            logger.info(f"Deduplication complete. Removed {removed} duplicates")
            return removed

        except Exception as e:
            logger.error(f"Error in deduplication: {e}")
            await db.rollback()
            return 0

    def _create_similarity_key(self, text: str) -> str:
        """Create a simple key for similarity matching"""
        import re
        # Remove common words and normalize
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove very common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        # Take first 5 significant words
        key = ' '.join(words[:5])
        return key


# Singleton instance
news_aggregator = NewsAggregator()