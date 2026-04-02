from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.finance import Ledger
from backend.app.models.transactions import JournalEntry


class AccountingService:
    @staticmethod
    def post_order_to_ledger(db: Session, order):
        """Post completed order to ledger with balanced double-entry."""
        sales_ledger = db.query(Ledger).filter(Ledger.name.in_(["Sales Account", "Profit & Loss A/c"]) ).first()
        tax_ledger = db.query(Ledger).filter(Ledger.name.in_(["Duties & Taxes", "Tax Account"]) ).first()
        debtors_ledger = db.query(Ledger).filter(Ledger.name.in_(["Sundry Debtors", "Cash Account"]) ).first()

        if not sales_ledger or not tax_ledger or not debtors_ledger:
            raise ValueError("Required ledgers not found for accounting post: sales=%s tax=%s debtors=%s" % (bool(sales_ledger), bool(tax_ledger), bool(debtors_ledger)))

        entries = [
            JournalEntry(
                ledger_id=debtors_ledger.id,
                debit=order.total_amount,
                credit=0,
                reference=f"INV-{order.id}",
                description=f"Order #{order.id} total"
            ),
            JournalEntry(
                ledger_id=sales_ledger.id,
                debit=0,
                credit=order.subtotal,
                reference=f"INV-{order.id}",
                description=f"Sales for order #{order.id}"
            ),
            JournalEntry(
                ledger_id=tax_ledger.id,
                debit=0,
                credit=order.tax_amount,
                reference=f"INV-{order.id}",
                description=f"Tax for order #{order.id}"
            ),
        ]

        db.add_all(entries)
        db.commit()
        return True
