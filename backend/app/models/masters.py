from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.db.base import Base


class TaxMaster(Base):
    __tablename__ = "tax_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    rate = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)

    orders = relationship("Order", back_populates="tax")


class UnitMaster(Base):
    __tablename__ = "unit_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    symbol = Column(String(10), nullable=False)

    orders = relationship("Order", back_populates="unit")
