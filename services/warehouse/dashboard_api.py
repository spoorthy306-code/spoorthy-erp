from db.schema import SessionLocal, WarehouseSalesFact


def dashboard_kpis():
    db = SessionLocal()
    try:
        total_sales = sum(float(f.amount or 0) for f in db.query(WarehouseSalesFact).all())
        return {"total_sales": total_sales, "orders": 0, "inventory_value": 0}
    finally:
        db.close()


def sales_trend(days: int = 30):
    datapoints = []
    for idx in range(days):
        datapoints.append({"day": idx, "sales": idx * 100})
    return {"trend": datapoints}
