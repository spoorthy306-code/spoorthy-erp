# SPOORTHY QUANTUM OS — Entities API
# CRUD operations for entities

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from ....db.session import get_db
from ....repositories.repositories import EntityRepository
from ....models.models import EntitySchema, EntityCreateSchema

router = APIRouter()

@router.post("/", response_model=EntitySchema)
async def create_entity(
    entity: EntityCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new entity"""
    repo = EntityRepository(db)
    db_entity = await repo.create(**entity.model_dump())
    return EntitySchema.model_validate(db_entity)

@router.get("/", response_model=List[EntitySchema])
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all entities with optional search"""
    repo = EntityRepository(db)
    if search:
        entities = await repo.search(search, skip, limit)
    else:
        entities = await repo.get_all(skip, limit)
    return [EntitySchema.model_validate(entity) for entity in entities]

@router.get("/{entity_id}", response_model=EntitySchema)
async def get_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get entity by ID"""
    repo = EntityRepository(db)
    entity = await repo.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntitySchema.model_validate(entity)

@router.put("/{entity_id}", response_model=EntitySchema)
async def update_entity(
    entity_id: UUID,
    entity_update: EntityCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update entity"""
    repo = EntityRepository(db)
    updated_entity = await repo.update(entity_id, **entity_update.model_dump())
    if not updated_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntitySchema.model_validate(updated_entity)

@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete entity"""
    repo = EntityRepository(db)
    deleted = await repo.delete(entity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted successfully"}

@router.get("/gstin/{gstin}", response_model=EntitySchema)
async def get_entity_by_gstin(
    gstin: str,
    db: AsyncSession = Depends(get_db)
):
    """Get entity by GSTIN"""
    repo = EntityRepository(db)
    entity = await repo.get_by_gstin(gstin)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntitySchema.model_validate(entity)

@router.get("/pan/{pan}", response_model=EntitySchema)
async def get_entity_by_pan(
    pan: str,
    db: AsyncSession = Depends(get_db)
):
    """Get entity by PAN"""
    repo = EntityRepository(db)
    entity = await repo.get_by_pan(pan)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntitySchema.model_validate(entity)