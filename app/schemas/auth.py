from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    email: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None

class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

class ChangePassword(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)