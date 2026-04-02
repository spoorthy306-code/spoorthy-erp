from typing import Dict, Any
from db.schema import SessionLocal, Party, SalesOrder


def check_credit_limit(customer_id: int, order_amount: float) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        customer = db.query(Party).filter_by(id=customer_id).first()
        if not customer:
            return {'error': 'customer_not_found'}
        if float(customer.credit_limit or 0) < order_amount:
            return {'allowed': False, 'reason': 'credit_exceeded'}
        return {'allowed': True}
    finally:
        db.close()
