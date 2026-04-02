# SPOORTHY QUANTUM OS — SQLAlchemy Models + Pydantic Schemas
# Full ORM with relationships, Pydantic v2 schemas, validators

from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, Boolean, ForeignKey, DECIMAL, JSON, UUID, func, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

from sqlalchemy import types, JSON
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB

class JSONB(types.TypeDecorator):
    """JSONB on PostgreSQL, JSON on SQLite for tests."""
    impl = JSON
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(JSON())



# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# Entities
class Entity(Base):
    __tablename__ = 'entities'

    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), unique=True)
    pan: Mapped[Optional[str]] = mapped_column(String(10), unique=True)
    tan: Mapped[Optional[str]] = mapped_column(String(10))
    address: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    currency: Mapped[str] = mapped_column(String(3), default='INR')
    reporting_currency: Mapped[str] = mapped_column(String(3), default='INR')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    journal_entries: Mapped[List["JournalEntry"]] = relationship(back_populates="entity")
    chart_of_accounts: Mapped[List["ChartOfAccount"]] = relationship(back_populates="entity")
    bank_transactions: Mapped[List["BankTransaction"]] = relationship(back_populates="entity")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="entity")
    fixed_assets: Mapped[List["FixedAsset"]] = relationship(back_populates="entity")
    inventory: Mapped[List["Inventory"]] = relationship(back_populates="entity")
    employees: Mapped[List["Employee"]] = relationship(back_populates="entity")
    payroll_runs: Mapped[List["PayrollRun"]] = relationship(back_populates="entity")
    loans: Mapped[List["Loan"]] = relationship(back_populates="entity")
    portfolios: Mapped[List["Portfolio"]] = relationship(back_populates="entity")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="entity")
    quantum_jobs: Mapped[List["QuantumJob"]] = relationship(back_populates="entity")
    gst_returns: Mapped[List["GSTReturn"]] = relationship(back_populates="entity")

# Chart of Accounts
class ChartOfAccount(Base):
    __tablename__ = 'chart_of_accounts'

    account_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[Optional[str]] = mapped_column(String(50))
    parent_code: Mapped[Optional[str]] = mapped_column(String(20))
    level: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="chart_of_accounts")
    journal_lines: Mapped[List["JournalLine"]] = relationship(back_populates="account")

# Journal Entries
class JournalEntry(Base):
    __tablename__ = 'journal_entries'

    entry_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    narration: Mapped[Optional[str]] = mapped_column(Text)
    total_debit: Mapped[float] = mapped_column(DECIMAL(15,2), default=0)
    total_credit: Mapped[float] = mapped_column(DECIMAL(15,2), default=0)
    posted_by: Mapped[Optional[str]] = mapped_column(String(100))
    pqc_signature: Mapped[Optional[str]] = mapped_column(Text)
    quantum_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="journal_entries")
    journal_lines: Mapped[List["JournalLine"]] = relationship(back_populates="entry")
    bank_transactions: Mapped[List["BankTransaction"]] = relationship(back_populates="reconciled_entry")

# Journal Lines
class JournalLine(Base):
    __tablename__ = 'journal_lines'

    line_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('journal_entries.entry_id'))
    account_code: Mapped[str] = mapped_column(String(20), ForeignKey('chart_of_accounts.account_code'))
    debit: Mapped[float] = mapped_column(DECIMAL(15,2), default=0)
    credit: Mapped[float] = mapped_column(DECIMAL(15,2), default=0)
    description: Mapped[Optional[str]] = mapped_column(Text)

    entry: Mapped["JournalEntry"] = relationship(back_populates="journal_lines")
    account: Mapped["ChartOfAccount"] = relationship(back_populates="journal_lines")

# Bank Transactions
class BankTransaction(Base):
    __tablename__ = 'bank_transactions'

    txn_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    bank_account: Mapped[Optional[str]] = mapped_column(String(50))
    txn_date: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    balance: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    reconciled_entry_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey('journal_entries.entry_id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="bank_transactions")
    reconciled_entry: Mapped[Optional["JournalEntry"]] = relationship(back_populates="bank_transactions")

# Invoices
class Invoice(Base):
    __tablename__ = 'invoices'

    invoice_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    invoice_no: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    buyer_gstin: Mapped[Optional[str]] = mapped_column(String(15))
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255))
    total_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    tax_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    irn: Mapped[Optional[str]] = mapped_column(Text)
    qr_code: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="invoices")

# Fixed Assets
class FixedAsset(Base):
    __tablename__ = 'fixed_assets'

    asset_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    asset_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    cost: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    accumulated_depreciation: Mapped[float] = mapped_column(DECIMAL(15,2), default=0)
    nbv: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    depreciation_method: Mapped[Optional[str]] = mapped_column(String(10))
    useful_life_years: Mapped[Optional[int]] = mapped_column(Integer)
    residual_value: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="fixed_assets")

