# SPOORTHY QUANTUM OS — Chart of Accounts API
# CRUD operations for chart of accounts

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from ....db.session import get_db
from ....repositories.repositories import ChartOfAccountsRepository
from ....models.models import ChartOfAccount

router = APIRouter()

@router.get("/{entity_id}", response_model=List[dict])
async def get_chart_of_accounts(
    entity_id: UUID,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """Get chart of accounts for entity"""
    repo = ChartOfAccountsRepository(db)
    accounts = await repo.get_by_entity(entity_id, active_only)
    return [{"account_code": acc.account_code, "account_name": acc.account_name,
             "account_type": acc.account_type, "level": acc.level} for acc in accounts]

@router.get("/{entity_id}/hierarchy")
async def get_accounts_hierarchy(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get hierarchical chart of accounts"""
    repo = ChartOfAccountsRepository(db)
    accounts = await repo.get_hierarchy(entity_id)
    return [{"account_code": acc.account_code, "account_name": acc.account_name,
             "parent_code": acc.parent_code, "level": acc.level} for acc in accounts]