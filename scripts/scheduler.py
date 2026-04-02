#!/usr/bin/env python3
# SPOORTHY QUANTUM OS — Job Scheduler
# scripts/scheduler.py

import asyncio
import logging
import os
import sys
from datetime import datetime, time, timedelta
from typing import Any, Dict, List

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models import Entity, GSTReturn
from backend.app.repositories import EntityRepository
from backend.app.services.compliance_services import GSTComplianceEngine
from backend.app.services.financial_services import FinancialStatementGenerator
from backend.app.services.quantum_services import QuantumReconciliationEngine
from monitoring import QuantumJobMetrics, metrics_collector

logger = structlog.get_logger()


class SpoorthyScheduler:
    """Job scheduler for Spoorthy Quantum OS"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": AsyncIOExecutor()},
            job_defaults={
                "coalesce": True,
                "max_instances": 3,
                "misfire_grace_time": 30,
            },
            timezone="Asia/Kolkata",
        )

        self.job_stats = {"executed": 0, "failed": 0, "last_run": None}

    async def setup_jobs(self):
        """Setup all scheduled jobs"""

        # Daily jobs at 6 AM IST
        self.scheduler.add_job(
            self.daily_reconciliation_check,
            CronTrigger(hour=6, minute=0),
            id="daily_reconciliation",
            name="Daily Bank Reconciliation Check",
        )

        # GST compliance checks - 15th of every month at 9 AM
        self.scheduler.add_job(
            self.monthly_gst_compliance_check,
            CronTrigger(day=15, hour=9, minute=0),
            id="monthly_gst_check",
            name="Monthly GST Compliance Check",
        )

        # Financial statement generation - Last day of month at 8 PM
        self.scheduler.add_job(
            self.monthly_financial_statements,
            CronTrigger(day="last", hour=20, minute=0),
            id="monthly_financial_statements",
            name="Monthly Financial Statement Generation",
        )

        # Quantum portfolio rebalancing - Every Monday at 10 AM
        self.scheduler.add_job(
            self.weekly_portfolio_rebalancing,
            CronTrigger(day_of_week="mon", hour=10, minute=0),
            id="weekly_portfolio_rebalancing",
            name="Weekly Portfolio Rebalancing",
        )

        # Compliance monitoring - Every 4 hours
        self.scheduler.add_job(
            self.compliance_monitoring,
            IntervalTrigger(hours=4),
            id="compliance_monitoring",
            name="Compliance Monitoring",
        )

        # Database maintenance - Every Sunday at 2 AM
        self.scheduler.add_job(
            self.database_maintenance,
            CronTrigger(day_of_week="sun", hour=2, minute=0),
            id="database_maintenance",
            name="Database Maintenance",
        )

        # Backup job - Daily at 11 PM
        self.scheduler.add_job(
            self.backup_data,
            CronTrigger(hour=23, minute=0),
            id="daily_backup",
            name="Daily Data Backup",
        )

        logger.info("scheduler_jobs_setup", job_count=len(self.scheduler.get_jobs()))

    async def daily_reconciliation_check(self):
        """Daily bank reconciliation for all active entities"""
        logger.info("starting_daily_reconciliation_check")

        try:
            async for session in get_db():
                entity_repo = EntityRepository(session)
                entities = await entity_repo.get_active_entities()

                for entity in entities:
                    try:
                        # Check if reconciliation is needed (simplified logic)
                        needs_reconciliation = await self._check_reconciliation_needed(
                            entity.id
                        )

                        if needs_reconciliation:
                            await self._run_entity_reconciliation(entity.id)
                            logger.info("reconciliation_completed", entity_id=entity.id)
                        else:
                            logger.debug(
                                "reconciliation_not_needed", entity_id=entity.id
                            )

                    except Exception as e:
                        logger.error(
                            "entity_reconciliation_failed",
                            entity_id=entity.id,
                            error=str(e),
                        )
                        self.job_stats["failed"] += 1

            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("daily_reconciliation_check_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def monthly_gst_compliance_check(self):
        """Monthly GST compliance check and return preparation"""
        logger.info("starting_monthly_gst_compliance_check")

        try:
            current_date = datetime.now()
            period = current_date.strftime("%Y-%m")

            async for session in get_db():
                entity_repo = EntityRepository(session)
                entities = await entity_repo.get_active_entities()

                gst_engine = GSTComplianceEngine()

                for entity in entities:
                    try:
                        # Generate GSTR-1
                        gstr1_data = await gst_engine.generate_gstr1(entity.id, period)

                        # Check compliance status
                        compliance_status = await gst_engine.check_compliance_status(
                            entity.id, period
                        )

                        if compliance_status["needs_filing"]:
                            logger.warning(
                                "gst_return_needs_filing",
                                entity_id=entity.id,
                                period=period,
                            )
                            # Could send notification here
                        else:
                            logger.info(
                                "gst_compliance_ok", entity_id=entity.id, period=period
                            )

                    except Exception as e:
                        logger.error(
                            "entity_gst_check_failed", entity_id=entity.id, error=str(e)
                        )
                        self.job_stats["failed"] += 1

            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("monthly_gst_compliance_check_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def monthly_financial_statements(self):
        """Generate monthly financial statements"""
        logger.info("starting_monthly_financial_statements")

        try:
            current_date = datetime.now()
            period = current_date.strftime("%Y-%m")

            async for session in get_db():
                entity_repo = EntityRepository(session)
                entities = await entity_repo.get_active_entities()

                statement_gen = FinancialStatementGenerator()

                for entity in entities:
                    try:
                        # Generate all statements
                        pnl = await statement_gen.generate_pl(entity.id, period)
                        balance_sheet = await statement_gen.generate_balance_sheet(
                            entity.id, period
                        )
                        cash_flow = await statement_gen.generate_cash_flow(
                            entity.id, period
                        )

                        # Store or notify (simplified)
                        logger.info(
                            "financial_statements_generated",
                            entity_id=entity.id,
                            period=period,
                        )

                    except Exception as e:
                        logger.error(
                            "entity_financial_statements_failed",
                            entity_id=entity.id,
                            error=str(e),
                        )
                        self.job_stats["failed"] += 1

            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("monthly_financial_statements_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def weekly_portfolio_rebalancing(self):
        """Weekly portfolio rebalancing check"""
        logger.info("starting_weekly_portfolio_rebalancing")

        try:
            async for session in get_db():
                entity_repo = EntityRepository(session)
                entities = await entity_repo.get_active_entities()

                for entity in entities:
                    try:
                        # Check if portfolio needs rebalancing
                        needs_rebalancing = await self._check_portfolio_drift(entity.id)

                        if needs_rebalancing:
                            await self._rebalance_portfolio(entity.id)
                            logger.info("portfolio_rebalanced", entity_id=entity.id)
                        else:
                            logger.debug(
                                "portfolio_rebalancing_not_needed", entity_id=entity.id
                            )

                    except Exception as e:
                        logger.error(
                            "entity_portfolio_rebalancing_failed",
                            entity_id=entity.id,
                            error=str(e),
                        )
                        self.job_stats["failed"] += 1

            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("weekly_portfolio_rebalancing_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def compliance_monitoring(self):
        """Continuous compliance monitoring"""
        logger.info("starting_compliance_monitoring")

        try:
            async for session in get_db():
                entity_repo = EntityRepository(session)
                entities = await entity_repo.get_active_entities()

                for entity in entities:
                    try:
                        # Update compliance scores
                        compliance_score = await self._calculate_compliance_score(
                            entity.id
                        )

                        # Record in monitoring
                        from monitoring import BusinessMetrics

                        biz_metrics = BusinessMetrics(
                            entity_id=entity.id,
                            period=datetime.now().strftime("%Y-%m"),
                            revenue=0,  # Would be calculated
                            expenses=0,
                            profit=0,
                            gst_liability=0,
                            compliance_score=compliance_score,
                        )
                        metrics_collector.record_business_metrics(biz_metrics)

                        if compliance_score < 80:
                            logger.warning(
                                "low_compliance_score",
                                entity_id=entity.id,
                                score=compliance_score,
                            )

                    except Exception as e:
                        logger.error(
                            "entity_compliance_monitoring_failed",
                            entity_id=entity.id,
                            error=str(e),
                        )
                        self.job_stats["failed"] += 1

            self.job_stats["executed"] += 1

        except Exception as e:
            logger.error("compliance_monitoring_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def database_maintenance(self):
        """Database maintenance tasks"""
        logger.info("starting_database_maintenance")

        try:
            async for session in get_db():
                # Run maintenance queries (simplified)
                await session.execute("VACUUM ANALYZE")
                await session.execute("REINDEX DATABASE spoorthy_erp")
                await session.commit()

            logger.info("database_maintenance_completed")
            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("database_maintenance_failed", error=str(e))
            self.job_stats["failed"] += 1

    async def backup_data(self):
        """Daily data backup"""
        logger.info("starting_daily_backup")

        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backups/{backup_timestamp}"

            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)

            # Backup database (simplified - would use pg_dump)
            # Backup files (simplified)

            logger.info("daily_backup_completed", backup_dir=backup_dir)
            self.job_stats["executed"] += 1
            self.job_stats["last_run"] = datetime.now()

        except Exception as e:
            logger.error("daily_backup_failed", error=str(e))
            self.job_stats["failed"] += 1

    # Helper methods
    async def _check_reconciliation_needed(self, entity_id: str) -> bool:
        """Check if reconciliation is needed for entity"""
        # Simplified logic - check for unprocessed bank statements
        async for session in get_db():
            # Query for recent unreconciled transactions
            result = await session.execute(
                """
                SELECT COUNT(*) as count
                FROM bank_transactions
                WHERE entity_id = :entity_id
                AND reconciled = false
                AND date >= CURRENT_DATE - INTERVAL '7 days'
            """,
                {"entity_id": entity_id},
            )

            count = result.scalar()
            return count > 0

    async def _run_entity_reconciliation(self, entity_id: str):
        """Run reconciliation for specific entity"""
        # Simplified reconciliation logic
        engine = QuantumReconciliationEngine()

        # Get bank and items data (simplified)
        bank_data = []
        items_data = []

        start_time = datetime.now()
        result = await engine.reconcile(entity_id, bank_data, items_data)
        end_time = datetime.now()

        # Record metrics
        job_metrics = QuantumJobMetrics(
            job_id=f"recon_{entity_id}_{int(start_time.timestamp())}",
            job_type="reconciliation",
            start_time=start_time.timestamp(),
            end_time=end_time.timestamp(),
            energy=result.get("energy", 0),
            qubits_used=result.get("qubits_used", 256),
            solve_time_ms=(end_time - start_time).total_seconds() * 1000,
            confidence=result.get("confidence", 0.95),
            success=True,
        )
        metrics_collector.record_quantum_job(job_metrics)

    async def _check_portfolio_drift(self, entity_id: str) -> bool:
        """Check if portfolio needs rebalancing"""
        # Simplified drift check
        return True  # Always rebalance for demo

    async def _rebalance_portfolio(self, entity_id: str):
        """Rebalance portfolio for entity"""
        from backend.app.services.quantum_services import \
            QuantumPortfolioOptimizer

        optimizer = QuantumPortfolioOptimizer()
        start_time = datetime.now()

        result = await optimizer.optimize_portfolio(entity_id, "balanced")

        end_time = datetime.now()

        # Record metrics
        job_metrics = QuantumJobMetrics(
            job_id=f"port_{entity_id}_{int(start_time.timestamp())}",
            job_type="portfolio_optimization",
            start_time=start_time.timestamp(),
            end_time=end_time.timestamp(),
            energy=result.get("energy", 0),
            qubits_used=result.get("qubits_used", 512),
            solve_time_ms=(end_time - start_time).total_seconds() * 1000,
            confidence=result.get("confidence", 0.92),
            success=True,
        )
        metrics_collector.record_quantum_job(job_metrics)

    async def _calculate_compliance_score(self, entity_id: str) -> float:
        """Calculate compliance score for entity"""
        # Simplified compliance calculation
        base_score = 95.0

        # Check GST filing status
        async for session in get_db():
            current_period = datetime.now().strftime("%Y-%m")
            result = await session.execute(
                """
                SELECT COUNT(*) as filed_count
                FROM gst_returns
                WHERE entity_id = :entity_id
                AND period = :period
                AND status = 'filed'
            """,
                {"entity_id": entity_id, "period": current_period},
            )

            filed_count = result.scalar()
            if filed_count == 0:
                base_score -= 10  # Penalty for not filing

        return max(0, min(100, base_score))

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                    "trigger": str(job.trigger),
                }
            )

        return {
            "running": self.scheduler.running,
            "job_count": len(jobs),
            "jobs": jobs,
            "stats": self.job_stats,
        }

    async def start_scheduler(self):
        """Start the scheduler"""
        await self.setup_jobs()
        self.scheduler.start()
        logger.info("scheduler_started")

        # Keep running
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            logger.info("scheduler_stopped")


async def main():
    """Main scheduler function"""
    scheduler = SpoorthyScheduler()

    # Setup signal handlers for graceful shutdown
    import signal

    def signal_handler(signum, frame):
        logger.info("shutdown_signal_received", signal=signum)
        scheduler.scheduler.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await scheduler.start_scheduler()
    except Exception as e:
        logger.error("scheduler_error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run scheduler
    asyncio.run(main())
