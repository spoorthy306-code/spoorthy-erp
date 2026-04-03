"""Authentication API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from backend.db.session import SessionLocal
from backend.app.models.finance import User
from backend.app.core.security import verify_password, create_access_token, get_password_hash
from backend.app.core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123",
    "email": "spoorthy306@gmail.com",
    "role": "admin",
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def ensure_default_admin(db: Session):
    """Create default admin user if no users exist; normalize admin email."""
    user_count = db.query(User).count()

    if user_count == 0:
        admin = User(
            username=DEFAULT_ADMIN["username"],
            password_hash=get_password_hash(DEFAULT_ADMIN["password"]),
            email=DEFAULT_ADMIN["email"],
            role=DEFAULT_ADMIN["role"],
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return {"created": True, "username": admin.username, "email": admin.email}

    admin = db.query(User).filter(User.username == DEFAULT_ADMIN["username"]).first()
    if admin and admin.email != DEFAULT_ADMIN["email"]:
        admin.email = DEFAULT_ADMIN["email"]
        db.commit()

    return {
        "created": False,
        "username": DEFAULT_ADMIN["username"],
        "email": DEFAULT_ADMIN["email"],
    }

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token)

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role}


@router.post("/init-default-admin")
def init_default_admin(db: Session = Depends(get_db)):
    result = ensure_default_admin(db)
    if result["created"]:
        return {
            "message": "Default admin created",
            "username": result["username"],
            "email": result["email"],
        }

    return {
        "message": "Admin already exists",
        "username": result["username"],
        "email": result["email"],
    }
