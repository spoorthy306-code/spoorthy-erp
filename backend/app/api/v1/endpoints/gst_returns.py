# SPOORTHY QUANTUM OS — GST Returns API
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import GSTReturn, GSTReturnCreateSchema, GSTReturnSchema

router = APIRouter()


@router.post("/", response_model=GSTReturnSchema, status_code=201)
async def create_gst_return(
    gst_return: GSTReturnCreateSchema, db: AsyncSession = Depends(get_db)
):
    db_return = GSTReturn(**gst_return.model_dump())
    db.add(db_return)
    await db.commit()
    await db.refresh(db_return)
    return GSTReturnSchema.model_validate(db_return)


@router.get("/", response_model=List[GSTReturnSchema])
async def list_gst_returns(
    entity_id: UUID,
    period: Optional[str] = None,
    return_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = select(GSTReturn).where(GSTReturn.entity_id == entity_id)
    if period:
        query = query.where(GSTReturn.period == period)
    if return_type:
        query = query.where(GSTReturn.return_type == return_type)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    returns = result.scalars().all()
    return [GSTReturnSchema.model_validate(r) for r in returns]


@router.get("/{return_id}", response_model=GSTReturnSchema)
async def get_gst_return(return_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GSTReturn).where(GSTReturn.return_id == return_id))
    gst_return = result.scalar_one_or_none()
    if not gst_return:
        raise HTTPException(status_code=404, detail="GST return not found")
    return GSTReturnSchema.model_validate(gst_return)


@router.post("/{return_id}/file")
async def file_gst_return(return_id: UUID, db: AsyncSession = Depends(get_db)):
    import secrets

    from sqlalchemy import update

    result = await db.execute(
        update(GSTReturn)
        .where(GSTReturn.return_id == return_id)
        .values(status="FILED", arn=f"AA{secrets.token_hex(9).upper()}")
        .returning(GSTReturn)
    )
    await db.commit()
    gst_return = result.scalar_one_or_none()
    if not gst_return:
        raise HTTPException(status_code=404, detail="GST return not found")
    return {"return_id": str(return_id), "status": "FILED", "arn": gst_return.arn}


@router.delete("/{return_id}", status_code=204)
async def delete_gst_return(return_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(GSTReturn).where(GSTReturn.return_id == return_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="GST return not found")
