from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum, Numeric, Date, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from backend.db.base import Base


# EMPLOYEES


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


# USER ROLES & USERS


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


# USER PREFERENCES


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


# APPROVAL RULES


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


# 
# TABLE CREATION & SUMMARY
# 

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

