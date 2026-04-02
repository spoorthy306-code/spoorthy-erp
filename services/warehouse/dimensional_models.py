from db.schema import SessionLocal, DimensionCustomer, DimensionProduct, DimensionTime
from typing import Dict, Any


def build_dimensional_models() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        customers = db.query(DimensionCustomer).count()
        products = db.query(DimensionProduct).count()
        times = db.query(DimensionTime).count()
        return {"customers": customers, "products": products, "times": times}
    finally:
        db.close()