# Inventory
class Inventory(Base):
    __tablename__ = 'inventory'

    sku: Mapped[str] = mapped_column(String(50), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    qty_on_hand: Mapped[Optional[float]] = mapped_column(DECIMAL(10,2))
    unit_cost: Mapped[Optional[float]] = mapped_column(DECIMAL(10,2))
    total_value: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    costing_method: Mapped[str] = mapped_column(String(20), default='FIFO')
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="inventory")

# Employees
class Employee(Base):
    __tablename__ = 'employees'
    __table_args__ = {'extend_existing': True}

    employee_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    pan: Mapped[Optional[str]] = mapped_column(String(10))
    uan: Mapped[Optional[str]] = mapped_column(String(12))
    basic_salary: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    hra: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    lta: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    medical: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    nps: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    pf_employee: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    joined_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')

    entity: Mapped["Entity"] = relationship(back_populates="employees")

# Payroll Runs
class PayrollRun(Base):
    __tablename__ = 'payroll_runs'

    run_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    period: Mapped[Optional[str]] = mapped_column(String(7))
    total_gross: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    total_deductions: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    total_net: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    pf_employer: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    esic_employer: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    pt: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    tds: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="payroll_runs")

# Loans
class Loan(Base):
    __tablename__ = 'loans'

    loan_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    facility_type: Mapped[Optional[str]] = mapped_column(String(50))
    bank: Mapped[Optional[str]] = mapped_column(String(100))
    sanctioned_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    outstanding: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    rate_pct: Mapped[Optional[float]] = mapped_column(DECIMAL(5,2))
    emi: Mapped[Optional[float]] = mapped_column(DECIMAL(12,2))
    tenure_months: Mapped[Optional[int]] = mapped_column(Integer)
    disbursement_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')

    entity: Mapped["Entity"] = relationship(back_populates="loans")

# Portfolios
class Portfolio(Base):
    __tablename__ = 'portfolios'

    portfolio_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    total_value: Mapped[Optional[float]] = mapped_column(DECIMAL(15,2))
    holdings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="portfolios")

# Audit Log
class AuditLog(Base):
    __tablename__ = 'audit_log'

    log_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    user_id: Mapped[Optional[str]] = mapped_column(String(100))
    action: Mapped[Optional[str]] = mapped_column(String(100))
    table_name: Mapped[Optional[str]] = mapped_column(String(50))
    record_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True))
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    entity: Mapped["Entity"] = relationship(back_populates="audit_logs")

# Quantum Jobs
class QuantumJob(Base):
    __tablename__ = 'quantum_jobs'

    job_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    module: Mapped[Optional[str]] = mapped_column(String(50))
    solver: Mapped[Optional[str]] = mapped_column(String(50))
    qubo_size: Mapped[Optional[int]] = mapped_column(Integer)
    energy: Mapped[Optional[float]] = mapped_column(DECIMAL(10,4))
    solve_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default='COMPLETED')
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="quantum_jobs")

# GST Returns
class GSTReturn(Base):
    __tablename__ = 'gst_returns'

    return_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('entities.entity_id'))
    return_type: Mapped[Optional[str]] = mapped_column(String(10))
    period: Mapped[Optional[str]] = mapped_column(String(7))
    json_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default='FILED')
    arn: Mapped[Optional[str]] = mapped_column(String(50))
    filed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="gst_returns")

# Pydantic Schemas
class EntitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    currency: str = 'INR'
    reporting_currency: str = 'INR'
    created_at: datetime
    updated_at: datetime

class EntityCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    gstin: Optional[str] = Field(None, pattern=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    pan: Optional[str] = Field(None, pattern=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    tan: Optional[str] = Field(None, pattern=r'^[A-Z]{4}[0-9]{5}[A-Z]{1}$')
    address: Optional[Dict[str, Any]] = None
    currency: str = 'INR'
    reporting_currency: str = 'INR'

class JournalEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_id: uuid.UUID
    entity_id: uuid.UUID
    entry_date: date
    period: str
    narration: Optional[str] = None
    total_debit: float
    total_credit: float
    posted_by: Optional[str] = None
    pqc_signature: Optional[str] = None
    quantum_job_id: Optional[uuid.UUID] = None
    created_at: datetime

class JournalEntryCreateSchema(BaseModel):
    entity_id: uuid.UUID
    entry_date: date
    narration: Optional[str] = None
    lines: List[Dict[str, Any]] = Field(..., min_length=1)

    @field_validator('lines')
    @classmethod
    def validate_lines(cls, v):
        total_debit = sum(line.get('debit', 0) for line in v)
        total_credit = sum(line.get('credit', 0) for line in v)
        if abs(total_debit - total_credit) > 0.01:
            raise ValueError('Debits must equal credits')
        return v

class InvoiceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice_id: uuid.UUID
    entity_id: uuid.UUID
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    buyer_gstin: Optional[str] = None
    buyer_name: Optional[str] = None
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    irn: Optional[str] = None
    qr_code: Optional[str] = None
    status: str = 'ACTIVE'
    created_at: datetime

class InvoiceCreateSchema(BaseModel):
    entity_id: uuid.UUID
    invoice_no: str
    invoice_date: date
    buyer_gstin: Optional[str] = None
    buyer_name: str
    total_amount: float = Field(..., gt=0)
    tax_amount: float = Field(..., ge=0)
    irn: Optional[str] = None
    qr_code: Optional[str] = None

class QuantumJobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    entity_id: uuid.UUID
    module: Optional[str] = None
    solver: Optional[str] = None
    qubo_size: Optional[int] = None
    energy: Optional[float] = None
    solve_time_ms: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    status: str = 'COMPLETED'
    submitted_at: datetime
    completed_at: datetime

class GSTReturnSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    return_id: uuid.UUID
    entity_id: uuid.UUID
    return_type: Optional[str] = None
    period: Optional[str] = None
    json_payload: Optional[Dict[str, Any]] = None
    status: str = 'FILED'
    arn: Optional[str] = None
    filed_at: datetime

class GSTReturnCreateSchema(BaseModel):
    entity_id: uuid.UUID
    return_type: str = Field(..., pattern=r'^GSTR[0-9]+[A-Z]?$')
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    json_payload: Optional[Dict[str, Any]] = None

class BankTransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    txn_id: uuid.UUID
    entity_id: uuid.UUID
    bank_account: Optional[str] = None
    txn_date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    balance: Optional[float] = None
    reconciled: bool = False
    reconciled_entry_id: Optional[uuid.UUID] = None
    created_at: datetime

class BankTransactionCreateSchema(BaseModel):
    entity_id: uuid.UUID
    bank_account: str
    txn_date: date
    description: Optional[str] = None
    amount: float
    balance: Optional[float] = None

class FixedAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: uuid.UUID
    entity_id: uuid.UUID
    asset_code: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None
    accumulated_depreciation: float = 0
    nbv: Optional[float] = None
    depreciation_method: Optional[str] = None
    useful_life_years: Optional[int] = None
    residual_value: Optional[float] = None
    status: str = 'ACTIVE'
    created_at: datetime

class FixedAssetCreateSchema(BaseModel):
    entity_id: uuid.UUID
    asset_code: str
    description: Optional[str] = None
    cost: float = Field(..., gt=0)
    depreciation_method: str = 'SLM'
    useful_life_years: int = Field(..., gt=0)
    residual_value: float = 0.0

class InventorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    entity_id: uuid.UUID
    description: Optional[str] = None
    qty_on_hand: Optional[float] = None
    unit_cost: Optional[float] = None
    total_value: Optional[float] = None
    costing_method: str = 'FIFO'
    last_updated: datetime

class InventoryCreateSchema(BaseModel):
    sku: str
    entity_id: uuid.UUID
    description: Optional[str] = None
    qty_on_hand: float = 0
    unit_cost: float = Field(..., ge=0)
    costing_method: str = 'FIFO'

class EmployeeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: uuid.UUID
    entity_id: uuid.UUID
    name: Optional[str] = None
    pan: Optional[str] = None
    uan: Optional[str] = None
    basic_salary: Optional[float] = None
    hra: Optional[float] = None
    lta: Optional[float] = None
    medical: Optional[float] = None
    nps: Optional[float] = None
    pf_employee: Optional[float] = None
    joined_date: Optional[date] = None
    status: str = 'ACTIVE'

class EmployeeCreateSchema(BaseModel):
    entity_id: uuid.UUID
    name: str
    pan: Optional[str] = Field(None, pattern=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    uan: Optional[str] = None
    basic_salary: float = Field(..., ge=0)
    hra: float = 0
    lta: float = 0
    medical: float = 0
    nps: float = 0
    joined_date: Optional[date] = None

class PayrollRunSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: uuid.UUID
    entity_id: uuid.UUID
    period: Optional[str] = None
    total_gross: Optional[float] = None
    total_deductions: Optional[float] = None
    total_net: Optional[float] = None
    pf_employer: Optional[float] = None
    esic_employer: Optional[float] = None
    pt: Optional[float] = None
    tds: Optional[float] = None
    created_at: datetime

class PayrollRunCreateSchema(BaseModel):
    entity_id: uuid.UUID
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')

class LoanSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_id: uuid.UUID
    entity_id: uuid.UUID
    facility_type: Optional[str] = None
    bank: Optional[str] = None
    sanctioned_amount: Optional[float] = None
    outstanding: Optional[float] = None
    rate_pct: Optional[float] = None
    emi: Optional[float] = None
    tenure_months: Optional[int] = None
    disbursement_date: Optional[date] = None
    status: str = 'ACTIVE'

class LoanCreateSchema(BaseModel):
    entity_id: uuid.UUID
    facility_type: str
    bank: str
    sanctioned_amount: float = Field(..., gt=0)
    rate_pct: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    disbursement_date: date

class PortfolioSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    portfolio_id: uuid.UUID
    entity_id: uuid.UUID
    name: Optional[str] = None
    total_value: Optional[float] = None
    holdings: Optional[Dict[str, Any]] = None
    created_at: datetime

class PortfolioCreateSchema(BaseModel):
    entity_id: uuid.UUID
    name: str
    holdings: Optional[Dict[str, Any]] = None