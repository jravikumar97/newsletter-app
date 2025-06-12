from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserInterest(Base):
    """User interests model for storing user's topic interests"""
    
    __tablename__ = "user_interests"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Interest information
    category = Column(String(100), nullable=False)  # e.g., "Technology", "Finance"
    subcategory = Column(String(100), nullable=True)  # e.g., "AI", "Cryptocurrency"
    interest_level = Column(Float, nullable=False, default=5.0)  # 1-10 scale
    
    # Keywords associated with this interest
    keywords = Column(String(500), nullable=True)  # Comma-separated keywords
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="interests")
    
    def __repr__(self):
        return f"<UserInterest(user_id={self.user_id}, category='{self.category}', level={self.interest_level})>"

class UserPreference(Base):
    """User preferences model for storing reading and content preferences"""
    
    __tablename__ = "user_preferences"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Reading preferences
    reading_time_preference = Column(String(20), nullable=True)  # "morning", "afternoon", "evening"
    content_depth_preference = Column(String(20), nullable=True)  # "summary", "detailed", "mixed"
    frequency_tolerance = Column(String(20), nullable=True)  # "daily", "weekly", "monthly"
    max_newsletters_per_day = Column(Integer, nullable=True, default=10)
    
    # Content preferences
    preferred_content_types = Column(String(200), nullable=True)  # JSON string
    auto_summarize_enabled = Column(Integer, nullable=False, default=1)  # Boolean as int
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="preferences", uselist=False)
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, reading_time='{self.reading_time_preference}')>"