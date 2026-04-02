from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.app.models.company import CompanyProfile
from backend.app.schemas.company import CompanyProfileCreate, CompanyProfileRead

router = APIRouter(prefix='/company', tags=['company'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/profile', response_model=CompanyProfileRead)
def get_company_profile(db: Session = Depends(get_db)):
    profile = db.query(CompanyProfile).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company profile not found')
    return profile


@router.post('/profile', response_model=CompanyProfileRead)
def create_or_update_company_profile(data: CompanyProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(CompanyProfile).first()
    if profile:
        profile.name = data.name
        profile.address = data.address
        profile.phone = data.phone
        profile.email = data.email
        profile.gstin = data.gstin
        profile.website = data.website
        profile.logo_path = data.logo_path
        profile.bank_details = data.bank_details
    else:
        profile = CompanyProfile(**data.model_dump())
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile
