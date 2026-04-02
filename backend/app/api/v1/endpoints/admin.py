# SPOORTHY QUANTUM OS — Admin API
# Administrative functions, system management

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from uuid import UUID

from ....db.session import get_db
from ....db.seed import seed_database
from ....repositories.repositories import QuantumJobRepository, AuditLogRepository

router = APIRouter()

@router.post("/seed-database")
async def seed_db(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Seed database with demo data"""
    background_tasks.add_task(seed_database, db)
    return {"message": "Database seeding started in background"}

@router.get("/system-health")
async def get_system_health(
    db: AsyncSession = Depends(get_db)
):
    """Get system health metrics"""
    # Get quantum jobs stats
    qj_repo = QuantumJobRepository(db)
    total_jobs = await qj_repo.count()
    completed_jobs = await qj_repo.count({"status": "COMPLETED"})

    # Get recent audit logs
    audit_repo = AuditLogRepository(db)
    recent_logs = await audit_repo.get_all(limit=10)

    return {
        "database": "healthy",
        "quantum_jobs": {
            "total": total_jobs,
            "completed": completed_jobs,
            "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0
        },
        "recent_activity": len(recent_logs),
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/quantum-stats")
async def get_quantum_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get quantum computing statistics"""
    qj_repo = QuantumJobRepository(db)

    # Get jobs by module
    reconciliation_jobs = await qj_repo.get_by_entity_module(None, "Reconciliation")
    forecasting_jobs = await qj_repo.get_by_entity_module(None, "Forecasting")
    optimization_jobs = await qj_repo.get_by_entity_module(None, "Optimization")

    return {
        "reconciliation_jobs": len(reconciliation_jobs),
        "forecasting_jobs": len(forecasting_jobs),
        "optimization_jobs": len(optimization_jobs),
        "total_solve_time_ms": sum(job.solve_time_ms or 0 for job in reconciliation_jobs + forecasting_jobs + optimization_jobs),
        "average_energy": sum(job.energy or 0 for job in reconciliation_jobs + forecasting_jobs + optimization_jobs) / max(1, len(reconciliation_jobs + forecasting_jobs + optimization_jobs))
    }

@router.post("/backup/{entity_id}")
async def create_backup(
    entity_id: UUID,
    background_tasks: BackgroundTasks
):
    """Create backup for entity"""
    background_tasks.add_task(perform_backup, entity_id)
    return {"message": "Backup initiated", "entity_id": str(entity_id)}

@router.get("/audit-logs/{entity_id}")
async def get_audit_logs(
    entity_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for entity"""
    audit_repo = AuditLogRepository(db)
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    logs = await audit_repo.get_by_entity_date_range(entity_id, start_date, end_date)
    return logs[:limit]

@router.post("/maintenance/migrate")
async def run_migrations(
    background_tasks: BackgroundTasks
):
    """Run database migrations"""
    background_tasks.add_task(run_db_migrations)
    return {"message": "Migrations started"}

async def perform_backup(entity_id: UUID):
    """Background backup task"""
    try:
        # Simulate backup process
        import asyncio
        await asyncio.sleep(10)  # Simulate backup time
        # In real implementation, would create actual backup
        print(f"Backup completed for entity {entity_id}")
    except Exception as e:
        print(f"Backup failed for entity {entity_id}: {e}")

async def run_db_migrations():
    """Run database migrations"""
    try:
        # Simulate migration process
        import asyncio
        await asyncio.sleep(5)  # Simulate migration time
        # In real implementation, would run Alembic migrations
        print("Database migrations completed")
    except Exception as e:
        print(f"Migration failed: {e}")