from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.models.newsletter import Newsletter, UserNewsletter, NewsletterEmail, EmailConnection
from app.schemas.newsletter import (
    NewsletterCreate, UserNewsletterCreate, EmailConnectionCreate,
    EmailSyncRequest
)

# Newsletter CRUD operations
def get_or_create_newsletter(db: Session, newsletter_data: Dict) -> Newsletter:
    """Get existing newsletter or create new one"""
    newsletter = db.query(Newsletter).filter(
        Newsletter.sender_email == newsletter_data['sender_email']
    ).first()
    
    if newsletter:
        # Update existing newsletter
        newsletter.last_received_at = datetime.now()
        newsletter.total_emails_count += 1
        if newsletter_data.get('newsletter_title') and not newsletter.newsletter_title:
            newsletter.newsletter_title = newsletter_data['newsletter_title']
        if newsletter_data.get('category') and not newsletter.category:
            newsletter.category = newsletter_data['category']
        
        db.commit()
        db.refresh(newsletter)
        return newsletter
    
    # Create new newsletter
    newsletter = Newsletter(
        sender_email=newsletter_data['sender_email'],
        sender_name=newsletter_data.get('sender_name'),
        newsletter_title=newsletter_data.get('newsletter_title'),
        domain=newsletter_data.get('domain'),
        category=newsletter_data.get('category'),
        publication_frequency=newsletter_data.get('publication_frequency'),
        average_length=newsletter_data.get('average_length', 0),
        total_emails_count=1,
        last_received_at=datetime.now()
    )
    
    db.add(newsletter)
    db.commit()
    db.refresh(newsletter)
    return newsletter

def get_newsletters(db: Session, skip: int = 0, limit: int = 100) -> List[Newsletter]:
    """Get all newsletters with pagination"""
    return db.query(Newsletter).filter(
        Newsletter.is_active == True
    ).order_by(desc(Newsletter.last_received_at)).offset(skip).limit(limit).all()

def get_newsletter_by_id(db: Session, newsletter_id: int) -> Optional[Newsletter]:
    """Get newsletter by ID"""
    return db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()

def search_newsletters(db: Session, query: str, limit: int = 20) -> List[Newsletter]:
    """Search newsletters by title, sender, or domain"""
    search_term = f"%{query}%"
    return db.query(Newsletter).filter(
        and_(
            Newsletter.is_active == True,
            (Newsletter.newsletter_title.ilike(search_term) |
             Newsletter.sender_email.ilike(search_term) |
             Newsletter.domain.ilike(search_term))
        )
    ).order_by(desc(Newsletter.total_emails_count)).limit(limit).all()

