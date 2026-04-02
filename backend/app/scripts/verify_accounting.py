from sqlalchemy import select
from backend.db.session import SessionLocal
from backend.app.models.transactions import JournalEntry
from backend.app.models.finance import Ledger


def verify_order_posting(order_reference: str):
    db = SessionLocal()
    try:
        stmt = select(JournalEntry, Ledger.name).join(Ledger, Ledger.id == JournalEntry.ledger_id).where(JournalEntry.reference == order_reference)
        results = db.execute(stmt).all()

        print(f"\n--- Accounting Audit for {order_reference} ---")
        total_debit = 0
        total_credit = 0

        for entry, ledger_name in results:
            print(f"Ledger: {ledger_name:<20} | Debit: {float(entry.debit):>7.2f} | Credit: {float(entry.credit):>7.2f}")
            total_debit += float(entry.debit)
            total_credit += float(entry.credit)

        print("-" * 45)
        print(f"TOTALS:                | Debit: {total_debit:>7.2f} | Credit: {total_credit:>7.2f}")

        if total_debit == total_credit and total_debit > 0:
            print("STATUS: ✅ Balanced")
        else:
            print("STATUS: ❌ Imbalanced or No Data Found")

    finally:
        db.close()


if __name__ == "__main__":
    # Replace with actual order reference (e.g., INV-4)
    verify_order_posting("INV-4")
