from typing import Dict, Any
from db.schema import SessionLocal, ManufacturingBOM, WorkOrder


def explode_bom(product_id: int, demand_qty: float) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        bom = db.query(ManufacturingBOM).filter_by(product_id=product_id).first()
        if not bom:
            return {'error': 'bom_not_found'}
        return {'schedule_qty': demand_qty, 'components': bom.components_json}
    finally:
        db.close()
