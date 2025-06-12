from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class NewsletterBase(BaseModel):
    """Base newsletter schema"""
    sender_email: EmailStr
    sender_name: Optional[str] = None
    newsletter_title: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None
    publication_frequency: Optional[str] = None

class NewsletterCreate(NewsletterBase):
    """Schema for creating newsletter"""
    pass

class NewsletterResponse(NewsletterBase):
    """Schema for newsletter response"""
    id: int
    average_length: Optional[int]
    first_detected_at: datetime
    last_received_at: Optional[datetime]
    total_emails_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

class UserNewsletterBase(BaseModel):
    """Base user newsletter subscription schema"""
    base_relevance_score: Optional[float] = Field(50.0, ge=0.0, le=100.0)
    is_subscribed: Optional[bool] = True

class UserNewsletterCreate(UserNewsletterBase):
    """Schema for creating user newsletter subscription"""
    newsletter_id: int

class UserNewsletterResponse(UserNewsletterBase):
    """Schema for user newsletter subscription response"""
    id: int
    newsletter_id: int
    subscribed_at: datetime
    last_received_at: Optional[datetime]
    total_received_count: int
    current_relevance_score: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Include newsletter details
    newsletter: NewsletterResponse
    
    class Config:
        from_attributes = True

class NewsletterEmailBase(BaseModel):
    """Base newsletter email schema"""
    subject: str = Field(..., max_length=1000)
    sender: str = Field(..., max_length=255)
    received_at: datetime
    content_length: Optional[int] = None
    snippet: Optional[str] = Field(None, max_length=500)

class NewsletterEmailResponse(NewsletterEmailBase):
    """Schema for newsletter email response"""
    id: int
    email_id: str
    newsletter_id: int
    thread_id: Optional[str]
    content_text: Optional[str]
    labels: Optional[str]
    has_been_opened: bool
    has_been_clicked: bool
    reading_time_seconds: Optional[int]
    engagement_score: float
    relevance_score: float
    summary_generated: bool
    key_takeaways: Optional[str]
    created_at: datetime
    analyzed_at: Optional[datetime]
    
    # Include newsletter details
    newsletter: NewsletterResponse
    
    class Config:
        from_attributes = True

class EmailConnectionBase(BaseModel):
    """Base email connection schema"""
    email_address: EmailStr
    provider: str = "gmail"
    sync_enabled: Optional[bool] = True
    sync_frequency_hours: Optional[int] = Field(6, ge=1, le=24)
    max_emails_per_sync: Optional[int] = Field(100, ge=10, le=1000)

class EmailConnectionCreate(EmailConnectionBase):
    """Schema for creating email connection"""
    pass

class EmailConnectionResponse(EmailConnectionBase):
    """Schema for email connection response"""
    id: int
    is_connected: bool
    connection_status: str
    last_sync_at: Optional[datetime]
    last_error: Optional[str]
    connected_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EmailSyncRequest(BaseModel):
    """Schema for email sync request"""
    max_emails: Optional[int] = Field(100, ge=1, le=500)
    days_back: Optional[int] = Field(7, ge=1, le=30)
    force_sync: Optional[bool] = False

class EmailSyncResponse(BaseModel):
    """Schema for email sync response"""
    status: str
    message: str
    emails_processed: int
    newsletters_detected: int
    new_newsletters: int
    errors: List[str] = []
    sync_started_at: datetime
    sync_completed_at: Optional[datetime]

class NewsletterStats(BaseModel):
    """Schema for newsletter statistics"""
    total_newsletters: int
    active_subscriptions: int
    total_emails: int
    emails_this_week: int
    emails_this_month: int
    top_categories: List[Dict[str, Any]]
    engagement_stats: Dict[str, float]

class NewsletterEmailSummary(BaseModel):
    """Schema for newsletter email summary"""
    email_id: int
    summary: str
    key_takeaways: List[str]
    main_topics: List[str]
    important_links: List[Dict[str, str]]
    reading_time_estimate: int  # in minutes

class NewsletterFeed(BaseModel):
    """Schema for personalized newsletter feed"""
    emails: List[NewsletterEmailResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    recommended_emails: List[NewsletterEmailResponse]

class NewsletterInteraction(BaseModel):
    """Schema for tracking newsletter interactions"""
    email_id: int
    interaction_type: str = Field(..., pattern="^(open|click|read|save|delete|unsubscribe)$")
    interaction_value: Optional[float] = None  # time spent, etc.
    context_data: Optional[Dict[str, Any]] = None