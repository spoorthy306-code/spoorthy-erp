from db.schema import SessionLocal, PerformanceReview
from typing import Dict, Any


def create_review(employee_id: int, score: float, comments: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        r = PerformanceReview(employee_id=employee_id, score=score, comments=comments, status='PENDING')
        db.add(r)
        db.commit()
        return {'review_id': r.id}
    finally:
        db.close()


def list_reviews(employee_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        reviews = db.query(PerformanceReview).filter_by(employee_id=employee_id).all()
        return [{'id': rv.id, 'score': float(rv.score), 'status': rv.status} for rv in reviews]
    finally:
        db.close()
