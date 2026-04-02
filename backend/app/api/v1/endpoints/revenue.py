# SPOORTHY QUANTUM OS — Revenue Recognition API (IFRS 15 / Ind AS 115)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal

from ....db.session import get_db
from ....models.models import Entity

router = APIRouter()

# ── In-memory store for demo (replace with DB table in production) ──
_contracts: Dict[str, Dict] = {}


def _get_contract_or_404(contract_id: str) -> Dict:
    c = _contracts.get(contract_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Revenue contract {contract_id} not found")
    return c


@router.post("/contracts", status_code=201)
async def create_revenue_contract(
    entity_id: UUID,
    customer_name: str,
    contract_date: date,
    total_contract_value: float,
    performance_obligations: List[str],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new revenue contract per IFRS 15 Step 1: Identify the contract.
    """
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    contract_id = str(uuid4())
    total = float(total_contract_value)
    # Allocate transaction price proportionally (equal weight by default — Step 4)
    n_obs = len(performance_obligations)
    per_ob = round(total / n_obs, 2) if n_obs else total
    remaining = total - per_ob * (n_obs - 1) if n_obs else total

    obligations = []
    for i, desc in enumerate(performance_obligations):
        ob_id = str(uuid4())
        allocated = remaining if i == n_obs - 1 else per_ob
        obligations.append({
            "ob_id": ob_id,
            "description": desc,
            "allocated_price": allocated,
            "recognised": 0.0,
            "status": "PENDING",
            "recognition_method": "point_in_time",
        })

    contract = {
        "contract_id": contract_id,
        "entity_id": str(entity_id),
        "customer_name": customer_name,
        "contract_date": str(contract_date),
        "total_contract_value": total,
        "unearned_revenue": total,
        "recognised_revenue": 0.0,
        "performance_obligations": obligations,
        "status": "ACTIVE",
        "created_at": datetime.utcnow().isoformat(),
    }
    _contracts[contract_id] = contract
    return contract


@router.post("/contracts/{contract_id}/allocate")
async def allocate_transaction_price(
    contract_id: str,
    allocations: Dict[str, float],  # {ob_id: standalone_selling_price}
    db: AsyncSession = Depends(get_db)
):
    """
    IFRS 15 Step 4: Allocate the transaction price to performance obligations
    based on relative standalone selling prices.
    """
    contract = _get_contract_or_404(contract_id)
    total_ssp = sum(allocations.values())
    if total_ssp <= 0:
        raise HTTPException(status_code=400, detail="Total SSP must be > 0")

    total_value = contract["total_contract_value"]
    ob_map = {ob["ob_id"]: ob for ob in contract["performance_obligations"]}

    for ob_id, ssp in allocations.items():
        if ob_id not in ob_map:
            raise HTTPException(status_code=400, detail=f"ob_id {ob_id} not found in contract")
        ob_map[ob_id]["allocated_price"] = round(total_value * (ssp / total_ssp), 2)

    contract["performance_obligations"] = list(ob_map.values())
    _contracts[contract_id] = contract
    return {"contract_id": contract_id, "reallocated": True, "obligations": contract["performance_obligations"]}


@router.post("/contracts/{contract_id}/recognise")
async def recognise_revenue(
    contract_id: str,
    ob_id: str,
    amount: float,
    recognition_date: date,
    method: str = "point_in_time",  # or "over_time"
    percentage_complete: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    IFRS 15 Step 5: Recognise revenue when (or as) a performance obligation is satisfied.
    """
    contract = _get_contract_or_404(contract_id)
    ob = next((o for o in contract["performance_obligations"] if o["ob_id"] == ob_id), None)
    if not ob:
        raise HTTPException(status_code=404, detail="Performance obligation not found")

    allocated = ob["allocated_price"]
    already_recognised = ob["recognised"]

    if method == "over_time":
        if percentage_complete is None:
            raise HTTPException(status_code=400, detail="percentage_complete required for over_time method")
        pct = min(max(percentage_complete, 0.0), 100.0) / 100.0
        recognisable = round(allocated * pct - already_recognised, 2)
    else:  # point_in_time
        recognisable = round(min(amount, allocated - already_recognised), 2)

    if recognisable < 0:
        raise HTTPException(status_code=400, detail="No additional revenue to recognise")

    ob["recognised"] = round(already_recognised + recognisable, 2)
    ob["status"] = "FULLY_RECOGNISED" if ob["recognised"] >= allocated - 0.01 else "PARTIALLY_RECOGNISED"
    ob["recognition_method"] = method

    contract["recognised_revenue"] = round(
        sum(o["recognised"] for o in contract["performance_obligations"]), 2
    )
    contract["unearned_revenue"] = round(
        contract["total_contract_value"] - contract["recognised_revenue"], 2
    )
    if contract["unearned_revenue"] <= 0.01:
        contract["status"] = "FULLY_RECOGNISED"

    _contracts[contract_id] = contract
    return {
        "contract_id": contract_id,
        "ob_id": ob_id,
        "recognised_now": recognisable,
        "total_recognised": ob["recognised"],
        "contract_recognised_revenue": contract["recognised_revenue"],
        "contract_unearned_revenue": contract["unearned_revenue"],
        "recognition_date": str(recognition_date),
    }


@router.get("/contracts/{contract_id}/schedule")
async def get_recognition_schedule(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Return the revenue recognition schedule for a contract.
    """
    contract = _get_contract_or_404(contract_id)
    schedule = []
    for ob in contract["performance_obligations"]:
        allocated = ob["allocated_price"]
        recognised = ob["recognised"]
        remaining = round(allocated - recognised, 2)
        schedule.append({
            "ob_id": ob["ob_id"],
            "description": ob["description"],
            "allocated_price": allocated,
            "recognised_to_date": recognised,
            "remaining_to_recognise": remaining,
            "completion_pct": round(recognised / allocated * 100, 1) if allocated else 0,
            "status": ob["status"],
            "method": ob["recognition_method"],
        })
    return {
        "contract_id": contract_id,
        "customer_name": contract["customer_name"],
        "total_value": contract["total_contract_value"],
        "total_recognised": contract["recognised_revenue"],
        "total_unearned": contract["unearned_revenue"],
        "contract_status": contract["status"],
        "obligations": schedule,
    }


@router.post("/contracts/{contract_id}/modify")
async def modify_contract(
    contract_id: str,
    new_total_value: Optional[float] = None,
    add_obligations: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    IFRS 15 contract modification — prospective or cumulative catch-up.
    """
    contract = _get_contract_or_404(contract_id)

    changes = []
    if new_total_value is not None and new_total_value != contract["total_contract_value"]:
        old_value = contract["total_contract_value"]
        delta = new_total_value - old_value
        contract["total_contract_value"] = new_total_value
        contract["unearned_revenue"] = round(contract["unearned_revenue"] + delta, 2)
        changes.append(f"Contract value changed from {old_value} to {new_total_value} (delta {delta:+.2f})")

    if add_obligations:
        for desc in add_obligations:
            ob_id = str(uuid4())
            contract["performance_obligations"].append({
                "ob_id": ob_id,
                "description": desc,
                "allocated_price": 0.0,
                "recognised": 0.0,
                "status": "PENDING",
                "recognition_method": "point_in_time",
            })
            changes.append(f"Added performance obligation: {desc} (ob_id={ob_id})")

    contract["modified_at"] = datetime.utcnow().isoformat()
    _contracts[contract_id] = contract

    return {
        "contract_id": contract_id,
        "changes_applied": changes,
        "contract": contract,
    }


@router.get("/contracts/{contract_id}/disclosure")
async def get_ifrs15_disclosure(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate IFRS 15 disclosure note for financial statements.
    """
    contract = _get_contract_or_404(contract_id)
    fully = sum(1 for o in contract["performance_obligations"] if o["status"] == "FULLY_RECOGNISED")
    partial = sum(1 for o in contract["performance_obligations"] if o["status"] == "PARTIALLY_RECOGNISED")
    pending = sum(1 for o in contract["performance_obligations"] if o["status"] == "PENDING")

    return {
        "contract_id": contract_id,
        "disclosure": {
            "ifrs_standard": "IFRS 15 / Ind AS 115",
            "customer": contract["customer_name"],
            "contract_date": contract["contract_date"],
            "total_transaction_price": contract["total_contract_value"],
            "revenue_recognised_to_date": contract["recognised_revenue"],
            "remaining_performance_obligations": contract["unearned_revenue"],
            "obligation_summary": {
                "total": len(contract["performance_obligations"]),
                "fully_recognised": fully,
                "partially_recognised": partial,
                "pending": pending,
            },
            "significant_judgements": [
                "Transaction price allocated using relative standalone selling prices",
                "Variable consideration constrained to amounts highly probable of not reversing",
                "Contract modifications assessed prospectively",
            ],
            "disaggregation_of_revenue": {
                "point_in_time": sum(
                    o["recognised"] for o in contract["performance_obligations"]
                    if o["recognition_method"] == "point_in_time"
                ),
                "over_time": sum(
                    o["recognised"] for o in contract["performance_obligations"]
                    if o["recognition_method"] == "over_time"
                ),
            },
        }
    }
