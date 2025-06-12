from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=13, le=120)
    location_city: Optional[str] = Field(None, max_length=100)
    location_country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    education_level: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=13, le=120)
    location_city: Optional[str] = Field(None, max_length=100)
    location_country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    education_level: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = Field(None, max_length=50)

class UserResponse(UserBase):
    """Schema for user response (without sensitive data)"""
    id: int
    is_active: bool
    is_verified: bool
    email_connected: bool
    email_connected_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    last_active_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None