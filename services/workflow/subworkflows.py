from db.schema import SessionLocal, WorkflowInstance, Task
from typing import Dict, Any


def spawn_subworkflow(parent_instance_id: int, sub_definition_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        parent = db.query(WorkflowInstance).filter_by(id=parent_instance_id).first()
        if not parent:
            return {"error": "parent instance not found"}
        sub = WorkflowInstance(definition_id=sub_definition_id, context_json=parent.context_json, status="RUNNING")
        db.add(sub)
        db.commit()
        t = Task(instance_id=sub.id, title="subworkflow_init", status="PENDING")
        db.add(t)
        db.commit()
        return {"subworkflow_id": sub.id}
    finally:
        db.close()
