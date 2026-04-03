import enum
from datetime import datetime

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, Enum,
                        Float, ForeignKey, Index, Integer, Numeric, String,
                        Text, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base

# STOCK GROUPS


class StockGroup(Base):
    __tablename__ = "stock_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("stock_groups.id"), nullable=True)

    parent = relationship("StockGroup", remote_side=[id], backref="children")
    items = relationship("StockItem", back_populates="group")


# STOCK UNITS


class StockUnit(Base):
    __tablename__ = "stock_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    unit_type = Column(String(20), nullable=True)  # weight/volume/count/length
    base_symbol = Column(String(10), nullable=True)
    factor = Column(Numeric(18, 8), default=1.0)


# STOCK ITEMS


class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    group_id = Column(Integer, ForeignKey("stock_groups.id"))
    unit_id = Column(Integer, ForeignKey("stock_units.id"))
    hsn_sac = Column(String(10), nullable=True)
    gst_rate = Column(Numeric(5, 2), default=18.0)
    cost_price = Column(Numeric(18, 2), default=0.0)
    sale_price = Column(Numeric(18, 2), default=0.0)
    mrp = Column(Numeric(18, 2), default=0.0)
    reorder_level = Column(Numeric(10, 3), default=0.0)
    reorder_qty = Column(Numeric(10, 3), default=0.0)
    current_stock = Column(Numeric(10, 3), default=0.0)
    valuation_method = Column(String(10), default="FIFO")
    serial_number = Column(String(100), nullable=True)
    lot_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    warehouse = Column(String(100), nullable=True)
    zone = Column(String(50), nullable=True)
    rack = Column(String(50), nullable=True)
    bin_location = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("StockGroup", back_populates="items")
    unit = relationship("StockUnit")


# INVOICE LINE ITEMS (for Purchase/Sales vouchers)


class VoucherLineItem(Base):
    __tablename__ = "voucher_line_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False, index=True)
    stock_item_id = Column(Integer, ForeignKey("stock_items.id"), nullable=True)
    description = Column(String(300), nullable=False)
    hsn_sac = Column(String(10), nullable=True)
    quantity = Column(Numeric(12, 3), default=1.0)
    unit_id = Column(Integer, ForeignKey("stock_units.id"), nullable=True)
    unit_price = Column(Numeric(18, 2), nullable=False)
    discount_pct = Column(Numeric(5, 2), default=0.0)
    discount_amt = Column(Numeric(18, 2), default=0.0)
    taxable_value = Column(Numeric(18, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=18.0)
    cgst_rate = Column(Numeric(5, 2), default=9.0)
    sgst_rate = Column(Numeric(5, 2), default=9.0)
    igst_rate = Column(Numeric(5, 2), default=0.0)
    cgst_amount = Column(Numeric(18, 2), default=0.0)
    sgst_amount = Column(Numeric(18, 2), default=0.0)
    igst_amount = Column(Numeric(18, 2), default=0.0)
    cess_amount = Column(Numeric(18, 2), default=0.0)
    line_total = Column(Numeric(18, 2), nullable=False)
    ledger_id = Column(Integer, ForeignKey("ledgers.id"), nullable=True)

    voucher = relationship("Voucher", backref="line_items")
    stock_item = relationship("StockItem")
    unit = relationship("StockUnit")
    ledger = relationship("Ledger")
