from db.schema import SessionLocal, StockItem
from typing import Dict, Any


def set_bin_location(item_id: int, warehouse: str, zone: str, rack: str, bin_code: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        item = db.query(StockItem).filter_by(id=item_id).first()
        if not item:
            return {'error': 'item_not_found'}
        item.warehouse = warehouse
        item.zone = zone
        item.rack = rack
        item.bin_location = bin_code
        db.commit()
        return {'status': 'bin_set'}
    finally:
        db.close()
