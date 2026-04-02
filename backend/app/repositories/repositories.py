# SPOORTHY QUANTUM OS — Repository Pattern
# Full CRUD repositories with async support, filtering, pagination

from datetime import date, datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.models import (AuditLog, BankTransaction, ChartOfAccount,
                             Employee, Entity, FixedAsset, GSTReturn,
                             Inventory, Invoice, JournalEntry, JournalLine,
                             Loan, PayrollRun, Portfolio, QuantumJob)

T = TypeVar("T")

# Mapping from model class to its primary-key column attribute name.
# Each model in models.py uses a different PK name rather than a generic "id".
_MODEL_PK: Dict[str, str] = {
    "Entity": "entity_id",
    "ChartOfAccount": "account_code",
    "JournalEntry": "entry_id",
    "JournalLine": "line_id",
    "BankTransaction": "txn_id",
    "Invoice": "invoice_id",
    "FixedAsset": "asset_id",
    "Inventory": "sku",
    "Employee": "employee_id",
    "PayrollRun": "run_id",
    "Loan": "loan_id",
    "Portfolio": "portfolio_id",
    "AuditLog": "log_id",
    "QuantumJob": "job_id",
    "GSTReturn": "return_id",
}


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
        pk_name = _MODEL_PK.get(model.__name__)
        if pk_name is None:
            raise ValueError(f"No PK mapping defined for model {model.__name__}")
        self._pk_col = getattr(model, pk_name)

    async def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).where(self._pk_col == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        query = select(self.model)
        if filters:
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        await self.session.execute(
            update(self.model).where(self._pk_col == id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self._pk_col == id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            conditions = [getattr(self.model, k) == v for k, v in filters.items()]
            query = query.where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar()


class EntityRepository(BaseRepository[Entity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Entity)

    async def get_by_gstin(self, gstin: str) -> Optional[Entity]:
        result = await self.session.execute(select(Entity).where(Entity.gstin == gstin))
        return result.scalar_one_or_none()

    async def get_by_pan(self, pan: str) -> Optional[Entity]:
        result = await self.session.execute(select(Entity).where(Entity.pan == pan))
        return result.scalar_one_or_none()

    async def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Entity]:
        search_filter = f"%{query}%"
        result = await self.session.execute(
            select(Entity)
            .where(
                or_(
                    Entity.name.ilike(search_filter),
                    Entity.gstin.ilike(search_filter),
                    Entity.pan.ilike(search_filter),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class ChartOfAccountsRepository(BaseRepository[ChartOfAccount]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChartOfAccount)

    async def get_by_entity(
        self, entity_id: UUID, active_only: bool = True
    ) -> List[ChartOfAccount]:
        query = select(ChartOfAccount).where(ChartOfAccount.entity_id == entity_id)
        if active_only:
            query = query.where(ChartOfAccount.is_active == True)
        query = query.order_by(ChartOfAccount.account_code)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_hierarchy(self, entity_id: UUID) -> List[ChartOfAccount]:
        result = await self.session.execute(
            select(ChartOfAccount)
            .where(ChartOfAccount.entity_id == entity_id)
            .order_by(ChartOfAccount.level, ChartOfAccount.account_code)
        )
        return result.scalars().all()


class JournalEntryRepository(BaseRepository[JournalEntry]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JournalEntry)

    async def get_by_entity_period(
        self, entity_id: UUID, period: str
    ) -> List[JournalEntry]:
        result = await self.session.execute(
            select(JournalEntry)
            .where(
                and_(JournalEntry.entity_id == entity_id, JournalEntry.period == period)
            )
            .order_by(desc(JournalEntry.entry_date))
        )
        return result.scalars().all()

    async def get_with_lines(self, entry_id: UUID) -> Optional[JournalEntry]:
        result = await self.session.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.journal_lines))
            .where(JournalEntry.entry_id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_unreconciled_bank_txns(
        self, entity_id: UUID
    ) -> List[BankTransaction]:
        result = await self.session.execute(
            select(BankTransaction)
            .where(
                and_(
                    BankTransaction.entity_id == entity_id,
                    BankTransaction.reconciled == False,
                )
            )
            .order_by(desc(BankTransaction.txn_date))
        )
        return result.scalars().all()


class BankTransactionRepository(BaseRepository[BankTransaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BankTransaction)

    async def get_by_entity_date_range(
        self, entity_id: UUID, start_date: date, end_date: date
    ) -> List[BankTransaction]:
        result = await self.session.execute(
            select(BankTransaction)
            .where(
                and_(
                    BankTransaction.entity_id == entity_id,
                    BankTransaction.txn_date.between(start_date, end_date),
                )
            )
            .order_by(BankTransaction.txn_date)
        )
        return result.scalars().all()

    async def reconcile(self, txn_id: UUID, entry_id: UUID) -> bool:
        result = await self.session.execute(
            update(BankTransaction)
            .where(BankTransaction.txn_id == txn_id)
            .values(reconciled=True, reconciled_entry_id=entry_id)
        )
        await self.session.commit()
        return result.rowcount > 0


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Invoice)

    async def get_by_entity_period(
        self, entity_id: UUID, start_date: date, end_date: date
    ) -> List[Invoice]:
        result = await self.session.execute(
            select(Invoice)
            .where(
                and_(
                    Invoice.entity_id == entity_id,
                    Invoice.invoice_date.between(start_date, end_date),
                )
            )
            .order_by(desc(Invoice.invoice_date))
        )
        return result.scalars().all()

    async def get_by_gstin(self, gstin: str) -> List[Invoice]:
        result = await self.session.execute(
            select(Invoice)
            .where(Invoice.buyer_gstin == gstin)
            .order_by(desc(Invoice.invoice_date))
        )
        return result.scalars().all()


class FixedAssetRepository(BaseRepository[FixedAsset]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FixedAsset)

    async def get_active_by_entity(self, entity_id: UUID) -> List[FixedAsset]:
        result = await self.session.execute(
            select(FixedAsset)
            .where(
                and_(FixedAsset.entity_id == entity_id, FixedAsset.status == "ACTIVE")
            )
            .order_by(FixedAsset.asset_code)
        )
        return result.scalars().all()

    async def update_depreciation(
        self, asset_id: UUID, accumulated_depr: float, nbv: float
    ) -> bool:
        result = await self.session.execute(
            update(FixedAsset)
            .where(FixedAsset.asset_id == asset_id)
            .values(accumulated_depreciation=accumulated_depr, nbv=nbv)
        )
        await self.session.commit()
        return result.rowcount > 0


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Inventory)

    async def get_by_entity(self, entity_id: UUID) -> List[Inventory]:
        result = await self.session.execute(
            select(Inventory)
            .where(Inventory.entity_id == entity_id)
            .order_by(Inventory.sku)
        )
        return result.scalars().all()

    async def update_qty(self, sku: str, qty_change: float) -> bool:
        # Get current qty
        result = await self.session.execute(
            select(Inventory.qty_on_hand, Inventory.unit_cost).where(
                Inventory.sku == sku
            )
        )
        current = result.first()
        if not current:
            return False

        new_qty = current.qty_on_hand + qty_change
        new_value = new_qty * current.unit_cost if current.unit_cost else 0

        update_result = await self.session.execute(
            update(Inventory)
            .where(Inventory.sku == sku)
            .values(qty_on_hand=new_qty, total_value=new_value, last_updated=func.now())
        )
        await self.session.commit()
        return update_result.rowcount > 0


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Employee)

    async def get_active_by_entity(self, entity_id: UUID) -> List[Employee]:
        result = await self.session.execute(
            select(Employee)
            .where(and_(Employee.entity_id == entity_id, Employee.status == "ACTIVE"))
            .order_by(Employee.name)
        )
        return result.scalars().all()


class PayrollRunRepository(BaseRepository[PayrollRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PayrollRun)

    async def get_by_entity_period(
        self, entity_id: UUID, period: str
    ) -> Optional[PayrollRun]:
        result = await self.session.execute(
            select(PayrollRun).where(
                and_(PayrollRun.entity_id == entity_id, PayrollRun.period == period)
            )
        )
        return result.scalar_one_or_none()


class LoanRepository(BaseRepository[Loan]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Loan)

    async def get_active_by_entity(self, entity_id: UUID) -> List[Loan]:
        result = await self.session.execute(
            select(Loan)
            .where(and_(Loan.entity_id == entity_id, Loan.status == "ACTIVE"))
            .order_by(Loan.disbursement_date)
        )
        return result.scalars().all()


class PortfolioRepository(BaseRepository[Portfolio]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Portfolio)

    async def get_by_entity(self, entity_id: UUID) -> List[Portfolio]:
        result = await self.session.execute(
            select(Portfolio)
            .where(Portfolio.entity_id == entity_id)
            .order_by(Portfolio.name)
        )
        return result.scalars().all()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)

    async def get_by_entity_date_range(
        self, entity_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.entity_id == entity_id,
                    AuditLog.timestamp.between(start_date, end_date),
                )
            )
            .order_by(desc(AuditLog.timestamp))
        )
        return result.scalars().all()


class QuantumJobRepository(BaseRepository[QuantumJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QuantumJob)

    async def get_by_entity_module(
        self, entity_id: UUID, module: str
    ) -> List[QuantumJob]:
        result = await self.session.execute(
            select(QuantumJob)
            .where(and_(QuantumJob.entity_id == entity_id, QuantumJob.module == module))
            .order_by(desc(QuantumJob.submitted_at))
        )
        return result.scalars().all()

    async def get_recent_jobs(
        self, entity_id: UUID, limit: int = 10
    ) -> List[QuantumJob]:
        result = await self.session.execute(
            select(QuantumJob)
            .where(QuantumJob.entity_id == entity_id)
            .order_by(desc(QuantumJob.submitted_at))
            .limit(limit)
        )
        return result.scalars().all()


class GSTReturnRepository(BaseRepository[GSTReturn]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, GSTReturn)

    async def get_by_entity_period(
        self, entity_id: UUID, period: str
    ) -> List[GSTReturn]:
        result = await self.session.execute(
            select(GSTReturn)
            .where(and_(GSTReturn.entity_id == entity_id, GSTReturn.period == period))
            .order_by(GSTReturn.return_type)
        )
        return result.scalars().all()

    async def get_filed_returns(
        self, entity_id: UUID, return_type: str
    ) -> List[GSTReturn]:
        result = await self.session.execute(
            select(GSTReturn)
            .where(
                and_(
                    GSTReturn.entity_id == entity_id,
                    GSTReturn.return_type == return_type,
                    GSTReturn.status == "FILED",
                )
            )
            .order_by(desc(GSTReturn.filed_at))
        )
        return result.scalars().all()
