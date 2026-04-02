import os
import pickle
from datetime import datetime
from typing import Dict, Any
from db.schema import SessionLocal, WarehouseSalesFact

MODEL_PATH = 'models/sales_forecast.pkl'

def train_pipeline() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        facts = db.query(WarehouseSalesFact).all()
        model = {
            'trained_at': datetime.utcnow().isoformat(),
            'rows': len(facts),
            'type': 'stub'
        }
        os.makedirs('models', exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        return {'status': 'trained', 'rows': len(facts)}
    finally:
        db.close()
