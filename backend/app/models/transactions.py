from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        func)
from sqlalchemy.orm import relationship

from backend.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ledger_id = Column(Integer, ForeignKey("ledgers.id"), nullable=False, index=True)
    debit = Column(Numeric(18, 2), default=0.0, nullable=False)
    credit = Column(Numeric(18, 2), default=0.0, nullable=False)
    reference = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    ledger = relationship("Ledger")
