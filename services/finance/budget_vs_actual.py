from typing import Dict, Any
from db.schema import SessionLocal, Budget, Transaction


def budget_variances() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        budgets = db.query(Budget).all()
        variances = []
        for b in budgets:
            actual = db.query(Transaction).filter(Transaction.cost_centre == b.cost_centre).count()
            variances.append({'cost_centre': b.cost_centre, 'budget': float(b.amount or 0), 'actual': actual})
        return {'variances': variances}
    finally:
        db.close()