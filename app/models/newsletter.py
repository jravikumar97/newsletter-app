from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Newsletter(Base):
    """Newsletter model for storing detected newsletters"""
    
    __tablename__ = "newsletters"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Newsletter identification
    sender_email = Column(String(255), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    newsletter_title = Column(String(500), nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    
    # Newsletter characteristics
    category = Column(String(100), nullable=True)  # Auto-detected category
    publication_frequency = Column(String(50), nullable=True)  # daily, weekly, monthly
    average_length = Column(Integer, nullable=True)  # Average email length
    
    # Newsletter stats
    first_detected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_received_at = Column(DateTime(timezone=True), nullable=True)
    total_emails_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_subscriptions = relationship("UserNewsletter", back_populates="newsletter", cascade="all, delete-orphan")
    emails = relationship("NewsletterEmail", back_populates="newsletter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Newsletter(id={self.id}, sender='{self.sender_email}', title='{self.newsletter_title}')>"

class UserNewsletter(Base):
    """User's subscription to a newsletter"""
    
    __tablename__ = "user_newsletters"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=False)
    
    # Subscription info
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    last_received_at = Column(DateTime(timezone=True), nullable=True)
    total_received_count = Column(Integer, default=0)
    
    # Relevance scoring
    base_relevance_score = Column(Float, default=50.0)  # 0-100 scale
    current_relevance_score = Column(Float, default=50.0)  # Updated based on interactions
    
    # Status
    is_active = Column(Boolean, default=True)
    is_subscribed = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="newsletters")
    newsletter = relationship("Newsletter", back_populates="user_subscriptions")
    
    def __repr__(self):
        return f"<UserNewsletter(user_id={self.user_id}, newsletter_id={self.newsletter_id}, score={self.current_relevance_score})>"

class NewsletterEmail(Base):
    """Individual newsletter emails"""
    
    __tablename__ = "newsletter_emails"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=False)
    
    # Email identification
    email_id = Column(String(255), nullable=False)  # Gmail message ID
    message_id_header = Column(String(500), nullable=True)  # Email Message-ID header
    thread_id = Column(String(255), nullable=True)  # Gmail thread ID
    
    # Email content
    subject = Column(String(1000), nullable=False)
    sender = Column(String(255), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False)
    content_text = Column(Text, nullable=True)  # Plain text content
    content_html = Column(Text, nullable=True)  # HTML content
    content_length = Column(Integer, nullable=True)
    
    # Email metadata
    labels = Column(String(500), nullable=True)  # Gmail labels (JSON string)
    snippet = Column(String(500), nullable=True)  # Gmail snippet
    
    # User interaction tracking
    has_been_opened = Column(Boolean, default=False)
    has_been_clicked = Column(Boolean, default=False)
    reading_time_seconds = Column(Integer, nullable=True)
    
    # Scoring
    engagement_score = Column(Float, default=0.0)  # 0-100 based on user interaction
    relevance_score = Column(Float, default=50.0)  # 0-100 based on content analysis
    
    # Content analysis flags
    summary_generated = Column(Boolean, default=False)
    key_takeaways = Column(Text, nullable=True)  # JSON string of key points
    extracted_links = Column(Text, nullable=True)  # JSON string of important links
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    newsletter = relationship("Newsletter", back_populates="emails")
    
    def __repr__(self):
        return f"<NewsletterEmail(id={self.id}, subject='{self.subject[:50]}...', score={self.relevance_score})>"

class EmailConnection(Base):
    """User's email account connections"""
    
    __tablename__ = "email_connections"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Connection details
    email_address = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False, default="gmail")  # gmail, outlook, etc.
    
    # OAuth credentials (encrypted)
    access_token = Column(Text, nullable=True)  # Encrypted access token
    refresh_token = Column(Text, nullable=True)  # Encrypted refresh token
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Connection status
    is_connected = Column(Boolean, default=False)
    connection_status = Column(String(50), default="disconnected")  # connected, disconnected, error, expired
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True)
    sync_frequency_hours = Column(Integer, default=6)  # How often to sync
    max_emails_per_sync = Column(Integer, default=100)
    
    # Permissions
    permissions_granted = Column(String(500), nullable=True)  # JSON string of granted permissions
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="email_connection", uselist=False)
    
    def __repr__(self):
        return f"<EmailConnection(user_id={self.user_id}, email='{self.email_address}', status='{self.connection_status}')>"