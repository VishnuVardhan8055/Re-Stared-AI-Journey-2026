"""
Application Dependencies
Database and Redis connection management
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from redis import asyncio as aioredis

from app.database.connection import async_session, redis_client
from app.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Get Redis client"""
    yield redis_client