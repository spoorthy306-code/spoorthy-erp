from datetime import datetime, timedelta
from db.schema import SessionLocal, WarehouseSalesFact, Transaction, Voucher


def incremental_etl(last_run: datetime = None):
    db = SessionLocal()
    try:
        if last_run is None:
            last_run = datetime.utcnow() - timedelta(days=1)
        source_txns = db.query(Transaction).join(Voucher).filter(Voucher.updated_at >= last_run).all()
        loaded = 0
        for txn in source_txns:
            fact = WarehouseSalesFact(transaction_date=txn.voucher.voucher_date, voucher_id=txn.voucher_id, ledger_id=txn.ledger_id, item_id=None, quantity=0, amount=float(txn.debit or 0) + float(txn.credit or 0), updated_at=datetime.utcnow())
            db.add(fact)
            loaded += 1
        db.commit()
        return {"loaded": loaded, "since": last_run.isoformat()}
    finally:
        db.close()
