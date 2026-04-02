# SPOORTHY QUANTUM OS — Treasury Management API
from datetime import date, datetime
from math import exp, log
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....models.models import Entity

router = APIRouter()


@router.get("/cash-position")
async def get_cash_position(
    entity_id: UUID, as_of: Optional[date] = None, db: AsyncSession = Depends(get_db)
):
    """
    Real-time treasury cash position across all accounts and currencies.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    as_of_str = str(as_of or date.today())

    # In production these would come from bank_transactions table
    accounts = [
        {
            "account": "Current Account — HDFC",
            "currency": "INR",
            "balance": 12_500_000.0,
            "bank": "HDFC Bank",
        },
        {
            "account": "Current Account — SBI",
            "currency": "INR",
            "balance": 3_200_000.0,
            "bank": "State Bank of India",
        },
        {
            "account": "EEFC Account — Citi",
            "currency": "USD",
            "balance": 85_000.0,
            "bank": "Citibank",
        },
        {
            "account": "Fixed Deposit — ICICI",
            "currency": "INR",
            "balance": 5_000_000.0,
            "bank": "ICICI Bank",
        },
    ]
    fx_rates = {"INR": 1.0, "USD": 83.5, "EUR": 91.2, "GBP": 106.1}

    total_inr = sum(a["balance"] * fx_rates.get(a["currency"], 1.0) for a in accounts)

    return {
        "entity_id": str(entity_id),
        "as_of": as_of_str,
        "accounts": accounts,
        "total_inr_equivalent": round(total_inr, 2),
        "fx_rates_used": fx_rates,
        "liquidity_coverage_ratio": round(total_inr / 8_000_000, 3),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/invest")
async def invest_surplus(
    entity_id: UUID,
    amount: float,
    tenor_days: int,
    instrument: str = "LIQUID_MF",  # LIQUID_MF | T_BILL | FD | OVERNIGHT_REPO
    db: AsyncSession = Depends(get_db),
):
    """
    Invest surplus cash in money-market instruments.
    Returns expected yield and maturity amount.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    INSTRUMENT_RATES = {
        "LIQUID_MF": 0.071,  # 7.1% p.a.
        "T_BILL": 0.068,  # 6.8% p.a. (91-day T-Bill)
        "FD": 0.075,  # 7.5% p.a. bank FD
        "OVERNIGHT_REPO": 0.065,  # 6.5% p.a. repo rate
        "CP": 0.076,  # 7.6% p.a. commercial paper
    }
    if instrument not in INSTRUMENT_RATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown instrument. Choose from: {list(INSTRUMENT_RATES)}",
        )

    annual_rate = INSTRUMENT_RATES[instrument]
    interest = round(amount * annual_rate * tenor_days / 365, 2)
    maturity = round(amount + interest, 2)
    effective_yield = round((interest / amount) * (365 / tenor_days) * 100, 4)

    return {
        "entity_id": str(entity_id),
        "instrument": instrument,
        "principal": amount,
        "tenor_days": tenor_days,
        "annual_rate_pct": round(annual_rate * 100, 2),
        "expected_interest": interest,
        "maturity_amount": maturity,
        "effective_yield_pct": effective_yield,
        "investment_date": str(date.today()),
        "maturity_date": str(date.fromordinal(date.today().toordinal() + tenor_days)),
        "status": "PENDING_EXECUTION",
    }


