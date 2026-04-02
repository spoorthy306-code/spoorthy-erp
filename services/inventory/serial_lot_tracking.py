from db.schema import SessionLocal, StockItem
from typing import Dict, Any


def add_serial_lot(item_id: int, serial_number: str, lot_number: str, expiry_date: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        item = db.query(StockItem).filter_by(id=item_id).first()
        if not item:
            return {'error': 'item_not_found'}
        item.serial_number = serial_number
        item.lot_number = lot_number
        item.expiry_date = expiry_date
        db.commit()
        return {'status': 'updated'}
    finally:
        db.close()