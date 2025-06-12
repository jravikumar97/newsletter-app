from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class UserInterestBase(BaseModel):
    """Base schema for user interests"""
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    interest_level: float = Field(..., ge=1.0, le=10.0)
    keywords: Optional[str] = Field(None, max_length=500)

class UserInterestCreate(UserInterestBase):
    """Schema for creating user interest"""
    pass

class UserInterestUpdate(BaseModel):
    """Schema for updating user interest"""
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    interest_level: Optional[float] = Field(None, ge=1.0, le=10.0)
    keywords: Optional[str] = Field(None, max_length=500)

class UserInterestResponse(UserInterestBase):
    """Schema for user interest response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserPreferenceBase(BaseModel):
    """Base schema for user preferences"""
    reading_time_preference: Optional[str] = Field(None, pattern="^(morning|afternoon|evening)$")
    content_depth_preference: Optional[str] = Field(None, pattern="^(summary|detailed|mixed)$")
    frequency_tolerance: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    max_newsletters_per_day: Optional[int] = Field(None, ge=1, le=50)
    preferred_content_types: Optional[str] = Field(None, max_length=200)
    auto_summarize_enabled: Optional[bool] = True

class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences"""
    pass

class UserPreferenceUpdate(UserPreferenceBase):
    """Schema for updating user preferences"""
    pass

class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BulkInterestsCreate(BaseModel):
    """Schema for creating multiple interests at once"""
    interests: List[UserInterestCreate]

class InterestCategory(BaseModel):
    """Schema for interest categories"""
    category: str
    subcategories: List[str]
    description: Optional[str] = None