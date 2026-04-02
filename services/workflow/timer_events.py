import threading
from datetime import datetime
from typing import Dict, Any
from db.schema import SessionLocal, WorkflowInstance

_scheduled = []


def schedule_workflow_start(definition_id: int, start_at: datetime) -> Dict[str, Any]:
    delay = max((start_at - datetime.utcnow()).total_seconds(), 0)

    def run():
        db = SessionLocal()
        try:
            wf = WorkflowInstance(definition_id=definition_id, status="RUNNING", context_json="{}")
            db.add(wf)
            db.commit()
        finally:
            db.close()

    timer = threading.Timer(delay, run)
    timer.start()
    _scheduled.append({"definition_id": definition_id, "start_at": start_at.isoformat()})
    return {"scheduled": True}
