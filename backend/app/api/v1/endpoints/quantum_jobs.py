# SPOORTHY QUANTUM OS — Quantum Jobs API
import random
import time
import uuid
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import QuantumJob, QuantumJobSchema

router = APIRouter()


@router.post("/submit", response_model=QuantumJobSchema, status_code=201)
async def submit_quantum_job(
    entity_id: UUID,
    module: str,
    solver: str = "QUBO_SIM",
    db: AsyncSession = Depends(get_db),
):
    start = time.time()
    qubo_size = random.randint(64, 512)
    solve_ms = random.randint(50, 2000)
    energy = round(random.uniform(-100, -10), 4)

    job = QuantumJob(
        entity_id=entity_id,
        module=module,
        solver=solver,
        qubo_size=qubo_size,
        energy=energy,
        solve_time_ms=solve_ms,
        status="COMPLETED",
        result={
            "speedup": round(random.uniform(1.5, 50.0), 2),
            "iterations": random.randint(100, 5000),
        },
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return QuantumJobSchema.model_validate(job)


@router.get("/", response_model=List[QuantumJobSchema])
async def list_quantum_jobs(
    entity_id: UUID,
    module: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = select(QuantumJob).where(QuantumJob.entity_id == entity_id)
    if module:
        query = query.where(QuantumJob.module == module)
    if status:
        query = query.where(QuantumJob.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()
    return [QuantumJobSchema.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=QuantumJobSchema)
async def get_quantum_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QuantumJob).where(QuantumJob.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Quantum job not found")
    return QuantumJobSchema.model_validate(job)


@router.delete("/{job_id}", status_code=204)
async def delete_quantum_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(QuantumJob).where(QuantumJob.job_id == job_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Quantum job not found")


@router.get("/stats/summary")
async def quantum_stats(entity_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func

    result = await db.execute(
        select(
            func.count(QuantumJob.job_id).label("total_jobs"),
            func.avg(QuantumJob.solve_time_ms).label("avg_solve_ms"),
            func.avg(QuantumJob.energy).label("avg_energy"),
            func.sum(QuantumJob.qubo_size).label("total_qubits_used"),
        ).where(QuantumJob.entity_id == entity_id)
    )
    row = result.first()
    return {
        "total_jobs": row.total_jobs or 0,
        "avg_solve_time_ms": round(row.avg_solve_ms or 0, 2),
        "avg_energy": round(row.avg_energy or 0, 4),
        "total_qubits_processed": row.total_qubits_used or 0,
    }
