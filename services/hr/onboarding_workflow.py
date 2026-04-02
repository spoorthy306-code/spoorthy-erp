from db.schema import SessionLocal, Employee, WorkflowInstance
from typing import Dict, Any


def start_onboarding(employee_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            return {'error': 'employee_not_found'}
        wf = WorkflowInstance(definition_id=1, context_json='{"employee_id": %d}' % employee_id, status='RUNNING')
        db.add(wf)
        db.commit()
        return {'onboarding_workflow_id': wf.id}
    finally:
        db.close()