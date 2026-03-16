"""
Twitter/X API Client Service
"""

import tweepy
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter/X API client for fetching news"""

    def __init__(self):
        """Initialize Twitter client"""
        self.client = None
        self._initialize()

    def _initialize(self):
        """Initialize Twitter API client"""
        try:
            # Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_secret,
                wait_on_rate_limit=True
            )
            logger.info("Twitter client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            self.client = None

    async def fetch_tweets_by_hashtag(
        self,
        hashtag: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch tweets by hashtag

        Args:
            hashtag: Hashtag to search for (with or without #)
            max_results: Maximum number of tweets to fetch

        Returns:
            List of tweet data dictionaries
        """
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        try:
            hashtag = hashtag if hashtag.startswith("#") else f"#{hashtag}"
            tweets = self.client.search_recent_tweets(
                query=hashtag,
                max_results=max_results,
                tweet_fields=[
                    "created_at", "author_id", "public_metrics",
                    "entities", "source", "context_annotations"
                ],
                expansions=["author_id"]
            )

            if not tweets.data:
                return []

            # Convert to article-like format
            articles = []
            for tweet in tweets.data:
                article = self._tweet_to_article(tweet)
                if article:
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} tweets for {hashtag}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching tweets by hashtag: {e}")
            return []

    async def fetch_tweets_by_user(
        self,
        username: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch tweets from a specific user

        Args:
            username: Twitter username (with or without @)
            max_results: Maximum number of tweets to fetch

        Returns:
            List of tweet data dictionaries
        """
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        try:
            username = username if username.startswith("@") else f"@{username}"
            user = self.client.get_user(username=username)

            if not user.data:
                logger.warning(f"User not found: {username}")
                return []

            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=max_results,
                tweet_fields=[
                    "created_at", "author_id", "public_metrics",
                    "entities", "source", "context_annotations"
                ]
            )

            if not tweets.data:
                return []

            articles = []
            for tweet in tweets.data:
                article = self._tweet_to_article(tweet, user.data.username)
                if article:
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} tweets from {username}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching tweets by user: {e}")
            return []

    async def fetch_trending_topics(
        self,
        woeid: int = 1,  # 1 = Worldwide
    ) -> List[str]:
        """
        Fetch trending topics

        Args:
            woeid: Where on Earth ID for location (1 = worldwide)

        Returns:
            List of trending topic names
        """
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        try:
            # Note: v2 API has limited trending support
            # This would require v1.1 API access
            logger.info("Trending topics feature requires v1.1 API access")
            return []

        except Exception as e:
            logger.error(f"Error fetching trending topics: {e}")
            return []

    def _tweet_to_article(
        self,
        tweet: tweepy.Tweet,
        username: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Convert tweet to article format

        Args:
            tweet: Tweet object
            username: Optional username override

        Returns:
            Dictionary in article format
        """
        try:
            # Extract URLs from tweet entities
            url = f"https://twitter.com/i/status/{tweet.id}"
            article_url = url

            if tweet.entities and "urls" in tweet.entities and tweet.entities["urls"]:
                # Use first expanded URL if available
                expanded_url = tweet.entities["urls"][0].get("expanded_url")
                if expanded_url:
                    article_url = expanded_url

            # Extract media if available
            image_url = None
            if tweet.attachments and "media_keys" in tweet.attachments:
                # Media would need to be fetched separately
                pass

            return {
                "title": tweet.text[:200] + "..." if len(tweet.text) > 200 else tweet.text,
                "content": tweet.text,
                "summary": tweet.text[:300],
                "url": article_url,
                "published_at": tweet.created_at,
                "author": username or "Unknown",
                "image_url": image_url,
                "source_type": "twitter",
                "metrics": tweet.public_metrics._asdict() if tweet.public_metrics else {}
            }

        except Exception as e:
            logger.error(f"Error converting tweet to article: {e}")
            return None

    async def search_news(
        self,
        query: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for news-related tweets

        Args:
            query: Search query
            max_results: Maximum number of tweets to fetch

        Returns:
            List of tweet data dictionaries
        """
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        try:
            # Add news-related filters
            search_query = f"{query} -is:retweet lang:en"

            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=max_results,
                tweet_fields=[
                    "created_at", "author_id", "public_metrics",
                    "entities", "source", "context_annotations"
                ],
                expansions=["author_id"]
            )

            if not tweets.data:
                return []

            articles = []
            for tweet in tweets.data:
                article = self._tweet_to_article(tweet)
                if article:
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} news tweets for query: {query}")
            return articles

        except Exception as e:
            logger.error(f"Error searching news tweets: {e}")
            return []


# Singleton instance
twitter_client = TwitterClient()