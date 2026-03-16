"""
Pydantic Schemas for API Request/Response Validation
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """News source types"""
    TWITTER = "twitter"
    RSS = "rss"
    SCRAPER = "scraper"
    API = "api"


class VerificationStatus(str, Enum):
    """Article verification status"""
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    UNVERIFIED = "unverified"
    MISLEADING = "misleading"


class ArticleCategory(str, Enum):
    """Article categories"""
    NEWS = "news"
    TECH = "tech"
    POLITICS = "politics"
    BUSINESS = "business"
    SCIENCE = "science"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    WORLD = "world"
    OTHER = "other"


# Source Schemas
class SourceBase(BaseModel):
    """Base source schema"""
    name: str = Field(..., max_length=200)
    url: str = Field(..., max_length=500)
    type: SourceType
    description: Optional[str] = None
    domain: Optional[str] = Field(None, max_length=200)


class SourceCreate(SourceBase):
    """Schema for creating a source"""
    credibility_score: Optional[float] = Field(50.0, ge=0, le=100)
    is_verified: Optional[bool] = False


class SourceUpdate(BaseModel):
    """Schema for updating a source"""
    name: Optional[str] = Field(None, max_length=200)
    url: Optional[str] = Field(None, max_length=500)
    type: Optional[SourceType] = None
    credibility_score: Optional[float] = Field(None, ge=0, le=100)
    is_verified: Optional[bool] = None
    description: Optional[str] = None
    domain: Optional[str] = Field(None, max_length=200)


class SourceResponse(SourceBase):
    """Schema for source response"""
    id: int
    credibility_score: float
    is_verified: bool
    last_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Article Schemas
class ArticleBase(BaseModel):
    """Base article schema"""
    title: str = Field(..., max_length=500)
    content: str
    summary: Optional[str] = None
    url: str = Field(..., max_length=1000)
    published_at: datetime
    source_id: int
    category: ArticleCategory = ArticleCategory.NEWS
    author: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = Field(None, max_length=1000)


class ArticleCreate(ArticleBase):
    """Schema for creating an article"""
    pass


class ArticleUpdate(BaseModel):
    """Schema for updating an article"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[ArticleCategory] = None
    author: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = Field(None, max_length=1000)
    views: Optional[int] = None


class ArticleVerificationDetail(BaseModel):
    """Article verification details"""
    cross_check_score: float
    cross_check_count: int
    credibility_score: float
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_sentiment: Optional[str] = None
    fact_check_result: Optional[Dict[str, Any]] = None
    fact_check_rating: Optional[str] = None
    overall_score: float
    status: VerificationStatus
    verified_at: Optional[datetime] = None


class ArticleResponse(ArticleBase):
    """Schema for article response"""
    id: int
    views: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    source: Optional[SourceResponse] = None
    verification: Optional[ArticleVerificationDetail] = None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for paginated article list"""
    articles: List[ArticleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Verification Schemas
class VerificationRequest(BaseModel):
    """Schema for verification request"""
    article_id: int


class VerificationResponse(BaseModel):
    """Schema for verification response"""
    article_id: int
    cross_check_score: float
    cross_check_count: int
    credibility_score: float
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_sentiment: Optional[str] = None
    fact_check_result: Optional[Dict[str, Any]] = None
    fact_check_rating: Optional[str] = None
    overall_score: float
    status: VerificationStatus
    verified_at: Optional[datetime] = None


# Query Schemas
class NewsQueryParams(BaseModel):
    """Schema for news query parameters"""
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    source_id: Optional[int] = None
    category: Optional[ArticleCategory] = None
    status: Optional[VerificationStatus] = None
    search: Optional[str] = Field(None, max_length=200)
    min_score: Optional[float] = Field(None, ge=0, le=100)
    sort_by: Optional[str] = Field("published_at", pattern="^(published_at|created_at|overall_score|views)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")


# Refresh Schemas
class RefreshResponse(BaseModel):
    """Schema for refresh response"""
    message: str
    articles_added: int
    articles_updated: int
    sources_processed: int


# Health Schema
class HealthResponse(BaseModel):
    """Schema for health check"""
    status: str
    database: str
    redis: str