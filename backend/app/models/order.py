import enum
from datetime import datetime

from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, Numeric,
                        String)
from sqlalchemy.orm import relationship

from backend.db.base import Base


class OrderStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Numeric(18, 3), default=1.0, nullable=False)
    unit_price = Column(Numeric(18, 2), default=0.0, nullable=False)
    item_description = Column(String(255), nullable=True)
    hsn_code = Column(String(64), nullable=True)
    subtotal = Column(Numeric(18, 2), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 2), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 2), default=0.0, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    notes = Column(String(1024), nullable=True)
    unit_id = Column(Integer, ForeignKey("unit_masters.id"), nullable=True)
    tax_id = Column(Integer, ForeignKey("tax_masters.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    unit = relationship("UnitMaster", back_populates="orders")
    tax = relationship("TaxMaster", back_populates="orders")

    # Optional relationship if a user model with id exists
    # customer = relationship("User", back_populates="orders")
