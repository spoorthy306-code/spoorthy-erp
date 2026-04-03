from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from backend.app.services.invoice_service import InvoiceService
from backend.app.services.order_service import (complete_order, create_order,
                                                delete_order, get_order,
                                                get_orders, update_order)
from backend.db.session import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_route(order_in: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order_in)


@router.get("/", response_model=list[OrderRead])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_orders(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderRead)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.patch("/{order_id}", response_model=OrderRead)
def update_order_route(
    order_id: int, order_in: OrderUpdate, db: Session = Depends(get_db)
):
    order = update_order(db, order_id, order_in)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.post("/{order_id}/complete", response_model=OrderRead)
def complete_order_route(order_id: int, db: Session = Depends(get_db)):
    order = complete_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.get("/{order_id}/print")
def print_invoice(order_id: int, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    pdf_path = InvoiceService.generate_pdf(order, filename=f"Invoice_{order_id}.pdf")
    return FileResponse(
        pdf_path, media_type="application/pdf", filename=f"Invoice_{order_id}.pdf"
    )


@router.delete("/{order_id}", response_model=OrderRead)
def delete_order_route(order_id: int, db: Session = Depends(get_db)):
    order = delete_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order
