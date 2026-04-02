from backend.db.session import SessionLocal
from backend.app.models.finance import AccountGroup, Ledger
from backend.app.models.masters import TaxMaster, UnitMaster


def _ensure_defaults():
    db = SessionLocal()
    try:
        # Account groups
        groups = [
            ("ASSETS", "Assets"),
            ("LIABILITIES", "Liabilities"),
            ("INCOME", "Income"),
            ("EXPENSES", "Expenses"),
        ]

        for group_type, name in groups:
            group = db.query(AccountGroup).filter_by(name=name).first()
            if not group:
                db.add(AccountGroup(code=name.lower(), name=name, group_type=group_type, affects_gross=False, is_system=True))
        db.commit()

        assets = db.query(AccountGroup).filter_by(name="Assets").first()
        liabilities = db.query(AccountGroup).filter_by(name="Liabilities").first()

        subgroups = [
            ("Bank Accounts", assets.id if assets else None),
            ("Duties & Taxes", liabilities.id if liabilities else None),
            ("Sundry Debtors", assets.id if assets else None),
        ]

        for name, parent_id in subgroups:
            if parent_id is None:
                continue
            group = db.query(AccountGroup).filter_by(name=name).first()
            if not group:
                db.add(AccountGroup(code=name.lower().replace(' ', '_'), name=name, group_type='ASSET' if parent_id == assets.id else 'LIABILITY', parent_id=parent_id, affects_gross=False, is_system=False))
        db.commit()

        # Ledgers
        assets = db.query(AccountGroup).filter_by(name="Assets").first()
        expenses = db.query(AccountGroup).filter_by(name="Expenses").first()
        income = db.query(AccountGroup).filter_by(name="Income").first()
        liabilities = db.query(AccountGroup).filter_by(name="Liabilities").first()

        ledger_defaults = [
            ("Cash Account", assets.id if assets else None),
            ("Profit & Loss A/c", expenses.id if expenses else None),
            ("Sales Account", income.id if income else None),
            ("Duties & Taxes", liabilities.id if liabilities else None),
            ("Sundry Debtors", assets.id if assets else None),
        ]

        for name, group_id in ledger_defaults:
            if group_id is None:
                continue
            ledger = db.query(Ledger).filter_by(name=name).first()
            if not ledger:
                code = name.lower().replace(' ', '_').replace('&', 'and').replace('/', '_')
                db.add(Ledger(code=code, name=name, group_id=group_id, nature='Dr', opening_balance=0.0, opening_type='Dr', currency='INR', is_active=True))
        db.commit()

        # Tax masters
        tax_defaults = [
            ("GST 5%", 5.0, "Output"),
            ("GST 12%", 12.0, "Output"),
            ("GST 18%", 18.0, "Output"),
            ("Exempt", 0.0, "Exempt"),
        ]

        for name, rate, type_ in tax_defaults:
            tax = db.query(TaxMaster).filter_by(name=name).first()
            if not tax:
                db.add(TaxMaster(name=name, rate=rate, type=type_))
        db.commit()

        # Unit masters
        unit_defaults = [
            ("Pieces", "Pcs"),
            ("Kilogram", "Kg"),
            ("Nos", "Nos"),
            ("Box", "Box"),
        ]

        for name, symbol in unit_defaults:
            unit = db.query(UnitMaster).filter_by(name=name).first()
            if not unit:
                db.add(UnitMaster(name=name, symbol=symbol))
        db.commit()

        # Company profile
        from backend.app.models.company import CompanyProfile

        company = db.query(CompanyProfile).first()
        if not company:
            db.add(CompanyProfile(
                name="Spoorthy Solutions Pvt Ltd",
                address="Plot 42, Tech Park, Hyderabad, 500081",
                phone="+91 98765 43210",
                email="info@spoorthy.erp",
                gstin="36ABCDE1234F1Z5",
                logo_path="static/logo.png",
                bank_details="Bank: ICICI Bank, A/c: 1234567890, IFSC: ICIC0000001"
            ))
        db.commit()

        print("Master data seed complete.")

    finally:
        db.close()


if __name__ == "__main__":
    _ensure_defaults()
