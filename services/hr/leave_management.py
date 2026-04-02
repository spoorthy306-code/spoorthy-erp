from db.schema import SessionLocal, LeaveRequest, Employee
from typing import Dict, Any


def request_leave(employee_id: int, from_date: str, to_date: str, reason: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        leave = LeaveRequest(employee_id=employee_id, from_date=from_date, to_date=to_date, reason=reason, status='PENDING')
        db.add(leave)
        db.commit()
        return {'leave_id': leave.id}
    finally:
        db.close()


def get_leave_balance(employee_id: int) -> Dict[str, Any]:
    return {'employee_id': employee_id, 'balance_days': 15}
