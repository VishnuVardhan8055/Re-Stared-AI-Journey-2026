"""
News API Endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from typing import Optional, List
import logging

from app.database.connection import get_db_session
from app.database.models import Article, Source, ArticleCategory, VerificationStatus
from app.database.schemas import (
    ArticleResponse, ArticleListResponse, NewsQueryParams,
    RefreshResponse, SourceResponse
)
from app.services.aggregator import news_aggregator
from app.verification.ai_analyzer import ai_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ArticleListResponse)
async def get_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source_id: Optional[int] = Query(None),
    category: Optional[ArticleCategory] = Query(None),
    status_filter: Optional[VerificationStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    sort_by: str = Query("published_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get paginated list of news articles

    Supports filtering by source, category, verification status, and score.
    Also supports full-text search and custom sorting.
    """
    try:
        # Build base query
        query = select(Article)

        # Apply filters
        if source_id:
            query = query.where(Article.source_id == source_id)

        if category:
            query = query.where(Article.category == category)

        if status_filter:
            query = query.where(Article.verification.has(status=status_filter))

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.summary.ilike(search_pattern)
                )
            )

        if min_score is not None:
            query = query.where(Article.verification.has(overall_score >= min_score))

        # Apply sorting
        sort_column = getattr(Article, sort_by, Article.published_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()

        # Load related data
        for article in articles:
            await db.refresh(article, ["source", "verification"])

        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0

        return ArticleListResponse(
            articles=[ArticleResponse.model_validate(article) for article in articles],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving news articles"
        )


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific article with full details"""
    try:
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

        # Load related data
        await db.refresh(article, ["source", "verification"])

        # Increment view count
        article.views += 1
        await db.commit()

        return ArticleResponse.model_validate(article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving article"
        )


@router.get("/trending", response_model=List[ArticleResponse])
async def get_trending(
    limit: int = Query(10, ge=1, le=50),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending articles based on views and recency"""
    try:
        from datetime import datetime, timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)

        query = (
            select(Article)
            .where(Article.published_at >= cutoff_time)
            .order_by(desc(Article.views))
            .limit(limit)
        )

        result = await db.execute(query)
        articles = result.scalars().all()

        # Load related data
        for article in articles:
            await db.refresh(article, ["source", "verification"])

        return [ArticleResponse.model_validate(article) for article in articles]

    except Exception as e:
        logger.error(f"Error getting trending news: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving trending articles"
        )


@router.get("/search", response_model=ArticleListResponse)
async def search_news(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[ArticleCategory] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Search for articles by keyword"""
    try:
        search_pattern = f"%{q}%"

        # Build query
        query = (
            select(Article)
            .where(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.summary.ilike(search_pattern)
                )
            )
        )

        if category:
            query = query.where(Article.category == category)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()

        # Load related data
        for article in articles:
            await db.refresh(article, ["source", "verification"])

        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0

        return ArticleListResponse(
            articles=[ArticleResponse.model_validate(article) for article in articles],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching articles"
        )


@router.get("/sources", response_model=List[SourceResponse])
async def get_sources(
    type_filter: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all news sources"""
    try:
        query = select(Source)

        if type_filter:
            query = query.where(Source.type == type_filter)

        query = query.order_by(Source.credibility_score.desc())

        result = await db.execute(query)
        sources = result.scalars().all()

        return [SourceResponse.model_validate(source) for source in sources]

    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sources"
        )


@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all available article categories"""
    return [cat.value for cat in ArticleCategory]


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_news(
    db: AsyncSession = Depends(get_db_session)
):
    """Trigger news aggregation from all sources"""
    try:
        stats = await news_aggregator.aggregate_all(db)

        return RefreshResponse(
            message=f"Aggregated news from {stats['sources_processed']} sources",
            articles_added=stats["articles_added"],
            articles_updated=stats["articles_updated"],
            sources_processed=stats["sources_processed"]
        )

    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing news"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_news_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """Get news statistics"""
    try:
        # Total articles
        total_articles = await db.execute(select(func.count()).select_from(Article))
        total = total_articles.scalar_one()

        # Articles by category
        category_stats = await db.execute(
            select(Article.category, func.count(Article.id))
            .group_by(Article.category)
        )
        by_category = {cat.value: count for cat, count in category_stats.all()}

        # Total sources
        total_sources = await db.execute(select(func.count()).select_from(Source))
        sources = total_sources.scalar_one()

        # Recent articles (last 24h)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent = await db.execute(
            select(func.count()).select_from(Article).where(Article.published_at >= yesterday)
        )
        recent_count = recent.scalar_one()

        return {
            "total_articles": total,
            "recent_articles_24h": recent_count,
            "total_sources": sources,
            "articles_by_category": by_category
        }

    except Exception as e:
        logger.error(f"Error getting news stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )