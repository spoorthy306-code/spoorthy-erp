# SPOORTHY QUANTUM OS — Loans API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from uuid import UUID
import math

from ....db.session import get_db
from ....repositories.repositories import LoanRepository
from ....models.models import LoanSchema, LoanCreateSchema, Loan

router = APIRouter()

@router.post("/", response_model=LoanSchema, status_code=201)
async def create_loan(
    loan: LoanCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    data = loan.model_dump()
    data['outstanding'] = data['sanctioned_amount']
    # Calculate EMI: P*r*(1+r)^n / ((1+r)^n - 1)
    r = data['rate_pct'] / 100 / 12
    n = data['tenure_months']
    p = data['sanctioned_amount']
    data['emi'] = p * r * (1 + r) ** n / ((1 + r) ** n - 1) if r > 0 else p / n
    repo = LoanRepository(db)
    db_loan = await repo.create(**data)
    return LoanSchema.model_validate(db_loan)

@router.get("/", response_model=List[LoanSchema])
async def list_loans(
    entity_id: UUID,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    repo = LoanRepository(db)
    if active_only:
        loans = await repo.get_active_by_entity(entity_id)
    else:
        loans = await repo.get_all(skip, limit)
        loans = [l for l in loans if l.entity_id == entity_id]
    return [LoanSchema.model_validate(l) for l in loans]

@router.get("/{loan_id}", response_model=LoanSchema)
async def get_loan(
    loan_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Loan).where(Loan.loan_id == loan_id))
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return LoanSchema.model_validate(loan)

@router.put("/{loan_id}", response_model=LoanSchema)
async def update_loan(
    loan_id: UUID,
    loan_update: LoanCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        update(Loan).where(Loan.loan_id == loan_id)
        .values(**loan_update.model_dump(exclude_unset=True))
        .returning(Loan)
    )
    await db.commit()
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return LoanSchema.model_validate(loan)

@router.post("/{loan_id}/close")
async def close_loan(
    loan_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        update(Loan).where(Loan.loan_id == loan_id)
        .values(status='CLOSED', outstanding=0)
        .returning(Loan)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"loan_id": str(loan_id), "status": "CLOSED"}

@router.delete("/{loan_id}", status_code=204)
async def delete_loan(
    loan_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(delete(Loan).where(Loan.loan_id == loan_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Loan not found")
