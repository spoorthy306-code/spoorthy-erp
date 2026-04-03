from db.schema import SessionLocal, CycleCount
from typing import Dict, Any


def schedule_cycle_count(item_id: int, count_date: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        c = CycleCount(item_id=item_id, scheduled_date=count_date, status='SCHEDULED')
        db.add(c)
        db.commit()
        return {'cycle_count_id': c.id}
    finally:
        db.close()


def record_count(cycle_id: int, counted_qty: float) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        c = db.query(CycleCount).filter_by(id=cycle_id).first()
        if not c:
            return {'error': 'not_found'}
        c.counted_quantity = counted_qty
        c.status = 'COMPLETED'
        db.commit()
        return {'status': 'recorded'}
    finally:
        db.close()
