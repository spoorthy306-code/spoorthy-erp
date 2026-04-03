"""Complete Finance and User Models"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Index,
                        Integer, Numeric, String, Text)
from sqlalchemy.orm import relationship

from backend.app.models.models import Base

# ============== USER MODELS ==============


class User(Base):
    """User Model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), default="viewer")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============== ACCOUNTING MODELS ==============


class AccountGroup(Base):
    """Chart of Accounts Group"""

    __tablename__ = "account_groups"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    group_type = Column(
        String(50), nullable=False
    )  # asset, liability, income, expense, equity
    parent_id = Column(Integer, ForeignKey("account_groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    children = relationship("AccountGroup", remote_side=[id])
    ledgers = relationship("Ledger", back_populates="group")


class Ledger(Base):
    """Ledger Accounts"""

    __tablename__ = "ledgers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey("account_groups.id"), nullable=False)
    nature = Column(String(50), nullable=False, default="Debit")
    opening_balance = Column(Numeric(15, 2), default=Decimal("0.00"))
    current_balance = Column(Numeric(15, 2), default=Decimal("0.00"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("AccountGroup", back_populates="ledgers")
    journal_lines = relationship("JournalLine", back_populates="ledger")


class Journal(Base):
    """Journal Entries"""

    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, nullable=False)
    date = Column(Date, nullable=False)
    narration = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    posted = Column(Boolean, default=False)
    posted_at = Column(DateTime, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lines = relationship(
        "JournalLine", back_populates="journal", cascade="all, delete-orphan"
    )


class JournalLine(Base):
    """Journal Entry Lines"""

    __tablename__ = "journal_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    ledger_id = Column(Integer, ForeignKey("ledgers.id"), nullable=False)
    debit = Column(Numeric(15, 2), default=Decimal("0.00"))
    credit = Column(Numeric(15, 2), default=Decimal("0.00"))
    memo = Column(Text, nullable=True)

    # Relationships
    journal = relationship("Journal", back_populates="lines")
    ledger = relationship("Ledger", back_populates="journal_lines")


class Party(Base):
    """Customer/Vendor Party Model"""

    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    party_type = Column(String(20), nullable=False)  # 'customer' or 'vendor'
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True)
    gstin = Column(String(15), index=True)
    pan = Column(String(10), index=True)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    credit_limit = Column(Numeric(15, 2), default=Decimal("0.00"))
    current_balance = Column(Numeric(15, 2), default=Decimal("0.00"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoices = relationship(
        "Invoice", back_populates="party", foreign_keys="Invoice.party_id"
    )
    bills = relationship("Bill", back_populates="party", foreign_keys="Bill.party_id")


class Invoice(Base):
    """Sales Invoice Model"""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    subtotal = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    paid_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    status = Column(
        String(20), default="draft"
    )  # draft, sent, paid, overdue, written_off
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    party = relationship("Party", back_populates="invoices", foreign_keys=[party_id])
    lines = relationship(
        "InvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments = relationship("Payment", back_populates="invoice")


class InvoiceLine(Base):
    """Invoice Line Items"""

    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(15, 3), default=Decimal("1.000"))
    unit_price = Column(Numeric(15, 2), default=Decimal("0.00"))
    amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_rate = Column(Numeric(5, 2), default=Decimal("18.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    hsn_code = Column(String(20))

    # Relationships
    invoice = relationship("Invoice", back_populates="lines")


class Payment(Base):
    """Payment Model"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    method = Column(String(20), nullable=False)  # cash, bank, card, cheque, upi
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")


class Bill(Base):
    """Purchase Bill Model"""

    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    bill_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    subtotal = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    paid_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    status = Column(String(20), default="unpaid")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    party = relationship("Party", back_populates="bills", foreign_keys=[party_id])
    lines = relationship(
        "BillLine", back_populates="bill", cascade="all, delete-orphan"
    )
    payments = relationship("BillPayment", back_populates="bill")


class BillLine(Base):
    """Bill Line Items"""

    __tablename__ = "bill_lines"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(15, 3), default=Decimal("1.000"))
    unit_price = Column(Numeric(15, 2), default=Decimal("0.00"))
    amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    tax_rate = Column(Numeric(5, 2), default=Decimal("18.00"))
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    hsn_code = Column(String(20))

    # Relationships
    bill = relationship("Bill", back_populates="lines")


class BillPayment(Base):
    """Bill Payment Model"""

    __tablename__ = "bill_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    method = Column(String(20), nullable=False)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bill = relationship("Bill", back_populates="payments")


class BankAccount(Base):
    """Bank Account Model"""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    account_number = Column(String(50), unique=True, nullable=False)
    bank_name = Column(String(100), nullable=False)
    ifsc_code = Column(String(20))
    swift_code = Column(String(20))
    current_balance = Column(Numeric(15, 2), default=Decimal("0.00"))
    currency = Column(String(3), default="INR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("BankTransaction", back_populates="bank_account")


class BankTransaction(Base):
    """Bank Transaction Model"""

    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20))
    reference = Column(String(100))
    reconciled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bank_account = relationship("BankAccount", back_populates="transactions")


class FixedAsset(Base):
    """Fixed Asset Model"""

    __tablename__ = "fixed_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    purchase_date = Column(Date, nullable=False)
    cost = Column(Numeric(15, 2), nullable=False)
    salvage_value = Column(Numeric(15, 2), default=Decimal("0.00"))
    useful_life = Column(Integer, nullable=False)
    depreciation_method = Column(String(20), default="SLM")
    current_book_value = Column(Numeric(15, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    depreciation_schedules = relationship(
        "DepreciationSchedule", back_populates="asset"
    )


class DepreciationSchedule(Base):
    """Depreciation Schedule Model"""

    __tablename__ = "depreciation_schedules"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False)
    period = Column(String(20), nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)
    book_value = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("FixedAsset", back_populates="depreciation_schedules")


class Budget(Base):
    """Budget Model"""

    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    fiscal_year = Column(String(9), nullable=False)
    account_id = Column(Integer, ForeignKey("ledgers.id"), nullable=False)
    planned_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    actual_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    account = relationship("Ledger")


class TaxSetting(Base):
    """Tax Settings Model"""

    __tablename__ = "tax_settings"

    id = Column(Integer, primary_key=True, index=True)
    tax_name = Column(String(50), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    applicable_accounts = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit Log Model"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_table_record", "table_name", "record_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )
