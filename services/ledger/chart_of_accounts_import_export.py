import io
import csv
from typing import Dict
from db.schema import SessionLocal, Ledger, AccountGroup


def import_coa_csv(csv_text: str) -> Dict[str, int]:
    db = SessionLocal()
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        created = 0
        for row in reader:
            if not row.get("code") or not row.get("name"):
                continue
            group = db.query(AccountGroup).filter_by(code=row.get("group_code")).first()
            group_id = group.id if group else 1
            ledger = Ledger(code=row["code"], name=row["name"], group_id=group_id, currency=row.get("currency", "INR"))
            db.add(ledger)
            created += 1
        db.commit()
        return {"imported": created}
    finally:
        db.close()


def export_coa_csv() -> str:
    db = SessionLocal()
    try:
        ledgers = db.query(Ledger).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["code", "name", "group_id", "currency"])
        for l in ledgers:
            writer.writerow([l.code, l.name, l.group_id, l.currency])
        return output.getvalue()
    finally:
        db.close()
