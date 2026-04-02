from typing import Dict, Any

BPMN_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {"type": "array"},
        "edges": {"type": "array"}
    },
    "required": ["nodes", "edges"]
}


def validate_workflow_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or "nodes" not in payload or "edges" not in payload:
        return {"valid": False, "message": "Invalid workflow structure"}
    return {"valid": True, "node_count": len(payload.get("nodes", []))}