@router.post("/fund-deficit")
async def fund_cash_deficit(
    entity_id: UUID,
    deficit_amount: float,
    required_by: date,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate funding options to cover a cash deficit.
    Ranks options by cost from lowest to highest.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    days = max((required_by - date.today()).days, 1)

    options = [
        {
            "source": "OD Facility — HDFC",
            "available": 20_000_000,
            "rate_pa": 0.095,
            "cost": deficit_amount * 0.095 * days / 365,
        },
        {
            "source": "Cash Credit — SBI",
            "available": 15_000_000,
            "rate_pa": 0.090,
            "cost": deficit_amount * 0.090 * days / 365,
        },
        {
            "source": "Commercial Paper (30d)",
            "available": 50_000_000,
            "rate_pa": 0.076,
            "cost": deficit_amount * 0.076 * days / 365,
        },
        {
            "source": "Inter-company Loan",
            "available": 5_000_000,
            "rate_pa": 0.080,
            "cost": deficit_amount * 0.080 * days / 365,
        },
        {
            "source": "Redeem Liquid MF",
            "available": 10_000_000,
            "rate_pa": 0.000,
            "cost": 0.0,
        },
    ]

    # Sort by cost
    options.sort(key=lambda x: x["cost"])
    for o in options:
        o["cost"] = round(o["cost"], 2)
        o["feasible"] = o["available"] >= deficit_amount

    recommended = next((o for o in options if o["feasible"]), options[0])

    return {
        "entity_id": str(entity_id),
        "deficit_amount": deficit_amount,
        "required_by": str(required_by),
        "days_to_cover": days,
        "funding_options_ranked": options,
        "recommended": recommended,
    }


@router.get("/fx-hedging")
async def get_fx_hedging_analysis(entity_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    FX exposure analysis and hedging recommendations.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    exposures = [
        {
            "currency": "USD",
            "receivable": 250_000,
            "payable": 80_000,
            "net": 170_000,
            "spot_rate": 83.5,
            "inr_equivalent": 14_195_000,
            "hedged_pct": 65.0,
        },
        {
            "currency": "EUR",
            "receivable": 50_000,
            "payable": 20_000,
            "net": 30_000,
            "spot_rate": 91.2,
            "inr_equivalent": 2_736_000,
            "hedged_pct": 40.0,
        },
        {
            "currency": "GBP",
            "receivable": 10_000,
            "payable": 5_000,
            "net": 5_000,
            "spot_rate": 106.1,
            "inr_equivalent": 530_500,
            "hedged_pct": 0.0,
        },
    ]

    hedges = [
        {
            "type": "USD Forward Sell",
            "notional_usd": 110_500,
            "forward_rate": 84.1,
            "maturity": "2026-06-30",
            "unrealised_pnl": 66_300,
            "status": "ACTIVE",
        },
    ]

    total_exposure_inr = sum(e["inr_equivalent"] for e in exposures)
    hedged_value = sum(h["notional_usd"] * 83.5 for h in hedges)
    hedge_ratio = (
        round(hedged_value / total_exposure_inr * 100, 1) if total_exposure_inr else 0
    )

    return {
        "entity_id": str(entity_id),
        "as_of": str(date.today()),
        "exposures": exposures,
        "active_hedges": hedges,
        "summary": {
            "total_exposure_inr": total_exposure_inr,
            "hedged_value_inr": round(hedged_value, 0),
            "unhedged_value_inr": round(total_exposure_inr - hedged_value, 0),
            "hedge_ratio_pct": hedge_ratio,
            "policy_min_hedge_pct": 50.0,
            "policy_compliant": hedge_ratio >= 50.0,
        },
    }


@router.get("/lcr")
async def get_liquidity_coverage_ratio(
    entity_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Liquidity Coverage Ratio (LCR) per Basel III framework.
    LCR = HQLA / Net Cash Outflows (30-day stress) >= 100%
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    hqla = {
        "level_1_cash": 12_500_000,
        "level_1_government_securities": 8_000_000,
        "level_2a_corporate_bonds": 3_000_000,
        "total_hqla": 23_500_000,
    }

    outflows_30d = {
        "retail_deposits_run_off": 1_200_000,
        "unsecured_wholesale_run_off": 4_000_000,
        "committed_facilities_drawdown": 2_500_000,
        "total_outflows": 7_700_000,
    }

    inflows_30d = {
        "trade_receivables": 2_800_000,
        "maturing_placements": 1_000_000,
        "total_inflows": 3_800_000,
    }

    net_outflows = max(
        outflows_30d["total_outflows"]
        - min(inflows_30d["total_inflows"], 0.75 * outflows_30d["total_outflows"]),
        0,
    )
    lcr = (
        round(hqla["total_hqla"] / net_outflows * 100, 2)
        if net_outflows
        else float("inf")
    )

    return {
        "entity_id": str(entity_id),
        "as_of": str(date.today()),
        "hqla": hqla,
        "outflows_30d": outflows_30d,
        "inflows_30d": inflows_30d,
        "net_cash_outflows_30d": round(net_outflows, 0),
        "lcr_pct": lcr,
        "regulatory_minimum_pct": 100.0,
        "compliant": lcr >= 100.0,
        "buffer_above_minimum": round(lcr - 100.0, 2),
    }


@router.get("/nsfr")
async def get_net_stable_funding_ratio(
    entity_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Net Stable Funding Ratio (NSFR) per Basel III.
    NSFR = Available Stable Funding / Required Stable Funding >= 100%
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    asf = {
        "tier_1_capital": 10_000_000,
        "stable_retail_deposits": 8_000_000,
        "less_stable_retail": 4_000_000,
        "wholesale_funding_gt_1yr": 6_000_000,
        "total_asf": 28_000_000,
    }

    rsf = {
        "unencumbered_loans_gt_1yr": 15_000_000,
        "hqla_unencumbered": 2_000_000,
        "off_balance_sheet": 1_500_000,
        "other_assets": 3_000_000,
        "total_rsf": 21_500_000,
    }

    nsfr = (
        round(asf["total_asf"] / rsf["total_rsf"] * 100, 2)
        if rsf["total_rsf"]
        else float("inf")
    )

    return {
        "entity_id": str(entity_id),
        "as_of": str(date.today()),
        "available_stable_funding": asf,
        "required_stable_funding": rsf,
        "nsfr_pct": nsfr,
        "regulatory_minimum_pct": 100.0,
        "compliant": nsfr >= 100.0,
        "surplus_stable_funding": asf["total_asf"] - rsf["total_rsf"],
    }
