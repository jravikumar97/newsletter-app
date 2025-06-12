from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.core.auth import get_current_active_user
from app.schemas.newsletter import (
    EmailConnectionResponse, EmailSyncRequest, EmailSyncResponse,
    NewsletterResponse, UserNewsletterResponse, NewsletterStats,
    NewsletterEmailResponse
)
from app.models.user import User
from app.services.gmail_service import GmailService
from app.crud import newsletter as newsletter_crud
from app.core.config import settings

router = APIRouter()

@router.get("/oauth/authorize")
async def start_email_authorization(
    current_user: User = Depends(get_current_active_user)
):
    """Start Gmail OAuth authorization flow"""
    gmail_service = GmailService()
    
    try:
        auth_url = gmail_service.get_authorization_url()
        return {
            "authorization_url": auth_url,
            "message": "Visit the authorization URL to connect your Gmail account"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )

@router.get("/oauth/callback")
async def handle_oauth_callback(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Handle Gmail OAuth callback"""
    gmail_service = GmailService()
    
    try:
        # Exchange code for tokens
        token_data = gmail_service.exchange_code_for_tokens(code)
        
        # Create or update email connection
        connection_data = {
            'email_address': token_data['email'],
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at']
        }
        
        connection = newsletter_crud.create_email_connection(
            db, current_user.id, connection_data
        )
        
        return {
            "status": "success",
            "message": "Gmail account connected successfully",
            "email_address": connection.email_address,
            "connected_at": connection.connected_at
        }
        
    except Exception as e:
        # Update connection status with error
        newsletter_crud.update_email_connection_status(
            db, current_user.id, 'error', str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Gmail account: {str(e)}"
        )

@router.get("/connection", response_model=EmailConnectionResponse)
async def get_email_connection(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current email connection status"""
    connection = newsletter_crud.get_email_connection(db, current_user.id)
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email connection found"
        )
    
    return connection

@router.post("/sync", response_model=EmailSyncResponse)
async def sync_emails(
    sync_request: EmailSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync emails and detect newsletters"""
    # Get email connection
    connection = newsletter_crud.get_email_connection(db, current_user.id)
    
    if not connection or not connection.is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail account not connected"
        )
    
    # Start sync in background
    background_tasks.add_task(
        sync_user_emails,
        current_user.id,
        connection,
        sync_request,
        db
    )
    
    return EmailSyncResponse(
        status="started",
        message="Email sync started in background",
        emails_processed=0,
        newsletters_detected=0,
        new_newsletters=0,
        sync_started_at=datetime.now()
    )

async def sync_user_emails(
    user_id: int,
    connection,
    sync_request: EmailSyncRequest,
    db: Session
):
    """Background task to sync user emails"""
    from datetime import datetime
    
    try:
        # Update sync status
        newsletter_crud.update_email_connection_status(
            db, user_id, 'syncing'
        )
        
        # Initialize Gmail service
        gmail_service = GmailService()
        authenticated = gmail_service.authenticate_with_tokens(
            connection.access_token,
            connection.refresh_token,
            connection.token_expires_at.isoformat() if connection.token_expires_at else None
        )
        
        if not authenticated:
            newsletter_crud.update_email_connection_status(
                db, user_id, 'error', 'Authentication failed'
            )
            return
        
        # Sync emails
        sync_result = gmail_service.sync_emails(
            max_emails=sync_request.max_emails,
            days_back=sync_request.days_back
        )
        
        if sync_result['status'] == 'error':
            newsletter_crud.update_email_connection_status(
                db, user_id, 'error', sync_result.get('error')
            )
            return
        
        # Process newsletters
        new_newsletters = 0
        for newsletter_data in sync_result['newsletters']:
            email_data = newsletter_data['email_data']
            metadata = newsletter_data['newsletter_metadata']
            
            # Create or get newsletter
            newsletter = newsletter_crud.get_or_create_newsletter(db, metadata)
            
            # Create user subscription if it doesn't exist
            existing_subscription = db.query(newsletter_crud.UserNewsletter).filter(
                and_(
                    newsletter_crud.UserNewsletter.user_id == user_id,
                    newsletter_crud.UserNewsletter.newsletter_id == newsletter.id
                )
            ).first()
            
            if not existing_subscription:
                newsletter_crud.create_user_newsletter_subscription(
                    db, user_id, newsletter.id
                )
                new_newsletters += 1
            
            # Create email record
            newsletter_crud.create_newsletter_email(
                db, user_id, newsletter.id, email_data
            )
        
        # Update connection status
        newsletter_crud.update_email_connection_status(
            db, user_id, 'connected'
        )
        
    except Exception as e:
        newsletter_crud.update_email_connection_status(
            db, user_id, 'error', str(e)
        )

@router.delete("/disconnect")
async def disconnect_email(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disconnect email account"""
    success = newsletter_crud.disconnect_email(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email connection found"
        )
    
    return {"message": "Email account disconnected successfully"}

@router.get("/newsletters", response_model=List[UserNewsletterResponse])
async def get_my_newsletters(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's newsletter subscriptions"""
    newsletters = newsletter_crud.get_user_newsletters(
        db, current_user.id, skip=skip, limit=limit
    )
    return newsletters

@router.post("/newsletters/{newsletter_id}/subscribe")
async def subscribe_to_newsletter(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Subscribe to a newsletter"""
    # Check if newsletter exists
    newsletter = newsletter_crud.get_newsletter_by_id(db, newsletter_id)
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Create subscription
    subscription = newsletter_crud.create_user_newsletter_subscription(
        db, current_user.id, newsletter_id
    )
    
    return {
        "message": "Subscribed to newsletter successfully",
        "subscription_id": subscription.id
    }

@router.post("/newsletters/{newsletter_id}/unsubscribe")
async def unsubscribe_from_newsletter(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from a newsletter"""
    success = newsletter_crud.unsubscribe_from_newsletter(
        db, current_user.id, newsletter_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter subscription not found"
        )
    
    return {"message": "Unsubscribed from newsletter successfully"}

@router.get("/newsletters/{newsletter_id}/emails", response_model=List[NewsletterEmailResponse])
async def get_newsletter_emails(
    newsletter_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get emails from a specific newsletter"""
    emails = newsletter_crud.get_newsletter_emails(
        db, current_user.id, newsletter_id=newsletter_id, skip=skip, limit=limit
    )
    return emails

@router.get("/emails", response_model=List[NewsletterEmailResponse])
async def get_all_newsletter_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all newsletter emails for user"""
    emails = newsletter_crud.get_newsletter_emails(
        db, current_user.id, skip=skip, limit=limit
    )
    return emails

@router.get("/stats", response_model=NewsletterStats)
async def get_newsletter_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get newsletter statistics for user"""
    stats = newsletter_crud.get_newsletter_stats(db, current_user.id)
    return stats

@router.post("/emails/{email_id}/interaction")
async def track_email_interaction(
    email_id: int,
    interaction_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track user interaction with newsletter email"""
    email_record = newsletter_crud.update_newsletter_email_interaction(
        db, email_id, current_user.id, interaction_data
    )
    
    if not email_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter email not found"
        )
    
    return {"message": "Interaction tracked successfully"}

@router.get("/search")
async def search_newsletters(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search for newsletters"""
    newsletters = newsletter_crud.search_newsletters(db, q, limit)
    return newsletters