from pydantic import BaseModel, ConfigDict


class CompanyProfileBase(BaseModel):
    name: str
    address: str
    phone: str | None = None
    email: str | None = None
    gstin: str | None = None
    website: str | None = None
    logo_path: str | None = None
    bank_details: str | None = None


class CompanyProfileCreate(CompanyProfileBase):
    pass


class CompanyProfileRead(CompanyProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
