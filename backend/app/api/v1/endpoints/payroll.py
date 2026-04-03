# SPOORTHY QUANTUM OS — Payroll API
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import (Employee, PayrollRun, PayrollRunCreateSchema,
                               PayrollRunSchema)
from ....repositories.repositories import (EmployeeRepository,
                                           PayrollRunRepository)

router = APIRouter()


@router.post("/run", response_model=PayrollRunSchema, status_code=201)
async def run_payroll(
    payroll: PayrollRunCreateSchema, db: AsyncSession = Depends(get_db)
):
    # Check for existing run
    run_repo = PayrollRunRepository(db)
    existing = await run_repo.get_by_entity_period(payroll.entity_id, payroll.period)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Payroll already run for period {payroll.period}"
        )

    # Get all active employees
    emp_repo = EmployeeRepository(db)
    employees = await emp_repo.get_active_by_entity(payroll.entity_id)
    if not employees:
        raise HTTPException(status_code=400, detail="No active employees found")

    # Calculate payroll
    total_gross = 0.0
    total_pf_employee = 0.0
    total_pf_employer = 0.0
    total_esic = 0.0
    total_tds = 0.0
    total_pt = 0.0

    for emp in employees:
        basic = emp.basic_salary or 0
        hra = emp.hra or 0
        lta = emp.lta or 0
        medical = emp.medical or 0
        nps = emp.nps or 0
        gross = basic + hra + lta + medical
        total_gross += gross

        pf_emp = min(basic * 0.12, 1800)
        pf_er = min(basic * 0.12, 1800)
        esic = gross * 0.0075 if gross <= 21000 else 0
        pt = 200 if gross > 15000 else 150
        tds = max((gross * 12 - 250000) * 0.05 / 12, 0) if gross > 0 else 0

        total_pf_employee += pf_emp
        total_pf_employer += pf_er
        total_esic += esic
        total_pt += pt
        total_tds += tds

    total_deductions = total_pf_employee + total_esic + total_pt + total_tds
    total_net = total_gross - total_deductions

    run = await run_repo.create(
        entity_id=payroll.entity_id,
        period=payroll.period,
        total_gross=round(total_gross, 2),
        total_deductions=round(total_deductions, 2),
        total_net=round(total_net, 2),
        pf_employer=round(total_pf_employer, 2),
        esic_employer=round(total_esic * 3.25 / 0.75, 2),
        pt=round(total_pt, 2),
        tds=round(total_tds, 2),
    )
    return PayrollRunSchema.model_validate(run)


@router.get("/", response_model=List[PayrollRunSchema])
async def list_payroll_runs(
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PayrollRun)
        .where(PayrollRun.entity_id == entity_id)
        .offset(skip)
        .limit(limit)
    )
    runs = result.scalars().all()
    return [PayrollRunSchema.model_validate(r) for r in runs]


@router.get("/{run_id}", response_model=PayrollRunSchema)
async def get_payroll_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PayrollRun).where(PayrollRun.run_id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    return PayrollRunSchema.model_validate(run)


@router.delete("/{run_id}", status_code=204)
async def delete_payroll_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(PayrollRun).where(PayrollRun.run_id == run_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Payroll run not found")
