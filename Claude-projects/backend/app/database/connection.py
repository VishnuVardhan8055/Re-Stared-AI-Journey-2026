"""
Database Connection Management
PostgreSQL and Redis connection setup
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

from app.config import settings


# PostgreSQL Async Engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Async Session Factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Redis Client
redis_client = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """Get database session context manager"""
    async with async_session() as session:
        yield session