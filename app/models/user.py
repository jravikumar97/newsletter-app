from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """User model for storing user information"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Personal information
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    
    # Location information
    location_city = Column(String(100), nullable=True)
    location_country = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Professional information
    job_title = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    education_level = Column(String(100), nullable=True)
    experience_level = Column(String(50), nullable=True)
    
    # Email integration
    email_connected = Column(Boolean, default=False)
    email_connected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Authentication tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", uselist=False)
    newsletters = relationship("UserNewsletter", back_populates="user", cascade="all, delete-orphan")
    email_connection = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"