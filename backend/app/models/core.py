import os

from sqlalchemy import JSON, types
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB


class JSONB(types.TypeDecorator):
    """JSONB on PostgreSQL, JSON on SQLite (for tests)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(JSON())


import enum
from datetime import datetime

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, Enum,
                        Float, ForeignKey, Index, Integer, Numeric, String,
                        Text, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base

# SYSTEM CONFIG


# COMPANY PROFILE


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    legal_name = Column(String(200), nullable=True)
    gstin = Column(String(15), nullable=True)
    pan = Column(String(10), nullable=True)
    cin = Column(String(21), nullable=True)  # Company ID No
    tan = Column(String(10), nullable=True)
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state_code = Column(String(4), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(50), default="India")
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    logo_path = Column(String(300), nullable=True)
    fiscal_year_start = Column(String(5), default="04-01")  # MM-DD
    currency = Column(String(3), default="INR")
    date_format = Column(String(20), default="DD-MM-YYYY")
    industry = Column(String(100), nullable=True)
    reg_date = Column(Date, nullable=True)
    # Branding
    brand_primary_color = Column(String(7), default="#1e293b")
    brand_secondary_color = Column(String(7), default="#3b82f6")
    invoice_footer_text = Column(Text, nullable=True)
    # Subscription
    subscription_plan = Column(String(20), default="FREE")
    subscription_expires = Column(Date, nullable=True)
    # MSME
    msme_udyam_no = Column(String(30), nullable=True)
    msme_payment_days = Column(Integer, default=45)
    # e-Invoice / e-Way Bill
    einvoice_enabled = Column(Boolean, default=False)
    eway_bill_enabled = Column(Boolean, default=False)
    eway_bill_threshold = Column(Numeric(18, 2), default=50000)
    is_setup_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
