from typing import Dict, Any
from db.schema import SessionLocal, DeadLetter


def list_dead_letter() -> Any:
    db = SessionLocal()
    try:
        rows = db.query(DeadLetter).all()
        return [{"id": r.id, "payload": r.payload, "status": r.status, "created_at": r.created_at.isoformat()} for r in rows]
    finally:
        db.close()


def replay_dead_letter(record_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rec = db.query(DeadLetter).filter_by(id=record_id).first()
        if not rec:
            return {"error": "not_found"}
        rec.status = "REPLAYED"
        db.commit()
        return {"status": "replayed", "id": record_id}
    finally:
        db.close()


def delete_dead_letter(record_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rec = db.query(DeadLetter).filter_by(id=record_id).first()
        if not rec:
            return {"error": "not_found"}
        db.delete(rec)
        db.commit()
        return {"status": "deleted", "id": record_id}
    finally:
        db.close()