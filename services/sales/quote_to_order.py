from typing import Dict, Any
from db.schema import SessionLocal, SalesQuote, SalesOrder


def convert_quote_to_order(quote_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        quote = db.query(SalesQuote).filter_by(id=quote_id).first()
        if not quote:
            return {'error': 'quote_not_found'}
        order = SalesOrder(quote_id=quote.id, customer_id=quote.customer_id, amount=quote.total, status='CONFIRMED')
        db.add(order)
        db.commit()
        return {'order_id': order.id}
    finally:
        db.close()
