from sqlalchemy.orm import Session
from backend.app.models.order import Order, OrderStatus
from backend.app.models.masters import TaxMaster
from backend.app.schemas.order import OrderCreate, OrderUpdate
from backend.app.services.accounting_service import AccountingService


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()


def create_order(db: Session, order_in: OrderCreate):
    subtotal = round(order_in.quantity * order_in.unit_price, 2)
    tax_amount = 0.0
    total_amount = subtotal

    if order_in.tax_id:
        tax_rate = db.query(TaxMaster.rate).filter(TaxMaster.id == order_in.tax_id).scalar()
        if tax_rate is not None:
            tax_amount = round((subtotal * tax_rate) / 100.0, 2)
            total_amount = round(subtotal + tax_amount, 2)

    order = Order(
        customer_id=order_in.customer_id,
        quantity=order_in.quantity,
        unit_price=order_in.unit_price,
        item_description=order_in.item_description,
        hsn_code=order_in.hsn_code,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status=order_in.status,
        notes=order_in.notes,
        unit_id=order_in.unit_id,
        tax_id=order_in.tax_id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    if order.status == OrderStatus.completed:
        AccountingService.post_order_to_ledger(db, order)

    return order


def complete_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if not order:
        return None

    if order.status != OrderStatus.completed:
        order.status = OrderStatus.completed
        order.subtotal = round(order.quantity * order.unit_price, 2)
        tax_rate = 0.0
        if order.tax_id:
            tax_rate = db.query(TaxMaster.rate).filter(TaxMaster.id == order.tax_id).scalar() or 0.0

        subtotal_float = float(order.subtotal)
        order.tax_amount = round((subtotal_float * tax_rate) / 100.0, 2)
        order.total_amount = round(subtotal_float + order.tax_amount, 2)

        db.commit()
        AccountingService.post_order_to_ledger(db, order)
        db.refresh(order)

    return order


def update_order(db: Session, order_id: int, order_in: OrderUpdate):
    order = get_order(db, order_id)
    if not order:
        return None

    previous_status = order.status
    changed = False

    if order_in.customer_id is not None:
        order.customer_id = order_in.customer_id
        changed = True
    if order_in.quantity is not None:
        order.quantity = order_in.quantity
        changed = True
    if order_in.unit_price is not None:
        order.unit_price = order_in.unit_price
        changed = True
    if order_in.status is not None:
        order.status = order_in.status
    if order_in.notes is not None:
        order.notes = order_in.notes
    if order_in.item_description is not None:
        order.item_description = order_in.item_description
    if order_in.hsn_code is not None:
        order.hsn_code = order_in.hsn_code
    if order_in.unit_id is not None:
        order.unit_id = order_in.unit_id
    if order_in.tax_id is not None:
        order.tax_id = order_in.tax_id
        changed = True

    if changed:
        order.subtotal = round(order.quantity * order.unit_price, 2)
        tax_rate = None
        if order.tax_id:
            tax_rate = db.query(TaxMaster.rate).filter(TaxMaster.id == order.tax_id).scalar()
        if tax_rate is None:
            tax_rate = 0.0

        subtotal_float = float(order.subtotal)
        order.tax_amount = round((subtotal_float * tax_rate) / 100.0, 2)
        order.total_amount = round(subtotal_float + order.tax_amount, 2)

    db.commit()

    # Post accounting entries only when order transitions to completed
    if previous_status != order.status and order.status == OrderStatus.completed:
        AccountingService.post_order_to_ledger(db, order)

    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if not order:
        return None
    db.delete(order)
    db.commit()
    return order
