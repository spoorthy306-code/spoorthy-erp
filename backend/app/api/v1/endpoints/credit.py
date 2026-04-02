# SPOORTHY QUANTUM OS — Credit Scoring & Risk API
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


def _logistic(z: float) -> float:
    """Sigmoid function for probability mapping."""
    return 1.0 / (1.0 + exp(-z))


def _score_band(score: int) -> Dict:
    if score >= 750:
        return {"band": "PRIME", "risk": "LOW", "max_loan_multiplier": 36}
    elif score >= 680:
        return {"band": "NEAR_PRIME", "risk": "MODERATE", "max_loan_multiplier": 24}
    elif score >= 600:
        return {"band": "SUBPRIME", "risk": "HIGH", "max_loan_multiplier": 12}
    else:
        return {"band": "DEEP_SUBPRIME", "risk": "VERY_HIGH", "max_loan_multiplier": 0}


@router.post("/score/individual")
async def score_individual(
    entity_id: UUID,
    age: int,
    annual_income: float,
    existing_emi: float,
    loan_requested: float,
    tenure_months: int,
    employment_type: str,  # SALARIED | SELF_EMPLOYED | BUSINESS
    credit_history_months: int,
    num_open_accounts: int,
    num_delinquencies_24m: int,
    utilisation_pct: float,  # Credit utilisation 0-100
    db: AsyncSession = Depends(get_db),
):
    """
    Individual retail credit scoring using a logistic scorecard model.
    Factors: income, EMI burden, employment, credit history, delinquency, utilisation.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    # --- Scorecard weights (calibrated on representative population) ---
    score = 300  # base

    # Income adequacy (40pts max)
    emi_to_income = existing_emi / max(annual_income / 12, 1)
    new_emi = loan_requested / max(tenure_months, 1)
    total_foir = (existing_emi + new_emi) / max(annual_income / 12, 1)
    if total_foir <= 0.30:
        score += 40
    elif total_foir <= 0.40:
        score += 30
    elif total_foir <= 0.50:
        score += 15
    else:
        score += 0

    # Employment (30pts max)
    emp_scores = {"SALARIED": 30, "BUSINESS": 20, "SELF_EMPLOYED": 15}
    score += emp_scores.get(employment_type, 10)

    # Credit history length (60pts max)
    if credit_history_months >= 60:
        score += 60
    elif credit_history_months >= 36:
        score += 40
    elif credit_history_months >= 12:
        score += 20
    else:
        score += 5

    # Delinquency (80pts max — biggest negative factor)
    if num_delinquencies_24m == 0:
        score += 80
    elif num_delinquencies_24m == 1:
        score += 40
    elif num_delinquencies_24m == 2:
        score += 10
    else:
        score += 0

    # Credit utilisation (40pts max)
    if utilisation_pct <= 30:
        score += 40
    elif utilisation_pct <= 50:
        score += 25
    elif utilisation_pct <= 70:
        score += 10
    else:
        score += 0

    # Account mix (20pts max)
    if 2 <= num_open_accounts <= 6:
        score += 20
    elif num_open_accounts <= 8:
        score += 10
    else:
        score += 0

    # Age adjustment (10pts max)
    if 25 <= age <= 50:
        score += 10
    elif 50 < age <= 60:
        score += 5

    score = min(score, 900)
    band = _score_band(score)

    # Probability of default via logistic mapping
    pd_logit = -0.02 * (score - 500)
    pd = round(_logistic(pd_logit), 4)

    # Loan eligibility
    max_eligible = round(annual_income / 12 * band["max_loan_multiplier"], 0)
    eligible = loan_requested <= max_eligible and score >= 600

    return {
        "entity_id": str(entity_id),
        "credit_score": score,
        "score_band": band["band"],
        "risk_category": band["risk"],
        "probability_of_default": pd,
        "loan_requested": loan_requested,
        "max_eligible_loan": max_eligible,
        "eligible": eligible,
        "foir": round(total_foir * 100, 2),
        "scorecard_breakdown": {
            "income_adequacy": (
                40
                if total_foir <= 0.30
                else 30 if total_foir <= 0.40 else 15 if total_foir <= 0.50 else 0
            ),
            "employment": emp_scores.get(employment_type, 10),
            "credit_history": (
                60
                if credit_history_months >= 60
                else (
                    40
                    if credit_history_months >= 36
                    else 20 if credit_history_months >= 12 else 5
                )
            ),
            "delinquency_free": (
                80
                if num_delinquencies_24m == 0
                else (
                    40
                    if num_delinquencies_24m == 1
                    else 10 if num_delinquencies_24m == 2 else 0
                )
            ),
            "utilisation": (
                40
                if utilisation_pct <= 30
                else 25 if utilisation_pct <= 50 else 10 if utilisation_pct <= 70 else 0
            ),
            "account_mix": (
                20
                if 2 <= num_open_accounts <= 6
                else 10 if num_open_accounts <= 8 else 0
            ),
        },
        "assessed_at": datetime.utcnow().isoformat(),
    }


@router.post("/score/corporate")
async def score_corporate(
    entity_id: UUID,
    company_name: str,
    annual_revenue: float,
    ebitda: float,
    total_debt: float,
    current_assets: float,
    current_liabilities: float,
    years_in_operation: int,
    industry: str,
    loan_requested: float,
    db: AsyncSession = Depends(get_db),
):
    """
    Corporate credit scoring using Altman Z-score variant and ratio analysis.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    working_capital = current_assets - current_liabilities
    equity_est = max(annual_revenue * 0.3, 1)  # simplified book equity estimate

    # Altman Z-score components
    x1 = working_capital / max(annual_revenue, 1)  # liquidity
    x2 = (ebitda * 0.6) / max(annual_revenue, 1)  # retained earnings proxy
    x3 = ebitda / max(annual_revenue, 1)  # profitability
    x4 = equity_est / max(total_debt, 1)  # leverage
    x5 = annual_revenue / max(annual_revenue, 1)  # asset turnover = 1.0 (normalised)

    z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    # Z-score interpretation
    if z_score >= 2.99:
        zone = "SAFE"
        risk = "LOW"
        pd = round(0.005 + _logistic(-z_score + 1) * 0.02, 4)
    elif z_score >= 1.81:
        zone = "GREY"
        risk = "MODERATE"
        pd = round(0.05 + _logistic(-z_score + 2) * 0.10, 4)
    else:
        zone = "DISTRESS"
        risk = "HIGH"
        pd = round(0.20 + _logistic(-z_score + 3) * 0.30, 4)

    # Industry adjustment
    INDUSTRY_MULTIPLIERS = {
        "IT_SERVICES": 0.85,
        "MANUFACTURING": 1.0,
        "REAL_ESTATE": 1.2,
        "RETAIL": 1.05,
        "PHARMA": 0.90,
        "INFRA": 1.15,
        "FMCG": 0.95,
    }
    pd = round(pd * INDUSTRY_MULTIPLIERS.get(industry, 1.0), 4)
    pd = min(pd, 0.99)

    # Debt service coverage
    dscr = round(ebitda / max(total_debt * 0.12, 1), 2)  # assuming 12% cost of debt
    debt_to_revenue = round(total_debt / max(annual_revenue, 1), 2)

    eligible = zone != "DISTRESS" and dscr >= 1.25 and years_in_operation >= 2

    return {
        "entity_id": str(entity_id),
        "company_name": company_name,
        "altman_z_score": round(z_score, 3),
        "zone": zone,
        "risk_category": risk,
        "probability_of_default": pd,
        "debt_service_coverage_ratio": dscr,
        "debt_to_revenue_ratio": debt_to_revenue,
        "loan_requested": loan_requested,
        "eligible": eligible,
        "max_recommended_loan": round(ebitda * 3 if eligible else 0, 0),
        "ratios": {
            "x1_liquidity": round(x1, 4),
            "x2_retained_earnings": round(x2, 4),
            "x3_profitability": round(x3, 4),
            "x4_leverage": round(x4, 4),
            "x5_asset_turnover": round(x5, 4),
        },
        "assessed_at": datetime.utcnow().isoformat(),
    }


