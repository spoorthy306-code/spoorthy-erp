# SPOORTHY QUANTUM OS — Journal Entries API
# CRUD operations for journal entries with quantum reconciliation

import asyncio
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import async_session, get_db
from ....models.models import (JournalEntryCreateSchema, JournalEntrySchema,
                               JournalLine)
from ....repositories.repositories import (BankTransactionRepository,
                                           JournalEntryRepository)
from ....services.quantum_services import QuantumReconciliationEngine

router = APIRouter()


@router.post("/", response_model=JournalEntrySchema)
async def create_journal_entry(
    entry: JournalEntryCreateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new journal entry"""
    repo = JournalEntryRepository(db)

    # Validate debits = credits
    total_debit = sum(line.get("debit", 0) for line in entry.lines)
    total_credit = sum(line.get("credit", 0) for line in entry.lines)

    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(status_code=400, detail="Debits must equal credits")

    # Create entry
    db_entry = await repo.create(
        entity_id=entry.entity_id,
        entry_date=entry.entry_date,
        period=entry.entry_date.strftime("%Y-%m"),
        narration=entry.narration,
        total_debit=total_debit,
        total_credit=total_credit,
    )

    # Create journal lines using ORM insert (avoids raw SQL positional-param mismatch)
    for line in entry.lines:
        db.add(
            JournalLine(
                entry_id=db_entry.entry_id,
                account_code=line["account_code"],
                debit=line.get("debit", 0),
                credit=line.get("credit", 0),
                description=line.get("description", ""),
            )
        )

    await db.commit()

    # Trigger quantum reconciliation — use a fresh session, not the request-scoped one
    background_tasks.add_task(run_quantum_reconciliation, entry.entity_id)

    return JournalEntrySchema.model_validate(db_entry)


@router.get("/", response_model=List[JournalEntrySchema])
async def list_journal_entries(
    entity_id: UUID,
    period: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List journal entries for an entity"""
    repo = JournalEntryRepository(db)
    if period:
        entries = await repo.get_by_entity_period(entity_id, period)
    else:
        entries = await repo.get_all(
            skip=skip, limit=limit, filters={"entity_id": entity_id}
        )
    return [JournalEntrySchema.model_validate(entry) for entry in entries]


@router.get("/{entry_id}", response_model=JournalEntrySchema)
async def get_journal_entry(entry_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get journal entry with lines"""
    repo = JournalEntryRepository(db)
    entry = await repo.get_with_lines(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return JournalEntrySchema.model_validate(entry)


@router.post("/reconcile/{entity_id}")
async def reconcile_bank_transactions(
    entity_id: UUID,
    background_tasks: BackgroundTasks,
):
    """Trigger quantum bank reconciliation"""
    background_tasks.add_task(run_quantum_reconciliation, entity_id)
    return {"message": "Quantum reconciliation started", "entity_id": str(entity_id)}


async def run_quantum_reconciliation(entity_id: UUID):
    """Background task for quantum reconciliation — opens its own session."""
    try:
        async with async_session() as db:
            bank_repo = BankTransactionRepository(db)
            unreconciled_txns = await bank_repo.get_unreconciled_bank_txns(entity_id)

            if unreconciled_txns:
                engine = QuantumReconciliationEngine()
                txn_dicts = [
                    {"txn_id": str(t.txn_id), "amount": float(t.amount or 0)}
                    for t in unreconciled_txns
                ]
                matches = await engine.reconcile(txn_dicts, [])

                for match in matches:
                    await bank_repo.reconcile(
                        UUID(match["txn_id"]), UUID(match["entry_id"])
                    )
    except Exception:
        # Background tasks must not raise — log and swallow
        import logging

        logging.getLogger(__name__).exception(
            "Quantum reconciliation failed for entity %s", entity_id
        )
