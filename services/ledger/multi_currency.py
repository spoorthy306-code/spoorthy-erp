from datetime import datetime
from typing import Dict, Any, List
from db.schema import SessionLocal, ExchangeRate


def get_exchange_rates() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rates = db.query(ExchangeRate).all()
        return [{"from": r.from_currency, "to": r.to_currency, "rate": float(r.rate), "updated_at": r.updated_at.isoformat() if r.updated_at else None} for r in rates]
    finally:
        db.close()


def set_exchange_rate(from_currency: str, to_currency: str, rate: float) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rec = db.query(ExchangeRate).filter_by(from_currency=from_currency, to_currency=to_currency).first()
        if not rec:
            rec = ExchangeRate(from_currency=from_currency, to_currency=to_currency, rate=rate, updated_at=datetime.utcnow())
            db.add(rec)
        else:
            rec.rate = rate
            rec.updated_at = datetime.utcnow()
        db.commit()
        return {"from": from_currency, "to": to_currency, "rate": rate}
    finally:
        db.close()
