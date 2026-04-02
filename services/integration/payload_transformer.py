import jinja2
from typing import Dict, Any


def transform_payload(template: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    t = jinja2.Template(template)
    rendered = t.render(payload)
    try:
        return eval(rendered)
    except Exception:
        return {"error": "render_failed", "raw": rendered}
