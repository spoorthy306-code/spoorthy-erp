"""
Spoorthy ERP — COMPLETE SYSTEM
db/schema.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full PostgreSQL Schema via SQLAlchemy ORM
All tables for:
  • Account Groups & Ledgers
  • Vouchers & Transactions (double-entry)
  • Stock Items & Units
  • Tax Master (GST/TDS/PF/ESI)
  • Documents (DMS)
  • Employees & Payroll
  • Customers & Suppliers (Parties)
  • Bank Accounts & Reconciliation
  • Cost Centres & Projects
  • Audit Trail (immutable chain)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    ForeignKey, DateTime, Text, Enum, Numeric, Date, Index,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Generator
import enum
import os

Base = declarative_base()

# ── DB Connection ──────────────────────────────────────────────────────────────
DB_URL = os.getenv(
    "SPOORTHY_DB_URL",
    "sqlite:///spoorthy_erp.db"   # fallback to SQLite if no PostgreSQL
)

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All Spoorthy ERP tables created.")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class GroupType(str, enum.Enum):
    ASSET     = "ASSET"
    LIABILITY = "LIABILITY"
    INCOME    = "INCOME"
    EXPENSE   = "EXPENSE"

class VoucherStatus(str, enum.Enum):
    DRAFT    = "DRAFT"
    POSTED   = "POSTED"
    REVERSED = "REVERSED"
    CANCELLED= "CANCELLED"

class DocStatus(str, enum.Enum):
    PENDING   = "PENDING"
    EXTRACTED = "EXTRACTED"
    PROCESSED = "PROCESSED"
    FAILED    = "FAILED"

class PartyType(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    SUPPLIER = "SUPPLIER"
    EMPLOYEE = "EMPLOYEE"
    BANK     = "BANK"
    OTHER    = "OTHER"

class TaxType(str, enum.Enum):
    GST_OUTPUT = "GST_OUTPUT"
    GST_INPUT  = "GST_INPUT"
    IGST_OUT   = "IGST_OUT"
    IGST_IN    = "IGST_IN"
    TDS        = "TDS"
    TCS        = "TCS"
    PF         = "PF"
    ESI        = "ESI"
    PT         = "PT"
    INCOME_TAX = "INCOME_TAX"
    CUSTOMS    = "CUSTOMS"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ACCOUNT GROUPS
# ═══════════════════════════════════════════════════════════════════════════════

class AccountGroup(Base):
    __tablename__ = "account_groups"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    code          = Column(String(20), unique=True, nullable=False, index=True)
    name          = Column(String(100), unique=True, nullable=False)
    group_type    = Column(String(20), nullable=False)   # ASSET/LIABILITY/INCOME/EXPENSE
    parent_id     = Column(Integer, ForeignKey("account_groups.id"), nullable=True)
    affects_gross = Column(Boolean, default=False)
    is_system     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    parent   = relationship("AccountGroup", remote_side=[id], backref="children")
    ledgers  = relationship("Ledger", back_populates="group")

    def __repr__(self):
        return f"<AccountGroup {self.code}: {self.name}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LEDGERS (Chart of Accounts)
# ═══════════════════════════════════════════════════════════════════════════════

class Ledger(Base):
    __tablename__ = "ledgers"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    code             = Column(String(30), unique=True, nullable=False, index=True)
    name             = Column(String(150), nullable=False)
    group_id         = Column(Integer, ForeignKey("account_groups.id"), nullable=False)
    nature           = Column(String(2), default="Dr")   # Dr / Cr
    opening_balance  = Column(Numeric(18, 2), default=0.0)
    opening_type     = Column(String(2), default="Dr")   # Dr / Cr
    currency         = Column(String(3), default="INR")
    gstin            = Column(String(15), nullable=True)
    is_bank          = Column(Boolean, default=False)
    is_cash          = Column(Boolean, default=False)
    bank_account_no  = Column(String(30), nullable=True)
    ifsc_code        = Column(String(15), nullable=True)
    is_tax_ledger    = Column(Boolean, default=False)
    tax_type         = Column(String(20), nullable=True)
    tax_rate         = Column(Numeric(6, 3), default=0.0)
    tax_section      = Column(String(10), nullable=True)   # TDS section
    is_active        = Column(Boolean, default=True)
    party_id         = Column(Integer, ForeignKey("parties.id"), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group       = relationship("AccountGroup", back_populates="ledgers")
    party       = relationship("Party", backref="ledger")
    transactions= relationship("Transaction", back_populates="ledger")

    def __repr__(self):
        return f"<Ledger {self.code}: {self.name}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PARTIES (Customers / Suppliers / Employees / Banks)
# ═══════════════════════════════════════════════════════════════════════════════

class Party(Base):
    __tablename__ = "parties"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    code           = Column(String(20), unique=True, nullable=False, index=True)
    name           = Column(String(200), nullable=False)
    party_type     = Column(String(20), nullable=False)
    gstin          = Column(String(15), nullable=True)
    pan            = Column(String(10), nullable=True)
    address_line1  = Column(String(200), nullable=True)
    address_line2  = Column(String(200), nullable=True)
    city           = Column(String(100), nullable=True)
    state_code     = Column(String(4), nullable=True)
    pincode        = Column(String(10), nullable=True)
    country        = Column(String(50), default="India")
    phone          = Column(String(20), nullable=True)
    email          = Column(String(100), nullable=True)
    credit_days    = Column(Integer, default=30)
    credit_limit   = Column(Numeric(18, 2), default=0.0)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. VOUCHER TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class VoucherType(Base):
    __tablename__ = "voucher_types"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    code         = Column(String(10), unique=True, nullable=False)
    name         = Column(String(50), nullable=False)
    prefix       = Column(String(10), nullable=False)
    affects_stock= Column(Boolean, default=False)
    affects_bank = Column(Boolean, default=False)
    is_system    = Column(Boolean, default=True)
    auto_number  = Column(Boolean, default=True)
    current_seq  = Column(Integer, default=0)

    vouchers     = relationship("Voucher", back_populates="voucher_type_rel")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. VOUCHERS
# ═══════════════════════════════════════════════════════════════════════════════

class Voucher(Base):
    __tablename__ = "vouchers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    voucher_no      = Column(String(50), unique=True, nullable=False, index=True)
    voucher_type_id = Column(Integer, ForeignKey("voucher_types.id"), nullable=False)
    voucher_date    = Column(Date, nullable=False, index=True)
    fiscal_year     = Column(String(7), nullable=False)   # e.g. 2025-26
    party_id        = Column(Integer, ForeignKey("parties.id"), nullable=True)
    narration       = Column(Text, nullable=True)
    ref_no          = Column(String(100), nullable=True)   # PO/Invoice ref
    total_amount    = Column(Numeric(18, 2), default=0.0)
    taxable_amount  = Column(Numeric(18, 2), default=0.0)
    tax_amount      = Column(Numeric(18, 2), default=0.0)
    status          = Column(String(15), default="POSTED")
    is_inter_state  = Column(Boolean, default=False)
    supply_state    = Column(String(4), nullable=True)
    created_by      = Column(String(50), default="system")
    doc_id          = Column(Integer, ForeignKey("documents.id"), nullable=True)
    reversed_by     = Column(Integer, ForeignKey("vouchers.id"), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pqc_signature   = Column(String(100), nullable=True)

    voucher_type_rel= relationship("VoucherType", back_populates="vouchers")
    party           = relationship("Party", backref="vouchers")
    transactions    = relationship("Transaction", back_populates="voucher",
                                    cascade="all, delete-orphan")
    document        = relationship("Document", backref="voucher")

    __table_args__ = (
        Index("idx_voucher_date_type", "voucher_date", "voucher_type_id"),
        Index("idx_voucher_fy",        "fiscal_year"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. TRANSACTIONS  (Journal Entry Lines — core double-entry)
# ═══════════════════════════════════════════════════════════════════════════════

class Transaction(Base):
    __tablename__ = "transactions"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    voucher_id    = Column(Integer, ForeignKey("vouchers.id"), nullable=False, index=True)
    ledger_id     = Column(Integer, ForeignKey("ledgers.id"),  nullable=False, index=True)
    debit         = Column(Numeric(18, 2), default=0.0)
    credit        = Column(Numeric(18, 2), default=0.0)
    narration     = Column(Text, nullable=True)
    cost_centre   = Column(String(20), nullable=True)
    project_code  = Column(String(20), nullable=True)
    currency      = Column(String(3), default="INR")
    fx_rate       = Column(Numeric(12, 6), default=1.0)
    amount_fc     = Column(Numeric(18, 2), default=0.0)   # foreign currency
    reconciled    = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    voucher       = relationship("Voucher", back_populates="transactions")
    ledger        = relationship("Ledger",  back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            "(debit = 0 AND credit > 0) OR (debit > 0 AND credit = 0) OR (debit = 0 AND credit = 0)",
            name="chk_dr_cr_exclusive"
        ),
    )


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_currency = Column(String(3), nullable=False, index=True)
    to_currency = Column(String(3), nullable=False, index=True)
    rate = Column(Numeric(18, 8), default=1.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    escalated_at = Column(DateTime, default=datetime.utcnow)
    action = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. STOCK GROUPS
# ═══════════════════════════════════════════════════════════════════════════════

class StockGroup(Base):
    __tablename__ = "stock_groups"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    code       = Column(String(20), unique=True, nullable=False)
    name       = Column(String(100), nullable=False)
    parent_id  = Column(Integer, ForeignKey("stock_groups.id"), nullable=True)

    parent     = relationship("StockGroup", remote_side=[id], backref="children")
    items      = relationship("StockItem", back_populates="group")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. STOCK UNITS
# ═══════════════════════════════════════════════════════════════════════════════

class StockUnit(Base):
    __tablename__ = "stock_units"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    symbol      = Column(String(10), unique=True, nullable=False)
    name        = Column(String(50), nullable=False)
    unit_type   = Column(String(20), nullable=True)   # weight/volume/count/length
    base_symbol = Column(String(10), nullable=True)
    factor      = Column(Numeric(18, 8), default=1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. STOCK ITEMS
# ═══════════════════════════════════════════════════════════════════════════════

class StockItem(Base):
    __tablename__ = "stock_items"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    code           = Column(String(30), unique=True, nullable=False, index=True)
    name           = Column(String(200), nullable=False)
    group_id       = Column(Integer, ForeignKey("stock_groups.id"))
    unit_id        = Column(Integer, ForeignKey("stock_units.id"))
    hsn_sac        = Column(String(10), nullable=True)
    gst_rate       = Column(Numeric(5, 2), default=18.0)
    cost_price     = Column(Numeric(18, 2), default=0.0)
    sale_price     = Column(Numeric(18, 2), default=0.0)
    mrp            = Column(Numeric(18, 2), default=0.0)
    reorder_level  = Column(Numeric(10, 3), default=0.0)
    reorder_qty    = Column(Numeric(10, 3), default=0.0)
    current_stock  = Column(Numeric(10, 3), default=0.0)
    valuation_method= Column(String(10), default="FIFO")
    serial_number  = Column(String(100), nullable=True)
    lot_number     = Column(String(100), nullable=True)
    expiry_date    = Column(Date, nullable=True)
    warehouse      = Column(String(100), nullable=True)
    zone           = Column(String(50), nullable=True)
    rack           = Column(String(50), nullable=True)
    bin_location   = Column(String(50), nullable=True)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)

    group          = relationship("StockGroup", back_populates="items")
    unit           = relationship("StockUnit")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. INVOICE LINE ITEMS (for Purchase/Sales vouchers)
# ═══════════════════════════════════════════════════════════════════════════════

class VoucherLineItem(Base):
    __tablename__ = "voucher_line_items"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    voucher_id     = Column(Integer, ForeignKey("vouchers.id"), nullable=False, index=True)
    stock_item_id  = Column(Integer, ForeignKey("stock_items.id"), nullable=True)
    description    = Column(String(300), nullable=False)
    hsn_sac        = Column(String(10), nullable=True)
    quantity       = Column(Numeric(12, 3), default=1.0)
    unit_id        = Column(Integer, ForeignKey("stock_units.id"), nullable=True)
    unit_price     = Column(Numeric(18, 2), nullable=False)
    discount_pct   = Column(Numeric(5, 2), default=0.0)
    discount_amt   = Column(Numeric(18, 2), default=0.0)
    taxable_value  = Column(Numeric(18, 2), nullable=False)
    gst_rate       = Column(Numeric(5, 2), default=18.0)
    cgst_rate      = Column(Numeric(5, 2), default=9.0)
    sgst_rate      = Column(Numeric(5, 2), default=9.0)
    igst_rate      = Column(Numeric(5, 2), default=0.0)
    cgst_amount    = Column(Numeric(18, 2), default=0.0)
    sgst_amount    = Column(Numeric(18, 2), default=0.0)
    igst_amount    = Column(Numeric(18, 2), default=0.0)
    cess_amount    = Column(Numeric(18, 2), default=0.0)
    line_total     = Column(Numeric(18, 2), nullable=False)
    ledger_id      = Column(Integer, ForeignKey("ledgers.id"), nullable=True)

    voucher        = relationship("Voucher", backref="line_items")
    stock_item     = relationship("StockItem")
    unit           = relationship("StockUnit")
    ledger         = relationship("Ledger")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. DOCUMENTS (DMS)
# ═══════════════════════════════════════════════════════════════════════════════

class Document(Base):
    __tablename__ = "documents"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    doc_ref          = Column(String(50), unique=True, nullable=False, index=True)
    original_filename= Column(String(300), nullable=False)
    stored_path      = Column(String(500), nullable=False)
    mime_type        = Column(String(100), nullable=True)
    file_size_kb     = Column(Numeric(10, 2), default=0.0)
    file_hash        = Column(String(64), nullable=True, unique=True)
    category         = Column(String(50), default="Other")
    tags             = Column(Text, nullable=True)           # JSON array string
    description      = Column(Text, nullable=True)
    extracted_text   = Column(Text, nullable=True)
    parsed_fields    = Column(Text, nullable=True)           # JSON
    status           = Column(String(20), default="PENDING")
    version          = Column(Integer, default=1)
    linked_party_id  = Column(Integer, ForeignKey("parties.id"), nullable=True)
    uploaded_by      = Column(String(50), default="system")
    upload_date      = Column(Date, default=func.current_date())
    extraction_method= Column(String(30), nullable=True)
    pqc_signature    = Column(String(100), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    party            = relationship("Party", backref="documents")


# ═══════════════════════════════════════════════════════════════════════════════
# 12. BANK RECONCILIATION
# ═══════════════════════════════════════════════════════════════════════════════

class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    bank_ledger_id        = Column(Integer, ForeignKey("ledgers.id"), nullable=False)
    statement_date        = Column(Date, nullable=False)
    statement_balance     = Column(Numeric(18, 2), nullable=False)
    book_balance          = Column(Numeric(18, 2), nullable=False)
    uncleared_deposits    = Column(Numeric(18, 2), default=0.0)
    uncleared_payments    = Column(Numeric(18, 2), default=0.0)
    bank_charges          = Column(Numeric(18, 2), default=0.0)
    interest_credited     = Column(Numeric(18, 2), default=0.0)
    adjusted_bank_balance = Column(Numeric(18, 2), nullable=False)
    difference            = Column(Numeric(18, 2), default=0.0)
    is_reconciled         = Column(Boolean, default=False)
    auto_jv_id            = Column(Integer, ForeignKey("vouchers.id"), nullable=True)
    reconciled_by         = Column(String(50), nullable=True)
    created_at            = Column(DateTime, default=datetime.utcnow)

    bank_ledger           = relationship("Ledger")


# ═══════════════════════════════════════════════════════════════════════════════
# 13. COST CENTRES
# ═══════════════════════════════════════════════════════════════════════════════

class CostCentre(Base):
    __tablename__ = "cost_centres"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    code       = Column(String(20), unique=True, nullable=False)
    name       = Column(String(100), nullable=False)
    parent_id  = Column(Integer, ForeignKey("cost_centres.id"), nullable=True)
    manager    = Column(String(100), nullable=True)
    budget     = Column(Numeric(18, 2), default=0.0)
    is_active  = Column(Boolean, default=True)

    parent     = relationship("CostCentre", remote_side=[id], backref="children")


# ═══════════════════════════════════════════════════════════════════════════════
# 14. CURRENCIES
# ═══════════════════════════════════════════════════════════════════════════════

class Currency(Base):
    __tablename__ = "currencies"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    code        = Column(String(3), unique=True, nullable=False)
    name        = Column(String(50), nullable=False)
    symbol      = Column(String(5), nullable=True)
    is_base     = Column(Boolean, default=False)
    exchange_rate = Column(Numeric(12, 6), default=1.0)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 15. FISCAL YEARS
# ═══════════════════════════════════════════════════════════════════════════════

class FiscalYear(Base):
    __tablename__ = "fiscal_years"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    label       = Column(String(7), unique=True, nullable=False)  # e.g. 2025-26
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    is_current  = Column(Boolean, default=False)
    is_closed   = Column(Boolean, default=False)
    closed_at   = Column(DateTime, nullable=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 16. AUDIT TRAIL (Immutable — never DELETE/UPDATE)
# ═══════════════════════════════════════════════════════════════════════════════

class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    entry_uid    = Column(String(50), unique=True, nullable=False, index=True)
    table_name   = Column(String(50), nullable=False)
    record_id    = Column(String(50), nullable=False)
    action       = Column(String(10), nullable=False)   # INSERT/UPDATE/DELETE
    old_value    = Column(Text, nullable=True)
    new_value    = Column(Text, nullable=True)
    prev_hash    = Column(String(64), nullable=False)
    record_hash  = Column(String(64), nullable=False)
    pqc_signature= Column(String(100), nullable=True)
    performed_by = Column(String(50), default="system")
    performed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_table_record", "table_name", "record_id"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 17. EMPLOYEES
# ═══════════════════════════════════════════════════════════════════════════════

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {'extend_existing': True}

    id              = Column(Integer, primary_key=True, autoincrement=True)
    emp_code        = Column(String(20), unique=True, nullable=False, index=True)
    name            = Column(String(150), nullable=False)
    designation     = Column(String(100), nullable=True)
    department      = Column(String(100), nullable=True)
    doj             = Column(Date, nullable=True)
    dob             = Column(Date, nullable=True)
    pan             = Column(String(10), nullable=True)
    pf_no           = Column(String(20), nullable=True)
    esic_no         = Column(String(20), nullable=True)
    bank_account_no = Column(String(30), nullable=True)
    ifsc_code       = Column(String(15), nullable=True)
    gross_salary    = Column(Numeric(18, 2), default=0.0)
    basic_pct       = Column(Numeric(5, 2), default=50.0)
    hra_pct         = Column(Numeric(5, 2), default=40.0)
    is_active       = Column(Boolean, default=True)
    party_id        = Column(Integer, ForeignKey("parties.id"), nullable=True)
    # Zoho-style additional fields
    gender          = Column(String(10), nullable=True)          # Male/Female/Other
    father_name     = Column(String(150), nullable=True)
    mobile          = Column(String(15), nullable=True)
    work_email      = Column(String(100), nullable=True)
    work_location   = Column(String(100), nullable=True)
    epf_enabled     = Column(Boolean, default=False)
    esi_enabled     = Column(Boolean, default=False)
    pt_enabled      = Column(Boolean, default=True)
    bank_name       = Column(String(100), nullable=True)
    payment_mode    = Column(String(50), default="Manual Bank Transfer")
    conveyance      = Column(Numeric(18, 2), default=1600.0)
    portal_access   = Column(Boolean, default=True)
    uan_no          = Column(String(20), nullable=True)          # UAN for PF

    party           = relationship("Party")


# ═══════════════════════════════════════════════════════════════════════════════
# 18. GST REGISTRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class GSTRegistration(Base):
    __tablename__ = "gst_registrations"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    gstin        = Column(String(15), unique=True, nullable=False)
    trade_name   = Column(String(200), nullable=False)
    legal_name   = Column(String(200), nullable=True)
    state_code   = Column(String(4), nullable=False)
    reg_type     = Column(String(20), default="Regular")  # Regular/Composite/SEZ
    is_primary   = Column(Boolean, default=True)
    reg_date     = Column(Date, nullable=True)
    email        = Column(String(100), nullable=True)
    mobile       = Column(String(15), nullable=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 19. TDS CHALLANS
# ═══════════════════════════════════════════════════════════════════════════════

class TDSChallan(Base):
    __tablename__ = "tds_challans"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    challan_no   = Column(String(30), unique=True, nullable=False)
    bsr_code     = Column(String(10), nullable=True)           # Bank BSR code
    section      = Column(String(10), nullable=False)
    deductee_name= Column(String(200), nullable=False)
    deductee_pan = Column(String(10), nullable=True)
    payment_date = Column(Date, nullable=False)
    tds_amount   = Column(Numeric(18, 2), nullable=False)
    surcharge    = Column(Numeric(18, 2), default=0.0)
    cess         = Column(Numeric(18, 2), default=0.0)
    total        = Column(Numeric(18, 2), nullable=False)
    quarter      = Column(String(5), nullable=True)   # Q1/Q2/Q3/Q4
    fy           = Column(String(7), nullable=True)
    deposited    = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 20. FIXED ASSETS REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

class FixedAsset(Base):
    __tablename__ = "fixed_assets"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    asset_code       = Column(String(30), unique=True, nullable=False, index=True)
    name             = Column(String(200), nullable=False)
    category         = Column(String(100), nullable=True)
    purchase_date    = Column(Date, nullable=True)
    cost             = Column(Numeric(18, 2), default=0.0)
    salvage_value    = Column(Numeric(18, 2), default=0.0)
    useful_life_yrs  = Column(Integer, default=5)
    depreciation_method = Column(String(10), default="SLM")  # SLM / WDV
    wdv_rate         = Column(Numeric(5, 2), default=20.0)
    accumulated_dep  = Column(Numeric(18, 2), default=0.0)
    book_value       = Column(Numeric(18, 2), default=0.0)
    location         = Column(String(100), nullable=True)
    serial_no        = Column(String(100), nullable=True)
    is_disposed      = Column(Boolean, default=False)
    disposal_date    = Column(Date, nullable=True)
    disposal_proceeds= Column(Numeric(18, 2), default=0.0)
    ledger_id        = Column(Integer, ForeignKey("ledgers.id"), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    ledger           = relationship("Ledger")


# ═══════════════════════════════════════════════════════════════════════════════
# 21. PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════

class Project(Base):
    __tablename__ = "projects"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    code           = Column(String(20), unique=True, nullable=False, index=True)
    name           = Column(String(200), nullable=False)
    customer_id    = Column(Integer, ForeignKey("parties.id"), nullable=True)
    contract_value = Column(Numeric(18, 2), default=0.0)
    start_date     = Column(Date, nullable=True)
    end_date       = Column(Date, nullable=True)
    status         = Column(String(20), default="ACTIVE")
    manager        = Column(String(100), nullable=True)
    cost_centre_id = Column(Integer, ForeignKey("cost_centres.id"), nullable=True)
    budgeted_cost  = Column(Numeric(18, 2), default=0.0)
    actual_cost    = Column(Numeric(18, 2), default=0.0)
    billed_amount  = Column(Numeric(18, 2), default=0.0)
    completion_pct = Column(Numeric(5, 2), default=0.0)
    created_at     = Column(DateTime, default=datetime.utcnow)

    customer       = relationship("Party")
    cost_centre    = relationship("CostCentre")


# ═══════════════════════════════════════════════════════════════════════════════
# 22. SYSTEM CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
# 20. COMPANY PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

class Company(Base):
    __tablename__ = "company"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(200), nullable=False)
    legal_name      = Column(String(200), nullable=True)
    gstin           = Column(String(15), nullable=True)
    pan             = Column(String(10), nullable=True)
    cin             = Column(String(21), nullable=True)           # Company ID No
    tan             = Column(String(10), nullable=True)
    address_line1   = Column(String(200), nullable=True)
    address_line2   = Column(String(200), nullable=True)
    city            = Column(String(100), nullable=True)
    state_code      = Column(String(4), nullable=True)
    pincode         = Column(String(10), nullable=True)
    country         = Column(String(50), default="India")
    phone           = Column(String(20), nullable=True)
    email           = Column(String(100), nullable=True)
    website         = Column(String(200), nullable=True)
    logo_path       = Column(String(300), nullable=True)
    fiscal_year_start = Column(String(5), default="04-01")        # MM-DD
    currency        = Column(String(3), default="INR")
    date_format     = Column(String(20), default="DD-MM-YYYY")
    industry        = Column(String(100), nullable=True)
    reg_date        = Column(Date, nullable=True)
    # Branding
    brand_primary_color   = Column(String(7), default="#1e293b")
    brand_secondary_color = Column(String(7), default="#3b82f6")
    invoice_footer_text   = Column(Text, nullable=True)
    # Subscription
    subscription_plan     = Column(String(20), default="FREE")
    subscription_expires  = Column(Date, nullable=True)
    # MSME
    msme_udyam_no         = Column(String(30), nullable=True)
    msme_payment_days     = Column(Integer, default=45)
    # e-Invoice / e-Way Bill
    einvoice_enabled      = Column(Boolean, default=False)
    eway_bill_enabled     = Column(Boolean, default=False)
    eway_bill_threshold   = Column(Numeric(18, 2), default=50000)
    is_setup_done         = Column(Boolean, default=False)
    created_at            = Column(DateTime, default=datetime.utcnow)
    updated_at            = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 21. USER ROLES & USERS
# ═══════════════════════════════════════════════════════════════════════════════

class Role(Base):
    __tablename__ = "roles"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(50), unique=True, nullable=False)  # ADMIN/ACCOUNTANT/VIEWER/HR/AUDITOR
    description = Column(String(200), nullable=True)
    can_post    = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)
    can_delete  = Column(Boolean, default=False)
    can_export  = Column(Boolean, default=True)
    can_admin   = Column(Boolean, default=False)
    is_system   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    can_view_reports   = Column(Boolean, default=True)
    can_manage_masters = Column(Boolean, default=False)
    module_access_json = Column(Text, nullable=True)   # JSON: {module: NONE/READ/WRITE/FULL}

    users       = relationship("AppUser", back_populates="role")


class AppUser(Base):
    __tablename__ = "app_users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    username        = Column(String(50), unique=True, nullable=False, index=True)
    full_name       = Column(String(150), nullable=False)
    email           = Column(String(150), unique=True, nullable=False)
    password_hash   = Column(String(256), nullable=False)
    role_id         = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active       = Column(Boolean, default=True)
    is_first_login  = Column(Boolean, default=True)
    last_login      = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    phone           = Column(String(20), nullable=True)
    mfa_enabled     = Column(Boolean, default=False)
    mfa_secret      = Column(String(128), nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    password_expires_at = Column(DateTime, nullable=True)

    role            = relationship("Role", back_populates="users")


# ═══════════════════════════════════════════════════════════════════════════════
# 22. ORG LOCATIONS (Branches / Warehouses)
# ═══════════════════════════════════════════════════════════════════════════════

class OrgLocation(Base):
    __tablename__ = "org_locations"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(150), nullable=False)
    gstin        = Column(String(15), nullable=True)
    address      = Column(Text, nullable=True)
    city         = Column(String(100), nullable=True)
    state_code   = Column(String(4), nullable=True)
    pincode      = Column(String(10), nullable=True)
    phone        = Column(String(20), nullable=True)
    is_primary   = Column(Boolean, default=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 23. TRANSACTION NUMBER SERIES
# ═══════════════════════════════════════════════════════════════════════════════

class TxnNumberSeries(Base):
    __tablename__ = "txn_number_series"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    voucher_type_code = Column(String(10), ForeignKey("voucher_types.code"), nullable=False)
    prefix        = Column(String(20), nullable=False)
    suffix        = Column(String(10), nullable=True)
    start_seq     = Column(Integer, default=1)
    current_seq   = Column(Integer, default=0)
    padding       = Column(Integer, default=6)    # zero-padding digits
    reset_period  = Column(String(10), default="YEARLY")  # YEARLY/MONTHLY/NEVER
    fy_label      = Column(String(7), nullable=True)      # e.g. 2025-26
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 24. REPORTING TAGS
# ═══════════════════════════════════════════════════════════════════════════════

class ReportingTag(Base):
    __tablename__ = "reporting_tags"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(80), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    color_hex   = Column(String(7), default="#3b82f6")
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 25. EMAIL / SMS TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    event_code  = Column(String(50), unique=True, nullable=False)  # INVOICE_SENT, PAYMENT_REC, etc.
    subject     = Column(String(300), nullable=False)
    body_html   = Column(Text, nullable=False)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


class SMSTemplate(Base):
    __tablename__ = "sms_templates"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    event_code  = Column(String(50), unique=True, nullable=False)
    message     = Column(String(160), nullable=False)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 26. WORKFLOW RULES & ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class WorkflowRule(Base):
    __tablename__ = "workflow_rules"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(150), nullable=False)
    module          = Column(String(30), nullable=False)   # INVOICE/PO/EXPENSE/PAYMENT
    trigger_event   = Column(String(50), nullable=False)   # ON_CREATE/ON_APPROVE/ON_DUE/AMOUNT_EXCEEDS
    condition_json  = Column(Text, nullable=True)          # JSON filter conditions
    is_active       = Column(Boolean, default=True)
    created_by      = Column(String(50), default="system")
    created_at      = Column(DateTime, default=datetime.utcnow)

    actions         = relationship("WorkflowAction", back_populates="rule", cascade="all, delete-orphan")
    logs            = relationship("WorkflowLog",    back_populates="rule", cascade="all, delete-orphan")


class WorkflowAction(Base):
    __tablename__ = "workflow_actions"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    rule_id         = Column(Integer, ForeignKey("workflow_rules.id"), nullable=False)
    action_type     = Column(String(30), nullable=False)   # SEND_EMAIL/NOTIFY/WEBHOOK/FIELD_UPDATE
    action_config_json = Column(Text, nullable=True)
    sequence        = Column(Integer, default=1)

    rule            = relationship("WorkflowRule", back_populates="actions")


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    rule_id         = Column(Integer, ForeignKey("workflow_rules.id"), nullable=False)
    triggered_at    = Column(DateTime, default=datetime.utcnow)
    record_type     = Column(String(30), nullable=True)
    record_id       = Column(String(50), nullable=True)
    outcome         = Column(String(10), default="SUCCESS")  # SUCCESS/FAILED
    log_text        = Column(Text, nullable=True)

    rule            = relationship("WorkflowRule", back_populates="logs")


# ═══════════════════════════════════════════════════════════════════════════════
# 27. WEBHOOKS
# ═══════════════════════════════════════════════════════════════════════════════

class Webhook(Base):
    __tablename__ = "webhooks"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    name             = Column(String(100), nullable=False)
    url              = Column(String(500), nullable=False)
    event_code       = Column(String(50), nullable=False)  # INVOICE_CREATED/PAYMENT_RECEIVED/etc.
    secret_token     = Column(String(100), nullable=True)
    is_active        = Column(Boolean, default=True)
    last_triggered_at= Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# 28. USER PREFERENCES
# ═══════════════════════════════════════════════════════════════════════════════

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(Integer, ForeignKey("app_users.id"), unique=True, nullable=False)
    default_fy          = Column(String(7), default="2025-26")
    date_format         = Column(String(20), default="DD-MM-YYYY")
    items_per_page      = Column(Integer, default=25)
    timezone            = Column(String(50), default="Asia/Kolkata")
    notify_by_email     = Column(Boolean, default=True)
    notify_by_sms       = Column(Boolean, default=False)
    dashboard_layout_json = Column(Text, nullable=True)

    user                = relationship("AppUser", backref="preferences")


# ═══════════════════════════════════════════════════════════════════════════════
# 29. APPROVAL RULES
# ═══════════════════════════════════════════════════════════════════════════════

class ApprovalRule(Base):
    __tablename__ = "approval_rules"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    module           = Column(String(30), nullable=False)  # INVOICE/PO/EXPENSE/PAYMENT
    min_amount       = Column(Numeric(18, 2), default=0)
    max_amount       = Column(Numeric(18, 2), nullable=True)  # NULL = no upper limit
    approver_user_id = Column(Integer, ForeignKey("app_users.id"), nullable=True)
    approver_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    sequence         = Column(Integer, default=1)
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    approver_user    = relationship("AppUser")
    approver_role    = relationship("Role")


class IdempotencyKey(Base):
    __tablename__  = "idempotency_keys"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    key            = Column(String(128), unique=True, nullable=False, index=True)
    endpoint       = Column(String(200), nullable=False)
    request_hash   = Column(String(64), nullable=True)
    response_json  = Column(Text, nullable=True)
    created_by     = Column(String(80), default="system")
    created_at     = Column(DateTime, default=datetime.utcnow)


class WarehouseSalesFact(Base):
    __tablename__  = "warehouse_sales_facts"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    transaction_date = Column(Date, nullable=False)
    voucher_id     = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    ledger_id      = Column(Integer, ForeignKey("ledgers.id"), nullable=False)
    item_id        = Column(Integer, ForeignKey("stock_items.id"), nullable=True)
    quantity       = Column(Numeric(18, 3), default=0.0)
    amount         = Column(Numeric(18, 2), default=0.0)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at     = Column(DateTime, default=datetime.utcnow)


class DimensionCustomer(Base):
    __tablename__ = "dim_customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(150), nullable=False)
    country = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DimensionProduct(Base):
    __tablename__ = "dim_product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(150), nullable=False)
    sku = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DimensionTime(Base):
    __tablename__ = "dim_time"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(150), nullable=False)
    description   = Column(Text, nullable=True)
    rule_json     = Column(Text, nullable=True)
    created_by    = Column(String(50), default="system")
    created_at    = Column(DateTime, default=datetime.utcnow)


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    definition_id = Column(Integer, ForeignKey("workflow_definitions.id"), nullable=False)
    status        = Column(String(20), default="PENDING")
    context_json  = Column(Text, nullable=True)
    started_at    = Column(DateTime, default=datetime.utcnow)
    completed_at  = Column(DateTime, nullable=True)

    definition    = relationship("WorkflowDefinition")


class Task(Base):
    __tablename__ = "tasks"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    instance_id   = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    title         = Column(String(200), nullable=False)
    description   = Column(Text, nullable=True)
    assigned_to   = Column(String(80), nullable=True)
    due_date      = Column(DateTime, nullable=True)
    status        = Column(String(20), default="PENDING")
    priority      = Column(String(20), default="NORMAL")
    escalated     = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instance      = relationship("WorkflowInstance")


class IntegrationLog(Base):
    __tablename__ = "integration_logs"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    source        = Column(String(100), nullable=False)
    event_type    = Column(String(100), nullable=False)
    request_body  = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    status_code   = Column(Integer, nullable=True)
    latency_ms    = Column(Numeric(18,3), default=0)
    executed_at   = Column(DateTime, default=datetime.utcnow)


class IntegrationToken(Base):
    __tablename__ = "integration_tokens"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    client_id     = Column(String(100), nullable=False)
    access_token  = Column(Text, nullable=False)
    expires_at    = Column(Integer, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)


class DeadLetter(Base):
    __tablename__ = "dead_letters"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    payload       = Column(Text, nullable=False)
    status        = Column(String(50), default="PENDING")
    error_message = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    cost_centre   = Column(String(50), nullable=False)
    amount        = Column(Numeric(18,2), default=0.0)
    fiscal_year   = Column(String(10), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)


class SalesQuote(Base):
    __tablename__ = "sales_quotes"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    customer_id   = Column(Integer, ForeignKey("parties.id"), nullable=False)
    total         = Column(Numeric(18,2), default=0.0)
    status        = Column(String(20), default="DRAFT")
    created_at    = Column(DateTime, default=datetime.utcnow)


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    quote_id      = Column(Integer, ForeignKey("sales_quotes.id"), nullable=True)
    customer_id   = Column(Integer, ForeignKey("parties.id"), nullable=False)
    amount        = Column(Numeric(18,2), default=0.0)
    status        = Column(String(20), default="NEW")
    created_at    = Column(DateTime, default=datetime.utcnow)


class TransferOrder(Base):
    __tablename__ = "transfer_orders"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    source_warehouse = Column(String(100), nullable=False)
    target_warehouse = Column(String(100), nullable=False)
    item_id       = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    quantity      = Column(Numeric(18,3), default=0.0)
    status        = Column(String(20), default="PENDING")
    created_at    = Column(DateTime, default=datetime.utcnow)


class CycleCount(Base):
    __tablename__ = "cycle_counts"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    item_id       = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    scheduled_date= Column(Date, nullable=False)
    counted_quantity = Column(Numeric(18,3), nullable=True)
    status        = Column(String(20), default="SCHEDULED")
    created_at    = Column(DateTime, default=datetime.utcnow)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=False)
    from_date     = Column(Date, nullable=False)
    to_date       = Column(Date, nullable=False)
    reason        = Column(Text, nullable=True)
    status        = Column(String(20), default="PENDING")
    created_at    = Column(DateTime, default=datetime.utcnow)


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=False)
    score         = Column(Numeric(5,2), nullable=False)
    comments      = Column(Text, nullable=True)
    status        = Column(String(20), default="PENDING")
    created_at    = Column(DateTime, default=datetime.utcnow)


class WorkCenterLoad(Base):
    __tablename__ = "work_center_loads"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    workcenter_id = Column(Integer, nullable=False)
    load          = Column(Numeric(5,2), default=0.0)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InspectionChecklist(Base):
    __tablename__ = "inspection_checklists"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    results       = Column(Text, nullable=True)
    status        = Column(String(20), default="PENDING")
    created_at    = Column(DateTime, default=datetime.utcnow)


class ManufacturingBOM(Base):
    __tablename__ = "manufacturing_bom"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    code          = Column(String(50), unique=True, nullable=False)
    name          = Column(String(150), nullable=False)
    product_id    = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    components_json = Column(Text, nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    work_order_no = Column(String(50), unique=True, nullable=False)
    bom_id        = Column(Integer, ForeignKey("manufacturing_bom.id"), nullable=False)
    quantity      = Column(Numeric(18, 3), default=0.0)
    status        = Column(String(30), default="OPEN")
    due_date      = Column(Date, nullable=True)
    started_at    = Column(DateTime, nullable=True)
    completed_at  = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    bom           = relationship("ManufacturingBOM")


class SystemConfig(Base):
    __tablename__ = "system_config"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    key         = Column(String(100), unique=True, nullable=False)
    value       = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# TABLE CREATION & SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_TABLES = [
    "account_groups", "ledgers", "parties", "voucher_types", "vouchers",
    "transactions", "stock_groups", "stock_units", "stock_items",
    "voucher_line_items", "documents", "bank_reconciliations", "cost_centres",
    "currencies", "fiscal_years", "audit_trail", "employees",
    "gst_registrations", "tds_challans", "fixed_assets", "projects",
    "system_config", "company", "roles", "app_users",
    "org_locations", "txn_number_series", "reporting_tags",
    "email_templates", "sms_templates",
    "workflow_rules", "workflow_actions", "workflow_logs",
    "webhooks", "user_preferences", "approval_rules",
    "idempotency_keys", "warehouse_sales_facts", "workflow_definitions", "workflow_instances", "tasks", "integration_logs",
    "manufacturing_bom", "work_orders",
]

if __name__ == "__main__":
    create_all_tables()
    print(f"\n  Tables created: {len(ALL_TABLES)}")
    for t in ALL_TABLES:
        print(f"    ✅  {t}")
