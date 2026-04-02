import csv
import io
from db.schema import SessionLocal, WarehouseSalesFact


def export_sales(format: str = "csv") -> str:
    db = SessionLocal()
    try:
        data = db.query(WarehouseSalesFact).all()
        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "transaction_date", "amount"])
            for d in data:
                writer.writerow([d.id, d.transaction_date, float(d.amount or 0)])
            return output.getvalue()
        raise ValueError("unsupported format")
    finally:
        db.close()


def export_inventory(format: str = "xlsx") -> bytes:
    csv_text = export_sales("csv")
    return csv_text.encode("utf-8")
