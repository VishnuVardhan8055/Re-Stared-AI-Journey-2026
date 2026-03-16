"""
Credibility Scoring System
Calculates credibility scores based on source reputation and historical accuracy
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Source, Article, ArticleVerification
from app.config import settings

logger = logging.getLogger(__name__)


# Domain authority database (simplified version)
DOMAIN_AUTHORITIES = {
    # High credibility news sources
    "reuters.com": 95,
    "apnews.com": 94,
    "bbc.com": 93,
    "nytimes.com": 92,
    "washingtonpost.com": 91,
    "theguardian.com": 90,
    "wsj.com": 89,
    "ft.com": 88,
    "economist.com": 87,
    "cnn.com": 85,
    "nbcnews.com": 84,
    "abcnews.go.com": 83,
    "usatoday.com": 82,

    # Tech sources
    "techcrunch.com": 88,
    "theverge.com": 87,
    "arstechnica.com": 89,
    "wired.com": 88,
    "mit.edu": 95,
    "stanford.edu": 94,
    "nature.com": 95,
    "science.org": 95,
    "ieee.org": 94,

    # Government sources
    "gov": 90,
    "nasa.gov": 95,
    "nih.gov": 94,
    "cdc.gov": 93,
}


class CredibilityScorer:
    """Credibility scoring based on source reputation"""

    def __init__(self):
        """Initialize credibility scorer"""
        self.domain_authorities = DOMAIN_AUTHORITIES

    async def score_source(
        self,
        db: AsyncSession,
        source_id: int
    ) -> float:
        """
        Calculate credibility score for a source

        Args:
            db: Database session
            source_id: Source ID

        Returns:
            Credibility score (0-100)
        """
        try:
            # Get source
            result = await db.execute(
                select(Source).where(Source.id == source_id)
            )
            source = result.scalar_one_or_none()

            if not source:
                logger.warning(f"Source {source_id} not found")
                return 50.0

            # Calculate score components
            domain_score = self._get_domain_authority(source.domain)
            verification_score = await self._get_average_verification_score(db, source_id)
            historical_score = await self._get_historical_accuracy(db, source_id)

            # Weighted average
            score = (
                domain_score * 0.5 +
                verification_score * 0.3 +
                historical_score * 0.2
            )

            # Update source credibility score
            source.credibility_score = score

            logger.info(f"Credibility score for {source.name}: {score:.2f}")
            return score

        except Exception as e:
            logger.error(f"Error scoring source: {e}")
            return 50.0

    def _get_domain_authority(self, domain: Optional[str]) -> float:
        """Get domain authority score"""
        if not domain:
            return 50.0

        # Check exact match
        if domain in self.domain_authorities:
            return self.domain_authorities[domain]

        # Check subdomain
        for auth_domain, score in self.domain_authorities.items():
            if domain.endswith(auth_domain):
                return score * 0.9  # Slightly lower for subdomains

        # Check for gov domains
        if domain.endswith(".gov") or domain.endswith(".gov.uk"):
            return 85.0

        # Check for educational domains
        if domain.endswith(".edu") or domain.endswith(".ac.uk"):
            return 80.0

        # Check for .org domains
        if domain.endswith(".org"):
            return 60.0

        # Default score for unknown domains
        return 50.0

    async def _get_average_verification_score(
        self,
        db: AsyncSession,
        source_id: int
    ) -> float:
        """Get average verification score for articles from source"""
        try:
            result = await db.execute(
                select(func.avg(ArticleVerification.overall_score))
                .join(Article, Article.id == ArticleVerification.article_id)
                .where(Article.source_id == source_id)
            )
            avg = result.scalar_one_or_none()

            return avg if avg else 50.0

        except Exception as e:
            logger.error(f"Error getting average verification score: {e}")
            return 50.0

    async def _get_historical_accuracy(
        self,
        db: AsyncSession,
        source_id: int
    ) -> float:
        """Calculate historical accuracy score based on verification status"""
        try:
            # Count verification statuses
            result = await db.execute(
                select(ArticleVerification.status, func.count(ArticleVerification.id))
                .join(Article, Article.id == ArticleVerification.article_id)
                .where(Article.source_id == source_id)
                .group_by(ArticleVerification.status)
            )

            status_counts = {row[0]: row[1] for row in result.all()}

            total = sum(status_counts.values())
            if total == 0:
                return 50.0

            # Calculate weighted score
            score = 0.0
            score += status_counts.get("verified", 0) * 100
            score += status_counts.get("needs_review", 0) * 50
            score += status_counts.get("unverified", 0) * 25
            score += status_counts.get("misleading", 0) * 0

            return score / total

        except Exception as e:
            logger.error(f"Error calculating historical accuracy: {e}")
            return 50.0

    async def score_article(
        self,
        db: AsyncSession,
        article_id: int
    ) -> float:
        """
        Calculate credibility score for an article

        Args:
            db: Database session
            article_id: Article ID

        Returns:
            Credibility score (0-100)
        """
        try:
            # Get article
            result = await db.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()

            if not article:
                logger.warning(f"Article {article_id} not found")
                return 50.0

            # Score the source
            source_score = await self.score_source(db, article.source_id)

            # Get source model
            source_result = await db.execute(
                select(Source).where(Source.id == article.source_id)
            )
            source = source_result.scalar_one_or_none()

            if source:
                credibility_score = source.credibility_score
            else:
                credibility_score = source_score

            logger.info(f"Credibility score for article {article_id}: {credibility_score:.2f}")
            return credibility_score

        except Exception as e:
            logger.error(f"Error scoring article: {e}")
            return 50.0

    async def update_all_sources(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update credibility scores for all sources"""
        logger.info("Updating credibility scores for all sources")

        try:
            # Get all sources
            result = await db.execute(select(Source))
            sources = result.scalars().all()

            updated = 0
            total_score = 0.0

            for source in sources:
                score = await self.score_source(db, source.id)
                total_score += score
                updated += 1

            avg_score = total_score / updated if updated > 0 else 0.0

            await db.commit()

            logger.info(
                f"Credibility scores updated. Sources: {updated}, Avg Score: {avg_score:.2f}"
            )

            return {
                "updated": updated,
                "avg_score": avg_score
            }

        except Exception as e:
            logger.error(f"Error updating all sources: {e}")
            await db.rollback()
            return {
                "updated": 0,
                "avg_score": 0.0
            }

    def add_domain_authority(self, domain: str, score: float):
        """Add or update domain authority"""
        self.domain_authorities[domain] = score
        logger.info(f"Added domain authority: {domain} = {score}")


# Singleton instance
credibility_scorer = CredibilityScorer()