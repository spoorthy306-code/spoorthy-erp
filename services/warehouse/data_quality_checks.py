from datetime import datetime
from db.schema import SessionLocal, WarehouseSalesFact, DQIssue


def run_data_quality():
    db = SessionLocal()
    try:
        violations = []
        facts = db.query(WarehouseSalesFact).all()
        for f in facts:
            if float(f.amount or 0) < 0:
                violations.append({"id": f.id, "issue": "negative_amount"})
                db.add(DQIssue(source="warehouse", issue_type="negative_amount", reference_id=f.id, detected_at=datetime.utcnow()))
        db.commit()
        return {"issues": len(violations)}
    finally:
        db.close()
