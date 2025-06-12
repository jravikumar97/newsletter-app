from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.interest import UserInterest, UserPreference
from app.schemas.interest import (
    UserInterestCreate, UserInterestUpdate,
    UserPreferenceCreate, UserPreferenceUpdate
)

# User Interest CRUD operations
def create_user_interest(db: Session, user_id: int, interest: UserInterestCreate) -> UserInterest:
    """Create a new user interest"""
    db_interest = UserInterest(
        user_id=user_id,
        category=interest.category,
        subcategory=interest.subcategory,
        interest_level=interest.interest_level,
        keywords=interest.keywords
    )
    db.add(db_interest)
    db.commit()
    db.refresh(db_interest)
    return db_interest

def get_user_interests(db: Session, user_id: int) -> List[UserInterest]:
    """Get all interests for a user"""
    return db.query(UserInterest).filter(UserInterest.user_id == user_id).all()

def get_user_interest_by_id(db: Session, user_id: int, interest_id: int) -> Optional[UserInterest]:
    """Get a specific user interest by ID"""
    return db.query(UserInterest).filter(
        UserInterest.id == interest_id,
        UserInterest.user_id == user_id
    ).first()

def update_user_interest(
    db: Session, 
    user_id: int, 
    interest_id: int, 
    interest_update: UserInterestUpdate
) -> Optional[UserInterest]:
    """Update a user interest"""
    db_interest = get_user_interest_by_id(db, user_id, interest_id)
    if not db_interest:
        return None
    
    update_data = interest_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_interest, field, value)
    
    db.commit()
    db.refresh(db_interest)
    return db_interest

def delete_user_interest(db: Session, user_id: int, interest_id: int) -> bool:
    """Delete a user interest"""
    db_interest = get_user_interest_by_id(db, user_id, interest_id)
    if not db_interest:
        return False
    
    db.delete(db_interest)
    db.commit()
    return True

def create_bulk_interests(db: Session, user_id: int, interests: List[UserInterestCreate]) -> List[UserInterest]:
    """Create multiple interests for a user"""
    db_interests = []
    for interest in interests:
        db_interest = UserInterest(
            user_id=user_id,
            category=interest.category,
            subcategory=interest.subcategory,
            interest_level=interest.interest_level,
            keywords=interest.keywords
        )
        db_interests.append(db_interest)
    
    db.add_all(db_interests)
    db.commit()
    
    for db_interest in db_interests:
        db.refresh(db_interest)
    
    return db_interests

def get_interests_by_category(db: Session, user_id: int, category: str) -> List[UserInterest]:
    """Get user interests by category"""
    return db.query(UserInterest).filter(
        UserInterest.user_id == user_id,
        UserInterest.category == category
    ).all()

# User Preference CRUD operations
def create_user_preferences(db: Session, user_id: int, preferences: UserPreferenceCreate) -> UserPreference:
    """Create user preferences"""
    db_preferences = UserPreference(
        user_id=user_id,
        reading_time_preference=preferences.reading_time_preference,
        content_depth_preference=preferences.content_depth_preference,
        frequency_tolerance=preferences.frequency_tolerance,
        max_newsletters_per_day=preferences.max_newsletters_per_day,
        preferred_content_types=preferences.preferred_content_types,
        auto_summarize_enabled=1 if preferences.auto_summarize_enabled else 0
    )
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

def get_user_preferences(db: Session, user_id: int) -> Optional[UserPreference]:
    """Get user preferences"""
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

def update_user_preferences(
    db: Session, 
    user_id: int, 
    preferences_update: UserPreferenceUpdate
) -> Optional[UserPreference]:
    """Update user preferences"""
    db_preferences = get_user_preferences(db, user_id)
    
    if not db_preferences:
        # Create new preferences if they don't exist
        return create_user_preferences(db, user_id, UserPreferenceCreate(**preferences_update.dict()))
    
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'auto_summarize_enabled':
            value = 1 if value else 0
        setattr(db_preferences, field, value)
    
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

def delete_user_preferences(db: Session, user_id: int) -> bool:
    """Delete user preferences"""
    db_preferences = get_user_preferences(db, user_id)
    if not db_preferences:
        return False
    
    db.delete(db_preferences)
    db.commit()
    return True