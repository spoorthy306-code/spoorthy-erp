from typing import Dict, Any
from db.schema import SessionLocal, IntegrationLog


def integration_metrics() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        total = db.query(IntegrationLog).count()
        failures = db.query(IntegrationLog).filter(IntegrationLog.status_code >= 400).count()
        return {"total": total, "errors": failures, "error_rate": (failures / total * 100) if total > 0 else 0}
    finally:
        db.close()
