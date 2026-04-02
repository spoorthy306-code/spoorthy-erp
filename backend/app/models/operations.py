import enum
from datetime import datetime

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, Enum,
                        Float, ForeignKey, Index, Integer, Numeric, String,
                        Text, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base

# DOCUMENTS (DMS)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_ref = Column(String(50), unique=True, nullable=False, index=True)
    original_filename = Column(String(300), nullable=False)
    stored_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size_kb = Column(Numeric(10, 2), default=0.0)
    file_hash = Column(String(64), nullable=True, unique=True)
    category = Column(String(50), default="Other")
    tags = Column(Text, nullable=True)  # JSON array string
    description = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    parsed_fields = Column(Text, nullable=True)  # JSON
    status = Column(String(20), default="PENDING")
    version = Column(Integer, default=1)
    linked_party_id = Column(Integer, ForeignKey("parties.id"), nullable=True)
    uploaded_by = Column(String(50), default="system")
    upload_date = Column(Date, default=func.current_date())
    extraction_method = Column(String(30), nullable=True)
    pqc_signature = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    party = relationship("Party", backref="documents")


# AUDIT TRAIL (Immutable — never DELETE/UPDATE)


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_uid = Column(String(50), unique=True, nullable=False, index=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(String(50), nullable=False)
    action = Column(String(10), nullable=False)  # INSERT/UPDATE/DELETE
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    prev_hash = Column(String(64), nullable=False)
    record_hash = Column(String(64), nullable=False)
    pqc_signature = Column(String(100), nullable=True)
    performed_by = Column(String(50), default="system")
    performed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_audit_table_record", "table_name", "record_id"),)


# ORG LOCATIONS (Branches / Warehouses)


class OrgLocation(Base):
    __tablename__ = "org_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    gstin = Column(String(15), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state_code = Column(String(4), nullable=True)
    pincode = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# TRANSACTION NUMBER SERIES


class TxnNumberSeries(Base):
    __tablename__ = "txn_number_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    voucher_type_code = Column(
        String(10), ForeignKey("voucher_types.code"), nullable=False
    )
    prefix = Column(String(20), nullable=False)
    suffix = Column(String(10), nullable=True)
    start_seq = Column(Integer, default=1)
    current_seq = Column(Integer, default=0)
    padding = Column(Integer, default=6)  # zero-padding digits
    reset_period = Column(String(10), default="YEARLY")  # YEARLY/MONTHLY/NEVER
    fy_label = Column(String(7), nullable=True)  # e.g. 2025-26
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
