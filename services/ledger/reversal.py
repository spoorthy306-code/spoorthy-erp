from datetime import datetime
from typing import Dict, Any
from db.schema import SessionLocal, Transaction, Voucher


def reverse_entry(original_voucher_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        original = db.query(Voucher).filter_by(id=original_voucher_id).first()
        if not original:
            return {"error": "Original voucher not found"}
        reversed_voucher = Voucher(voucher_no=f"REV-{original.voucher_no}", voucher_type_id=original.voucher_type_id, voucher_date=datetime.utcnow().date(), fiscal_year=original.fiscal_year, narration=f"Reversal of {original.voucher_no}", total_amount=original.total_amount, status="REVERSED")
        db.add(reversed_voucher)
        db.flush()
        for txn in original.transactions:
            db.add(Transaction(voucher_id=reversed_voucher.id, ledger_id=txn.ledger_id, debit=float(txn.credit or 0), credit=float(txn.debit or 0), narration=f"Reversal of txn {txn.id}"))
        original.status = "REVERSED"
        db.commit()
        return {"reversal_voucher_id": reversed_voucher.id, "original_voucher_id": original.id}
    finally:
        db.close()
