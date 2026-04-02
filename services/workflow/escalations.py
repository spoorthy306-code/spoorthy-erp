from datetime import datetime
from db.schema import SessionLocal, Task, Escalation
from typing import Dict, Any


def check_escalations() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        events = []
        overdue = db.query(Task).filter(Task.status == "PENDING", Task.due_date != None, Task.due_date < now, Task.escalated == False).all()
        for t in overdue:
            t.escalated = True
            e = Escalation(task_id=t.id, escalated_at=now, action="EMAIL/SMS/TICKET", status="CREATED")
            db.add(e)
            events.append({"task": t.id, "escalated": True})
        db.commit()
        return {"escalated": len(events)}
    finally:
        db.close()
