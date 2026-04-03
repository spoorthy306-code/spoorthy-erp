from db.schema import SessionLocal, TransferOrder, StockItem
from typing import Dict, Any


def create_transfer(source_warehouse: str, target_warehouse: str, item_id: int, quantity: float) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        order = TransferOrder(source_warehouse=source_warehouse, target_warehouse=target_warehouse, item_id=item_id, quantity=quantity, status='PENDING')
        db.add(order)
        db.commit()
        return {'transfer_id': order.id}
    finally:
        db.close()


def complete_transfer(transfer_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        order = db.query(TransferOrder).filter_by(id=transfer_id).first()
        if not order:
            return {'error': 'not_found'}
        order.status = 'COMPLETED'
        db.commit()
        return {'status': 'completed'}
    finally:
        db.close()
