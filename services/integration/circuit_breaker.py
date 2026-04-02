import time
from typing import Callable, Dict, Any

state = {"failures": 0, "opened_at": None, "open": False}


def call_with_circuit(fn: Callable[..., Any], *args, **kwargs) -> Dict[str, Any]:
    if state["open"] and time.time() - state["opened_at"] < 30:
        return {"error": "circuit_open"}

    try:
        result = fn(*args, **kwargs)
        state["failures"] = 0
        state["open"] = False
        return {"result": result}
    except Exception as exc:
        state["failures"] += 1
        if state["failures"] >= 3:
            state["open"] = True
            state["opened_at"] = time.time()
        return {"error": "call_failed", "message": str(exc)}