# User Newsletter Subscription CRUD
def create_user_newsletter_subscription(
    db: Session, 
    user_id: int, 
    newsletter_id: int,
    base_relevance_score: float = 50.0
) -> UserNewsletter:
    """Create user newsletter subscription"""
    # Check if subscription already exists
    existing = db.query(UserNewsletter).filter(
        and_(
            UserNewsletter.user_id == user_id,
            UserNewsletter.newsletter_id == newsletter_id
        )
    ).first()
    
    if existing:
        # Reactivate if it was deactivated
        existing.is_active = True
        existing.is_subscribed = True
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new subscription
    subscription = UserNewsletter(
        user_id=user_id,
        newsletter_id=newsletter_id,
        base_relevance_score=base_relevance_score,
        current_relevance_score=base_relevance_score
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

def get_user_newsletters(
    db: Session, 
    user_id: int, 
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[UserNewsletter]:
    """Get user's newsletter subscriptions"""
    query = db.query(UserNewsletter).filter(UserNewsletter.user_id == user_id)
    
    if active_only:
        query = query.filter(UserNewsletter.is_active == True)
    
    return query.order_by(desc(UserNewsletter.current_relevance_score)).offset(skip).limit(limit).all()

def update_user_newsletter_subscription(
    db: Session,
    user_id: int,
    newsletter_id: int,
    is_subscribed: Optional[bool] = None,
    relevance_score: Optional[float] = None
) -> Optional[UserNewsletter]:
    """Update user newsletter subscription"""
    subscription = db.query(UserNewsletter).filter(
        and_(
            UserNewsletter.user_id == user_id,
            UserNewsletter.newsletter_id == newsletter_id
        )
    ).first()
    
    if not subscription:
        return None
    
    if is_subscribed is not None:
        subscription.is_subscribed = is_subscribed
    
    if relevance_score is not None:
        subscription.current_relevance_score = relevance_score
    
    db.commit()
    db.refresh(subscription)
    return subscription

def unsubscribe_from_newsletter(db: Session, user_id: int, newsletter_id: int) -> bool:
    """Unsubscribe user from newsletter"""
    subscription = db.query(UserNewsletter).filter(
        and_(
            UserNewsletter.user_id == user_id,
            UserNewsletter.newsletter_id == newsletter_id
        )
    ).first()
    
    if subscription:
        subscription.is_subscribed = False
        subscription.is_active = False
        db.commit()
        return True
    
    return False

# Newsletter Email CRUD
def create_newsletter_email(
    db: Session,
    user_id: int,
    newsletter_id: int,
    email_data: Dict
) -> NewsletterEmail:
    """Create newsletter email record"""
    # Check if email already exists
    existing = db.query(NewsletterEmail).filter(
        and_(
            NewsletterEmail.user_id == user_id,
            NewsletterEmail.email_id == email_data['id']
        )
    ).first()
    
    if existing:
        return existing
    
    newsletter_email = NewsletterEmail(
        user_id=user_id,
        newsletter_id=newsletter_id,
        email_id=email_data['id'],
        message_id_header=email_data.get('message_id_header'),
        thread_id=email_data.get('thread_id'),
        subject=email_data['subject'],
        sender=email_data['sender_email'],
        received_at=email_data['received_at'],
        content_text=email_data.get('content_text'),
        content_html=email_data.get('content_html'),
        content_length=email_data.get('content_length', 0),
        labels=','.join(email_data.get('labels', [])),
        snippet=email_data.get('snippet')
    )
    
    db.add(newsletter_email)
    db.commit()
    db.refresh(newsletter_email)
    return newsletter_email

def get_newsletter_emails(
    db: Session,
    user_id: int,
    newsletter_id: Optional[int] = None,
    limit: int = 50,
    skip: int = 0
) -> List[NewsletterEmail]:
    """Get newsletter emails for user"""
    query = db.query(NewsletterEmail).filter(NewsletterEmail.user_id == user_id)
    
    if newsletter_id:
        query = query.filter(NewsletterEmail.newsletter_id == newsletter_id)
    
    return query.order_by(desc(NewsletterEmail.received_at)).offset(skip).limit(limit).all()

def get_newsletter_email_by_id(db: Session, email_id: int, user_id: int) -> Optional[NewsletterEmail]:
    """Get specific newsletter email"""
    return db.query(NewsletterEmail).filter(
        and_(
            NewsletterEmail.id == email_id,
            NewsletterEmail.user_id == user_id
        )
    ).first()

def update_newsletter_email_interaction(
    db: Session,
    email_id: int,
    user_id: int,
    interaction_data: Dict
) -> Optional[NewsletterEmail]:
    """Update newsletter email interaction data"""
    email_record = get_newsletter_email_by_id(db, email_id, user_id)
    
    if not email_record:
        return None
    
    # Update interaction fields
    if 'has_been_opened' in interaction_data:
        email_record.has_been_opened = interaction_data['has_been_opened']
    
    if 'has_been_clicked' in interaction_data:
        email_record.has_been_clicked = interaction_data['has_been_clicked']
    
    if 'reading_time_seconds' in interaction_data:
        email_record.reading_time_seconds = interaction_data['reading_time_seconds']
    
    if 'engagement_score' in interaction_data:
        email_record.engagement_score = interaction_data['engagement_score']
    
    db.commit()
    db.refresh(email_record)
    return email_record

# Email Connection CRUD
def create_email_connection(
    db: Session,
    user_id: int,
    connection_data: Dict
) -> EmailConnection:
    """Create or update email connection"""
    # Check if connection already exists
    existing = db.query(EmailConnection).filter(
        EmailConnection.user_id == user_id
    ).first()
    
    if existing:
        # Update existing connection
        existing.email_address = connection_data['email_address']
        existing.access_token = connection_data.get('access_token')
        existing.refresh_token = connection_data.get('refresh_token')
        existing.token_expires_at = connection_data.get('expires_at')
        existing.is_connected = True
        existing.connection_status = 'connected'
        existing.connected_at = datetime.now()
        existing.last_error = None
        
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new connection
    connection = EmailConnection(
        user_id=user_id,
        email_address=connection_data['email_address'],
        access_token=connection_data.get('access_token'),
        refresh_token=connection_data.get('refresh_token'),
        token_expires_at=connection_data.get('expires_at'),
        is_connected=True,
        connection_status='connected',
        connected_at=datetime.now()
    )
    
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

def get_email_connection(db: Session, user_id: int) -> Optional[EmailConnection]:
    """Get user's email connection"""
    return db.query(EmailConnection).filter(EmailConnection.user_id == user_id).first()

def update_email_connection_status(
    db: Session,
    user_id: int,
    status: str,
    error_message: str = None
) -> Optional[EmailConnection]:
    """Update email connection status"""
    connection = get_email_connection(db, user_id)
    
    if connection:
        connection.connection_status = status
        connection.is_connected = status == 'connected'
        connection.last_error = error_message
        
        if status == 'connected':
            connection.last_sync_at = datetime.now()
        
        db.commit()
        db.refresh(connection)
    
    return connection

def disconnect_email(db: Session, user_id: int) -> bool:
    """Disconnect user's email"""
    connection = get_email_connection(db, user_id)
    
    if connection:
        connection.is_connected = False
        connection.connection_status = 'disconnected'
        connection.access_token = None
        connection.refresh_token = None
        connection.token_expires_at = None
        
        db.commit()
        return True
    
    return False

# Analytics and Stats
def get_newsletter_stats(db: Session, user_id: int) -> Dict:
    """Get newsletter statistics for user"""
    try:
        # Total newsletters
        total_newsletters = db.query(Newsletter).join(UserNewsletter).filter(
            UserNewsletter.user_id == user_id
        ).count()
        
        # Active subscriptions
        active_subscriptions = db.query(UserNewsletter).filter(
            and_(
                UserNewsletter.user_id == user_id,
                UserNewsletter.is_active == True
            )
        ).count()
        
        # Total emails
        total_emails = db.query(NewsletterEmail).filter(
            NewsletterEmail.user_id == user_id
        ).count()
        
        # Emails this week
        week_ago = datetime.now() - timedelta(days=7)
        emails_this_week = db.query(NewsletterEmail).filter(
            and_(
                NewsletterEmail.user_id == user_id,
                NewsletterEmail.received_at >= week_ago
            )
        ).count()
        
        # Emails this month
        month_ago = datetime.now() - timedelta(days=30)
        emails_this_month = db.query(NewsletterEmail).filter(
            and_(
                NewsletterEmail.user_id == user_id,
                NewsletterEmail.received_at >= month_ago
            )
        ).count()
        
        # Top categories - handle case where user has no newsletters
        top_categories_query = db.query(
            Newsletter.category,
            func.count(NewsletterEmail.id).label('count')
        ).join(NewsletterEmail).filter(
            NewsletterEmail.user_id == user_id
        ).group_by(Newsletter.category).order_by(desc('count')).limit(5).all()
        
        top_categories = [
            {'category': cat or 'Unknown', 'count': count} 
            for cat, count in top_categories_query
        ] if top_categories_query else []
        
        return {
            'total_newsletters': total_newsletters,
            'active_subscriptions': active_subscriptions,
            'total_emails': total_emails,
            'emails_this_week': emails_this_week,
            'emails_this_month': emails_this_month,
            'top_categories': top_categories,
            'engagement_stats': {
                'average_relevance_score': 0.0,  # Calculate based on actual data
                'open_rate': 0.0,  # Calculate based on interaction data
                'click_rate': 0.0
            }
        }
    except Exception as e:
        # Return empty stats if there's an error
        return {
            'total_newsletters': 0,
            'active_subscriptions': 0,
            'total_emails': 0,
            'emails_this_week': 0,
            'emails_this_month': 0,
            'top_categories': [],
            'engagement_stats': {
                'average_relevance_score': 0.0,
                'open_rate': 0.0,
                'click_rate': 0.0
            }
        }