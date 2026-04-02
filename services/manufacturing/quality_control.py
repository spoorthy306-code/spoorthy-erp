from typing import Dict, Any
from db.schema import SessionLocal, InspectionChecklist


def create_inspection(order_id: int, results: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        insp = InspectionChecklist(work_order_id=order_id, results=str(results), status='COMPLETE')
        db.add(insp)
        db.commit()
        return {'inspection_id': insp.id}
    finally:
        db.close()
