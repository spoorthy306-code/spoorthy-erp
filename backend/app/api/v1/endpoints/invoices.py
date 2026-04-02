# SPOORTHY QUANTUM OS — Invoices API
# CRUD operations for invoices with GST integration

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from ....db.session import get_db
from ....repositories.repositories import InvoiceRepository
from ....models.models import InvoiceSchema, InvoiceCreateSchema

router = APIRouter()

@router.post("/", response_model=InvoiceSchema)
async def create_invoice(
    invoice: InvoiceCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new invoice"""
    repo = InvoiceRepository(db)
    db_invoice = await repo.create(**invoice.model_dump())
    return InvoiceSchema.model_validate(db_invoice)

@router.get("/", response_model=List[InvoiceSchema])
async def list_invoices(
    entity_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    buyer_gstin: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List invoices with filters"""
    repo = InvoiceRepository(db)
    if buyer_gstin:
        invoices = await repo.get_by_gstin(buyer_gstin)
    elif start_date and end_date:
        invoices = await repo.get_by_entity_period(entity_id, start_date, end_date)
    else:
        invoices = await repo.get_all(skip=skip, limit=limit, filters={"entity_id": entity_id})
    return [InvoiceSchema.model_validate(inv) for inv in invoices]

@router.get("/{invoice_id}", response_model=InvoiceSchema)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get invoice by ID"""
    repo = InvoiceRepository(db)
    invoice = await repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceSchema.model_validate(invoice)

@router.post("/{invoice_id}/generate-irn")
async def generate_irn(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generate IRN for invoice"""
    repo = InvoiceRepository(db)
    invoice = await repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Simulate IRN generation
    irn = f"IRN{invoice_id.hex[:20].upper()}"
    qr_code = f"QR{invoice_id.hex[:16].upper()}"

    await repo.update(invoice_id, irn=irn, qr_code=qr_code)

    return {
        "invoice_id": str(invoice_id),
        "irn": irn,
        "qr_code": qr_code,
        "message": "IRN generated successfully"
    }