from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user, get_db, require_roles
from backend.app.models.finance import Journal, JournalLine, Ledger
from backend.app.schemas.finance import (JournalCreate, JournalLineBase,
                                         JournalRead)

router = APIRouter(prefix="/journals", tags=["journals"])


def _calculate_totals(lines: List[JournalLineBase]):
    total_debit = sum((line.debit or 0.0) for line in lines)
    total_credit = sum((line.credit or 0.0) for line in lines)
    return float(total_debit), float(total_credit)


@router.post("/", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
def create_journal(
    entry: JournalCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(["Admin", "Accountant"])),
):
    if not entry.transactions or len(entry.transactions) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least two transaction lines are required for double-entry",
        )

    total_debit, total_credit = _calculate_totals(entry.transactions)
    if (
        total_debit <= 0
        or total_credit <= 0
        or abs(total_debit - total_credit) > 0.0001
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debits and credits must match and be > 0",
        )

    ledger_ids = [t.ledger_id for t in entry.transactions]
    count = db.query(func.count(Ledger.id)).filter(Ledger.id.in_(ledger_ids)).scalar()
    if count != len(ledger_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more ledgers not found",
        )

    journal = Journal(
        date=entry.date,
        narration=entry.narration,
        voucher_type=entry.voucher_type,
        voucher_number=entry.voucher_number,
        posted=False,
    )
    db.add(journal)
    db.flush()

    for line in entry.transactions:
        jline = JournalLine(
            journal_id=journal.id,
            ledger_id=line.ledger_id,
            debit=line.debit,
            credit=line.credit,
            narration=line.narration,
        )
        db.add(jline)

    db.commit()
    db.refresh(journal)

    return journal


@router.get("/", response_model=List[JournalRead])
def list_journals(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    query = db.query(Journal)
    if start_date:
        query = query.filter(Journal.date >= start_date)
    if end_date:
        query = query.filter(Journal.date <= end_date)
    if status_filter:
        query = query.filter(Journal.voucher_type == status_filter)

    return query.order_by(Journal.date.desc()).all()


@router.put("/{journal_id}", response_model=JournalRead)
def update_journal(
    journal_id: int,
    entry: JournalCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(["Admin", "Accountant"])),
):
    journal = db.query(Journal).get(journal_id)
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found"
        )

    if journal.posted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit posted journal entry",
        )

    total_debit, total_credit = _calculate_totals(entry.transactions)
    if abs(total_debit - total_credit) > 0.0001:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debits and credits must match",
        )

    journal.date = entry.date
    journal.narration = entry.narration
    journal.voucher_type = entry.voucher_type
    journal.voucher_number = entry.voucher_number

    db.query(JournalLine).filter(JournalLine.journal_id == journal.id).delete()
    for line in entry.transactions:
        jline = JournalLine(
            journal_id=journal.id,
            ledger_id=line.ledger_id,
            debit=line.debit,
            credit=line.credit,
            narration=line.narration,
        )
        db.add(jline)

    db.commit()
    db.refresh(journal)

    return journal


@router.post("/{journal_id}/post")
def post_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(["Admin", "Accountant"])),
):
    journal = db.query(Journal).get(journal_id)
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found"
        )

    if journal.posted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journal entry already posted",
        )

    journal.posted = True
    db.add(journal)
    db.commit()

    return {"detail": "Journal posted"}
