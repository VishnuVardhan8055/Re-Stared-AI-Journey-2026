"""
Application Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost/news_platform"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Twitter/X API
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    twitter_bearer_token: str = ""

    # News APIs
    news_api_key: str = ""
    gnews_api_key: str = ""

    # Anthropic/Claude API
    anthropic_api_key: str = ""

    # Fact Check
    google_fact_check_api_key: str = ""

    # Application
    cors_origins: List[str] = ["http://localhost:3000"]
    app_name: str = "News Platform"
    environment: str = "development"

    # Aggregation Settings
    aggregation_interval_minutes: int = 30
    max_articles_per_source: int = 50
    articles_per_page: int = 20

    # Credibility Scoring Weights
    cross_check_weight: float = 0.3
    source_credibility_weight: float = 0.25
    ai_analysis_weight: float = 0.25
    fact_check_weight: float = 0.2

    # Thresholds
    verified_threshold: float = 70.0
    needs_review_threshold: float = 40.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()