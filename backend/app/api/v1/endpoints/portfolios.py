# SPOORTHY QUANTUM OS — Portfolios API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Dict, Any
from uuid import UUID

from ....db.session import get_db
from ....repositories.repositories import PortfolioRepository
from ....models.models import PortfolioSchema, PortfolioCreateSchema, Portfolio

router = APIRouter()

@router.post("/", response_model=PortfolioSchema, status_code=201)
async def create_portfolio(
    portfolio: PortfolioCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    data = portfolio.model_dump()
    holdings = data.get('holdings') or {}
    data['total_value'] = sum(h.get('value', 0) for h in holdings.values() if isinstance(h, dict))
    repo = PortfolioRepository(db)
    db_portfolio = await repo.create(**data)
    return PortfolioSchema.model_validate(db_portfolio)

@router.get("/", response_model=List[PortfolioSchema])
async def list_portfolios(
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    repo = PortfolioRepository(db)
    portfolios = await repo.get_by_entity(entity_id)
    return [PortfolioSchema.model_validate(p) for p in portfolios]

@router.get("/{portfolio_id}", response_model=PortfolioSchema)
async def get_portfolio(
    portfolio_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Portfolio).where(Portfolio.portfolio_id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioSchema.model_validate(portfolio)

@router.put("/{portfolio_id}", response_model=PortfolioSchema)
async def update_portfolio(
    portfolio_id: UUID,
    portfolio_update: PortfolioCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    data = portfolio_update.model_dump(exclude_unset=True)
    if 'holdings' in data:
        holdings = data.get('holdings') or {}
        data['total_value'] = sum(h.get('value', 0) for h in holdings.values() if isinstance(h, dict))
    result = await db.execute(
        update(Portfolio).where(Portfolio.portfolio_id == portfolio_id)
        .values(**data)
        .returning(Portfolio)
    )
    await db.commit()
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioSchema.model_validate(portfolio)

@router.post("/{portfolio_id}/optimize")
async def optimize_portfolio(
    portfolio_id: UUID,
    risk_profile: str = "balanced",
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Portfolio).where(Portfolio.portfolio_id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Simulated quantum portfolio optimization
    risk_weights = {"conservative": 0.3, "balanced": 0.5, "aggressive": 0.7}
    risk_factor = risk_weights.get(risk_profile, 0.5)

    return {
        "portfolio_id": str(portfolio_id),
        "risk_profile": risk_profile,
        "expected_return": round(0.08 + risk_factor * 0.12, 4),
        "volatility": round(0.05 + risk_factor * 0.15, 4),
        "sharpe_ratio": round(0.8 + risk_factor * 0.6, 4),
        "quantum_solver": "QUBO",
        "allocation": portfolio.holdings or {}
    }

@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(
    portfolio_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(delete(Portfolio).where(Portfolio.portfolio_id == portfolio_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")
