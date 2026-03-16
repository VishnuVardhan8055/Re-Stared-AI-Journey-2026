"""
SQLAlchemy ORM Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime

Base = declarative_base()


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


class Source(Base):
    """News source model"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    type = Column(SQLEnum(SourceType), nullable=False, default=SourceType.RSS)
    credibility_score = Column(Float, default=50.0, index=True)
    is_verified = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    domain = Column(String(200), nullable=True, index=True)
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type='{self.type}')>"


class Article(Base):
    """News article model"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    category = Column(SQLEnum(ArticleCategory), default=ArticleCategory.NEWS, index=True)
    author = Column(String(200), nullable=True)
    image_url = Column(String(1000), nullable=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    source = relationship("Source", back_populates="articles")
    verification = relationship("ArticleVerification", back_populates="article", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"


class ArticleVerification(Base):
    """Article verification model"""
    __tablename__ = "article_verifications"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True, index=True)
    cross_check_score = Column(Float, default=0.0)
    cross_check_count = Column(Integer, default=0)
    credibility_score = Column(Float, default=0.0)
    ai_analysis = Column(Text, nullable=True)  # JSON string
    ai_sentiment = Column(String(50), nullable=True)
    fact_check_result = Column(Text, nullable=True)  # JSON string
    fact_check_rating = Column(String(50), nullable=True)
    overall_score = Column(Float, default=0.0)
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    article = relationship("Article", back_populates="verification")

    def __repr__(self):
        return f"<ArticleVerification(id={self.id}, article_id={self.article_id}, overall_score={self.overall_score})>"


class UserFeedback(Base):
    """User feedback model for articles"""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    is_accurate = Column(Boolean, nullable=True)
    is_misleading = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserFeedback(id={self.id}, article_id={self.article_id})>"