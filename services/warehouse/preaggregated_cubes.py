from db.schema import SessionLocal, WarehouseSalesFact


def daily_sales_cube():
    db = SessionLocal()
    try:
        rows = db.query(WarehouseSalesFact).all()
        return {"days": len(rows)}
    finally:
        db.close()


def monthly_inventory_turnover_cube():
    return {"status": "stub"}
