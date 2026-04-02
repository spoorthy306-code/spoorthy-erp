from datetime import date, datetime
from typing import Dict, Any
from db.schema import SessionLocal, AccountGroup, Ledger, Voucher, Transaction


def period_close(period_end: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        closing_date = date.fromisoformat(period_end)
        retained_amount = 0.0
        income_group_ids = [g.id for g in db.query(AccountGroup).filter(AccountGroup.group_type == "INCOME").all()]
        expense_group_ids = [g.id for g in db.query(AccountGroup).filter(AccountGroup.group_type == "EXPENSE").all()]

        for l in db.query(Ledger).filter(Ledger.group_id.in_(income_group_ids)).all():
            for t in l.transactions:
                retained_amount += float(t.credit or 0) - float(t.debit or 0)
        for l in db.query(Ledger).filter(Ledger.group_id.in_(expense_group_ids)).all():
            for t in l.transactions:
                retained_amount -= float(t.debit or 0) - float(t.credit or 0)

        re = db.query(Ledger).filter(Ledger.code == "RETAINED_EARNINGS").first()
        if not re:
            re = Ledger(code="RETAINED_EARNINGS", name="Retained Earnings", group_id=1, nature="Cr", currency="INR")
            db.add(re)
            db.commit()

        voucher = Voucher(voucher_no=f"PC-{period_end}", voucher_type_id=1, voucher_date=closing_date, fiscal_year=f"{closing_date.year}-{closing_date.year+1}", narration="Period close retained earnings", total_amount=abs(retained_amount), status="POSTED")
        db.add(voucher)
        db.flush()
        db.add(Transaction(voucher_id=voucher.id, ledger_id=re.id, debit=0.0, credit=abs(retained_amount), narration="Retained earnings close"))
        original = db.query(Voucher).filter_by(id=voucher.id).first()
        if original:
            original.status = "REVERSED"
        db.commit()
        return {"period_end": period_end, "retained_earnings": retained_amount}
    finally:
        db.close()
