"""
Verification API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
import logging

from app.database.connection import get_db_session
from app.database.models import Article, ArticleVerification, VerificationStatus
from app.database.schemas import VerificationResponse
from app.verification.cross_check import cross_check_verifier
from app.verification.credibility import credibility_scorer
from app.verification.ai_analyzer import ai_analyzer
from app.verification.fact_check import fact_check_api
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/verify/{article_id}", response_model=VerificationResponse)
async def verify_article(
    article_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify a specific article using all verification methods
    """
    try:
        # Get article
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

        # Run all verification methods
        cross_check_score, cross_check_count = await cross_check_verifier.verify_article(db, article_id)
        credibility_score = await credibility_scorer.score_article(db, article_id)

        # AI Analysis
        ai_analysis = await ai_analyzer.analyze_article(
            title=article.title,
            content=article.content,
            summary=article.summary
        )
        ai_score = ai_analyzer.calculate_ai_score(ai_analysis)
        ai_sentiment = ai_analyzer.get_sentiment(ai_analysis)

        # Fact Check
        fact_check_result = await fact_check_api.check_article(
            title=article.title,
            content=article.content
        )
        fact_check_score = fact_check_api.calculate_fact_check_score(fact_check_result)

        # Calculate overall score
        overall_score = calculate_overall_score(
            cross_check_score=cross_check_score,
            credibility_score=credibility_score,
            ai_score=ai_score,
            fact_check_score=fact_check_score
        )

        # Determine verification status
        verification_status = determine_status(overall_score)

        # Create or update verification record
        result = await db.execute(
            select(ArticleVerification).where(ArticleVerification.article_id == article_id)
        )
        verification = result.scalar_one_or_none()

        import json
        from datetime import datetime

        if verification:
            verification.cross_check_score = cross_check_score
            verification.cross_check_count = cross_check_count
            verification.credibility_score = credibility_score
            verification.ai_analysis = json.dumps(ai_analysis)
            verification.ai_sentiment = ai_sentiment
            verification.fact_check_result = json.dumps(fact_check_result)
            verification.fact_check_rating = fact_check_result.get("overall_rating", {}).get("rating")
            verification.overall_score = overall_score
            verification.status = verification_status
            verification.verified_at = datetime.now()
            verification.updated_at = datetime.now()
        else:
            verification = ArticleVerification(
                article_id=article_id,
                cross_check_score=cross_check_score,
                cross_check_count=cross_check_count,
                credibility_score=credibility_score,
                ai_analysis=json.dumps(ai_analysis),
                ai_sentiment=ai_sentiment,
                fact_check_result=json.dumps(fact_check_result),
                fact_check_rating=fact_check_result.get("overall_rating", {}).get("rating"),
                overall_score=overall_score,
                status=verification_status,
                verified_at=datetime.now()
            )
            db.add(verification)

        await db.commit()

        return VerificationResponse(
            article_id=article_id,
            cross_check_score=cross_check_score,
            cross_check_count=cross_check_count,
            credibility_score=credibility_score,
            ai_analysis=ai_analysis,
            ai_sentiment=ai_sentiment,
            fact_check_result=fact_check_result,
            fact_check_rating=fact_check_result.get("overall_rating", {}).get("rating"),
            overall_score=overall_score,
            status=verification_status,
            verified_at=verification.verified_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying article"
        )


@router.get("/stats")
async def get_verification_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """Get verification statistics"""
    try:
        # Total articles
        total_articles = await db.execute(select(func.count()).select_from(Article))
        total = total_articles.scalar_one()

        # Verified articles
        verified = await db.execute(
            select(func.count()).select_from(ArticleVerification)
            .where(ArticleVerification.status == VerificationStatus.VERIFIED)
        )
        verified_count = verified.scalar_one()

        # Needs review
        needs_review = await db.execute(
            select(func.count()).select_from(ArticleVerification)
            .where(ArticleVerification.status == VerificationStatus.NEEDS_REVIEW)
        )
        needs_review_count = needs_review.scalar_one()

        # Unverified
        unverified = await db.execute(
            select(func.count()).select_from(ArticleVerification)
            .where(ArticleVerification.status == VerificationStatus.UNVERIFIED)
        )
        unverified_count = unverified.scalar_one()

        # Misleading
        misleading = await db.execute(
            select(func.count()).select_from(ArticleVerification)
            .where(ArticleVerification.status == VerificationStatus.MISLEADING)
        )
        misleading_count = misleading.scalar_one()

        # Average score
        avg_score = await db.execute(
            select(func.avg(ArticleVerification.overall_score))
            .select_from(ArticleVerification)
        )
        avg_score_value = avg_score.scalar_one() or 0

        return {
            "total_articles": total,
            "verified": verified_count,
            "needs_review": needs_review_count,
            "unverified": unverified_count,
            "misleading": misleading_count,
            "average_score": round(avg_score_value, 2)
        }

    except Exception as e:
        logger.error(f"Error getting verification stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving verification statistics"
        )


@router.post("/batch-verify")
async def batch_verify(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify multiple unverified articles
    """
    try:
        # Get articles without verification
        result = await db.execute(
            select(Article).order_by(Article.published_at.desc()).limit(limit)
        )
        articles = result.scalars().all()

        verified_count = 0
        failed_count = 0

        for article in articles:
            try:
                await verify_article(article.id, db)
                verified_count += 1
            except Exception as e:
                logger.error(f"Failed to verify article {article.id}: {e}")
                failed_count += 1

        return {
            "message": f"Batch verification complete",
            "verified": verified_count,
            "failed": failed_count,
            "total": len(articles)
        }

    except Exception as e:
        logger.error(f"Error in batch verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in batch verification"
        )


@router.post("/update-sources")
async def update_source_scores(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update credibility scores for all sources
    """
    try:
        stats = await credibility_scorer.update_all_sources(db)

        return {
            "message": "Source credibility scores updated",
            "updated": stats["updated"],
            "average_score": round(stats["avg_score"], 2)
        }

    except Exception as e:
        logger.error(f"Error updating source scores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating source scores"
        )


def calculate_overall_score(
    cross_check_score: float,
    credibility_score: float,
    ai_score: float,
    fact_check_score: float
) -> float:
    """
    Calculate overall verification score using weighted average

    Weights from settings:
    - Cross check: 30%
    - Source credibility: 25%
    - AI analysis: 25%
    - Fact check: 20%
    """
    return (
        cross_check_score * settings.cross_check_weight +
        credibility_score * settings.source_credibility_weight +
        ai_score * settings.ai_analysis_weight +
        fact_check_score * settings.fact_check_weight
    )


def determine_status(score: float) -> VerificationStatus:
    """
    Determine verification status based on overall score

    Thresholds from settings:
    - >= 70: Verified
    - >= 40: Needs Review
    - < 40: Unverified
    - Very low: Misleading
    """
    if score >= settings.verified_threshold:
        return VerificationStatus.VERIFIED
    elif score >= settings.needs_review_threshold:
        return VerificationStatus.NEEDS_REVIEW
    elif score >= 20:
        return VerificationStatus.UNVERIFIED
    else:
        return VerificationStatus.MISLEADING