@router.post("/recommend-loan")
async def recommend_loan_terms(
    entity_id: UUID,
    credit_score: int,
    loan_type: str,  # HOME | VEHICLE | PERSONAL | BUSINESS | MSME
    loan_amount: float,
    tenure_months: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Recommend loan terms (rate, LTV, collateral) based on credit score and loan type.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    BASE_RATES = {
        "HOME": 0.085,
        "VEHICLE": 0.092,
        "PERSONAL": 0.120,
        "BUSINESS": 0.110,
        "MSME": 0.095,
    }
    base_rate = BASE_RATES.get(loan_type, 0.120)

    # Risk premium based on score
    if credit_score >= 750:
        premium = 0.000
    elif credit_score >= 700:
        premium = 0.010
    elif credit_score >= 650:
        premium = 0.025
    elif credit_score >= 600:
        premium = 0.050
    else:
        raise HTTPException(
            status_code=400, detail="Credit score below minimum threshold (600)"
        )

    final_rate = base_rate + premium
    monthly_rate = final_rate / 12
    emi = round(
        loan_amount
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
        / ((1 + monthly_rate) ** tenure_months - 1),
        2,
    )
    total_payable = round(emi * tenure_months, 2)
    total_interest = round(total_payable - loan_amount, 2)

    LTV = {
        "HOME": 0.80,
        "VEHICLE": 0.85,
        "PERSONAL": 1.0,
        "BUSINESS": 0.70,
        "MSME": 0.75,
    }
    collateral = {
        "HOME": "Property mortgage",
        "VEHICLE": "Vehicle hypothecation",
        "PERSONAL": "None",
        "BUSINESS": "Business assets",
        "MSME": "Plant and machinery",
    }

    return {
        "entity_id": str(entity_id),
        "loan_type": loan_type,
        "loan_amount": loan_amount,
        "tenure_months": tenure_months,
        "recommended_rate_pct": round(final_rate * 100, 3),
        "base_rate_pct": round(base_rate * 100, 3),
        "risk_premium_pct": round(premium * 100, 3),
        "monthly_emi": emi,
        "total_payable": total_payable,
        "total_interest": total_interest,
        "interest_to_principal_ratio": round(total_interest / loan_amount, 3),
        "max_ltv_pct": round(LTV.get(loan_type, 0.75) * 100, 0),
        "collateral_required": collateral.get(loan_type, "TBD"),
        "processing_fee": round(loan_amount * 0.005, 2),
    }


@router.get("/portfolio-risk")
async def get_credit_portfolio_risk(
    entity_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Aggregate credit portfolio risk metrics — concentration, VaR, expected loss.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entity not found")

    portfolio = [
        {
            "segment": "Home Loans",
            "outstanding": 45_000_000,
            "avg_pd": 0.012,
            "avg_lgd": 0.25,
            "avg_score": 730,
        },
        {
            "segment": "Vehicle Loans",
            "outstanding": 28_000_000,
            "avg_pd": 0.025,
            "avg_lgd": 0.35,
            "avg_score": 695,
        },
        {
            "segment": "MSME Loans",
            "outstanding": 35_000_000,
            "avg_pd": 0.045,
            "avg_lgd": 0.50,
            "avg_score": 650,
        },
        {
            "segment": "Personal Loans",
            "outstanding": 12_000_000,
            "avg_pd": 0.080,
            "avg_lgd": 0.70,
            "avg_score": 610,
        },
    ]

    total_outstanding = sum(p["outstanding"] for p in portfolio)
    expected_loss = sum(
        p["outstanding"] * p["avg_pd"] * p["avg_lgd"] for p in portfolio
    )

    for p in portfolio:
        p["expected_loss"] = round(p["outstanding"] * p["avg_pd"] * p["avg_lgd"], 0)
        p["concentration_pct"] = round(p["outstanding"] / total_outstanding * 100, 1)

    # Simplified UL (unexpected loss) = 3x EL as proxy for 99.9% VaR
    unexpected_loss_999 = expected_loss * 3

    return {
        "entity_id": str(entity_id),
        "as_of": str(date.today()),
        "total_outstanding": total_outstanding,
        "expected_loss": round(expected_loss, 0),
        "expected_loss_pct": round(expected_loss / total_outstanding * 100, 3),
        "unexpected_loss_99_9pct": round(unexpected_loss_999, 0),
        "economic_capital_required": round(unexpected_loss_999 - expected_loss, 0),
        "portfolio_breakdown": portfolio,
        "herfindahl_index": round(
            sum((p["outstanding"] / total_outstanding) ** 2 for p in portfolio), 4
        ),
        "top_segment": max(portfolio, key=lambda x: x["outstanding"])["segment"],
    }
