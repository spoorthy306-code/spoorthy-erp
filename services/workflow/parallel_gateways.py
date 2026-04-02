from typing import Dict, Any
from db.schema import SessionLocal, WorkflowDefinition, WorkflowInstance, Task


def define_parallel_workflow(name: str, nodes: Dict[str, Any], branches: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        wf = WorkflowDefinition(name=name, description="parallel gateway flow", rule_json=str({"nodes": nodes, "branches": branches}))
        db.add(wf)
        db.commit()
        return {"workflow_id": wf.id}
    finally:
        db.close()


def fork_join_instance(workflow_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        start = WorkflowInstance(definition_id=workflow_id, context_json=str(data), status="RUNNING")
        db.add(start)
        db.commit()
        for branch in data.get("branches", []):
            t = Task(instance_id=start.id, title=f"parallel_{branch}", assigned_to=None, status="PENDING")
            db.add(t)
        db.commit()
        return {"instance_id": start.id, "branches": len(data.get("branches", []))}
    finally:
        db.close()
