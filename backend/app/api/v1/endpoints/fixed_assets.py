# SPOORTHY QUANTUM OS — Fixed Assets API
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import (FixedAsset, FixedAssetCreateSchema,
                               FixedAssetSchema)
from ....repositories.repositories import FixedAssetRepository

router = APIRouter()


@router.post("/", response_model=FixedAssetSchema, status_code=201)
async def create_fixed_asset(
    asset: FixedAssetCreateSchema, db: AsyncSession = Depends(get_db)
):
    data = asset.model_dump()
    data["nbv"] = data["cost"] - data.get("residual_value", 0)
    repo = FixedAssetRepository(db)
    db_asset = await repo.create(**data)
    return FixedAssetSchema.model_validate(db_asset)


@router.get("/", response_model=List[FixedAssetSchema])
async def list_fixed_assets(
    entity_id: UUID,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    repo = FixedAssetRepository(db)
    if active_only:
        assets = await repo.get_active_by_entity(entity_id)
    else:
        assets = await repo.get_all(skip, limit)
        assets = [a for a in assets if a.entity_id == entity_id]
    return [FixedAssetSchema.model_validate(a) for a in assets]


@router.get("/{asset_id}", response_model=FixedAssetSchema)
async def get_fixed_asset(asset_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FixedAsset).where(FixedAsset.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Fixed asset not found")
    return FixedAssetSchema.model_validate(asset)


@router.put("/{asset_id}", response_model=FixedAssetSchema)
async def update_fixed_asset(
    asset_id: UUID,
    asset_update: FixedAssetCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        update(FixedAsset)
        .where(FixedAsset.asset_id == asset_id)
        .values(**asset_update.model_dump(exclude_unset=True))
        .returning(FixedAsset)
    )
    await db.commit()
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Fixed asset not found")
    return FixedAssetSchema.model_validate(asset)


@router.post("/{asset_id}/depreciate")
async def run_depreciation(asset_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FixedAsset).where(FixedAsset.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Fixed asset not found")
    if not asset.cost or not asset.useful_life_years:
        raise HTTPException(status_code=400, detail="Asset missing cost or useful life")
    annual_depr = (asset.cost - (asset.residual_value or 0)) / asset.useful_life_years
    new_accum = (asset.accumulated_depreciation or 0) + annual_depr
    new_nbv = max(asset.cost - new_accum, 0)
    repo = FixedAssetRepository(db)
    await repo.update_depreciation(asset_id, new_accum, new_nbv)
    return {
        "asset_id": str(asset_id),
        "annual_depreciation": annual_depr,
        "accumulated": new_accum,
        "nbv": new_nbv,
    }


@router.delete("/{asset_id}", status_code=204)
async def delete_fixed_asset(asset_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(FixedAsset).where(FixedAsset.asset_id == asset_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Fixed asset not found")
