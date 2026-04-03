# SPOORTHY QUANTUM OS — Bank Transactions API
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import (BankTransactionCreateSchema,
                               BankTransactionSchema)
from ....repositories.repositories import BankTransactionRepository

router = APIRouter()


@router.post("/", response_model=BankTransactionSchema, status_code=201)
async def create_bank_transaction(
    txn: BankTransactionCreateSchema, db: AsyncSession = Depends(get_db)
):
    repo = BankTransactionRepository(db)
    db_txn = await repo.create(**txn.model_dump())
    return BankTransactionSchema.model_validate(db_txn)


@router.get("/", response_model=List[BankTransactionSchema])
async def list_bank_transactions(
    entity_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    reconciled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    repo = BankTransactionRepository(db)
    if start_date and end_date:
        txns = await repo.get_by_entity_date_range(entity_id, start_date, end_date)
    else:
        txns = await repo.get_all(skip, limit)
        txns = [t for t in txns if t.entity_id == entity_id]
    if reconciled is not None:
        txns = [t for t in txns if t.reconciled == reconciled]
    return [BankTransactionSchema.model_validate(t) for t in txns]


@router.get("/{txn_id}", response_model=BankTransactionSchema)
async def get_bank_transaction(txn_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    from ....models.models import BankTransaction

    result = await db.execute(
        select(BankTransaction).where(BankTransaction.txn_id == txn_id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Bank transaction not found")
    return BankTransactionSchema.model_validate(txn)


@router.post("/{txn_id}/reconcile")
async def reconcile_transaction(
    txn_id: UUID, entry_id: UUID, db: AsyncSession = Depends(get_db)
):
    repo = BankTransactionRepository(db)
    success = await repo.reconcile(txn_id, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "message": "Transaction reconciled",
        "txn_id": str(txn_id),
        "entry_id": str(entry_id),
    }


@router.delete("/{txn_id}", status_code=204)
async def delete_bank_transaction(txn_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete

    result = await db.execute(
        delete(BankTransaction).where(BankTransaction.txn_id == txn_id)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
