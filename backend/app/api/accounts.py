"""Accounts API"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user
from backend.app.db.session import get_db
from backend.app.models.finance import AccountGroup, Invoice, Ledger, Party

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/groups")
def list_groups(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(AccountGroup).all()


@router.get("/ledgers")
def list_ledgers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Ledger).all()


@router.get("/parties")
def list_parties(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Party).all()


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_invoices = db.query(Invoice).count()
    total_value = db.query(Invoice.total_amount).all()
    total = sum(v[0] for v in total_value if v[0]) if total_value else 0

    return {
        "total_invoices": total_invoices,
        "total_value": float(total),
        "active_parties": db.query(Party).filter(Party.is_active == True).count(),
        "account_groups": db.query(AccountGroup).count(),
        "ledgers": db.query(Ledger).count(),
    }
