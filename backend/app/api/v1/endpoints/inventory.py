# SPOORTHY QUANTUM OS — Inventory API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from uuid import UUID

from ....db.session import get_db
from ....repositories.repositories import InventoryRepository
from ....models.models import InventorySchema, InventoryCreateSchema, Inventory

router = APIRouter()

@router.post("/", response_model=InventorySchema, status_code=201)
async def create_inventory_item(
    item: InventoryCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    data = item.model_dump()
    data['total_value'] = data['qty_on_hand'] * data['unit_cost']
    db_item = Inventory(**data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return InventorySchema.model_validate(db_item)

@router.get("/", response_model=List[InventorySchema])
async def list_inventory(
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    repo = InventoryRepository(db)
    items = await repo.get_by_entity(entity_id)
    return [InventorySchema.model_validate(i) for i in items]

@router.get("/{sku}", response_model=InventorySchema)
async def get_inventory_item(
    sku: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Inventory).where(Inventory.sku == sku))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return InventorySchema.model_validate(item)

@router.put("/{sku}", response_model=InventorySchema)
async def update_inventory_item(
    sku: str,
    item_update: InventoryCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    data = item_update.model_dump(exclude_unset=True)
    if 'qty_on_hand' in data and 'unit_cost' in data:
        data['total_value'] = data['qty_on_hand'] * data['unit_cost']
    result = await db.execute(
        update(Inventory).where(Inventory.sku == sku)
        .values(**data)
        .returning(Inventory)
    )
    await db.commit()
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return InventorySchema.model_validate(item)

@router.post("/{sku}/adjust")
async def adjust_inventory_qty(
    sku: str,
    qty_change: float,
    db: AsyncSession = Depends(get_db)
):
    repo = InventoryRepository(db)
    success = await repo.update_qty(sku, qty_change)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"sku": sku, "qty_change": qty_change, "message": "Quantity adjusted"}

@router.delete("/{sku}", status_code=204)
async def delete_inventory_item(
    sku: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(delete(Inventory).where(Inventory.sku == sku))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found")
