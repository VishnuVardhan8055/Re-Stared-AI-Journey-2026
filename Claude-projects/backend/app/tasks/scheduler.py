"""
Background Task Scheduler
Schedules news aggregation and verification tasks
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime

from app.config import settings
from app.database.connection import get_db_session
from app.services.aggregator import news_aggregator
from app.verification.cross_check import cross_check_verifier
from app.verification.credibility import credibility_scorer

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Background task scheduler"""

    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    def start(self):
        """Start the scheduler"""
        try:
            # Schedule news aggregation
            self.scheduler.add_job(
                self._aggregate_news_job,
                IntervalTrigger(minutes=settings.aggregation_interval_minutes),
                id='aggregate_news',
                name='Aggregate news from all sources',
                replace_existing=True
            )

            # Schedule source credibility updates (daily)
            self.scheduler.add_job(
                self._update_source_scores_job,
                IntervalTrigger(hours=24),
                id='update_source_scores',
                name='Update source credibility scores',
                replace_existing=True
            )

            # Schedule cross-check verification (hourly)
            self.scheduler.add_job(
                self._cross_check_job,
                IntervalTrigger(hours=1),
                id='cross_check',
                name='Run cross-check verification',
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Background task scheduler started")

            # Log scheduled jobs
            jobs = self.scheduler.get_jobs()
            logger.info(f"Scheduled jobs: {[job.name for job in jobs]}")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")

    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Background task scheduler shutdown")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")

    async def _aggregate_news_job(self):
        """Background job to aggregate news from all sources"""
        try:
            logger.info(f"Starting news aggregation job at {datetime.now()}")

            async with get_db_session() as db:
                stats = await news_aggregator.aggregate_all(db, max_per_source=settings.max_articles_per_source)

            logger.info(
                f"News aggregation complete: "
                f"{stats['sources_processed']} sources, "
                f"{stats['articles_added']} added, "
                f"{stats['articles_updated']} updated"
            )

        except Exception as e:
            logger.error(f"Error in news aggregation job: {e}")

    async def _update_source_scores_job(self):
        """Background job to update source credibility scores"""
        try:
            logger.info(f"Starting source score update job at {datetime.now()}")

            async with get_db_session() as db:
                stats = await credibility_scorer.update_all_sources(db)

            logger.info(
                f"Source score update complete: "
                f"{stats['updated']} sources updated, "
                f"avg score: {stats['avg_score']:.2f}"
            )

        except Exception as e:
            logger.error(f"Error in source score update job: {e}")

    async def _cross_check_job(self):
        """Background job to run cross-check verification"""
        try:
            logger.info(f"Starting cross-check job at {datetime.now()}")

            async with get_db_session() as db:
                stats = await cross_check_verifier.verify_all_articles(db, limit=50)

            logger.info(
                f"Cross-check verification complete: "
                f"{stats['verified']} articles verified, "
                f"avg score: {stats['avg_score']:.2f}"
            )

        except Exception as e:
            logger.error(f"Error in cross-check job: {e}")


# Singleton instance
scheduler = TaskScheduler()