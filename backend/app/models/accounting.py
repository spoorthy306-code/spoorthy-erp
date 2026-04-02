from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.db.base import Base


class AccountGroup(Base):
    __tablename__ = "account_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("account_groups.id"), nullable=True)
    is_primary = Column(Boolean, default=False)

    parent = relationship("AccountGroup", remote_side=[id], backref="children")
    ledgers = relationship("Ledger", back_populates="group")


class Ledger(Base):
    __tablename__ = "ledgers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey("account_groups.id"), nullable=False)
    nature = Column(String(50), nullable=False, default="Debit")
    opening_balance = Column(Float, default=0.0)

    group = relationship("AccountGroup", back_populates="ledgers")
