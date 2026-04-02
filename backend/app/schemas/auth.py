"""Authentication Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Login request schema"""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    """User profile schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
