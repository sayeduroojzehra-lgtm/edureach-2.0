from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.user import UserRole

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default=UserRole.STUDENT)
    standard: Optional[int] = Field(default=8, ge=1, le=10)

    @field_validator("email")
    def validate_email(cls, v):
        v = v.strip().lower()
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v

class UserLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(...)
    role: Optional[UserRole] = None
    name: Optional[str] = None
    standard: Optional[int] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    standard: Optional[int] = None
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    standard: Optional[int] = Field(None, ge=1, le=10)
