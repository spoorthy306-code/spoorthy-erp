import csv
from typing import Dict, Any
from fastapi import HTTPException
from db.schema import SessionLocal, Transaction, Voucher, Ledger


def reconcile_bank_statement(csv_text: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        reader = csv.DictReader(csv_text.splitlines())
        statement = []
        for row in reader:
            statement.append({
                "date": row.get("date"),
                "amount": float(row.get("amount", "0")),
                "ledger_code": row.get("ledger_code"),
                "description": row.get("description", ""),
            })

        matched = []
        unmatched = []
        for item in statement:
            ledger = db.query(Ledger).filter_by(code=item.get("ledger_code")).first()
            if ledger:
                txn = db.query(Transaction).join(Voucher).filter(Transaction.ledger_id == ledger.id).filter(Voucher.voucher_date == item.get("date")).filter((Transaction.debit == item["amount"]) | (Transaction.credit == item["amount"])) .first()
                if txn:
                    matched.append(item)
                    continue
            unmatched.append(item)

        return {"matched": matched, "unmatched": unmatched, "count": len(statement)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        db.close()
