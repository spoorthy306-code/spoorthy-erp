from datetime import datetime
from db.schema import SessionLocal, WorkflowInstance, Task
from typing import Dict, Any


def workflow_metrics() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        total = db.query(WorkflowInstance).count()
        completed = db.query(WorkflowInstance).filter(WorkflowInstance.status == "COMPLETED").count()
        overdue_tasks = db.query(Task).filter(Task.status == "PENDING", Task.due_date != None, Task.due_date < datetime.utcnow()).count()
        return {"total_workflows": total, "completed_workflows": completed, "overdue_tasks": overdue_tasks}
    finally:
        db.close()
