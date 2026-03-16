"""
Source Cross-Check Verification
Compares articles across sources to identify similar content
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Article, ArticleVerification
from app.config import settings

logger = logging.getLogger(__name__)


class CrossCheckVerifier:
    """Cross-reference verification across sources"""

    def __init__(self):
        """Initialize cross-check verifier"""
        self.similarity_threshold = 0.7
        self.time_window_hours = 48

    async def verify_article(
        self,
        db: AsyncSession,
        article_id: int
    ) -> Tuple[float, int]:
        """
        Verify an article by cross-checking with similar articles

        Args:
            db: Database session
            article_id: Article ID to verify

        Returns:
            Tuple of (cross_check_score, cross_check_count)
        """
        try:
            # Get the article
            result = await db.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()

            if not article:
                logger.warning(f"Article {article_id} not found")
                return 0.0, 0

            # Find similar articles from other sources
            similar_articles = await self._find_similar_articles(db, article)

            if not similar_articles:
                logger.info(f"No similar articles found for {article_id}")
                return 0.0, 0

            # Calculate cross-check score
            score = self._calculate_cross_check_score(article, similar_articles)

            logger.info(
                f"Cross-check for article {article_id}: "
                f"score={score:.2f}, count={len(similar_articles)}"
            )

            return score, len(similar_articles)

        except Exception as e:
            logger.error(f"Error in cross-check verification: {e}")
            return 0.0, 0

    async def _find_similar_articles(
        self,
        db: AsyncSession,
        article: Article
    ) -> List[Article]:
        """Find similar articles from other sources"""
        try:
            # Get articles from other sources published within time window
            time_threshold = article.published_at - timedelta(hours=self.time_window_hours)

            result = await db.execute(
                select(Article).where(
                    Article.id != article.id,
                    Article.source_id != article.source_id,
                    Article.published_at >= time_threshold
                )
            )
            candidates = result.scalars().all()

            # Filter by similarity
            similar = []
            for candidate in candidates:
                similarity = self._calculate_similarity(article, candidate)
                if similarity >= self.similarity_threshold:
                    similar.append((candidate, similarity))

            # Sort by similarity (descending)
            similar.sort(key=lambda x: x[1], reverse=True)

            return [article for article, _ in similar[:10]]  # Return top 10

        except Exception as e:
            logger.error(f"Error finding similar articles: {e}")
            return []

    def _calculate_similarity(
        self,
        article1: Article,
        article2: Article
    ) -> float:
        """Calculate similarity between two articles"""
        # Title similarity (weighted more)
        title_sim = self._text_similarity(article1.title, article2.title)

        # Content similarity
        content_sim = self._text_similarity(
            article1.content[:500],
            article2.content[:500]
        )

        # Combined similarity
        return (title_sim * 0.6) + (content_sim * 0.4)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard similarity"""
        try:
            # Tokenize and normalize
            words1 = self._tokenize(text1)
            words2 = self._tokenize(text2)

            if not words1 or not words2:
                return 0.0

            # Calculate Jaccard similarity
            intersection = len(words1 & words2)
            union = len(words1 | words2)

            return intersection / union if union > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0

    def _tokenize(self, text: str) -> set:
        """Tokenize text into words"""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                      'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were',
                      'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
                      'did', 'will', 'would', 'could', 'should', 'may', 'might',
                      'must', 'shall', 'can', 'need', 'dare', 'ought', 'used'}

        return {w for w in words if w not in stop_words and len(w) > 2}

    def _calculate_cross_check_score(
        self,
        article: Article,
        similar_articles: List[Article]
    ) -> float:
        """
        Calculate cross-check score based on similar articles

        Score ranges from 0-100
        """
        if not similar_articles:
            return 0.0

        # Count unique sources
        unique_sources = len({a.source_id for a in similar_articles})

        # Calculate average similarity
        similarities = [
            self._calculate_similarity(article, similar)
            for similar in similar_articles
        ]
        avg_similarity = sum(similarities) / len(similarities)

        # Combine source count and similarity
        # More sources = higher score, but max out at 5 sources
        source_score = min(unique_sources * 20, 100)
        similarity_score = avg_similarity * 100

        # Weighted average
        return (source_score * 0.4) + (similarity_score * 0.6)

    async def verify_all_articles(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> Dict[str, int]:
        """
        Verify all recent articles

        Args:
            db: Database session
            limit: Maximum number of articles to verify

        Returns:
            Statistics dictionary
        """
        logger.info("Starting cross-check verification for all articles")

        try:
            # Get recent articles without verification
            result = await db.execute(
                select(Article).order_by(Article.published_at.desc()).limit(limit)
            )
            articles = result.scalars().all()

            verified_count = 0
            total_score = 0.0

            for article in articles:
                score, count = await self.verify_article(db, article.id)
                total_score += score
                verified_count += 1

            avg_score = total_score / verified_count if verified_count > 0 else 0.0

            logger.info(
                f"Cross-check verification complete. "
                f"Verified: {verified_count}, Avg Score: {avg_score:.2f}"
            )

            return {
                "verified": verified_count,
                "avg_score": avg_score
            }

        except Exception as e:
            logger.error(f"Error in verify_all_articles: {e}")
            return {
                "verified": 0,
                "avg_score": 0.0
            }


# Singleton instance
cross_check_verifier = CrossCheckVerifier()