from datetime import datetime
from typing import Dict, Any
from db.schema import SessionLocal, Voucher, VoucherLineItem, Party, StockItem


def create_invoice(order_id: int, customer_id: int, lines: list) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        total = sum(float(l.get('amount', 0)) for l in lines)
        invoice = Voucher(voucher_no=f'INV-{order_id}', voucher_type_id=2, voucher_date=datetime.utcnow().date(), fiscal_year='2025-26', party_id=customer_id, narration='Invoice from sales order', total_amount=total, status='POSTED')
        db.add(invoice)
        db.flush()
        for l in lines:
            item = db.query(StockItem).filter_by(id=l.get('item_id')).first()
            db.add(VoucherLineItem(voucher_id=invoice.id, stock_item_id=item.id if item else None, description=l.get('description',''), quantity=l.get('quantity',1), unit_price=l.get('price',0), taxable_value=l.get('amount',0), line_total=l.get('amount',0)))
        db.commit()
        return {'invoice_id': invoice.id, 'total': total}
    finally:
        db.close()

def list_invoices():
    db = SessionLocal()
    try:
        invoices = db.query(Voucher).filter(Voucher.voucher_type_id==2).all()
        return [{'voucher_id': inv.id, 'invoice': inv.voucher_no, 'amount': float(inv.total_amount or 0)} for inv in invoices]
    finally:
        db.close()


def match_payment(payment_id: int, invoice_id: int):
    return {'status': 'matched', 'payment_id': payment_id, 'invoice_id': invoice_id}
