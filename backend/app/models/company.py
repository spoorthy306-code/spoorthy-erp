from sqlalchemy import Column, Integer, String, Text
from backend.db.base import Base


class CompanyProfile(Base):
    __tablename__ = "company_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    gstin = Column(String(15), nullable=True)
    website = Column(String(100), nullable=True)
    logo_path = Column(String(255), nullable=True)
    bank_details = Column(Text, nullable=True)
