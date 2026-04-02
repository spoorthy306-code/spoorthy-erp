from typing import Dict, Any
from db.schema import SessionLocal, WorkCenterLoad


def get_capacity_load(workcenter_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        load = db.query(WorkCenterLoad).filter_by(workcenter_id=workcenter_id).first()
        if not load:
            return {'workcenter': workcenter_id, 'load': 0}
        return {'workcenter': workcenter_id, 'load': float(load.load)}
    finally:
        db.close()
