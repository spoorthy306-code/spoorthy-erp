# SPOORTHY QUANTUM OS — Reports API
# Financial reports with quantum acceleration

from datetime import date
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....services.financial_services import (BudgetActualEngine,
                                             FinancialStatementGenerator)
from ....services.quantum_services import QuantumPortfolioOptimizer

router = APIRouter()


@router.get("/trial-balance/{entity_id}")
async def get_trial_balance(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate trial balance for entity and period"""
    generator = FinancialStatementGenerator(db)
    trial_balance = await generator.generate_trial_balance(entity_id, period)
    return trial_balance


@router.get("/pnl/{entity_id}")
async def get_profit_loss(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate profit & loss statement"""
    generator = FinancialStatementGenerator(db)
    pnl = await generator.generate_pl(entity_id, period)
    return pnl


@router.get("/balance-sheet/{entity_id}")
async def get_balance_sheet(
    entity_id: UUID,
    as_of_date: date = Query(..., description="Balance sheet date"),
    db: AsyncSession = Depends(get_db),
):
    """Generate balance sheet"""
    generator = FinancialStatementGenerator(db)
    bs = await generator.generate_balance_sheet(entity_id, as_of_date)
    return bs


@router.get("/cash-flow/{entity_id}")
async def get_cash_flow(
    entity_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Generate cash flow statement"""
    generator = FinancialStatementGenerator(db)
    cf = await generator.generate_cash_flow(entity_id, start_date, end_date)
    return cf


@router.get("/budget-variance/{entity_id}")
async def get_budget_variance(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate budget vs actual variance report"""
    engine = BudgetActualEngine(db)
    variance_report = await engine.variance_report(entity_id, period)
    return variance_report


@router.get("/portfolio-optimization/{entity_id}")
async def optimize_portfolio(
    entity_id: UUID,
    risk_tolerance: float = Query(0.5, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
):
    """Quantum portfolio optimization"""
    optimizer = QuantumPortfolioOptimizer()
    optimization = await optimizer.optimize_portfolio(entity_id, risk_tolerance, db)
    return optimization


@router.get("/aging/{entity_id}")
async def get_receivables_aging(
    entity_id: UUID, as_of_date: date = Query(...), db: AsyncSession = Depends(get_db)
):
    """Generate receivables aging report"""
    generator = FinancialStatementGenerator(db)
    aging = await generator.generate_aging_report(entity_id, as_of_date)
    return aging


@router.get("/depreciation-schedule/{entity_id}")
async def get_depreciation_schedule(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate depreciation schedule"""
    from ....services.fixed_asset_services import FixedAssetEngine

    engine = FixedAssetEngine(db)
    schedule = await engine.depreciation_schedule(entity_id, period)
    return schedule


@router.get("/gst-summary/{entity_id}")
async def get_gst_summary(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate GST summary report"""
    from ....services.compliance_services import GSTComplianceEngine

    engine = GSTComplianceEngine(db)
    summary = await engine.generate_gst_summary(entity_id, period)
    return summary


@router.get("/payroll-summary/{entity_id}")
async def get_payroll_summary(
    entity_id: UUID,
    period: str = Query(..., description="Period in YYYY-MM format"),
    db: AsyncSession = Depends(get_db),
):
    """Generate payroll summary"""
    from ....services.payroll_services import PayrollEngine

    engine = PayrollEngine(db)
    summary = await engine.generate_payroll_summary(entity_id, period)
    return summary
