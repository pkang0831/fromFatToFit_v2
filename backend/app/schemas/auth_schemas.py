from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    ethnicity: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    consent_terms: bool = Field(False, description="Agreed to Terms of Service and Health Disclaimer")
    consent_privacy: bool = Field(False, description="Agreed to Privacy Policy including third-party AI processing")
    consent_sensitive_data: bool = Field(False, description="Consented to collection of sensitive personal data")
    consent_age_verification: bool = Field(False, description="Confirmed at least 18 years of age")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    age: Optional[int]
    gender: Optional[str]
    ethnicity: Optional[str]
    activity_level: Optional[str]
    calorie_goal: Optional[float]
    premium_status: bool
    onboarding_completed: bool = False
    created_at: datetime


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8)
