"""
FastAPI Application Entry Point
News Aggregation & Verification Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.connection import engine, Base
from app.api import news, verification
from app.tasks.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await create_tables()
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown()
    await engine.dispose()


async def create_tables():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(
    title="News Aggregation & Verification Platform",
    description="A comprehensive platform for aggregating and verifying news from multiple sources",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "News Aggregation & Verification Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}